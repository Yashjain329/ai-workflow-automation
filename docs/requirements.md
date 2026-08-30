# Functional & Non-Functional Requirements (Week 2)

## Functional Requirements (FR)
- **FR-01**: System shall accept a workflow job from an API, form payload, or PDF document source.
- **FR-02**: System shall normalize and validate the incoming payload before AI processing.
- **FR-03**: System shall classify the job into one of the configured workflow categories (`invoice`, `service_request`, `unknown`).
- **FR-04**: System shall extract required structured fields (amount, vendor, date, urgency, requester) and output confidence values ($0.0 - 1.0$).
- **FR-05**: System shall evaluate deterministic business policy rules after AI prediction.
- **FR-06**: System shall route the task to a workflow execution path based on the combined hybrid decision.
- **FR-07**: System shall support a human approval queue when prediction confidence is medium ($0.70 - 0.89$) or policy requires human signoff.
- **FR-08**: System shall execute actions such as database record updates, simulated email/slack notifications, or API updates.
- **FR-09**: System shall maintain an audit trail of inputs, AI outputs, policy decisions, actions, and human reviews.
- **FR-10**: System shall expose operational metrics such as total jobs, throughput, average latency, automation rate, escalation rate, and failure taxonomy.
- **FR-11**: System shall retry transient failures up to 3 times and record permanent failures without dropping jobs.
- **FR-12**: System shall make workflow policy definitions configurable without changing core engine code.

## Non-Functional Requirements (NFR)
- **Traceability**: Every automated decision must be explainable from recorded inputs, confidence scores, policy rules, and action logs.
- **Reliability**: Failed actions must be visible, retriable, and idempotent.
- **Security**: Use synthetic credentials; sanitize log outputs.
- **Performance**: Target latency under 500ms for synchronous task routing.
- **Maintainability**: Modular separation of backend, ML models, policy rules, connectors, and frontend dashboard.
- **Reproducibility**: Reproducible synthetic dataset generation script and automated benchmark scripts.
