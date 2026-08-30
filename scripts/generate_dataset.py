import os
import json
import random

# Synthetic Dataset Generator for Invoice & Support Ticket Workflows

VENDORS = ["Acme Corp", "TechSupplies Inc", "Global Logistics", "CloudServices LLC", "OfficeDepot Ltd"]
DEPARTMENTS = ["IT", "HR", "Finance", "Facilities", "Legal"]
SERVICE_ISSUES = [
    "Need password reset for corporate email account",
    "Laptop screen flicker and battery power failure",
    "Request access to financial quarterly report folder",
    "HVAC air conditioning repair on floor 4",
    "Software license key request for PyCharm Pro"
]

def generate_sample(sample_id: int) -> dict:
    is_invoice = random.choice([True, False])
    
    if is_invoice:
        vendor = random.choice(VENDORS)
        amount = round(random.uniform(150.0, 12500.0), 2)
        inv_no = f"INV-2026-{random.randint(1000, 9999)}"
        
        # Add random noise or clean format
        noise_type = random.choice(["clean", "noisy", "ambiguous"])
        if noise_type == "clean":
            text = f"INVOICE #{inv_no} from {vendor}. Total Amount Due: ${amount:.2f}. Remit payment to finance department."
        elif noise_type == "noisy":
            text = f"Bill receipt {inv_no} - {vendor} sum ${amount:.2f} text with extraneous characters #$%^."
        else:
            # Ambiguous (might confuse simple keyword rules)
            text = f"Purchase request summary for {vendor} estimating cost around ${amount:.2f} for upcoming project."

        return {
            "sample_id": f"SAMP-{sample_id:04d}",
            "text": text,
            "true_category": "invoice",
            "extracted_fields": {"vendor": vendor, "amount": amount, "invoice_number": inv_no},
            "difficulty": noise_type
        }
    else:
        dept = random.choice(DEPARTMENTS)
        issue = random.choice(SERVICE_ISSUES)
        urgency = random.choice(["normal", "high", "low"])
        text = f"SUPPORT TICKET [{dept}]: {issue}. Urgency level: {urgency.upper()}. Requesting assistance."

        return {
            "sample_id": f"SAMP-{sample_id:04d}",
            "text": text,
            "true_category": "service_request",
            "extracted_fields": {"department": dept, "urgency": urgency},
            "difficulty": "clean"
        }

def main():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    samples = [generate_sample(i) for i in range(1, 201)]
    random.shuffle(samples)

    # 60% Train, 20% Val, 20% Test
    train_split = int(len(samples) * 0.6)
    val_split = int(len(samples) * 0.8)

    train_data = samples[:train_split]
    val_data = samples[train_split:val_split]
    test_data = samples[val_split:]

    with open(os.path.join(data_dir, "train.json"), "w") as f:
        json.dump(train_data, f, indent=2)

    with open(os.path.join(data_dir, "val.json"), "w") as f:
        json.dump(val_data, f, indent=2)

    with open(os.path.join(data_dir, "test.json"), "w") as f:
        json.dump(test_data, f, indent=2)

    print(f"Dataset successfully generated in '{data_dir}':")
    print(f"  - Train: {len(train_data)} samples")
    print(f"  - Validation: {len(val_data)} samples")
    print(f"  - Test: {len(test_data)} samples")

if __name__ == "__main__":
    main()
