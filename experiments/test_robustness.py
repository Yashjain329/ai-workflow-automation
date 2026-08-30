import os
import json
import random
import sys
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.models.classifier import MLTaskClassifier

def inject_typo_noise(text: str, noise_rate: float) -> str:
    """Injects random character swaps and typos at a given noise rate."""
    chars = list(text)
    num_to_corrupt = int(len(chars) * noise_rate)
    indices = random.sample(range(len(chars)), min(num_to_corrupt, len(chars)))
    
    for idx in indices:
        if chars[idx].isalpha():
            chars[idx] = random.choice('abcdefghijklmnopqrstuvwxyz')
            
    return "".join(chars)

def run_robustness_study():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "test.json")
    if not os.path.exists(data_path):
        from scripts.generate_dataset import main as gen_data
        gen_data()

    with open(data_path, "r") as f:
        test_samples = json.load(f)

    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    classifier = MLTaskClassifier()
    noise_levels = [0.0, 0.10, 0.20, 0.30]
    records = []

    print("Running Controlled Robustness & Perturbation Study...")

    for noise in noise_levels:
        y_true = []
        y_pred = []
        confidences = []

        for sample in test_samples:
            noisy_text = inject_typo_noise(sample["text"], noise) if noise > 0 else sample["text"]
            cat, conf = classifier.predict(noisy_text)
            y_true.append(sample["workflow_category"])
            y_pred.append(cat)
            confidences.append(conf)

        acc = accuracy_score(y_true, y_pred)
        p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
        avg_conf = sum(confidences) / len(confidences)

        records.append({
            "Perturbation Level": f"{int(noise * 100)}% Character Noise" if noise > 0 else "0% (Clean Baseline)",
            "Accuracy (%)": round(acc * 100, 2),
            "Macro F1 (%)": round(f1 * 100, 2),
            "Macro Precision (%)": round(p * 100, 2),
            "Macro Recall (%)": round(r * 100, 2),
            "Avg AI Confidence": round(avg_conf, 2)
        })

    df = pd.DataFrame(records)
    csv_path = os.path.join(results_dir, "robustness_metrics.csv")
    df.to_csv(csv_path, index=False)

    print("\n" + "=" * 75)
    print("        CONTROLLED ROBUSTNESS & DEGRADATION REPORT (Semester 1)")
    print("=" * 75)
    print(df.to_string(index=False))
    print("=" * 75 + "\n")
    print(f"Robustness metrics exported to: '{csv_path}'")

if __name__ == "__main__":
    run_robustness_study()
