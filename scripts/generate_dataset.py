import os
import json
import random

# Master Plan Schema Synthetic Dataset Generator for Invoice, Service Request, & Out-of-Domain Tasks

VENDORS = ["Acme Corp", "TechSupplies Inc", "Global Logistics", "CloudServices LLC", "OfficeDepot Ltd"]
DEPARTMENTS = ["IT", "HR", "Finance", "Facilities", "Legal"]
SERVICE_ISSUES = [
    "Need password reset for corporate email account",
    "Laptop screen flicker and battery power failure",
    "Request access to financial quarterly report folder",
    "HVAC air conditioning repair on floor 4",
    "Software license key request for PyCharm Pro"
]
OOD_TEXTS = [
    "What is the weather forecast for London tomorrow?",
    "Can you give me a recipe for chocolate chip cookies?",
    "Who won the 1998 World Cup final?",
    "Summarize the plot of Hamlet in two sentences."
]

def generate_sample(sample_id: int) -> dict:
    rand_val = random.random()
    
    # 45% Invoice, 45% Service Request, 10% Out-of-Domain
    if rand_val < 0.45:
        category = "invoice"
        vendor = random.choice(VENDORS)
        amount = round(random.uniform(150.0, 12500.0), 2)
        inv_no = f"INV-2026-{random.randint(1000, 9999)}"
        
        quality = random.choice(["clean", "paraphrased", "noisy", "incomplete", "ambiguous"])
        if quality == "clean":
            text = f"INVOICE #{inv_no} from {vendor}. Total Amount Due: ${amount:.2f}. Remit payment to finance."
        elif quality == "paraphrased":
            text = f"Billing statement {inv_no} issued by {vendor} for total sum of ${amount:.2f} due upon receipt."
        elif quality == "noisy":
            text = f"Bill receipt {inv_no} - {vendor} sum ${amount:.2f} text with extraneous noise chars #$%^."
        elif quality == "incomplete":
            text = f"Invoice notification from {vendor} with unstated total amount."
            amount = 0.0
        else: # ambiguous
            text = f"Purchase request summary for {vendor} estimating software laptop cost around ${amount:.2f}."

        expected_route = "human_approval" if (amount > 5000.0 or quality in ["noisy", "incomplete", "ambiguous"]) else "auto_approve"

        return {
            "id": f"sample-{sample_id:04d}",
            "text": text,
            "workflow_category": "invoice",
            "subtype": "standard_invoice",
            "expected_safe_route": expected_route,
            "fields": {"vendor": vendor if quality != "incomplete" else "Unknown Vendor", "amount": amount, "invoice_number": inv_no},
            "quality": quality,
            "source_template": f"invoice_template_{random.randint(1, 5)}"
        }
        
    elif rand_val < 0.90:
        category = "service_request"
        dept = random.choice(DEPARTMENTS)
        issue = random.choice(SERVICE_ISSUES)
        urgency = random.choice(["normal", "high", "low"])
        quality = random.choice(["clean", "paraphrased", "noisy", "incomplete"])

        if quality == "clean":
            text = f"SUPPORT TICKET [{dept}]: {issue}. Urgency level: {urgency.upper()}."
        elif quality == "paraphrased":
            text = f"Employee inquiry directed to {dept}: {issue}. Requires attention with {urgency} priority."
        elif quality == "noisy":
            text = f"Helpdesk msg [{dept}] {issue} urg: {urgency} raw text noise err."
        else:
            text = f"Support ticket: {issue} without specified department or priority."

        expected_route = "human_approval" if (urgency == "high" or quality in ["noisy", "incomplete"]) else "auto_approve"

        return {
            "id": f"sample-{sample_id:04d}",
            "text": text,
            "workflow_category": "service_request",
            "subtype": "support_ticket",
            "expected_safe_route": expected_route,
            "fields": {"department": dept if quality != "incomplete" else "General", "urgency": urgency},
            "quality": quality,
            "source_template": f"ticket_template_{random.randint(1, 5)}"
        }
    else:
        text = random.choice(OOD_TEXTS)
        return {
            "id": f"sample-{sample_id:04d}",
            "text": text,
            "workflow_category": "unknown",
            "subtype": "out_of_domain",
            "expected_safe_route": "reject",
            "fields": {},
            "quality": "out_of_domain",
            "source_template": "ood_template"
        }

def main():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    samples = [generate_sample(i) for i in range(1, 301)]
    random.shuffle(samples)

    # 70% Train, 15% Val, 15% Test
    train_split = int(len(samples) * 0.70)
    val_split = int(len(samples) * 0.85)

    train_data = samples[:train_split]
    val_data = samples[train_split:val_split]
    test_data = samples[val_split:]

    for item in train_data: item["split"] = "train"
    for item in val_data: item["split"] = "val"
    for item in test_data: item["split"] = "test"

    with open(os.path.join(data_dir, "train.json"), "w") as f:
        json.dump(train_data, f, indent=2)

    with open(os.path.join(data_dir, "val.json"), "w") as f:
        json.dump(val_data, f, indent=2)

    with open(os.path.join(data_dir, "test.json"), "w") as f:
        json.dump(test_data, f, indent=2)

    print(f"Master Plan Dataset successfully generated in '{data_dir}':")
    print(f"  - Train: {len(train_data)} samples")
    print(f"  - Validation: {len(val_data)} samples")
    print(f"  - Test: {len(test_data)} samples")

if __name__ == "__main__":
    main()
