import os
import json
import re
import joblib
from typing import Tuple, Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

MODEL_PATH = os.path.join(os.path.dirname(__file__), "tfidf_logreg_model.pkl")

class RuleOnlyClassifier:
    """Operational Baseline: Heuristic keyword mapping"""
    def __init__(self):
        self.model_name = "Rule-Only Keyword Baseline v1.0"

    def predict(self, text: str) -> Tuple[str, float]:
        text_lower = text.lower()
        if not text_lower.strip():
            return "unknown", 0.0

        invoice_keywords = ["invoice", "bill", "vendor", "payment", "amount due", "remit", "subtotal", "tax"]
        service_keywords = ["ticket", "support", "issue", "bug", "password reset", "laptop", "request", "urgency", "hr", "it"]

        invoice_score = sum(2 if re.search(r'\b' + re.escape(kw) + r'\b', text_lower) else 0 for kw in invoice_keywords)
        service_score = sum(2 if re.search(r'\b' + re.escape(kw) + r'\b', text_lower) else 0 for kw in service_keywords)

        if re.search(r'\$\d+|\b\d+\.\d{2}\b', text_lower):
            invoice_score += 3

        total_score = invoice_score + service_score
        if total_score == 0:
            return "unknown", 0.40

        if invoice_score > service_score:
            confidence = min(0.95, 0.60 + (invoice_score / (total_score + 2)) * 0.40)
            return "invoice", round(confidence, 2)
        elif service_score > invoice_score:
            confidence = min(0.95, 0.60 + (service_score / (total_score + 2)) * 0.40)
            return "service_request", round(confidence, 2)
        else:
            return "invoice", 0.70

class MLTaskClassifier:
    """Primary Lightweight ML Model: Trained scikit-learn TF-IDF + Logistic Regression Pipeline"""
    def __init__(self):
        self.model_name = "TF-IDF + Logistic Regression (scikit-learn v1.0)"
        self.pipeline = None
        self._ensure_model_trained()

    def _ensure_model_trained(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.pipeline = joblib.load(MODEL_PATH)
                return
            except Exception:
                pass

        # Train model if artifact does not exist
        train_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "train.json")
        if not os.path.exists(train_path):
            from scripts.generate_dataset import main as gen_data
            gen_data()

        with open(train_path, "r") as f:
            train_data = json.load(f)

        X_train = [d["text"] for d in train_data]
        y_train = [d["workflow_category"] for d in train_data]

        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000)),
            ('clf', LogisticRegression(C=1.0, max_iter=200, random_state=42))
        ])

        self.pipeline.fit(X_train, y_train)
        joblib.dump(self.pipeline, MODEL_PATH)

    def predict(self, text: str) -> Tuple[str, float]:
        if not text.strip() or self.pipeline is None:
            return "unknown", 0.0

        probs = self.pipeline.predict_proba([text])[0]
        classes = self.pipeline.classes_
        top_idx = probs.argmax()
        
        predicted_cat = str(classes[top_idx])
        confidence = round(float(probs[top_idx]), 2)

        return predicted_cat, confidence

    def predict_detailed(self, text: str) -> Dict[str, Any]:
        cat, conf = self.predict(text)
        probs_dict = {}
        if self.pipeline:
            probs = self.pipeline.predict_proba([text])[0]
            for cls, prob in zip(self.pipeline.classes_, probs):
                probs_dict[str(cls)] = round(float(prob), 4)

        return {
            "predicted_category": cat,
            "confidence": conf,
            "alternatives": probs_dict,
            "model_version": self.model_name
        }
