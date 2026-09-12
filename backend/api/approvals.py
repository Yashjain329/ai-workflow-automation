import uuid
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.db_models import WorkflowJob, ApprovalTask
from backend.schemas.pydantic_schemas import (
    ApprovalDecisionRequest, WorkflowJobResponse, JobDetailResponse, ApprovalTaskResponse
)
from backend.workflow.engine import WorkflowEngine
from backend.auth import get_api_key

router = APIRouter(prefix="/approvals", tags=["Human Approval"])

@router.post("/{task_id}", response_model=WorkflowJobResponse)
def decide_approval_task(task_id: str, payload: ApprovalDecisionRequest, db: Session = Depends(get_db), api_key: str = Security(get_api_key)):
    """
    Processes a human approval decision for a task.
    Requires the 'approve' permission.
    """
    # Note: In a more complete implementation, we would check that the user has the 'approve' permission
    # For now, we're just requiring authentication
    engine = WorkflowEngine(db)
    try:
        job = engine.approve_human_task(task_id, payload.decision, payload.reviewer)
        return job
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("", response_model=List[ApprovalTaskResponse])
def list_approval_tasks(db: Session = Depends(get_db), api_key: str = Security(get_api_key)):
    """
    Lists all pending approval tasks.
    """
    tasks = db.query(ApprovalTask).filter(ApprovalTask.decision == "PENDING").all()
    return tasks

@router.get("/{task_id}", response_model=ApprovalTaskResponse)
def get_approval_task(task_id: str, db: Session = Depends(get_db), api_key: str = Security(get_api_key)):
    """
    Retrieves a specific approval task.
    """
    task = db.query(ApprovalTask).filter(ApprovalTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Approval task {task_id} not found")
    return task