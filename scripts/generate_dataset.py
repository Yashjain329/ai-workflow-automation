import os
import json
import random

# Large-Scale Deterministic Dataset Generator (v1.0-semester1)
# Fixed Seed = 42 for 100% scientific reproducibility

VENDORS = ["Acme Corp", "TechSupplies Inc", "Global Logistics", "CloudServices LLC", "OfficeDepot Ltd", "Apex Industries", "Nexus Systems", "Vertex Hardware"]
DEPARTMENTS = ["IT", "HR", "Finance", "Facilities", "Legal", "Operations", "Security"]
SERVICE_ISSUES = [
    "Need password reset for corporate email account",
    "Laptop screen flicker and battery power failure",
    "Request access to financial quarterly report folder",
    "HVAC air conditioning repair on floor 4",
    "Software license key request for PyCharm Pro",
    "VPN authentication failure during remote login",
    "Health insurance dental plan enrollment query",
    "Keycard badge reader malfunctioning at building entrance"
]
OOD_TEXTS = [
    "What is the weather forecast for London tomorrow?",
    "Can you give me a recipe for chocolate chip cookies?",
    "Who won the 1998 World Cup final?",
    "Summarize the plot of Hamlet in two sentences.",
    "Recommend three tourist attractions in Tokyo Japan.",
    "How do I solve a quadratic equation using the formula?",
    "What is the speed of light in vacuum in meters per second?",
    "Tell me a short bedtime story about a curious astronaut."
]

# Indirect, natural semantic phrasing templates to avoid blatant category keyword leakage
INVOICE_TEMPLATES = [
    "Please find attached the billing statement {inv_no} from {vendor} totaling ${amount:.2f} for recent quarterly deliverables. Remit payment upon receipt.",
    "Statement of account issued by {vendor} for reference {inv_no}. Total balance payable: ${amount:.2f}.",
    "Commercial receipt {inv_no} submitted by {vendor}. Amount payable: ${amount:.2f}.",
    "Kindly process remittance for {vendor} referenced under contract #{inv_no} in the amount of ${amount:.2f}.",
    "Expense settlement document from {vendor} indicating a balance of ${amount:.2f} with reference code {inv_no}."
]

TICKET_TEMPLATES = [
    "Employee inquiry directed to {dept}: {issue}. Requires assistance with {urgency} priority.",
    "Internal helpdesk ticket for {dept} department: {issue}. Flagged as {urgency} severity.",
    "Staff assistance request regarding {issue}. Please route to {dept} team.",
    "Service desk incident logged for {dept}: {issue}. Priority is {urgency}."
]

def generate_sample(sample_id: int) -> dict:
    rand_val = random.random()
    
    # 45% Invoice, 45% Service Request, 10% Out-of-Domain (OOD)
    if rand_val < 0.45:
        category = "invoice"
        vendor = random.choice(VENDORS)
        amount = round(random.uniform(150.0, 14500.0), 2)
        inv_no = f"INV-2026-{random.randint(1000, 9999)}"
        
        quality = random.choice(["clean", "paraphrased", "noisy", "incomplete", "ambiguous"])
        template = random.choice(INVOICE_TEMPLATES)

        if quality == "clean":
            text = template.format(inv_no=inv_no, vendor=vendor, amount=amount)
        elif quality == "paraphrased":
            text = f"Notice of payable fees from {vendor} on code {inv_no}. The total sum required is ${amount:.2f} for hardware infrastructure maintenance."
        elif quality == "noisy":
            text = f"Billing stmt {inv_no} - {vendor} sum ${amount:.2f} text with extraneous noise chars #$%^."
        elif quality == "incomplete":
            text = f"Payment notification from {vendor} with unstated total amount."
            amount = 0.0
        else: # ambiguous
            text = f"Purchase request summary for {vendor} estimating laptop software licensing cost around ${amount:.2f}."

        expected_route = "human_approval" if (amount > 5000.0 or quality in ["noisy", "incomplete", "ambiguous"]) else "auto_approve"

        return {
            "id": f"sample-{sample_id:04d}",
            "text": text,
            "workflow_category": "invoice",
            "subtype": "standard_invoice",
            "expected_safe_route": expected_route,
            "fields": {
                "vendor": vendor if quality != "incomplete" else "MISSING_VENDOR",
                "amount": amount if quality != "incomplete" else None,
                "invoice_number": inv_no
            },
            "quality": quality,
            "source_template": "invoice_generator_v1"
        }
        
    elif rand_val < 0.90:
        category = "service_request"
        dept = random.choice(DEPARTMENTS)
        issue = random.choice(SERVICE_ISSUES)
        urgency = random.choice(["normal", "high", "low"])
        quality = random.choice(["clean", "paraphrased", "noisy", "incomplete"])
        template = random.choice(TICKET_TEMPLATES)

        if quality == "clean":
            text = template.format(dept=dept, issue=issue, urgency=urgency)
        elif quality == "paraphrased":
            text = f"Request for administrative support: {issue}. Please notify the {dept} desk. Urgency: {urgency}."
        elif quality == "noisy":
            text = f"Helpdesk msg [{dept}] {issue} urg: {urgency} text noise err."
        else:
            text = f"Support inquiry: {issue} without specified department or priority."

        expected_route = "human_approval" if (urgency == "high" or quality in ["noisy", "incomplete"]) else "auto_approve"

        return {
            "id": f"sample-{sample_id:04d}",
            "text": text,
            "workflow_category": "service_request",
            "subtype": "support_ticket",
            "expected_safe_route": expected_route,
            "fields": {
                "department": dept if quality != "incomplete" else "General",
                "urgency": urgency
            },
            "quality": quality,
            "source_template": "ticket_generator_v1"
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
            "source_template": "ood_generator_v1"
        }

def main(total_samples: int = 3000, seed: int = 42):
    random.seed(seed)
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    samples = [generate_sample(i) for i in range(1, total_samples + 1)]
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

    # Compute class distribution
    counts = {}
    for s in samples:
        counts[s["workflow_category"]] = counts.get(s["workflow_category"], 0) + 1

    manifest = {
        "dataset_version": "v1.0_large_scale",
        "random_seed": seed,
        "total_records": total_samples,
        "train_records": len(train_data),
        "validation_records": len(val_data),
        "test_records": len(test_data),
        "class_distribution": counts,
        "quality_classes": ["clean", "paraphrased", "noisy", "incomplete", "ambiguous", "out_of_domain"]
    }

    with open(os.path.join(data_dir, "dataset_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Deterministic Dataset (Seed={seed}) successfully generated in '{data_dir}':")
    print(f"  - Total Samples: {total_samples}")
    print(f"  - Train: {len(train_data)} | Val: {len(val_data)} | Test: {len(test_data)}")
    print(f"  - Class Distribution: {counts}")

if __name__ == "__main__":
    main()
