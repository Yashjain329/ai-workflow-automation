from typing import Dict, Any, List, Tuple
from backend.config import settings

class PolicyRules:
    @staticmethod
    def evaluate_policy(category: str, extracted_fields: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Evaluates deterministic business policy rules.
        Returns (risk_level, rules_applied).
        risk_level can be: 'low', 'medium', 'high'.
        """
        rules_applied = []

        if category == "invoice":
            amount = extracted_fields.get("amount", 0.0)
            vendor = extracted_fields.get("vendor", "Unknown Vendor")

            # Policy Rule 1: Unknown vendor check
            if vendor == "Unknown Vendor":
                rules_applied.append("RULE_UNKNOWN_VENDOR: Vendor identity unverified")
                return "high", rules_applied

            # Policy Rule 2: Amount threshold check
            if amount > settings.AUTO_APPROVE_MAX_AMOUNT:
                rules_applied.append(f"RULE_HIGH_AMOUNT: Invoice amount (${amount:.2f}) exceeds auto-approval limit (${settings.AUTO_APPROVE_MAX_AMOUNT:.2f})")
                return "medium", rules_applied

            # Policy Rule 3: Missing amount check
            if amount <= 0.0:
                rules_applied.append("RULE_INVALID_AMOUNT: Invoice amount is zero or unextracted")
                return "high", rules_applied

            rules_applied.append("RULE_PASSED: Invoice meets standard policy thresholds")
            return "low", rules_applied

        elif category == "service_request":
            urgency = extracted_fields.get("urgency", "normal")
            if urgency == "high":
                rules_applied.append("RULE_HIGH_URGENCY: High-priority service request requires supervisor notification")
                return "medium", rules_applied

            rules_applied.append("RULE_PASSED: Service request meets standard policy thresholds")
            return "low", rules_applied

        else:
            rules_applied.append("RULE_UNRECOGNIZED_CATEGORY: Unclassified task category")
            return "high", rules_applied
