import pytest
from backend.policy.rules import PolicyRules
from backend.policy.hybrid_engine import HybridDecisionEngine

def test_invoice_policy_rules():
    # Low risk invoice
    extracted = {"vendor": "Acme Corp", "amount": 1500.0}
    risk, rules = PolicyRules.evaluate_policy("invoice", extracted)
    assert risk == "low"
    assert "RULE_PASSED" in rules[0]

    # Medium risk invoice (exceeds $5000)
    extracted_high = {"vendor": "Acme Corp", "amount": 8500.0}
    risk, rules = PolicyRules.evaluate_policy("invoice", extracted_high)
    assert risk == "medium"

    # High risk invoice (unknown vendor)
    extracted_unknown = {"vendor": "Unknown Vendor", "amount": 1500.0}
    risk, rules = PolicyRules.evaluate_policy("invoice", extracted_unknown)
    assert risk == "high"

def test_hybrid_decision_engine():
    # High confidence & low risk -> auto approve
    route, exp = HybridDecisionEngine.make_decision(0.95, "low", ["RULE_PASSED"])
    assert route == "auto_approve"

    # Medium confidence -> human approval
    route, exp = HybridDecisionEngine.make_decision(0.78, "low", ["RULE_PASSED"])
    assert route == "human_approval"

    # Low confidence (< 0.70) -> reject
    route, exp = HybridDecisionEngine.make_decision(0.55, "low", ["RULE_PASSED"])
    assert route == "reject"

    # High risk -> human approval escalation safety gate
    route, exp = HybridDecisionEngine.make_decision(0.98, "high", ["RULE_UNKNOWN_VENDOR"])
    assert route == "human_approval"
