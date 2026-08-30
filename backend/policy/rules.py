from typing import Dict, Any, List, Tuple
from backend.config import settings

class PolicyRules:
    @staticmethod
    def evaluate_policy(category: str, extracted_fields: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Evaluates deterministic business policy rules and extraction safety constraints.
        Returns: (risk_level: str, rules_applied: List[str])
        risk_level options: 'low', 'medium', 'high'.
        """
        rules_applied = []

        if category == "invoice":
            amount = extracted_fields.get("amount")
            vendor = extracted_fields.get("vendor", "MISSING_VENDOR")
            vendor_conf = extracted_fields.get("vendor_confidence", 1.0)
            amount_conf = extracted_fields.get("amount_confidence", 1.0)

            # Safety Rule 1: Unknown or missing vendor identity
            if vendor in ["MISSING_VENDOR", "Unknown Vendor", "Unknown", None] or vendor_conf < 0.80:
                rules_applied.append("RULE_UNKNOWN_VENDOR: Vendor identity unverified or extraction confidence low")
                return "high", rules_applied

            # Safety Rule 2: Invalid or missing amount
            if amount is None or amount <= 0.0 or amount_conf < 0.80:
                rules_applied.append("RULE_INVALID_AMOUNT: Invoice amount missing, zero, or extraction uncertain")
                return "high", rules_applied

            # Safety Rule 3: High dollar amount threshold (> $5,000)
            if amount > settings.AUTO_APPROVE_MAX_AMOUNT:
                rules_applied.append(f"RULE_HIGH_AMOUNT: Invoice amount (${amount:.2f}) exceeds auto-approval limit (${settings.AUTO_APPROVE_MAX_AMOUNT:.2f})")
                return "medium", rules_applied

            # Safety Rule 4: Ambiguity or mixed-domain indicator
            if vendor_conf < 0.90:
                rules_applied.append("RULE_AMBIGUOUS_EXTRACTION: Field extraction confidence requires human validation")
                return "medium", rules_applied

            rules_applied.append("RULE_PASSED: Invoice satisfies all deterministic business policy constraints")
            return "low", rules_applied

        elif category == "service_request":
            urgency = extracted_fields.get("urgency", "normal")
            dept = extracted_fields.get("department", "General")
            dept_conf = extracted_fields.get("department_confidence", 1.0)

            # Safety Rule 1: High urgency or critical priority
            if urgency == "high":
                rules_applied.append("RULE_HIGH_URGENCY: High-priority service request requires supervisor assignment")
                return "medium", rules_applied

            # Safety Rule 2: Unspecified or uncertain department
            if dept == "General" or dept_conf < 0.80:
                rules_applied.append("RULE_UNSPECIFIED_DEPARTMENT: Department routing unconfirmed")
                return "medium", rules_applied

            rules_applied.append("RULE_PASSED: Service request meets standard policy thresholds")
            return "low", rules_applied

        else:
            rules_applied.append("RULE_UNRECOGNIZED_CATEGORY: Out-of-domain or unclassified request")
            return "high", rules_applied
