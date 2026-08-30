import pytest
from backend.policy.hybrid_engine import HybridDecisionEngine
from backend.connectors.database_connector import DatabaseConnector
from backend.connectors.notification_connector import NotificationConnector
from backend.models.classifier import RuleOnlyClassifier, MLTaskClassifier
from backend.models.extractor import FieldExtractor
from backend.database import SessionLocal, Base, engine
from backend.models.db_models import WorkflowJob, ActionLog
from backend.schemas.pydantic_schemas import JobCreate
from backend.api.jobs import create_job

Base.metadata.create_all(bind=engine)

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

def test_idempotency_duplicate_prevention():
    fields = {"vendor": "Acme Corp", "amount": 2500.0, "invoice_number": "INV-DUP-TEST"}
    
    DatabaseConnector.clear_idempotency_cache()
    DatabaseConnector.set_failure_mode("NORMAL")
    
    # Run 1: Original execution
    s1, r1, err1, is_dup1 = DatabaseConnector.execute_action("JOB-DUP-1", "invoice", fields)
    assert s1 == True
    assert is_dup1 == False

    # Run 2: Exact duplicate submission
    s2, r2, err2, is_dup2 = DatabaseConnector.execute_action("JOB-DUP-2", "invoice", fields)
    assert s2 == True
    assert is_dup2 == True
    assert "IDEMPOTENT_SKIPPED" in r2

def test_database_transient_failure_and_retry():
    db = SessionLocal()
    DatabaseConnector.clear_idempotency_cache()
    DatabaseConnector.set_failure_mode("TRANSIENT_FAILURE")
    NotificationConnector.set_failure_mode("NORMAL")

    payload = JobCreate(source="test", raw_payload="Please find attached the billing statement INV-2026-9999 from TechSupplies Inc totaling $350.00 for deliverables.")
    job = create_job(payload, db)
    assert job.status == "AUDITED"

    logs = db.query(ActionLog).filter(ActionLog.job_id == job.job_id, ActionLog.connector == "database_connector").all()
    assert len(logs) >= 3 # Retried twice then succeeded on 3rd attempt!

    DatabaseConnector.set_failure_mode("NORMAL")
    db.close()

def test_database_permanent_failure_exhaustion():
    db = SessionLocal()
    DatabaseConnector.clear_idempotency_cache()
    DatabaseConnector.set_failure_mode("PERMANENT_FAILURE")

    payload = JobCreate(source="test", raw_payload="Statement of account issued by CloudServices LLC for reference INV-2026-8888. Total balance payable: $450.00.")
    job = create_job(payload, db)
    assert job.status == "FAILED"
    assert job.error_code == "ERR_PERMANENT"

    DatabaseConnector.set_failure_mode("NORMAL")
    db.close()

def test_notification_transient_failure_and_retry():
    db = SessionLocal()
    DatabaseConnector.clear_idempotency_cache()
    DatabaseConnector.set_failure_mode("NORMAL")
    NotificationConnector.set_failure_mode("TRANSIENT_FAILURE")

    payload = JobCreate(source="test", raw_payload="Commercial receipt INV-2026-3311 submitted by Apex Industries. Amount payable: $620.00.")
    job = create_job(payload, db)
    assert job.status == "AUDITED"

    mail_logs = db.query(ActionLog).filter(ActionLog.job_id == job.job_id, ActionLog.connector == "notification_connector").all()
    assert len(mail_logs) >= 3 # Retried twice then succeeded on 3rd attempt!

    NotificationConnector.set_failure_mode("NORMAL")
    db.close()

def test_notification_permanent_failure_exhaustion():
    db = SessionLocal()
    DatabaseConnector.clear_idempotency_cache()
    DatabaseConnector.set_failure_mode("NORMAL")
    NotificationConnector.set_failure_mode("NOTIFICATION_FAILURE")

    payload = JobCreate(source="test", raw_payload="Statement of account issued by Global Logistics for reference INV-2026-1122. Total balance payable: $750.00.")
    job = create_job(payload, db)
    assert job.status == "FAILED"
    assert job.error_code == "ERR_SMTP_GATEWAY"

    NotificationConnector.set_failure_mode("NORMAL")
    db.close()

def test_ood_out_of_domain_handling():
    ml_clf = MLTaskClassifier()
    cat, conf = ml_clf.predict("Can you give me a recipe for chocolate chip cookies?")
    assert cat == "unknown"
    assert conf >= 0.70

    fields = FieldExtractor.extract_fields("Can you give me a recipe for chocolate chip cookies?", "unknown")
    assert fields == {}
