import pytest
from backend.workflow.state_machine import StateMachine, StateMachineError

def test_valid_state_transitions():
    assert StateMachine.validate_transition("RECEIVED", "VALIDATING") == True
    assert StateMachine.validate_transition("VALIDATING", "CLASSIFIED") == True
    assert StateMachine.validate_transition("CLASSIFIED", "EXTRACTED") == True
    assert StateMachine.validate_transition("EXTRACTED", "DECIDING") == True
    assert StateMachine.validate_transition("DECIDING", "EXECUTING") == True
    assert StateMachine.validate_transition("EXECUTING", "COMPLETED") == True
    assert StateMachine.validate_transition("COMPLETED", "AUDITED") == True

def test_invalid_state_transitions():
    with pytest.raises(StateMachineError):
        StateMachine.validate_transition("RECEIVED", "COMPLETED")

    with pytest.raises(StateMachineError):
        StateMachine.validate_transition("AUDITED", "RECEIVED")
