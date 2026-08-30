import os
import json
import random
import sys
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.models.classifier import MLTaskClassifier

def inject_char_noise(text: str, noise_rate: float) -> str:
    """Injects random character swaps and typos at a given rate."""
    chars = list(text)
    num_to_corrupt = int(len(chars) * noise_rate)
    indices = random.sample(range(len(chars)), min(num_to_corrupt, len(chars)))
    for idx in indices:
        if chars[idx].isalpha():
            chars[idx] = random.choice('abcdefghijklmnopqrstuvwxyz')
    return "".join(chars)

def inject_word_dropout(text: str, dropout_rate: float) -> str:
    """Randomly deletes words at a given dropout rate."""
    words = text.split()
    if len(words) <= 3:
        return text
    keep_count = max(2, int(len(words) * (1.0 - dropout_rate)))
    kept_words = random.sample(words, keep_count)
    return " ".join(kept_words)

def run_multi_dimensional_robustness_study():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "test.json")
    if not os.path.exists(data_path):
        from scripts.generate_dataset import main as gen_data
        gen_data()

    with open(data_path, "r") as f:
        test_samples = json.load(f)

    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    classifier = MLTaskClassifier()
    records = []

    print(f"Running Multi-Dimensional Robustness Study on {len(test_samples)} Test Samples...")

    # 1. Clean Baseline
    y_true_0 = [s["workflow_category"] for s in test_samples]
    y_pred_0 = []
    confs_0 = []
    for s in test_samples:
        cat, conf = classifier.predict(s["text"])
        y_pred_0.append(cat)
        confs_0.append(conf)
    acc_0 = accuracy_score(y_true_0, y_pred_0)
    p_0, r_0, f1_0, _ = precision_recall_fscore_support(y_true_0, y_pred_0, average='macro', zero_division=0)
    records.append({
        "Perturbation Type": "0% Clean Baseline",
        "Perturbation Level": "None",
        "Accuracy (%)": round(acc_0 * 100, 2),
        "Macro F1 (%)": round(f1_0 * 100, 2),
        "Macro Precision (%)": round(p_0 * 100, 2),
        "Macro Recall (%)": round(r_0 * 100, 2),
        "Avg AI Confidence": round(sum(confs_0) / len(confs_0), 2)
    })

    # 2. Character Noise Levels
    for c_rate in [0.10, 0.20, 0.30]:
        y_pred = []
        confs = []
        for s in test_samples:
            noisy = inject_char_noise(s["text"], c_rate)
            cat, conf = classifier.predict(noisy)
            y_pred.append(cat)
            confs.append(conf)
        acc = accuracy_score(y_true_0, y_pred)
        p, r, f1, _ = precision_recall_fscore_support(y_true_0, y_pred, average='macro', zero_division=0)
        records.append({
            "Perturbation Type": "Character Typo Noise",
            "Perturbation Level": f"{int(c_rate * 100)}%",
            "Accuracy (%)": round(acc * 100, 2),
            "Macro F1 (%)": round(f1 * 100, 2),
            "Macro Precision (%)": round(p * 100, 2),
            "Macro Recall (%)": round(r * 100, 2),
            "Avg AI Confidence": round(sum(confs) / len(confs), 2)
        })

    # 3. Word Dropout / Deletion Perturbations
    for w_rate in [0.10, 0.20, 0.30]:
        y_pred = []
        confs = []
        for s in test_samples:
            dropped = inject_word_dropout(s["text"], w_rate)
            cat, conf = classifier.predict(dropped)
            y_pred.append(cat)
            confs.append(conf)
        acc = accuracy_score(y_true_0, y_pred)
        p, r, f1, _ = precision_recall_fscore_support(y_true_0, y_pred, average='macro', zero_division=0)
        records.append({
            "Perturbation Type": "Word Dropout / Deletion",
            "Perturbation Level": f"{int(w_rate * 100)}%",
            "Accuracy (%)": round(acc * 100, 2),
            "Macro F1 (%)": round(f1 * 100, 2),
            "Macro Precision (%)": round(p * 100, 2),
            "Macro Recall (%)": round(r * 100, 2),
            "Avg AI Confidence": round(sum(confs) / len(confs), 2)
        })

    df = pd.DataFrame(records)
    csv_path = os.path.join(results_dir, "robustness_metrics.csv")
    df.to_csv(csv_path, index=False)

    print("\n" + "=" * 85)
    print("      MULTI-DIMENSIONAL ROBUSTNESS & DEGRADATION REPORT (Semester 1)")
    print("=" * 85)
    print(df.to_string(index=False))
    print("=" * 85 + "\n")
    print(f"Robustness report exported to: '{csv_path}'")

if __name__ == "__main__":
    run_multi_dimensional_robustness_study()
