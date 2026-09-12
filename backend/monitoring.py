"""
Monitoring service for collecting model performance, data drift, and system metrics.
"""
import datetime
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from backend.config import settings
from backend.database import SessionLocal
from backend.models.monitoring_models import (
    ModelPerformanceMetrics, DataDriftMetrics, SystemPerformanceMetrics
)
from backend.models.db_models import WorkflowJob, Prediction, Decision, ApprovalTask
from backend.workflow.engine import WorkflowEngine

logger = logging.getLogger(__name__)

class MonitoringService:
    """Service for collecting and storing monitoring metrics."""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self._owns_session = db is None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._owns_session:
            self.db.close()
    
    def collect_model_performance_metrics(self, model_version: str = None, 
                                        hours_back: int = 24) -> ModelPerformanceMetrics:
        """
        Collect and store model performance metrics based on jobs with ground truth.
        
        Args:
            model_version: Specific model version to evaluate (defaults to current)
            hours_back: How many hours back to look for data
            
        Returns:
            ModelPerformanceMetrics object that was stored
        """
        start_time = time.time()
        
        if model_version is None:
            model_version = settings.MODEL_VERSION if hasattr(settings, 'MODEL_VERSION') else "tf-idf-logreg-v1"
        
        # Calculate time window
        since_time = datetime.datetime.utcnow() - datetime.timedelta(hours=hours_back)
        
        # Query jobs with predictions and decisions (ground truth from human approval or auto-execution)
        # We'll use jobs that have reached AUDITED state as having ground truth
        jobs_query = self.db.query(WorkflowJob).filter(
            and_(
                WorkflowJob.status == "AUDITED",
                WorkflowJob.updated_at >= since_time
            )
        )
        
        jobs = jobs_query.all()
        
        if not jobs:
            logger.warning(f"No audited jobs found in the last {hours_back} hours for model performance evaluation")
            # Return empty metrics
            metrics = ModelPerformanceMetrics(
                model_version=model_version,
                model_type="TF-IDF-LogReg",
                sample_size=0
            )
            self.db.add(metrics)
            self.db.commit()
            return metrics
        
        # Get predictions for these jobs
        job_ids = [job.job_id for job in jobs]
        predictions = self.db.query(Prediction).filter(
            Prediction.job_id.in_(job_ids)
        ).all()
        
        # Get decisions to determine actual outcomes
        decisions = self.db.query(Decision).filter(
            Decision.job_id.in_(job_ids)
        ).all()
        
        # Create mappings for easy lookup
        pred_map = {p.job_id: p for p in predictions}
        dec_map = {d.job_id: d for d in decisions}
        
        # For now, we'll use a simplified approach:
        # - Correct prediction if the predicted category matches the job's final category
        # - We'll need to enhance this when we have explicit ground truth labels
        
        correct_predictions = 0
        total_predictions = len(predictions)
        confidences = []
        category_counts = {"invoice": 0, "service_request": 0, "unknown": 0}
        confidence_ranges = {"high": 0, "medium": 0, "low": 0}
        
        for job in jobs:
            pred = pred_map.get(job.job_id)
            if not pred:
                continue
                
            confidences.append(pred.confidence)
            
            # Count by category
            category = pred.predicted_category
            if category in category_counts:
                category_counts[category] += 1
            
            # Count by confidence range
            if pred.confidence >= settings.CONFIDENCE_HIGH:
                confidence_ranges["high"] += 1
            elif pred.confidence >= settings.CONFIDENCE_MEDIUM:
                confidence_ranges["medium"] += 1
            else:
                confidence_ranges["low"] += 1
            
            # Simplified correctness check: 
            # In a real system, we would compare against explicit ground truth
            # For now, we'll consider a prediction "correct" if it led to auto-approval 
            # and the job completed successfully, or if it led to human approval and 
            # the human approved it
            dec = dec_map.get(job.job_id)
            is_correct = False
            
            if dec:
                if dec.route == "auto_approve" and job.status == "AUDITED":
                    is_correct = True  # Auto-approved and completed successfully
                elif dec.route == "human_approval":
                    # Find the approval task and check if it was approved
                    approval_task = self.db.query(ApprovalTask).filter(
                        ApprovalTask.job_id == job.job_id
                    ).first()
                    if approval_task and approval_task.decision == "APPROVED":
                        is_correct = True  # Human approved
                    elif approval_task and approval_task.decision == "REJECTED":
                        is_correct = False  # Human rejected
                    else:
                        # Still pending - we can't determine correctness yet
                        pass
            
            if is_correct:
                correct_predictions += 1
        
        # Calculate metrics
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Calculate confidence std (simplified)
        if len(confidences) > 1:
            variance = sum((c - avg_confidence) ** 2 for c in confidences) / len(confidences)
            confidence_std = variance ** 0.5
        else:
            confidence_std = 0.0
        
        # Create and store metrics
        computation_time_ms = int((time.time() - start_time) * 1000)
        
        metrics = ModelPerformanceMetrics(
            model_version=model_version,
            model_type="TF-IDF-LogReg",
            accuracy=accuracy,
            precision=accuracy,  # Simplified - in reality would need per-class metrics
            recall=accuracy,     # Simplified
            f1_score=accuracy,   # Simplified
            avg_confidence=avg_confidence,
            confidence_std=confidence_std,
            high_confidence_count=confidence_ranges["high"],
            medium_confidence_count=confidence_ranges["medium"],
            low_confidence_count=confidence_ranges["low"],
            invoice_predictions=category_counts["invoice"],
            service_request_predictions=category_counts["service_request"],
            unknown_predictions=category_counts["unknown"],
            sample_size=total_predictions,
            computation_time_ms=computation_time_ms
        )
        
        self.db.add(metrics)
        self.db.commit()
        self.db.refresh(metrics)
        
        logger.info(f"Collected model performance metrics: accuracy={accuracy:.3f}, avg_confidence={avg_confidence:.3f}")
        return metrics
    
    def collect_system_performance_metrics(self, hours_back: int = 1) -> SystemPerformanceMetrics:
        """
        Collect and store system performance metrics.
        
        Args:
            hours_back: How many hours back to look for data
            
        Returns:
            SystemPerformanceMetrics object that was stored
        """
        start_time = time.time()
        
        # Calculate time window
        since_time = datetime.datetime.utcnow() - datetime.timedelta(hours=hours_back)
        
        # Query jobs in the time window
        jobs_query = self.db.query(WorkflowJob).filter(
            WorkflowJob.created_at >= since_time
        )
        
        jobs = jobs_query.all()
        
        if not jobs:
            logger.warning(f"No jobs found in the last {hours_back} hours for system performance evaluation")
            metrics = SystemPerformanceMetrics(timestamp=datetime.datetime.utcnow())
            self.db.add(metrics)
            self.db.commit()
            return metrics
        
        total_jobs = len(jobs)
        
        # Count by status
        completed_jobs = sum(1 for job in jobs if job.status == "AUDITED")
        failed_jobs = sum(1 for job in jobs if job.status == "FAILED")
        pending_approvals = self.db.query(ApprovalTask).filter(
            and_(
                ApprovalTask.decision == "PENDING",
                ApprovalTask.created_at >= since_time
            )
        ).count()
        
        # Calculate rates
        automation_rate = 0.0
        escalation_rate = 0.0
        failure_rate = failed_jobs / total_jobs if total_jobs > 0 else 0.0
        
        # To calculate automation and escalation rates, we need to check decisions
        auto_completed = 0
        escalated = 0
        
        for job in jobs:
            decision = self.db.query(Decision).filter(
                Decision.job_id == job.job_id
            ).first()
            
            if decision:
                if decision.route == "auto_approve" and job.status == "AUDITED":
                    auto_completed += 1
                elif decision.route == "human_approval":
                    escalated += 1
        
        automation_rate = auto_completed / total_jobs if total_jobs > 0 else 0.0
        escalation_rate = escalated / total_jobs if total_jobs > 0 else 0.0
        
        # Calculate average latencies (we don't have detailed timing yet, so we'll use placeholders)
        # In a real implementation, we would store timing information in the workflow steps
        avg_latency_total = 0.0
        avg_latency_ingestion = 0.0
        avg_latency_classification = 0.0
        avg_latency_extraction = 0.0
        avg_latency_decision = 0.0
        avg_latency_execution = 0.0
        
        # Calculate retry metrics from action logs
        action_logs = self.db.query(ActionLog).filter(
            ActionLog.created_at >= since_time
        ).all()
        
        retry_counts = [log.retry_count for log in action_logs if log.retry_count > 0]
        avg_retry_count = sum(retry_counts) / len(retry_counts) if retry_counts else 0.0
        max_retry_count = max(retry_counts) if retry_counts else 0
        
        # Count errors by type (simplified)
        error_count_total = sum(1 for job in jobs if job.error_code is not None)
        error_count_database = sum(1 for job in jobs if job.error_code and "DB" in job.error_code)
        error_count_notification = sum(1 for job in jobs if job.error_code and "NOTIF" in job.error_code)
        error_count_validation = sum(1 for job in jobs if job.error_code and "VALID" in job.error_code)
        
        # Calculate throughput (jobs per minute)
        time_window_minutes = hours_back * 60
        jobs_processed_per_minute = total_jobs / time_window_minutes if time_window_minutes > 0 else 0
        jobs_completed_per_minute = completed_jobs / time_window_minutes if time_window_minutes > 0 else 0
        jobs_failed_per_minute = failed_jobs / time_window_minutes if time_window_minutes > 0 else 0
        
        # Create and store metrics
        computation_time_ms = int((time.time() - start_time) * 1000)
        
        metrics = SystemPerformanceMetrics(
            timestamp=datetime.datetime.utcnow(),
            jobs_processed_per_minute=jobs_processed_per_minute,
            jobs_completed_per_minute=jobs_completed_per_minute,
            jobs_failed_per_minute=jobs_failed_per_minute,
            jobs_pending_approval=pending_approvals,
            avg_latency_total=avg_latency_total,
            avg_latency_ingestion=avg_latency_ingestion,
            avg_latency_classification=avg_latency_classification,
            avg_latency_extraction=avg_latency_extraction,
            avg_latency_decision=avg_latency_decision,
            avg_latency_execution=avg_latency_execution,
            automation_rate=automation_rate,
            escalation_rate=escalation_rate,
            failure_rate=failure_rate,
            error_count_total=error_count_total,
            error_count_database=error_count_database,
            error_count_notification=error_count_notification,
            error_count_validation=error_count_validation,
            avg_retry_count=avg_retry_count,
            max_retry_count=max_retry_count
        )
        
        self.db.add(metrics)
        self.db.commit()
        self.db.refresh(metrics)
        
        logger.info(f"Collected system performance metrics: {total_jobs} jobs processed, "
                   f"automation_rate={automation_rate:.3f}")
        return metrics
    
    def collect_data_drift_metrics(self, hours_back: int = 24) -> DataDriftMetrics:
        """
        Collect and store data drift metrics by comparing recent data to a reference period.
        
        Args:
            hours_back: How many hours back to look for current data
            
        Returns:
            DataDriftMetrics object that was stored
        """
        # For now, we'll implement a simplified version
        # A full implementation would:
        # 1. Define a reference period (e.g., training data or last week)
        # 2. Extract features from text data in both periods
        # 3. Perform statistical tests (KS test, chi-square) to detect drift
        # 4. Store the results
        
        # Placeholder implementation
        metrics = DataDriftMetrics(
            timestamp=datetime.datetime.utcnow(),
            drift_detected=False,
            drift_score=0.0,
            feature_drift_scores={},
            ks_test_p_value=1.0,
            chi_square_p_value=1.0,
            sample_size_reference=0,
            sample_size_current=0
        )
        
        self.db.add(metrics)
        self.db.commit()
        self.db.refresh(metrics)
        
        logger.info("Collected data drift metrics (placeholder implementation)")
        return metrics
    
    def run_collection_cycle(self):
        """Run a full collection cycle for all metric types."""
        try:
            logger.info("Starting monitoring collection cycle")
            
            # Collect model performance (last 24 hours)
            self.collect_model_performance_metrics(hours_back=24)
            
            # Collect system performance (last hour)
            self.collect_system_performance_metrics(hours_back=1)
            
            # Collect data drift (last 24 hours vs reference)
            self.collect_data_drift_metrics(hours_back=24)
            
            logger.info("Monitoring collection cycle completed")
            
        except Exception as e:
            logger.error(f"Error during monitoring collection: {e}")
            self.db.rollback()
            raise
        finally:
            if self._owns_session:
                self.db.close()

def collect_metrics():
    """Convenience function to run a monitoring collection cycle."""
    with MonitoringService() as service:
        service.run_collection_cycle()