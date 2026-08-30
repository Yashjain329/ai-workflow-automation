# System Architecture & State Machine Specification (Week 3)

## Architectural Diagram

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
  │   - Field Extraction & Entity Parser                        │
  │   - Confidence Score Assignment ($0.00 - 1.00$)            │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                   HYBRID POLICY ENGINE                      │
  │   - Evaluate AI predictions against Business Policy Rules   │
  │   - Confidence Threshold Gate:                              │
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

## State Machine Lifecycle
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
