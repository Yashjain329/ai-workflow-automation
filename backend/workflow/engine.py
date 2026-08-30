import uuid
import datetime
import time
from sqlalchemy.orm import Session
from backend.config import settings
from backend.models.db_models import WorkflowJob, Prediction, Decision, WorkflowStep, ActionLog, ApprovalTask
from backend.workflow.state_machine import StateMachine, WorkflowState
from backend.services.ingestion import IngestionService
from backend.models.classifier import MLTaskClassifier
from backend.models.extractor import FieldExtractor
from backend.policy.rules import PolicyRules
from backend.policy.hybrid_engine import HybridDecisionEngine
from backend.connectors.database_connector import DatabaseConnector
from backend.connectors.notification_connector import NotificationConnector

class WorkflowEngine:
    def __init__(self, db: Session):
        self.db = db
        self.classifier = MLTaskClassifier()

    def process_job(self, job_id: str) -> WorkflowJob:
        """
        Executes end-to-end workflow processing for a job.
        """
        job = self.db.query(WorkflowJob).filter(WorkflowJob.job_id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")

        try:
            # 1. VALIDATING
            self._transition_state(job, WorkflowState.VALIDATING)
            norm_text, metadata = IngestionService.process_payload(job.raw_payload, job.source)
            job.normalized_text = norm_text

            # 2. CLASSIFIED
            self._transition_state(job, WorkflowState.CLASSIFIED)
            category, confidence = self.classifier.predict(norm_text)
            job.category = category

            # Record Prediction
            pred = Prediction(
                job_id=job.job_id,
                model_version=self.classifier.model_name,
                predicted_category=category,
                confidence=confidence
            )
            self.db.add(pred)

            # 3. EXTRACTED
            self._transition_state(job, WorkflowState.EXTRACTED)
            extracted_fields = FieldExtractor.extract_fields(norm_text, category)
            pred.extracted_fields = extracted_fields

            # 4. DECIDING
            self._transition_state(job, WorkflowState.DECIDING)
            risk_level, rules_applied = PolicyRules.evaluate_policy(category, extracted_fields)
            route, explanation = HybridDecisionEngine.make_decision(confidence, risk_level, rules_applied)

            dec = Decision(
                job_id=job.job_id,
                route=route,
                policy_version="policy-v1.0",
                risk_level=risk_level,
                explanation=explanation,
                rules_applied=rules_applied
            )
            self.db.add(dec)

            # Route Handling
            if route == "auto_approve":
                self._execute_actions_with_retry(job, category, extracted_fields)
            elif route == "human_approval":
                self._escalate_to_human(job, explanation, confidence)
            else:
                # Reject
                job.status = WorkflowState.FAILED.value
                job.error_code = "ERR_HYBRID_REJECTED"
                self._log_action(job, "decision_engine", "FAILED", explanation, "ERR_REJECTED", 0)

            self.db.commit()
            return job

        except Exception as e:
            self.db.rollback()
            job.status = WorkflowState.FAILED.value
            job.error_code = f"ERR_UNHANDLED: {str(e)}"
            self.db.commit()
            raise e

    def approve_human_task(self, task_id: str, decision: str, reviewer: str) -> WorkflowJob:
        """
        Processes human approval queue decision.
        """
        task = self.db.query(ApprovalTask).filter(ApprovalTask.task_id == task_id).first()
        if not task:
            raise ValueError(f"Approval task {task_id} not found")

        job = task.job
        task.decision = decision
        task.reviewer = reviewer
        task.decided_at = datetime.datetime.utcnow()

        if decision == "APPROVED":
            self._transition_state(job, WorkflowState.APPROVAL_APPROVED)
            pred = self.db.query(Prediction).filter(Prediction.job_id == job.job_id).first()
            extracted = pred.extracted_fields if pred else {}
            self._execute_actions_with_retry(job, job.category, extracted)
        else:
            self._transition_state(job, WorkflowState.APPROVAL_REJECTED)
            job.status = WorkflowState.FAILED.value
            job.error_code = "ERR_HUMAN_REJECTED"

        self.db.commit()
        return job

    def _execute_actions_with_retry(self, job: WorkflowJob, category: str, extracted_fields: dict):
        """
        Executes external connectors with a real retry loop up to settings.MAX_RETRIES.
        """
        self._transition_state(job, WorkflowState.EXECUTING)
        
        # 1. Database Connector with real retry loop
        db_success = False
        last_db_err = ""
        for attempt in range(1, settings.MAX_RETRIES + 1):
            success, result_msg, err_code, is_dup = DatabaseConnector.execute_action(
                job.job_id, category, extracted_fields, attempt=attempt
            )
            if success:
                db_success = True
                self._log_action(job, "database_connector", "SUCCESS", result_msg, "", attempt)
                break
            else:
                last_db_err = err_code
                self._log_action(job, "database_connector", "RETRYING" if attempt < settings.MAX_RETRIES else "FAILURE", result_msg, err_code, attempt)

        # 2. Notification Connector with real retry loop
        mail_success = False
        last_mail_err = ""
        if db_success:
            for attempt in range(1, settings.MAX_RETRIES + 1):
                success, result_msg, err_code = NotificationConnector.send_notification(
                    job.job_id, "finance-team@org.internal", f"Workflow execution completed for Job {job.job_id}", attempt=attempt
                )
                if success:
                    mail_success = True
                    self._log_action(job, "notification_connector", "SUCCESS", result_msg, "", attempt)
                    break
                else:
                    last_mail_err = err_code
                    self._log_action(job, "notification_connector", "RETRYING" if attempt < settings.MAX_RETRIES else "FAILURE", result_msg, err_code, attempt)

        # 3. Final State Resolution
        if db_success and mail_success:
            self._transition_state(job, WorkflowState.COMPLETED)
            self._transition_state(job, WorkflowState.AUDITED)
        else:
            job.status = WorkflowState.FAILED.value
            job.error_code = last_db_err or last_mail_err or "ERR_ACTION_EXECUTION_FAILED"

    def _escalate_to_human(self, job: WorkflowJob, reason: str, confidence: float):
        self._transition_state(job, WorkflowState.APPROVAL_PENDING)
        job.human_intervention = True

        task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
        task = ApprovalTask(
            task_id=task_id,
            job_id=job.job_id,
            reason=reason,
            confidence=confidence,
            decision="PENDING"
        )
        self.db.add(task)
        self._log_action(job, "approval_queue", "ESCALATED", f"Escalated to Human Queue: {reason}", "", 0)

    def _transition_state(self, job: WorkflowJob, new_state: WorkflowState):
        StateMachine.validate_transition(job.status, new_state.value)
        job.status = new_state.value
        
        step = WorkflowStep(
            job_id=job.job_id,
            step_name=f"Transition to {new_state.value}",
            step_type=new_state.value.lower(),
            status="COMPLETED",
            started_at=datetime.datetime.utcnow(),
            completed_at=datetime.datetime.utcnow()
        )
        self.db.add(step)

    def _log_action(self, job: WorkflowJob, connector: str, status: str, result: str, error_code: str, retry_count: int = 0):
        log = ActionLog(
            job_id=job.job_id,
            connector=connector,
            status=status,
            result=result,
            error_code=error_code,
            retry_count=retry_count
        )
        self.db.add(log)
