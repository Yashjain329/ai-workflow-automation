import hashlib
import json
from typing import Dict, Any, Tuple

# Registry of executed business action hashes to enforce strict idempotency per business action
EXECUTED_ACTION_HASHES = set()

class DatabaseConnector:
    # Failure injection mode: 'NORMAL', 'DB_FAILURE', 'TIMEOUT', 'TRANSIENT_FAILURE', 'PERMANENT_FAILURE'
    failure_mode: str = "NORMAL"
    _transient_attempts: Dict[str, int] = {}

    @classmethod
    def set_failure_mode(cls, mode: str):
        cls.failure_mode = mode

    @classmethod
    def clear_idempotency_cache(cls):
        global EXECUTED_ACTION_HASHES
        EXECUTED_ACTION_HASHES = set()
        cls._transient_attempts = {}

    @classmethod
    def execute_action(cls, job_id: str, category: str, extracted_fields: Dict[str, Any], attempt: int = 1) -> Tuple[bool, str, str, bool]:
        """
        Executes persistent record update with idempotency check and failure injection support.
        Returns: (success: bool, result_message: str, error_code: str, is_duplicate: bool)
        """
        # 1. Failure Injection Logic
        if cls.failure_mode == "DB_FAILURE":
            return False, "DB_CONNECTION_ERROR: Simulated database connection failure.", "ERR_DB_CONN", False

        if cls.failure_mode == "TIMEOUT":
            return False, "TIMEOUT_ERROR: Simulated database transaction timeout.", "ERR_TIMEOUT", False

        if cls.failure_mode == "TRANSIENT_FAILURE":
            current_tries = cls._transient_attempts.get(job_id, 0) + 1
            cls._transient_attempts[job_id] = current_tries
            if current_tries < 3:
                return False, f"TRANSIENT_FAILURE: Attempt {current_tries} failed (simulating network blip).", "ERR_TRANSIENT", False
            # Succeeded on 3rd attempt!
            cls._transient_attempts.pop(job_id, None)

        if cls.failure_mode == "PERMANENT_FAILURE":
            return False, "FATAL_ERROR: Permanent unrecoverable connector failure.", "ERR_PERMANENT", False

        # 2. Generate deterministic business idempotency hash
        inv_no = extracted_fields.get("invoice_number") or ""
        business_key = f"{category}:{inv_no}:{json.dumps(extracted_fields, sort_keys=True)}"
        req_hash = hashlib.sha256(business_key.encode()).hexdigest()[:16]

        # 3. Idempotency Check
        if req_hash in EXECUTED_ACTION_HASHES:
            return True, f"IDEMPOTENT_SKIPPED: Action previously executed (Hash: {req_hash}). No duplicate record created.", "", True

        EXECUTED_ACTION_HASHES.add(req_hash)

        if category == "invoice":
            amount = extracted_fields.get("amount", 0.0) or 0.0
            vendor = extracted_fields.get("vendor", "Unknown")
            inv_no = extracted_fields.get("invoice_number", "GENERIC")
            result = f"RECORDED_INVOICE: Inv #{inv_no} from '{vendor}' for ${amount:.2f} updated in Finance Ledger (Hash: {req_hash})."
            return True, result, "", False

        elif category == "service_request":
            dept = extracted_fields.get("department", "General")
            urgency = extracted_fields.get("urgency", "normal")
            result = f"CREATED_TICKET: Request assigned to '{dept}' queue with urgency '{urgency}' (Hash: {req_hash})."
            return True, result, "", False

        return False, "UNKNOWN_CATEGORY_ACTION_FAILED", "ERR_INVALID_CATEGORY", False
