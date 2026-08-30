import os
import json
import time
import sys
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal, Base, engine
from backend.schemas.pydantic_schemas import JobCreate
from backend.api.jobs import create_job

# Ensure DB tables exist
Base.metadata.create_all(bind=engine)

def run_master_plan_benchmark():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    test_path = os.path.join(data_dir, "test.json")

    if not os.path.exists(test_path):
        print("Master Plan dataset not found. Generating dataset...")
        from scripts.generate_dataset import main as gen_data
        gen_data()

    with open(test_path, "r") as f:
        test_samples = json.load(f)

    db = SessionLocal()
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    y_true_cat = []
    y_pred_cat = []
    y_true_route = []
    y_pred_route = []
    latencies_ms = []

    print("Running Master Plan 5-Layer Benchmark Evaluation...")

    for sample in test_samples:
        t0 = time.time()
        payload = JobCreate(source="benchmark", raw_payload=sample["text"])
        job_res = create_job(payload, db)
        elapsed_ms = (time.time() - t0) * 1000
        latencies_ms.append(elapsed_ms)

        # Retrieve prediction & decision from database trace
        from backend.models.db_models import Prediction, Decision
        pred_obj = db.query(Prediction).filter(Prediction.job_id == job_res.job_id).first()
        dec_obj = db.query(Decision).filter(Decision.job_id == job_res.job_id).first()

        pred_cat = pred_obj.predicted_category if pred_obj else "unknown"
        pred_route = dec_obj.route if dec_obj else "reject"

        y_true_cat.append(sample["workflow_category"])
        y_pred_cat.append(pred_cat)

        y_true_route.append(sample["expected_safe_route"])
        y_pred_route.append(pred_route)

    # 1. Prediction Metrics
    accuracy = accuracy_score(y_true_cat, y_pred_cat)
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_true_cat, y_pred_cat, average='macro', zero_division=0)
    conf_mat = confusion_matrix(y_true_cat, y_pred_cat, labels=["invoice", "service_request", "unknown"])

    # 2. Decision Routing Metrics
    total = len(test_samples)
    safe_auto = sum(1 for t, p in zip(y_true_route, y_pred_route) if t == "auto_approve" and p == "auto_approve")
    correct_esc = sum(1 for t, p in zip(y_true_route, y_pred_route) if t == "human_approval" and p == "human_approval")
    unsafe_auto = sum(1 for t, p in zip(y_true_route, y_pred_route) if t != "auto_approve" and p == "auto_approve")
    correct_rej = sum(1 for t, p in zip(y_true_route, y_pred_route) if t == "reject" and p in ["reject", "human_approval"])

    # 3. Latency Metrics
    mean_lat = float(np.mean(latencies_ms))
    median_lat = float(np.median(latencies_ms))
    p95_lat = float(np.percentile(latencies_ms, 95))

    # Print Summary Report
    print("\n" + "=" * 70)
    print("      MASTER PLAN BENCHMARK EVALUATION REPORT (v1.0 Release)")
    print("=" * 70)
    print(f" Total Samples Evaluated : {total}")
    print(f" Classification Accuracy : {accuracy * 100:.2f}%")
    print(f" Macro Precision / Recall: {p_macro * 100:.2f}% / {r_macro * 100:.2f}%")
    print(f" Macro F1 Score          : {f1_macro * 100:.2f}%")
    print("-" * 70)
    print(f" Safe Auto-Approvals     : {safe_auto} / {total} ({(safe_auto/total)*100:.1f}%)")
    print(f" Correct Escalations     : {correct_esc} / {total} ({(correct_esc/total)*100:.1f}%)")
    print(f" Unsafe Auto-Executions  : {unsafe_auto} / {total} ({(unsafe_auto/total)*100:.1f}%) [Safety Gate Target = 0]")
    print("-" * 70)
    print(f" Mean Latency per Job    : {mean_lat:.2f} ms")
    print(f" Median Latency per Job  : {median_lat:.2f} ms")
    print(f" p95 Latency per Job     : {p95_lat:.2f} ms")
    print("=" * 70 + "\n")

    # Export Results CSVs and JSON Manifest
    df_clf = pd.DataFrame({
        "sample_id": [s["id"] for s in test_samples],
        "true_category": y_true_cat,
        "predicted_category": y_pred_cat,
        "true_route": y_true_route,
        "predicted_route": y_pred_route,
        "latency_ms": latencies_ms
    })
    df_clf.to_csv(os.path.join(results_dir, "classification_metrics.csv"), index=False)

    df_conf = pd.DataFrame(conf_mat, index=["invoice", "service_request", "unknown"], columns=["invoice", "service_request", "unknown"])
    df_conf.to_csv(os.path.join(results_dir, "confusion_matrix.csv"))

    manifest = {
        "dataset_version": "v1.0_master_plan",
        "model_version": "TF-IDF + Logistic Regression (scikit-learn v1.0)",
        "policy_version": "policy-v1.0",
        "total_samples": total,
        "classification_accuracy": round(accuracy, 4),
        "macro_f1": round(f1_macro, 4),
        "safe_auto_rate": round(safe_auto / total, 4),
        "unsafe_auto_count": unsafe_auto,
        "latency_p95_ms": round(p95_lat, 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(results_dir, "experiment_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Experiment results exported to '{results_dir}':")
    print("  - classification_metrics.csv")
    print("  - confusion_matrix.csv")
    print("  - experiment_manifest.json")

    db.close()

if __name__ == "__main__":
    run_master_plan_benchmark()
