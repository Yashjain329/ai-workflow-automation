import re
from typing import Dict, Any

class FieldExtractor:
    @staticmethod
    def extract_fields(text: str, category: str) -> Dict[str, Any]:
        """
        Extracts structured fields based on category with explicit missing field representation and field confidence.
        """
        extracted = {}

        if category == "invoice":
            # Extract Amount
            amount_match = re.search(r'\$\s*([0-9,]+(?:\.[0-9]{1,2})?)', text)
            if not amount_match:
                amount_match = re.search(r'(?:amount|total|due|sum|cost)\s*[:\$]?\s*([0-9,]+(?:\.[0-9]{1,2})?)', text, re.IGNORECASE)
            
            if amount_match:
                try:
                    amount_str = amount_match.group(1).replace(",", "")
                    extracted["amount"] = float(amount_str)
                    extracted["amount_confidence"] = 0.95
                except ValueError:
                    extracted["amount"] = 0.0
                    extracted["amount_confidence"] = 0.0
            else:
                extracted["amount"] = None # Explicitly missing
                extracted["amount_confidence"] = 0.0

            # Extract Vendor
            vendor_match = re.search(r'(?:vendor|from|company|supplier):\s*([A-Za-z0-9\s]+)', text, re.IGNORECASE)
            if not vendor_match:
                vendor_match = re.search(r'from\s+([A-Za-z0-9\s]+?)(?=\s+Total|\s+Invoice|\s+Amount|\.|$)', text, re.IGNORECASE)
            
            if vendor_match:
                vendor_val = vendor_match.group(1).strip()
                extracted["vendor"] = vendor_val
                extracted["vendor_confidence"] = 0.90 if vendor_val != "Unknown Vendor" else 0.40
            else:
                extracted["vendor"] = "MISSING_VENDOR"
                extracted["vendor_confidence"] = 0.0

            # Extract Invoice Number
            inv_match = re.search(r'(?:invoice|inv|po)[#:\s]*([A-Za-z0-9-]+)', text, re.IGNORECASE)
            if inv_match:
                extracted["invoice_number"] = inv_match.group(1).strip()
                extracted["invoice_number_confidence"] = 0.95
            else:
                extracted["invoice_number"] = "MISSING_INV_NUMBER"
                extracted["invoice_number_confidence"] = 0.0

        elif category == "service_request":
            # Extract Urgency
            if re.search(r'\b(urgent|critical|high|emergency)\b', text, re.IGNORECASE):
                extracted["urgency"] = "high"
                extracted["urgency_confidence"] = 0.95
            elif re.search(r'\b(low|minor)\b', text, re.IGNORECASE):
                extracted["urgency"] = "low"
                extracted["urgency_confidence"] = 0.90
            else:
                extracted["urgency"] = "normal"
                extracted["urgency_confidence"] = 0.70

            # Extract Department / Subcategory
            if re.search(r'\b(laptop|password|software|network|it)\b', text, re.IGNORECASE):
                extracted["department"] = "IT"
                extracted["department_confidence"] = 0.90
            elif re.search(r'\b(payroll|leave|benefits|hr)\b', text, re.IGNORECASE):
                extracted["department"] = "HR"
                extracted["department_confidence"] = 0.90
            else:
                extracted["department"] = "General"
                extracted["department_confidence"] = 0.50

        return extracted
