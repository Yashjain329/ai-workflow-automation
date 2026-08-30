import os
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.models.classifier import MLTaskClassifier

def evaluate_rule_vs_ml():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "test.json")
    if not os.path.exists(data_path):
        print("Dataset test.json not found. Run 'python scripts/generate_dataset.py' first.")
        return

    with open(data_path, "r") as f:
        test_samples = json.load(f)

    classifier = MLTaskClassifier()
    correct_count = 0
    total = len(test_samples)

    for sample in test_samples:
        text = sample["text"]
        true_cat = sample["true_category"]
        pred_cat, conf = classifier.predict(text)

        if pred_cat == true_cat:
            correct_count += 1

    accuracy = (correct_count / total) * 100
    print("=" * 60)
    print("      ML CLASSIFIER EVALUATION REPORT")
    print("=" * 60)
    print(f"Total Test Samples Evaluated: {total}")
    print(f"Correct Classification Count : {correct_count}")
    print(f"Model Classification Accuracy : {accuracy:.2f}%")
    print("=" * 60)

if __name__ == "__main__":
    evaluate_rule_vs_ml()
