import re
from typing import Dict, Any

class FieldExtractor:
    @staticmethod
    def extract_fields(text: str, category: str) -> Dict[str, Any]:
        """
        Extracts structured fields based on category.
        """
        extracted = {}

        if category == "invoice":
            # Extract Amount with priority on currency symbol or total keyword
            amount_match = re.search(r'\$\s*([0-9,]+(?:\.[0-9]{1,2})?)', text)
            if not amount_match:
                amount_match = re.search(r'(?:amount|total|due|sum|cost)\s*[:\$]?\s*([0-9,]+(?:\.[0-9]{1,2})?)', text, re.IGNORECASE)
            
            if amount_match:
                try:
                    amount_str = amount_match.group(1).replace(",", "")
                    extracted["amount"] = float(amount_str)
                except ValueError:
                    extracted["amount"] = 0.0
            else:
                extracted["amount"] = 0.0

            # Extract Vendor
            vendor_match = re.search(r'(?:vendor|from|company|supplier):\s*([A-Za-z0-9\s]+)', text, re.IGNORECASE)
            if not vendor_match:
                vendor_match = re.search(r'from\s+([A-Za-z0-9\s]+?)(?=\s+Total|\s+Invoice|\s+Amount|\.|$)', text, re.IGNORECASE)
            
            if vendor_match:
                extracted["vendor"] = vendor_match.group(1).strip()
            else:
                extracted["vendor"] = "Unknown Vendor"

            # Extract Invoice Number
            inv_match = re.search(r'(?:invoice|inv|po)[#:\s]*([A-Za-z0-9-]+)', text, re.IGNORECASE)
            if inv_match:
                extracted["invoice_number"] = inv_match.group(1).strip()
            else:
                extracted["invoice_number"] = "INV-GENERIC"

        elif category == "service_request":
            # Extract Urgency
            if re.search(r'\b(urgent|critical|high|emergency)\b', text, re.IGNORECASE):
                extracted["urgency"] = "high"
            elif re.search(r'\b(low|minor)\b', text, re.IGNORECASE):
                extracted["urgency"] = "low"
            else:
                extracted["urgency"] = "normal"

            # Extract Department / Subcategory
            if re.search(r'\b(laptop|password|software|network|it)\b', text, re.IGNORECASE):
                extracted["department"] = "IT"
            elif re.search(r'\b(payroll|leave|benefits|hr)\b', text, re.IGNORECASE):
                extracted["department"] = "HR"
            else:
                extracted["department"] = "General"

        return extracted
