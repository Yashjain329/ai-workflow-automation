from typing import Tuple

class NotificationConnector:
    @staticmethod
    def send_notification(job_id: str, recipient: str, message: str) -> Tuple[bool, str, str]:
        """
        Simulates email/messaging notification delivery.
        Returns (success, result_message, error_code).
        """
        if not recipient:
            return False, "NOTIFICATION_FAILED: Missing recipient address", "ERR_MISSING_RECIPIENT"
            
        result = f"NOTIFICATION_SENT: Delivered message to '{recipient}' regarding Job '{job_id}'."
        return True, result, ""
