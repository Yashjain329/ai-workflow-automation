import datetime
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base

class WorkflowJob(Base):
    __tablename__ = "workflow_jobs"

    job_id = Column(String, primary_key=True, index=True)
    source = Column(String, default="api") # api, email, document, form
    raw_payload = Column(Text, nullable=True)
    normalized_text = Column(Text, nullable=True)
    category = Column(String, default="unknown") # invoice, service_request, unknown
    priority = Column(String, default="normal") # low, normal, high, urgent
    status = Column(String, default="RECEIVED", index=True)
    human_intervention = Column(Boolean, default=False)
    error_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    predictions = relationship("Prediction", back_populates="job", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="job", cascade="all, delete-orphan")
    steps = relationship("WorkflowStep", back_populates="job", cascade="all, delete-orphan")
    action_logs = relationship("ActionLog", back_populates="job", cascade="all, delete-orphan")
    approval_tasks = relationship("ApprovalTask", back_populates="job", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("workflow_jobs.job_id"), index=True)
    model_version = Column(String, default="tf-idf-logreg-v1")
    predicted_category = Column(String)
    confidence = Column(Float)
    extracted_fields = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("WorkflowJob", back_populates="predictions")


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("workflow_jobs.job_id"), index=True)
    route = Column(String) # auto_approve, human_approval, reject
    policy_version = Column(String, default="policy-v1")
    risk_level = Column(String) # low, medium, high
    explanation = Column(Text)
    rules_applied = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("WorkflowJob", back_populates="decisions")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("workflow_jobs.job_id"), index=True)
    step_name = Column(String)
    step_type = Column(String) # validation, classification, extraction, decisioning, execution, audit
    status = Column(String) # PENDING, IN_PROGRESS, COMPLETED, FAILED
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    job = relationship("WorkflowJob", back_populates="steps")


class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("workflow_jobs.job_id"), index=True)
    connector = Column(String) # database_update, notification, webhook
    request_hash = Column(String, nullable=True)
    result = Column(Text, nullable=True)
    status = Column(String) # SUCCESS, FAILURE, RETRYING
    error_code = Column(String, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("WorkflowJob", back_populates="action_logs")


class ApprovalTask(Base):
    __tablename__ = "approval_tasks"

    task_id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("workflow_jobs.job_id"), index=True)
    reason = Column(Text)
    confidence = Column(Float)
    reviewer = Column(String, nullable=True)
    decision = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    decided_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("WorkflowJob", back_populates="approval_tasks")
