# System Architecture & State Machine Specification (Semester 1 Master Spec)

## 1. Architectural Overview & Component Boundaries

```text
  ┌─────────────────────────────────────────────────────────────┐
  │                    INPUT SOURCES                            │
  │     (REST API Payload / PDF Document Upload / Form)         │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                    INGESTION SERVICE                        │
  │     (Text Extraction / PDF Metadata / Field Normalizer)     │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                     AI / ML LAYER                           │
  │   - Task Classification (TF-IDF + Logistic Regression)      │
  │   - Field Extraction & Entity Parser with Field Confidence  │
  │   - Calibrated Confidence Score ($0.00 - 1.00$)             │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                   HYBRID POLICY ENGINE                      │
  │   - Evaluate AI predictions against Business Policy Rules   │
  │   - Confidence Threshold Safety Gate:                       │
  │       * ≥ 0.90 & Policy Pass  ──► Auto-Approve              │
  │       * 0.70-0.89 or Policy Flag──► Escalate to Human Queue │
  │       * < 0.70 or Policy Fail ──► Reject / Manual Review   │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                WORKFLOW STATE MACHINE                       │
  │   State Transitions & Execution Orchestrator                │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
            ┌────────────────────┴────────────────────┐
            ▼                                         ▼
  ┌───────────────────┐                     ┌───────────────────┐
  │ ACTION CONNECTORS │                     │ HUMAN APPROVAL UI │
  │ DB Update / Mail  │                     │ Decision Review   │
  └─────────┬─────────┘                     └─────────┬─────────┘
            │                                         │
            └────────────────────┬────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                   AUDIT & OBSERVABILITY                     │
  │   Workflow Logs / State History / Analytics Dashboard       │
  └─────────────────────────────────────────────────────────────┘
```

---

## 2. State Machine Lifecycle
```text
RECEIVED ──► VALIDATING ──► CLASSIFIED ──► EXTRACTED ──► DECIDING 
                                                             │
                  ┌──────────────────────────────────────────┴──────────────────────────┐
                  ▼                                                                     ▼
           [Auto-Approved]                                                      [Escalated / Review]
                  │                                                                     │
                  ▼                                                                     ▼
              EXECUTING ◄───────────────── APPROVAL_APPROVED ───────────── APPROVAL_PENDING
                  │                                                                     │
                  ├──────────────────────────────────────────────┐                      │ (If Rejected)
                  ▼                                              ▼                      ▼
              COMPLETED                                       FAILED ◄──────────── APPROVAL_REJECTED
                  │                                              │
                  └──────────────────────┬───────────────────────┘
                                         ▼
                                      AUDITED
```

---

## 3. Sequence Diagrams

### Sequence 1: Successful Invoice Auto-Approval Workflow
```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant API as FastAPI Backend
    participant Ingest as Ingestion Service
    participant ML as ML Classifier
    participant Ext as Field Extractor
    participant Policy as Hybrid Policy Engine
    participant Engine as Workflow Engine
    participant DBConn as DB Connector
    participant MailConn as Notification Connector
    participant DB as SQLite / Postgres Audit

    Client->>API: POST /api/jobs (Clean Invoice Text)
    API->>Engine: process_job(job_id)
    Engine->>Ingest: process_payload() [State: VALIDATING]
    Ingest-->>Engine: normalized_text, metadata
    Engine->>ML: predict(text) [State: CLASSIFIED]
    ML-->>Engine: ("invoice", confidence=0.96)
    Engine->>Ext: extract_fields(text, "invoice") [State: EXTRACTED]
    Ext-->>Engine: {amount: 2400.0, vendor: "Acme Corp"}
    Engine->>Policy: evaluate(confidence=0.96, amount=2400.0) [State: DECIDING]
    Policy-->>Engine: route="auto_approve", risk="low"
    Engine->>DBConn: execute_action(job_id, fields) [State: EXECUTING]
    DBConn-->>Engine: SUCCESS (Hash: sha256_id)
    Engine->>MailConn: send_notification(job_id)
    MailConn-->>Engine: SUCCESS
    Engine->>DB: transition to COMPLETED -> AUDITED
    Engine-->>API: WorkflowJob(status="AUDITED", auto=True)
    API-->>Client: 200 OK
```

### Sequence 2: Human Escalation & Approval Workflow
```mermaid
sequenceDiagram
    autonumber
    actor Client
    actor Reviewer as Human Operator
    participant API as FastAPI Backend
    participant Engine as Workflow Engine
    participant Policy as Hybrid Policy Engine
    participant Queue as Approval Queue DB

    Client->>API: POST /api/jobs (High Amount / Ambiguous Invoice)
    API->>Engine: process_job(job_id)
    Engine->>Policy: evaluate(confidence=0.82 or amount=$12,500)
    Policy-->>Engine: route="human_approval", risk="medium"
    Engine->>Queue: Create ApprovalTask [State: APPROVAL_PENDING]
    Engine-->>API: WorkflowJob(status="APPROVAL_PENDING", human_intervention=True)
    
    Note over Reviewer,API: Operator inspects Dashboard UI
    Reviewer->>API: GET /api/approvals
    API-->>Reviewer: List of Pending ApprovalTasks
    Reviewer->>API: POST /api/approvals/{task_id}/decision {"decision": "APPROVED"}
    API->>Engine: approve_human_task(task_id, "APPROVED")
    Engine->>Engine: [State: APPROVAL_APPROVED -> EXECUTING]
    Engine->>Engine: Execute Actions -> COMPLETED -> AUDITED
    Engine-->>API: 200 OK (Workflow Completed)
```

### Sequence 3: Failure & Retry Handling Workflow
```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Engine as Workflow Engine
    participant Connector as External Action Connector
    participant Audit as ActionLog DB

    Client->>Engine: Execute Connector Action (Transient DB/Network Timeout)
    loop Retry up to MAX_RETRIES (3)
        Engine->>Connector: execute_action() [Attempt i]
        Connector-->>Engine: Connection Timeout (Failure)
        Engine->>Audit: log_action(status="RETRYING", retry_count=i)
    end
    alt Max Retries Exhausted
        Engine->>Audit: log_action(status="FAILURE", error_code="ERR_MAX_RETRIES")
        Engine->>Engine: transition to FAILED -> AUDITED
    end
```

---

## 4. Formal Hybrid Decision Matrix

| AI Confidence Range | Policy Risk Level | Mandatory Fields Status | Assigned Route | Action Executed |
| :---: | :---: | :---: | :---: | :--- |
| $\ge 0.90$ | Low ($\text{Amount} \le \$5,000$, Known Vendor) | Complete | `auto_approve` | Automated DB Ledger Update + Notification |
| $\ge 0.90$ | Medium/High ($\text{Amount} > \$5,000$) | Complete | `human_approval` | Route to Approval Queue (Safety Override) |
| $0.70 \le \text{Conf} < 0.90$ | Any Risk Level | Complete | `human_approval` | Route to Approval Queue (Uncertainty Escalation) |
| $< 0.70$ | Any Risk Level | Any | `reject` | Reject / Manual Re-intake Required |
| Any Confidence | High (`MISSING_VENDOR`, Zero Amount) | Incomplete | `human_approval` | Route to Approval Queue (Missing Critical Data) |
