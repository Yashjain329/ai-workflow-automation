import uuid
import datetime
from sqlalchemy.orm import Session
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
                self._execute_actions(job, category, extracted_fields)
            elif route == "human_approval":
                self._escalate_to_human(job, explanation, confidence)
            else:
                # Reject
                job.status = WorkflowState.FAILED.value
                job.error_code = "ERR_HYBRID_REJECTED"
                self._log_action(job, "decision_engine", "FAILED", explanation, "ERR_REJECTED")
                self._transition_state(job, WorkflowState.AUDITED)

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
            self._execute_actions(job, job.category, extracted)
        else:
            self._transition_state(job, WorkflowState.APPROVAL_REJECTED)
            job.status = WorkflowState.FAILED.value
            job.error_code = "ERR_HUMAN_REJECTED"
            self._transition_state(job, WorkflowState.AUDITED)

        self.db.commit()
        return job

    def _execute_actions(self, job: WorkflowJob, category: str, extracted_fields: dict):
        self._transition_state(job, WorkflowState.EXECUTING)
        
        # Action 1: Database update
        success_db, result_db, err_db = DatabaseConnector.execute_action(job.job_id, category, extracted_fields)
        self._log_action(job, "database_connector", "SUCCESS" if success_db else "FAILURE", result_db, err_db)

        # Action 2: Notification
        success_mail, result_mail, err_mail = NotificationConnector.send_notification(
            job.job_id, "finance-team@org.internal", f"Workflow execution completed for Job {job.job_id}"
        )
        self._log_action(job, "notification_connector", "SUCCESS" if success_mail else "FAILURE", result_mail, err_mail)

        if success_db and success_mail:
            self._transition_state(job, WorkflowState.COMPLETED)
            self._transition_state(job, WorkflowState.AUDITED)
        else:
            job.status = WorkflowState.FAILED.value
            job.error_code = "ERR_ACTION_EXECUTION_FAILED"
            self._transition_state(job, WorkflowState.AUDITED)

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
        self._log_action(job, "approval_queue", "ESCALATED", f"Escalated to Human Queue: {reason}", "")

    def _transition_state(self, job: WorkflowJob, new_state: WorkflowState):
        StateMachine.validate_transition(job.status, new_state.value)
        job.status = new_state.value
        
        # Log Step
        step = WorkflowStep(
            job_id=job.job_id,
            step_name=f"Transition to {new_state.value}",
            step_type=new_state.value.lower(),
            status="COMPLETED",
            started_at=datetime.datetime.utcnow(),
            completed_at=datetime.datetime.utcnow()
        )
        self.db.add(step)

    def _log_action(self, job: WorkflowJob, connector: str, status: str, result: str, error_code: str):
        log = ActionLog(
            job_id=job.job_id,
            connector=connector,
            status=status,
            result=result,
            error_code=error_code,
            retry_count=0
        )
        self.db.add(log)
