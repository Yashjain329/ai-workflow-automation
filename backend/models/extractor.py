import re
from typing import Dict, Any

KNOWN_DEPARTMENTS = ["IT", "HR", "Finance", "Facilities", "Legal", "Operations", "Security"]
KNOWN_VENDORS = ["Acme Corp", "TechSupplies Inc", "Global Logistics", "CloudServices LLC", "OfficeDepot Ltd", "Apex Industries", "Nexus Systems", "Vertex Hardware"]

class FieldExtractor:
    @staticmethod
    def extract_fields(text: str, category: str) -> Dict[str, Any]:
        """
        Extracts structured fields based on category with explicit missing field representation and field confidence scores.
        """
        extracted = {}

        if category == "invoice":
            # 1. Extract Amount
            amount_match = re.search(r'\$\s*([0-9,]+(?:\.[0-9]{1,2})?)', text)
            if not amount_match:
                amount_match = re.search(r'(?:amount|total|due|sum|cost|balance)\s*[:\$]?\s*([0-9,]+(?:\.[0-9]{1,2})?)', text, re.IGNORECASE)
            
            if amount_match:
                try:
                    amount_str = amount_match.group(1).replace(",", "")
                    extracted["amount"] = float(amount_str)
                    extracted["amount_confidence"] = 0.95
                except ValueError:
                    extracted["amount"] = 0.0
                    extracted["amount_confidence"] = 0.0
            else:
                extracted["amount"] = None
                extracted["amount_confidence"] = 0.0

            # 2. Extract Vendor (Pattern extraction with known vendor alignment)
            vendor_found = None
            for v in KNOWN_VENDORS:
                if re.search(r'\b' + re.escape(v) + r'\b', text, re.IGNORECASE):
                    vendor_found = v
                    break

            if not vendor_found:
                vendor_match = re.search(r'(?:from|issued by|submitted by|vendor|remittance for)\s+([A-Za-z0-9\s]+?)(?=\s+total|\s+for|\s+referenced|\s+indicating|\s+with|\.|\$|,|$)', text, re.IGNORECASE)
                if vendor_match:
                    vendor_found = vendor_match.group(1).strip()

            if vendor_found and vendor_found.lower() not in ["unknown", "unknown vendor"]:
                extracted["vendor"] = vendor_found
                extracted["vendor_confidence"] = 0.92
            else:
                extracted["vendor"] = "MISSING_VENDOR"
                extracted["vendor_confidence"] = 0.0

            # 3. Extract Invoice Number
            inv_match = re.search(r'\b(INV-\d{4}-\d{4})\b', text, re.IGNORECASE)
            if not inv_match:
                inv_match = re.search(r'(?:invoice|inv|statement|receipt|contract|code)[#:\s]*([A-Za-z0-9-]+)', text, re.IGNORECASE)

            if inv_match:
                extracted["invoice_number"] = inv_match.group(1).strip()
                extracted["invoice_number_confidence"] = 0.95
            else:
                extracted["invoice_number"] = "MISSING_INV_NUMBER"
                extracted["invoice_number_confidence"] = 0.0

        elif category == "service_request":
            # 1. Extract Urgency
            if re.search(r'\b(urgent|critical|high|emergency)\b', text, re.IGNORECASE):
                extracted["urgency"] = "high"
                extracted["urgency_confidence"] = 0.95
            elif re.search(r'\b(low|minor)\b', text, re.IGNORECASE):
                extracted["urgency"] = "low"
                extracted["urgency_confidence"] = 0.90
            else:
                extracted["urgency"] = "normal"
                extracted["urgency_confidence"] = 0.75

            # 2. Extract Department
            dept_found = "General"
            for dept in KNOWN_DEPARTMENTS:
                if re.search(r'\b' + re.escape(dept) + r'\b', text, re.IGNORECASE):
                    dept_found = dept
                    break

            extracted["department"] = dept_found
            extracted["department_confidence"] = 0.90 if dept_found != "General" else 0.50

        return extracted
