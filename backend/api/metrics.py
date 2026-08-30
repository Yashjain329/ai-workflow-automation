from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.db_models import WorkflowJob, Prediction, ApprovalTask
from backend.schemas.pydantic_schemas import OperationalMetricsResponse

router = APIRouter(prefix="/metrics", tags=["Operational Metrics"])

@router.get("", response_model=OperationalMetricsResponse)
def get_operational_metrics(db: Session = Depends(get_db)):
    """
    Computes key dissertation research metrics: automation rate, escalation rate, failure rate, and average confidence.
    """
    total_jobs = db.query(func.count(WorkflowJob.job_id)).scalar() or 0
    if total_jobs == 0:
        return OperationalMetricsResponse(
            total_jobs=0,
            completed_jobs=0,
            failed_jobs=0,
            pending_approvals=0,
            automation_rate=0.0,
            escalation_rate=0.0,
            failure_rate=0.0,
            avg_confidence=0.0
        )

    completed_jobs = db.query(func.count(WorkflowJob.job_id)).filter(WorkflowJob.status == "AUDITED").scalar() or 0
    failed_jobs = db.query(func.count(WorkflowJob.job_id)).filter(WorkflowJob.status == "FAILED").scalar() or 0
    pending_approvals = db.query(func.count(ApprovalTask.task_id)).filter(ApprovalTask.decision == "PENDING").scalar() or 0
    
    escalated_count = db.query(func.count(WorkflowJob.job_id)).filter(WorkflowJob.human_intervention == True).scalar() or 0
    auto_completed_count = completed_jobs - db.query(func.count(WorkflowJob.job_id)).filter(
        WorkflowJob.status == "AUDITED", WorkflowJob.human_intervention == True
    ).scalar() or 0

    automation_rate = round((auto_completed_count / total_jobs) * 100, 2)
    escalation_rate = round((escalated_count / total_jobs) * 100, 2)
    failure_rate = round((failed_jobs / total_jobs) * 100, 2)

    avg_conf = db.query(func.avg(Prediction.confidence)).scalar() or 0.0

    return OperationalMetricsResponse(
        total_jobs=total_jobs,
        completed_jobs=completed_jobs,
        failed_jobs=failed_jobs,
        pending_approvals=pending_approvals,
        automation_rate=automation_rate,
        escalation_rate=escalation_rate,
        failure_rate=failure_rate,
        avg_confidence=round(float(avg_conf), 2)
    )
