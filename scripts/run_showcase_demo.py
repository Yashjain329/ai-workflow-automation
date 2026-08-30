import os
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal, Base, engine
from backend.models.db_models import WorkflowJob, Prediction, Decision, ActionLog
from backend.schemas.pydantic_schemas import JobCreate
from backend.api.jobs import create_job
from backend.connectors.database_connector import DatabaseConnector

Base.metadata.create_all(bind=engine)

def run_10_showcase_demo():
    demo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "showcase_demo_cases.json")
    with open(demo_path, "r") as f:
        cases = json.load(f)

    db = SessionLocal()
    print("\n" + "=" * 85)
    print("      EXECUTING 10 SHOWCASE END-TO-END WORKFLOW DEMONSTRATION CASES")
    print("=" * 85)

    passed_cases = 0

    for c in cases:
        print(f"\n[Case {c['case_num']}] {c['title']}")
        print(f"  Input  : \"{c['input_text']}\"")

        # Simulate transient failure mode on case 10
        if c["case_num"] == "10":
            DatabaseConnector.set_failure_mode("TRANSIENT_FAILURE")
        else:
            DatabaseConnector.set_failure_mode("NORMAL")

        payload = JobCreate(source="demo", raw_payload=c["input_text"])
        job_res = create_job(payload, db)

        pred = db.query(Prediction).filter(Prediction.job_id == job_res.job_id).first()
        dec = db.query(Decision).filter(Decision.job_id == job_res.job_id).first()
        logs = db.query(ActionLog).filter(ActionLog.job_id == job_res.job_id).all()

        p_cat = pred.predicted_category if pred else "unknown"
        p_conf = pred.confidence if pred else 0.0
        p_route = dec.route if dec else "reject"
        p_status = job_res.status

        print(f"  Result : Category='{p_cat}' (Conf={p_conf*100:.0f}%), Route='{p_route}', State='{p_status}'")
        if logs:
            for l in logs:
                print(f"    • Action Log: {l.connector} -> {l.status} (Attempt: {l.retry_count})")

        # Verify against expected
        if p_status == c["expected_final_state"]:
            print("  Status : PASS (Matches Expected Lifecycle)")
            passed_cases += 1
        else:
            print(f"  Status : DISCREPANCY (Expected '{c['expected_final_state']}', Got '{p_status}')")

    print("\n" + "=" * 85)
    print(f" Showcase Summary: {passed_cases} / {len(cases)} Test Scenarios Verified Successfully!")
    print("=" * 85 + "\n")
    db.close()

if __name__ == "__main__":
    run_10_showcase_demo()
