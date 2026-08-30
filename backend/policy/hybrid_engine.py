from typing import Dict, Any, List, Tuple
from backend.config import settings

class HybridDecisionEngine:
    @staticmethod
    def make_decision(confidence: float, risk_level: str, rules_applied: List[str]) -> Tuple[str, str]:
        """
        Combines AI Prediction Confidence and Policy Risk Level into a final operational decision.
        
        Returns:
            (route, explanation)
            route options:
              - 'auto_approve': Proceed directly to automated execution connector
              - 'human_approval': Escalate to Human Approval Queue
              - 'reject': Reject job / require manual re-submission
        """
        # Rule 1: High Risk Policy Violation override regardless of confidence
        if risk_level == "high":
            explanation = (
                f"Policy Risk High. Triggered rules: {'; '.join(rules_applied)}. "
                f"Auto-execution blocked by safety gate."
            )
            return "human_approval", explanation

        # Rule 2: High Confidence & Low Risk -> Auto Approve
        if confidence >= settings.CONFIDENCE_HIGH and risk_level == "low":
            explanation = (
                f"High AI Confidence ({confidence:.2f} >= {settings.CONFIDENCE_HIGH}) and Low Policy Risk. "
                f"Approved for immediate automated execution."
            )
            return "auto_approve", explanation

        # Rule 3: Medium Confidence OR Medium Risk -> Human Approval Queue
        if confidence >= settings.CONFIDENCE_MEDIUM:
            explanation = (
                f"Moderate Confidence ({confidence:.2f}) or Policy Flag ({risk_level.upper()} Risk). "
                f"Escalating task to Human Approval Queue."
            )
            return "human_approval", explanation

        # Rule 4: Low Confidence (< 0.70) -> Reject / Manual Review
        explanation = (
            f"Low AI Confidence ({confidence:.2f} < {settings.CONFIDENCE_MEDIUM}). "
            f"Automated processing rejected. Requires manual intake."
        )
        return "reject", explanation
