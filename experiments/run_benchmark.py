import os
import json
import time
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal, Base, engine
from backend.schemas.pydantic_schemas import JobCreate
from backend.api.jobs import create_job
from backend.models.db_models import Prediction, Decision

Base.metadata.create_all(bind=engine)

def run_comprehensive_benchmark():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    test_path = os.path.join(data_dir, "test.json")

    if not os.path.exists(test_path):
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

    # Extraction evaluation accumulators
    vendor_matches = []
    amount_matches = []
    amount_rel_errors = []
    inv_num_matches = []
    dept_matches = []
    urgency_matches = []

    print(f"Running Comprehensive 5-Layer Benchmark Evaluation on {len(test_samples)} Test Samples...")

    for sample in test_samples:
        t0 = time.time()
        payload = JobCreate(source="benchmark", raw_payload=sample["text"])
        job_res = create_job(payload, db)
        elapsed_ms = (time.time() - t0) * 1000
        latencies_ms.append(elapsed_ms)

        pred_obj = db.query(Prediction).filter(Prediction.job_id == job_res.job_id).first()
        dec_obj = db.query(Decision).filter(Decision.job_id == job_res.job_id).first()

        pred_cat = pred_obj.predicted_category if pred_obj else "unknown"
        pred_route = dec_obj.route if dec_obj else "reject"
        extracted_fields = pred_obj.extracted_fields if pred_obj and pred_obj.extracted_fields else {}

        y_true_cat.append(sample["workflow_category"])
        y_pred_cat.append(pred_cat)
        y_true_route.append(sample["expected_safe_route"])
        y_pred_route.append(pred_route)

        # Evaluate Field Extraction Ground Truth
        true_fields = sample.get("fields", {})
        if sample["workflow_category"] == "invoice":
            # Vendor
            t_vendor = true_fields.get("vendor", "")
            p_vendor = extracted_fields.get("vendor", "")
            vendor_matches.append(1 if t_vendor.lower() in p_vendor.lower() or p_vendor.lower() in t_vendor.lower() else 0)

            # Amount
            t_amt = true_fields.get("amount")
            p_amt = extracted_fields.get("amount")
            if t_amt is not None and p_amt is not None and t_amt > 0:
                amount_matches.append(1 if abs(t_amt - p_amt) < 0.01 else 0)
                amount_rel_errors.append(abs(t_amt - p_amt) / t_amt)
            elif t_amt is None and p_amt is None:
                amount_matches.append(1)
                amount_rel_errors.append(0.0)

            # Invoice Number
            t_inv = true_fields.get("invoice_number", "")
            p_inv = extracted_fields.get("invoice_number", "")
            inv_num_matches.append(1 if t_inv.replace("-", "").lower() in p_inv.replace("-", "").lower() else 0)

        elif sample["workflow_category"] == "service_request":
            # Department
            t_dept = true_fields.get("department", "")
            p_dept = extracted_fields.get("department", "")
            dept_matches.append(1 if t_dept.lower() == p_dept.lower() else 0)

            # Urgency
            t_urg = true_fields.get("urgency", "")
            p_urg = extracted_fields.get("urgency", "")
            urgency_matches.append(1 if t_urg.lower() == p_urg.lower() else 0)

    # 1. Classification Metrics
    accuracy = accuracy_score(y_true_cat, y_pred_cat)
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_true_cat, y_pred_cat, average='macro', zero_division=0)
    conf_mat = confusion_matrix(y_true_cat, y_pred_cat, labels=["invoice", "service_request", "unknown"])

    # 2. Field Extraction Metrics
    vendor_acc = np.mean(vendor_matches) * 100 if vendor_matches else 0.0
    amount_acc = np.mean(amount_matches) * 100 if amount_matches else 0.0
    amount_mre = np.mean(amount_rel_errors) * 100 if amount_rel_errors else 0.0
    inv_acc = np.mean(inv_num_matches) * 100 if inv_num_matches else 0.0
    dept_acc = np.mean(dept_matches) * 100 if dept_matches else 0.0
    urg_acc = np.mean(urgency_matches) * 100 if urgency_matches else 0.0

    # 3. Decision & OOD Safety Metrics
    total = len(test_samples)
    safe_auto = sum(1 for t, p in zip(y_true_route, y_pred_route) if t == "auto_approve" and p == "auto_approve")
    correct_esc = sum(1 for t, p in zip(y_true_route, y_pred_route) if t == "human_approval" and p == "human_approval")
    unsafe_auto = sum(1 for t, p in zip(y_true_route, y_pred_route) if t != "auto_approve" and p == "auto_approve")
    
    # OOD Specific Safety: ensure 0 out-of-domain tasks auto-execute
    ood_samples = [s for s in test_samples if s["workflow_category"] == "unknown"]
    ood_indices = [i for i, s in enumerate(test_samples) if s["workflow_category"] == "unknown"]
    ood_unsafe_auto = sum(1 for i in ood_indices if y_pred_route[i] == "auto_approve")

    # 4. Latencies
    mean_lat = float(np.mean(latencies_ms))
    median_lat = float(np.median(latencies_ms))
    p95_lat = float(np.percentile(latencies_ms, 95))

    # Print Full Report
    print("\n" + "=" * 75)
    print(f"      COMPREHENSIVE DISSERTATION BENCHMARK REPORT (N = {total} Test Samples)")
    print("=" * 75)
    print(f" [1] Classification Accuracy : {accuracy * 100:.2f}%")
    print(f"     Macro Precision / Recall: {p_macro * 100:.2f}% / {r_macro * 100:.2f}%")
    print(f"     Macro F1-Score          : {f1_macro * 100:.2f}%")
    print("-" * 75)
    print(" [2] Field Extraction Accuracy:")
    print(f"     • Vendor Name Accuracy  : {vendor_acc:.2f}%")
    print(f"     • Invoice Amount Match  : {amount_acc:.2f}% (Mean Relative Error: {amount_mre:.2f}%)")
    print(f"     • Invoice Number Match  : {inv_acc:.2f}%")
    print(f"     • Department Accuracy   : {dept_acc:.2f}%")
    print(f"     • Urgency Level Accuracy: {urg_acc:.2f}%")
    print("-" * 75)
    print(" [3] Hybrid Decision & Safety Routing:")
    print(f"     • Safe Auto-Approvals   : {safe_auto} / {total} ({(safe_auto/total)*100:.1f}%)")
    print(f"     • Correct Escalations   : {correct_esc} / {total} ({(correct_esc/total)*100:.1f}%)")
    print(f"     • Total Unsafe Auto-Exec: {unsafe_auto} / {total} ({(unsafe_auto/total)*100:.1f}%)")
    print(f"     • OOD Unsafe Auto-Exec  : {ood_unsafe_auto} / {len(ood_samples)} [TARGET: 0]")
    print("-" * 75)
    print(" [4] Latency Benchmark:")
    print(f"     • Mean Latency per Job  : {mean_lat:.2f} ms")
    print(f"     • Median Latency        : {median_lat:.2f} ms")
    print(f"     • p95 Latency (Target<500): {p95_lat:.2f} ms")
    print("=" * 75 + "\n")

    # Export Results
    df_clf = pd.DataFrame({
        "sample_id": [s["id"] for s in test_samples],
        "true_category": y_true_cat,
        "predicted_category": y_pred_cat,
        "true_route": y_true_route,
        "predicted_route": y_pred_route,
        "latency_ms": latencies_ms
    })
    df_clf.to_csv(os.path.join(results_dir, "classification_metrics.csv"), index=False)

    df_extract = pd.DataFrame([{
        "vendor_accuracy": vendor_acc,
        "amount_accuracy": amount_acc,
        "amount_mean_rel_error": amount_mre,
        "invoice_number_accuracy": inv_acc,
        "department_accuracy": dept_acc,
        "urgency_accuracy": urg_acc
    }])
    df_extract.to_csv(os.path.join(results_dir, "extraction_metrics.csv"), index=False)

    df_conf = pd.DataFrame(conf_mat, index=["invoice", "service_request", "unknown"], columns=["invoice", "service_request", "unknown"])
    df_conf.to_csv(os.path.join(results_dir, "confusion_matrix.csv"))

    manifest = {
        "dataset_version": "v1.0_large_scale",
        "random_seed": 42,
        "total_test_samples": total,
        "classification_accuracy": round(accuracy, 4),
        "macro_f1": round(f1_macro, 4),
        "vendor_extraction_accuracy": round(vendor_acc, 2),
        "amount_extraction_accuracy": round(amount_acc, 2),
        "safe_auto_approval_rate": round(safe_auto / total, 4),
        "unsafe_auto_count": unsafe_auto,
        "ood_unsafe_auto_count": ood_unsafe_auto,
        "p95_latency_ms": round(p95_lat, 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(results_dir, "experiment_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"All 4 benchmark result artifacts exported to '{results_dir}'.")
    db.close()

if __name__ == "__main__":
    run_comprehensive_benchmark()
