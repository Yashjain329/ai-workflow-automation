import uuid
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.db_models import WorkflowJob, Prediction, Decision, ActionLog, ApprovalTask
from backend.schemas.pydantic_schemas import (
    JobCreate, WorkflowJobResponse, JobDetailResponse,
    PredictionResponse, DecisionResponse, ActionLogResponse
)
from backend.workflow.engine import WorkflowEngine
from backend.auth import get_api_key
from backend.config import settings
from backend.tasks import process_workflow_job

router = APIRouter(prefix="/jobs", tags=["Workflow Jobs"])

@router.post("", response_model=WorkflowJobResponse)
def create_job(payload: JobCreate, db: Session = Depends(get_db), api_key: str = Security(get_api_key)):
    """
    Submits a new workflow job for processing.
    """
    job_id = f"J-{uuid.uuid4().hex[:6].upper()}"
    job = WorkflowJob(
        job_id=job_id,
        source=payload.source,
        raw_payload=payload.raw_payload,
        category=payload.category_hint if payload.category_hint else "unknown",
        status="RECEIVED"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Process job using workflow engine or Celery based on configuration
    if settings.USE_CELERY:
        # Trigger asynchronous processing via Celery
        task = process_workflow_job.delay(job.job_id)  # Pass the business job_id string
        # For now, we return the job immediately and the client can poll for status
        # In a more advanced implementation, we would return a task ID for tracking
        db.refresh(job)  # Ensure we have the latest state
        return job
    else:
        # Synchronous processing (original behavior)
        engine = WorkflowEngine(db)
        processed_job = engine.process_job(job.job_id)
        return processed_job

@router.get("", response_model=List[WorkflowJobResponse])
def list_jobs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), api_key: str = Security(get_api_key)):
    """
    Lists all submitted workflow jobs.
    """
    jobs = db.query(WorkflowJob).order_by(WorkflowJob.created_at.desc()).offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job_detail(job_id: str, db: Session = Depends(get_db), api_key: str = Security(get_api_key)):
    """
    Retrieves full execution trace, prediction, decision, and logs for a job.
    """
    job = db.query(WorkflowJob).filter(WorkflowJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    pred = db.query(Prediction).filter(Prediction.job_id == job_id).first()
    dec = db.query(Decision).filter(Decision.job_id == job_id).first()
    logs = db.query(ActionLog).filter(ActionLog.job_id == job_id).all()
    task = db.query(ApprovalTask).filter(ApprovalTask.job_id == job_id).first()

    pred_res = PredictionResponse.model_validate(pred) if pred else None
    dec_res = DecisionResponse.model_validate(dec) if dec else None
    logs_res = [ActionLogResponse.model_validate(l) for l in logs]
    task_dict = {
        "task_id": task.task_id,
        "reason": task.reason,
        "confidence": task.confidence,
        "decision": task.decision,
        "reviewer": task.reviewer
    } if task else None

    return JobDetailResponse(
        job=WorkflowJobResponse.model_validate(job),
        prediction=pred_res,
        decision=dec_res,
        action_logs=logs_res,
        approval_task=task_dict
    )

@router.post("/{job_id}/retry", response_model=WorkflowJobResponse)
def retry_job(job_id: str, db: Session = Depends(get_db), api_key: str = Security(get_api_key)):
    """
    Retries processing for a failed or rejected job.
    """
    job = db.query(WorkflowJob).filter(WorkflowJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job.status = "RECEIVED"
    job.error_code = None
    db.commit()

    # Retry using workflow engine or Celery based on configuration
    if settings.USE_CELERY:
        task = process_workflow_job.delay(job.job_id)
        db.refresh(job)
        return job
    else:
        engine = WorkflowEngine(db)
        return engine.process_job(job.job_id)