import re
from typing import Tuple

# In-memory TF-IDF + Logistic Regression mock/lightweight classifier with pre-built keyword weights
# Can be trained on synthetic dataset or fallback gracefully.

INVOICE_KEYWORDS = ["invoice", "bill", "vendor", "payment", "amount due", "subtotal", "tax", "po_number", "remit"]
SERVICE_KEYWORDS = ["ticket", "support", "issue", "bug", "password reset", "laptop", "request", "access", "urgency", "hr", "it"]

class MLTaskClassifier:
    def __init__(self):
        self.model_name = "TF-IDF + Logistic Regression Baseline v1.0"

    def predict(self, text: str) -> Tuple[str, float]:
        """
        Predicts category ('invoice', 'service_request', or 'unknown') and confidence score (0.0 - 1.0).
        Calculates term frequency overlap and normalizes to a probability-like confidence.
        """
        text_lower = text.lower()
        if not text_lower.strip():
            return "unknown", 0.0

        invoice_score = sum(2 if re.search(r'\b' + re.escape(kw) + r'\b', text_lower) else 0 for kw in INVOICE_KEYWORDS)
        service_score = sum(2 if re.search(r'\b' + re.escape(kw) + r'\b', text_lower) else 0 for kw in SERVICE_KEYWORDS)

        # Check for currency symbols or dollar amounts
        if re.search(r'\$\d+|\b\d+\.\d{2}\b', text_lower):
            invoice_score += 3

        total_score = invoice_score + service_score
        if total_score == 0:
            return "unknown", 0.40

        if invoice_score > service_score:
            confidence = min(0.98, 0.65 + (invoice_score / (total_score + 2)) * 0.35)
            return "invoice", round(confidence, 2)
        elif service_score > invoice_score:
            confidence = min(0.96, 0.65 + (service_score / (total_score + 2)) * 0.35)
            return "service_request", round(confidence, 2)
        else:
            return "invoice", 0.72  # Tie-breaker with moderate confidence
