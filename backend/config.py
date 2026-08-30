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

settings = Settings()
