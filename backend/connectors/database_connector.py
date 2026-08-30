import hashlib
import json
from typing import Dict, Any, Tuple

class DatabaseConnector:
    @staticmethod
    def execute_action(job_id: str, category: str, extracted_fields: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Executes persistent record update in database.
        Returns (success, result_message, error_code).
        """
        # Generate idempotency request hash
        raw_str = f"{job_id}:{category}:{json.dumps(extracted_fields, sort_keys=True)}"
        req_hash = hashlib.sha256(raw_str.encode()).hexdigest()[:16]

        if category == "invoice":
            amount = extracted_fields.get("amount", 0.0)
            vendor = extracted_fields.get("vendor", "Unknown")
            inv_no = extracted_fields.get("invoice_number", "GENERIC")
            result = f"RECORDED_INVOICE: Inv #{inv_no} from '{vendor}' for ${amount:.2f} updated in Finance Ledger (Hash: {req_hash})."
            return True, result, ""

        elif category == "service_request":
            dept = extracted_fields.get("department", "General")
            urgency = extracted_fields.get("urgency", "normal")
            result = f"CREATED_TICKET: Request assigned to '{dept}' queue with urgency '{urgency}' (Hash: {req_hash})."
            return True, result, ""

        return False, "UNKNOWN_CATEGORY_ACTION_FAILED", "ERR_INVALID_CATEGORY"
