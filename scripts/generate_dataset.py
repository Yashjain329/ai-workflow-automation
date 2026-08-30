import os
import json
import random

# Advanced Realistic Dataset Generator (Semester 1 Final Edition)
# Fixed Seed = 42 for 100% scientific reproducibility

VENDORS = [
    "Acme Corp", "TechSupplies Inc", "Global Logistics", "CloudServices LLC", 
    "OfficeDepot Ltd", "Apex Industries", "Nexus Systems", "Vertex Hardware",
    "DataCore Analytics", "Horizon Networks"
]

DEPARTMENTS = ["IT", "HR", "Finance", "Facilities", "Legal", "Operations", "Security"]

SERVICE_ISSUES = [
    "Need password reset for corporate email account",
    "Laptop screen flicker and battery power failure",
    "Request access to financial quarterly report folder",
    "HVAC air conditioning repair on floor 4",
    "Software license key request for PyCharm Pro",
    "VPN authentication failure during remote login",
    "Health insurance dental plan enrollment query",
    "Keycard badge reader malfunctioning at building entrance",
    "Printer on floor 2 is out of toner and paper jams constantly",
    "Requesting dual monitor setup for software development workstation"
]

OOD_TEXTS = [
    "What is the weather forecast for London tomorrow?",
    "Can you give me a recipe for chocolate chip cookies?",
    "Who won the 1998 World Cup final?",
    "Summarize the plot of Hamlet in two sentences.",
    "Recommend three tourist attractions in Tokyo Japan.",
    "How do I solve a quadratic equation using the formula?",
    "What is the speed of light in vacuum in meters per second?",
    "Tell me a short bedtime story about a curious astronaut.",
    "Can you compose a sonnet about autumn leaves?",
    "What is the capital of Australia?"
]

# Indirect, challenging, implicit, and mixed-intent templates
INVOICE_TEMPLATES_CLEAN = [
    "Please find attached the billing statement {inv_no} from {vendor} totaling ${amount:.2f} for recent quarterly deliverables. Remit payment upon receipt.",
    "Statement of account issued by {vendor} for reference {inv_no}. Total balance payable: ${amount:.2f}.",
    "Commercial receipt {inv_no} submitted by {vendor}. Amount payable: ${amount:.2f}.",
    "Kindly process remittance for {vendor} referenced under contract #{inv_no} in the amount of ${amount:.2f}."
]

INVOICE_TEMPLATES_IMPLICIT = [
    "Payment is due against the recent procurement deliverables from {vendor}. The outstanding sum is ${amount:.2f} under voucher reference {inv_no}.",
    "Disbursement required for {vendor} consulting fees totaling ${amount:.2f} (Ref: {inv_no}). Please arrange ledger wire transfer.",
    "Kindly settle the remaining balance of ${amount:.2f} billed by {vendor} regarding deliverable milestone #{inv_no}.",
    "Accounts payable notice: {vendor} has completed maintenance services. Total fee due: ${amount:.2f}. Tracking code: {inv_no}."
]

INVOICE_TEMPLATES_AMBIGUOUS_MIXED = [
    "Can finance confirm if the attached billing statement #{inv_no} for ${amount:.2f} from {vendor} requires IT director signoff before ledger posting?",
    "Purchase inquiry and expense settlement summary for {vendor} estimating software tooling cost around ${amount:.2f} for upcoming quarter (Ref {inv_no}).",
    "Reimbursement voucher #{inv_no} submitted for {vendor} supplies amounting to ${amount:.2f}. Please review department allocation."
]

TICKET_TEMPLATES_CLEAN = [
    "Employee inquiry directed to {dept}: {issue}. Requires assistance with {urgency} priority.",
    "Internal helpdesk ticket for {dept} department: {issue}. Flagged as {urgency} severity.",
    "Staff assistance request regarding {issue}. Please route to {dept} team.",
    "Service desk incident logged for {dept}: {issue}. Priority is {urgency}."
]

TICKET_TEMPLATES_IMPLICIT = [
    "Staff member experiencing {issue}. Kindly dispatch technician or support personnel from {dept}. Urgency level: {urgency}.",
    "Ongoing operational blocker: {issue}. Requesting immediate escalation to the on-duty {dept} administrator with {urgency} priority.",
    "Workstation incident reported: {issue}. Please assign to {dept} queue for resolution. Priority status: {urgency}."
]

def generate_sample(sample_id: int) -> dict:
    rand_val = random.random()
    
    # 45% Invoice, 45% Service Request, 10% Out-of-Domain
    if rand_val < 0.45:
        category = "invoice"
        vendor = random.choice(VENDORS)
        amount = round(random.uniform(150.0, 16500.0), 2)
        inv_no = f"INV-2026-{random.randint(1000, 9999)}"
        
        quality = random.choices(
            ["clean", "implicit", "paraphrased", "noisy", "incomplete", "ambiguous"],
            weights=[0.30, 0.25, 0.15, 0.12, 0.08, 0.10]
        )[0]

        if quality == "clean":
            text = random.choice(INVOICE_TEMPLATES_CLEAN).format(inv_no=inv_no, vendor=vendor, amount=amount)
        elif quality == "implicit":
            text = random.choice(INVOICE_TEMPLATES_IMPLICIT).format(inv_no=inv_no, vendor=vendor, amount=amount)
        elif quality == "ambiguous":
            text = random.choice(INVOICE_TEMPLATES_AMBIGUOUS_MIXED).format(inv_no=inv_no, vendor=vendor, amount=amount)
        elif quality == "paraphrased":
            text = f"Notice of payable fees from {vendor} on reference {inv_no}. The total sum required is ${amount:.2f} for maintenance."
        elif quality == "noisy":
            text = f"Billing stmt {inv_no} - {vendor} sum ${amount:.2f} noise chars #$%^."
        else: # incomplete
            text = f"Payment notification from {vendor} on code {inv_no} with unstated balance."
            amount = 0.0

        # Safe route rule: Clean invoices with amount <= 5000 and complete fields are safe for auto-execution
        expected_route = "auto_approve" if (amount > 0 and amount <= 5000.0 and quality in ["clean", "paraphrased"]) else "human_approval"

        return {
            "id": f"sample-{sample_id:04d}",
            "text": text,
            "workflow_category": "invoice",
            "subtype": f"invoice_{quality}",
            "expected_safe_route": expected_route,
            "fields": {
                "vendor": vendor if quality != "incomplete" else "MISSING_VENDOR",
                "amount": amount if quality != "incomplete" else None,
                "invoice_number": inv_no
            },
            "quality": quality,
            "source_template": f"invoice_{quality}_v2"
        }
        
    elif rand_val < 0.90:
        category = "service_request"
        dept = random.choice(DEPARTMENTS)
        issue = random.choice(SERVICE_ISSUES)
        urgency = random.choice(["normal", "high", "low"])
        quality = random.choices(
            ["clean", "implicit", "paraphrased", "noisy", "incomplete"],
            weights=[0.35, 0.25, 0.18, 0.12, 0.10]
        )[0]

        if quality == "clean":
            text = random.choice(TICKET_TEMPLATES_CLEAN).format(dept=dept, issue=issue, urgency=urgency)
        elif quality == "implicit":
            text = random.choice(TICKET_TEMPLATES_IMPLICIT).format(dept=dept, issue=issue, urgency=urgency)
        elif quality == "paraphrased":
            text = f"Request for administrative support: {issue}. Please notify the {dept} desk. Urgency: {urgency}."
        elif quality == "noisy":
            text = f"Helpdesk msg [{dept}] {issue} urg: {urgency} text noise err."
        else:
            text = f"Support inquiry: {issue} without specified department or priority."
            urgency = "normal"

        expected_route = "auto_approve" if (urgency in ["normal", "low"] and quality in ["clean", "paraphrased", "implicit"]) else "human_approval"

        return {
            "id": f"sample-{sample_id:04d}",
            "text": text,
            "workflow_category": "service_request",
            "subtype": f"ticket_{quality}",
            "expected_safe_route": expected_route,
            "fields": {
                "department": dept if quality != "incomplete" else "General",
                "urgency": urgency
            },
            "quality": quality,
            "source_template": f"ticket_{quality}_v2"
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
            "source_template": "ood_generator_v2"
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

    # Quality & class distribution
    class_counts = {}
    quality_counts = {}
    for s in samples:
        class_counts[s["workflow_category"]] = class_counts.get(s["workflow_category"], 0) + 1
        quality_counts[s["quality"]] = quality_counts.get(s["quality"], 0) + 1

    manifest = {
        "dataset_version": "v1.0_realistic_hardened",
        "random_seed": seed,
        "total_records": total_samples,
        "train_records": len(train_data),
        "validation_records": len(val_data),
        "test_records": len(test_data),
        "class_distribution": class_counts,
        "quality_distribution": quality_counts,
        "methodology_note": "Includes implicit invoices, procurement phrasing, ambiguous mixed-intent tasks, and OOD distractors."
    }

    with open(os.path.join(data_dir, "dataset_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Realistic Hardened Dataset (Seed={seed}) generated in '{data_dir}':")
    print(f"  - Total Samples: {total_samples}")
    print(f"  - Train: {len(train_data)} | Val: {len(val_data)} | Test: {len(test_data)}")
    print(f"  - Class Distribution: {class_counts}")
    print(f"  - Quality Distribution: {quality_counts}")

if __name__ == "__main__":
    main()
