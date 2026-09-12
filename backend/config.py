import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "AI-Based Intelligent Workflow Automation Platform"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./workflow_automation.db")

    # Confidence Thresholds
    CONFIDENCE_HIGH: float = 0.90   # Auto-execute
    CONFIDENCE_MEDIUM: float = 0.70 # Escalate to Human Approval Queue
                                    # Below 0.70 = Reject / Manual Review

    # Financial Thresholds
    AUTO_APPROVE_MAX_AMOUNT: float = 5000.0  # Max invoice amount for auto-approval without policy escalation

    # Retry Limits
    MAX_RETRIES: int = 3

    # Monitoring Settings
    MODEL_VERSION: str = "tf-idf-logreg-v1"
    METRICS_COLLECTION_ENABLED: bool = True
    MODEL_PERFORMANCE_COLLECTION_INTERVAL_HOURS: int = 24
    SYSTEM_PERFORMANCE_COLLECTION_INTERVAL_HOURS: int = 1
    DATA_DRIFT_COLLECTION_INTERVAL_HOURS: int = 24

    # Task Queue Settings
    BROKER_URL: str = os.getenv("BROKER_URL", "redis://localhost:6379/0")
    RESULT_BACKEND: str = os.getenv("RESULT_BACKEND", "redis://localhost:6379/0")
    TASK_SERIALIZER: str = "json"
    RESULT_SERIALIZER: str = "json"
    ACCEPT_CONTENT: list = ["json"]
    TIMEZONE: str = "UTC"
    ENABLE_UTC: bool = True
    USE_CELERY: bool = False  # Set to True to enable Celery for background processing

    # Additional thresholds to make configurable
    # From classifier.py
    CLASSIFIER_UNKNOWN_CONFIDENCE: float = 0.40  # Default confidence for unknown classification
    CLASSIFIER_INVOICE_KEYWORD_BONUS: int = 3    # Bonus score for finding currency/invoice patterns

    # From extractor.py
    EXTRACTOR_AMOUNT_CONFIDENCE_HIGH: float = 0.95  # Confidence when amount found
    EXTRACTOR_AMOUNT_CONFIDENCE_ZERO: float = 0.0   # Confidence when amount not found or invalid
    EXTRACTOR_VENDOR_CONFIDENCE_HIGH: float = 0.94  # Confidence for verified vendor
    EXTRACTOR_VENDOR_CONFIDENCE_AMBIGUOUS: float = 0.78  # Confidence for ambiguous vendor
    EXTRACTOR_VENDOR_CONFIDENCE_ZERO: float = 0.0   # Confidence for missing vendor
    EXTRACTOR_INVOICE_NUMBER_CONFIDENCE_HIGH: float = 0.95  # Confidence when invoice number found
    EXTRACTOR_INVOICE_NUMBER_CONFIDENCE_ZERO: float = 0.0   # Confidence when invoice number not found
    EXTRACTOR_URGENCY_CONFIDENCE_HIGH: float = 0.95   # Confidence for high urgency
    EXTRACTOR_URGENCY_CONFIDENCE_LOW: float = 0.90    # Confidence for low urgency
    EXTRACTOR_URGENCY_CONFIDENCE_NORMAL: float = 0.85 # Confidence for normal urgency
    EXTRACTOR_DEPARTMENT_CONFIDENCE_KNOWN: float = 0.92 # Confidence for known department
    EXTRACTOR_DEPARTMENT_CONFIDENCE_GENERAL: float = 0.50 # Confidence for general department

    # From rules.py
    RULES_VENDOR_CONFIDENCE_THRESHOLD: float = 0.80  # Threshold for vendor confidence check
    RULES_AMOUNT_CONFIDENCE_THRESHOLD: float = 0.80  # Threshold for amount confidence check
    RULES_VENDOR_CONFIDENCE_AMBIGUITY_THRESHOLD: float = 0.90  # Threshold for ambiguous extraction rule
    RULES_DEPARTMENT_CONFIDENCE_THRESHOLD: float = 0.80  # Threshold for department confidence check

settings = Settings()