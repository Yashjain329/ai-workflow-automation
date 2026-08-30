from enum import Enum
from typing import List

class WorkflowState(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATING = "VALIDATING"
    CLASSIFIED = "CLASSIFIED"
    EXTRACTED = "EXTRACTED"
    DECIDING = "DECIDING"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    APPROVAL_APPROVED = "APPROVAL_APPROVED"
    APPROVAL_REJECTED = "APPROVAL_REJECTED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    AUDITED = "AUDITED"

# Allowed state transition map to enforce strict lifecycle control
ALLOWED_TRANSITIONS = {
    WorkflowState.RECEIVED: [WorkflowState.VALIDATING, WorkflowState.FAILED],
    WorkflowState.VALIDATING: [WorkflowState.CLASSIFIED, WorkflowState.FAILED],
    WorkflowState.CLASSIFIED: [WorkflowState.EXTRACTED, WorkflowState.FAILED],
    WorkflowState.EXTRACTED: [WorkflowState.DECIDING, WorkflowState.FAILED],
    WorkflowState.DECIDING: [WorkflowState.EXECUTING, WorkflowState.APPROVAL_PENDING, WorkflowState.FAILED],
    WorkflowState.APPROVAL_PENDING: [WorkflowState.APPROVAL_APPROVED, WorkflowState.APPROVAL_REJECTED, WorkflowState.FAILED],
    WorkflowState.APPROVAL_APPROVED: [WorkflowState.EXECUTING, WorkflowState.FAILED],
    WorkflowState.APPROVAL_REJECTED: [WorkflowState.FAILED, WorkflowState.AUDITED],
    WorkflowState.EXECUTING: [WorkflowState.COMPLETED, WorkflowState.FAILED],
    WorkflowState.COMPLETED: [WorkflowState.AUDITED],
    WorkflowState.FAILED: [WorkflowState.AUDITED],
    WorkflowState.AUDITED: [],
}

class StateMachineError(Exception):
    pass

class StateMachine:
    @staticmethod
    def validate_transition(current_state: str, new_state: str) -> bool:
        try:
            curr = WorkflowState(current_state)
            target = WorkflowState(new_state)
        except ValueError:
            raise StateMachineError(f"Invalid state enum: {current_state} -> {new_state}")
            
        allowed = ALLOWED_TRANSITIONS.get(curr, [])
        if target not in allowed:
            raise StateMachineError(
                f"Invalid state transition from '{current_state}' to '{new_state}'. "
                f"Allowed target states: {[s.value for s in allowed]}"
            )
        return True
