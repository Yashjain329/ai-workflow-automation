import os
import json
import time
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal, Base, engine
from backend.models.db_models import WorkflowJob
from backend.schemas.pydantic_schemas import JobCreate
from backend.api.jobs import create_job

# Ensure tables are built
Base.metadata.create_all(bind=engine)

def run_benchmark():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "test.json")
    if not os.path.exists(data_path):
        print("Test dataset not found. Generating dataset first...")
        from scripts.generate_dataset import main as gen_dataset
        gen_dataset()

    with open(data_path, "r") as f:
        test_samples = json.load(f)

    db = SessionLocal()
    start_time = time.time()

    auto_completed = 0
    escalated = 0
    rejected = 0

    print("Running End-to-End Workflow Benchmark...")

    for sample in test_samples:
        payload = JobCreate(source="benchmark", raw_payload=sample["text"])
        res = create_job(payload, db)

        if res.status == "AUDITED" and not res.human_intervention:
            auto_completed += 1
        elif res.status == "APPROVAL_PENDING" or res.human_intervention:
            escalated += 1
        else:
            rejected += 1

    total_time = time.time() - start_time
    total_jobs = len(test_samples)
    avg_latency = (total_time / total_jobs) * 1000

    auto_rate = (auto_completed / total_jobs) * 100
    esc_rate = (escalated / total_jobs) * 100
    rej_rate = (rejected / total_jobs) * 100

    print("\n" + "=" * 65)
    print("        END-TO-END WORKFLOW BENCHMARK REPORT (v1.0)")
    print("=" * 65)
    print(f" Total Jobs Processed   : {total_jobs}")
    print(f" Total Execution Time   : {total_time:.2f} seconds")
    print(f" Average Latency per Job: {avg_latency:.2f} ms")
    print("-" * 65)
    print(f" Straight-Through Auto  : {auto_completed} ({auto_rate:.2f}%)")
    print(f" Escalated to Human Queue: {escalated} ({esc_rate:.2f}%)")
    print(f" Rejected / Manual Intake: {rejected} ({rej_rate:.2f}%)")
    print("=" * 65 + "\n")

    db.close()

if __name__ == "__main__":
    run_benchmark()
