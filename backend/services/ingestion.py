import json
import re
from typing import Dict, Any, Tuple

class IngestionService:
    @staticmethod
    def process_payload(raw_payload: str, source: str = "api") -> Tuple[str, Dict[str, Any]]:
        """
        Normalizes input payload from API JSON, form text, or simulated document.
        Returns (normalized_text, metadata).
        """
        if not raw_payload:
            return "", {"status": "empty"}
            
        normalized_text = ""
        metadata = {"source": source}

        # Try parsing JSON payload
        try:
            parsed = json.loads(raw_payload)
            if isinstance(parsed, dict):
                # Extract text fields
                text_parts = []
                for k, v in parsed.items():
                    text_parts.append(f"{k}: {v}")
                    metadata[k] = v
                normalized_text = "\n".join(text_parts)
            else:
                normalized_text = str(parsed)
        except json.JSONDecodeError:
            # Plain text or document text
            normalized_text = raw_payload

        # Basic text cleaning & normalization
        normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()
        metadata["character_count"] = len(normalized_text)
        metadata["word_count"] = len(normalized_text.split())

        return normalized_text, metadata
