from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.db_models import ApprovalTask
from backend.schemas.pydantic_schemas import ApprovalTaskResponse, ApprovalDecisionRequest, WorkflowJobResponse
from backend.workflow.engine import WorkflowEngine

router = APIRouter(prefix="/approvals", tags=["Human Approval Queue"])

@router.get("", response_model=List[ApprovalTaskResponse])
def list_pending_approvals(db: Session = Depends(get_db)):
    """
    Lists tasks waiting in the human approval queue.
    """
    tasks = db.query(ApprovalTask).filter(ApprovalTask.decision == "PENDING").order_by(ApprovalTask.created_at.desc()).all()
    return tasks

@router.post("/{task_id}/decision", response_model=WorkflowJobResponse)
def submit_approval_decision(task_id: str, payload: ApprovalDecisionRequest, db: Session = Depends(get_db)):
    """
    Submits a human approval decision (APPROVED or REJECTED).
    """
    if payload.decision not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Decision must be 'APPROVED' or 'REJECTED'")

    engine = WorkflowEngine(db)
    try:
        updated_job = engine.approve_human_task(task_id, payload.decision, payload.reviewer)
        return updated_job
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
