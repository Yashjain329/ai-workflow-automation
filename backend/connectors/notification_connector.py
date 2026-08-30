from typing import Tuple, Dict

class NotificationConnector:
    failure_mode: str = "NORMAL"
    _transient_attempts: Dict[str, int] = {}

    @classmethod
    def set_failure_mode(cls, mode: str):
        cls.failure_mode = mode

    @classmethod
    def send_notification(cls, job_id: str, recipient: str, message: str, attempt: int = 1) -> Tuple[bool, str, str]:
        """
        Simulates notification delivery with failure injection and retry tracking.
        Returns: (success: bool, result_message: str, error_code: str)
        """
        if not recipient:
            return False, "NOTIFICATION_FAILED: Missing recipient address", "ERR_MISSING_RECIPIENT"

        if cls.failure_mode == "NOTIFICATION_FAILURE":
            return False, "SMTP_ERROR: Failed to connect to notification gateway.", "ERR_SMTP_GATEWAY"

        if cls.failure_mode == "TRANSIENT_FAILURE":
            current_tries = cls._transient_attempts.get(job_id, 0) + 1
            cls._transient_attempts[job_id] = current_tries
            if current_tries < 3:
                return False, f"NOTIFICATION_TRANSIENT_FAILURE: Attempt {current_tries} failed.", "ERR_NOTIF_TRANSIENT"
            cls._transient_attempts.pop(job_id, None)

        result = f"NOTIFICATION_SENT: Delivered message to '{recipient}' regarding Job '{job_id}' (Attempt: {attempt})."
        return True, result, ""
