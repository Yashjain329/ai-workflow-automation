import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List

class JobCreate(BaseModel):
    source: str = Field(default="api", description="Source of input: api, form, email, document")
    raw_payload: Optional[str] = Field(default=None, description="Raw text, JSON string, or form content")
    category_hint: Optional[str] = Field(default=None, description="Optional category hint for testing")

class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., description="APPROVED or REJECTED")
    reviewer: str = Field(default="human_operator", description="Reviewer identifier")

class WorkflowJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    source: str
    category: str
    priority: str
    status: str
    human_intervention: bool
    error_code: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    model_version: str
    predicted_category: str
    confidence: float
    extracted_fields: Optional[Dict[str, Any]] = None

class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    route: str
    policy_version: str
    risk_level: str
    explanation: str
    rules_applied: Optional[List[str]] = None

class ActionLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    connector: str
    status: str
    result: Optional[str] = None
    error_code: Optional[str] = None
    retry_count: int

class JobDetailResponse(BaseModel):
    job: WorkflowJobResponse
    prediction: Optional[PredictionResponse] = None
    decision: Optional[DecisionResponse] = None
    action_logs: List[ActionLogResponse] = []
    approval_task: Optional[Dict[str, Any]] = None

class ApprovalTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: str
    job_id: str
    reason: str
    confidence: float
    reviewer: Optional[str] = None
    decision: str
    created_at: datetime.datetime
    decided_at: Optional[datetime.datetime] = None

class OperationalMetricsResponse(BaseModel):
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    pending_approvals: int
    automation_rate: float
    escalation_rate: float
    failure_rate: float
    avg_confidence: float
