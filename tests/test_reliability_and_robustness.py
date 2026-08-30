import pytest
from backend.policy.hybrid_engine import HybridDecisionEngine
from backend.connectors.database_connector import DatabaseConnector
from backend.connectors.notification_connector import NotificationConnector
from backend.models.classifier import RuleOnlyClassifier, MLTaskClassifier

def test_exact_threshold_boundaries():
    # Exactly 0.90 & low risk -> auto_approve
    route, exp = HybridDecisionEngine.make_decision(0.90, "low", ["RULE_PASSED"])
    assert route == "auto_approve"

    # Exactly 0.70 & low risk -> human_approval
    route, exp = HybridDecisionEngine.make_decision(0.70, "low", ["RULE_PASSED"])
    assert route == "human_approval"

    # Exactly 0.69 -> reject
    route, exp = HybridDecisionEngine.make_decision(0.69, "low", ["RULE_PASSED"])
    assert route == "reject"

def test_idempotency_key_generation():
    # Identical fields produce identical execution hashes
    fields = {"vendor": "Acme Corp", "amount": 2500.0, "invoice_number": "INV-101"}
    s1, r1, _ = DatabaseConnector.execute_action("JOB-TEST-1", "invoice", fields)
    s2, r2, _ = DatabaseConnector.execute_action("JOB-TEST-1", "invoice", fields)
    assert s1 == True and s2 == True
    assert r1 == r2 # Identical hash trace

def test_rule_vs_ml_classifiers():
    rule_clf = RuleOnlyClassifier()
    ml_clf = MLTaskClassifier()

    cat_rule, _ = rule_clf.predict("INVOICE #9981 from Acme Corp for $1200.00")
    cat_ml, _ = ml_clf.predict("INVOICE #9981 from Acme Corp for $1200.00")

    assert cat_rule == "invoice"
    assert cat_ml == "invoice"
