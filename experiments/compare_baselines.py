import os
import json
import time
import sys
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.models.classifier import RuleOnlyClassifier, MLTaskClassifier
from backend.models.extractor import FieldExtractor
from backend.policy.rules import PolicyRules
from backend.policy.hybrid_engine import HybridDecisionEngine

def run_three_way_comparison():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "test.json")
    if not os.path.exists(data_path):
        from scripts.generate_dataset import main as gen_data
        gen_data()

    with open(data_path, "r") as f:
        test_samples = json.load(f)

    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    rule_clf = RuleOnlyClassifier()
    ml_clf = MLTaskClassifier()

    records = []

    # 1. GROUP A: Rule-Only Baseline
    t0 = time.time()
    y_true_a = []
    y_pred_a = []
    routes_a = []
    for s in test_samples:
        cat, conf = rule_clf.predict(s["text"])
        y_true_a.append(s["workflow_category"])
        y_pred_a.append(cat)
        # Rule-only routes auto if category is known, no confidence gating
        routes_a.append("auto_approve" if cat != "unknown" else "reject")
    lat_a = ((time.time() - t0) / len(test_samples)) * 1000
    acc_a = accuracy_score(y_true_a, y_pred_a)
    p_a, r_a, f1_a, _ = precision_recall_fscore_support(y_true_a, y_pred_a, average='macro', zero_division=0)
    auto_a = sum(1 for r in routes_a if r == "auto_approve") / len(test_samples)
    unsafe_a = sum(1 for s, r in zip(test_samples, routes_a) if s["expected_safe_route"] != "auto_approve" and r == "auto_approve") / len(test_samples)

    records.append({
        "Experimental Group": "Group A: Rule-Only Baseline",
        "Accuracy (%)": round(acc_a * 100, 2),
        "Macro F1 (%)": round(f1_a * 100, 2),
        "Automation Rate (%)": round(auto_a * 100, 2),
        "Human Escalation Rate (%)": 0.0,
        "Unsafe Auto Rate (%)": round(unsafe_a * 100, 2),
        "Avg Latency (ms)": round(lat_a, 2)
    })

    # 2. GROUP B: AI-Only (No Policy Safety Gates)
    t0 = time.time()
    y_true_b = []
    y_pred_b = []
    routes_b = []
    for s in test_samples:
        cat, conf = ml_clf.predict(s["text"])
        y_true_b.append(s["workflow_category"])
        y_pred_b.append(cat)
        # AI-only blindly executes whenever confidence > 0.50
        routes_b.append("auto_approve" if conf >= 0.50 else "reject")
    lat_b = ((time.time() - t0) / len(test_samples)) * 1000
    acc_b = accuracy_score(y_true_b, y_pred_b)
    p_b, r_b, f1_b, _ = precision_recall_fscore_support(y_true_b, y_pred_b, average='macro', zero_division=0)
    auto_b = sum(1 for r in routes_b if r == "auto_approve") / len(test_samples)
    unsafe_b = sum(1 for s, r in zip(test_samples, routes_b) if s["expected_safe_route"] != "auto_approve" and r == "auto_approve") / len(test_samples)

    records.append({
        "Experimental Group": "Group B: AI-Only (No Policy Gates)",
        "Accuracy (%)": round(acc_b * 100, 2),
        "Macro F1 (%)": round(f1_b * 100, 2),
        "Automation Rate (%)": round(auto_b * 100, 2),
        "Human Escalation Rate (%)": 0.0,
        "Unsafe Auto Rate (%)": round(unsafe_b * 100, 2),
        "Avg Latency (ms)": round(lat_b, 2)
    })

    # 3. GROUP C: Proposed Hybrid AI + Policy + Human-in-the-Loop
    t0 = time.time()
    y_true_c = []
    y_pred_c = []
    routes_c = []
    for s in test_samples:
        cat, conf = ml_clf.predict(s["text"])
        y_true_c.append(s["workflow_category"])
        y_pred_c.append(cat)
        extracted = FieldExtractor.extract_fields(s["text"], cat)
        risk, rules = PolicyRules.evaluate_policy(cat, extracted)
        route, _ = HybridDecisionEngine.make_decision(conf, risk, rules)
        routes_c.append(route)
    lat_c = ((time.time() - t0) / len(test_samples)) * 1000
    acc_c = accuracy_score(y_true_c, y_pred_c)
    p_c, r_c, f1_c, _ = precision_recall_fscore_support(y_true_c, y_pred_c, average='macro', zero_division=0)
    auto_c = sum(1 for r in routes_c if r == "auto_approve") / len(test_samples)
    esc_c = sum(1 for r in routes_c if r == "human_approval") / len(test_samples)
    unsafe_c = sum(1 for s, r in zip(test_samples, routes_c) if s["expected_safe_route"] != "auto_approve" and r == "auto_approve") / len(test_samples)

    records.append({
        "Experimental Group": "Group C: Proposed Hybrid AI + Policy",
        "Accuracy (%)": round(acc_c * 100, 2),
        "Macro F1 (%)": round(f1_c * 100, 2),
        "Automation Rate (%)": round(auto_c * 100, 2),
        "Human Escalation Rate (%)": round(esc_c * 100, 2),
        "Unsafe Auto Rate (%)": round(unsafe_c * 100, 2),
        "Avg Latency (ms)": round(lat_c, 2)
    })

    df = pd.DataFrame(records)
    csv_path = os.path.join(results_dir, "baseline_comparison.csv")
    df.to_csv(csv_path, index=False)

    print("\n" + "=" * 80)
    print("      THREE-WAY RESEARCH BASELINE COMPARISON REPORT (Semester 1)")
    print("=" * 80)
    print(df.to_string(index=False))
    print("=" * 80 + "\n")
    print(f"Results exported to: '{csv_path}'")

if __name__ == "__main__":
    run_three_way_comparison()
