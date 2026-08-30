# Dissertation Research Framing & Scope Lock (Week 1)

## 1. Working Title
**Design and Development of an AI-Driven Intelligent Workflow Automation System for Adaptive Task Processing**

---

## 2. Problem Statement
Many organizational workflows rely on manual intervention or brittle rule-based automation when processing unstructured or variable inputs such as invoices, service requests, and emails. Traditional Robotic Process Automation (RPA) performs well under fixed inputs but requires excessive manual rule updates as input formats shift. Conversely, purely autonomous AI models lack execution guarantees and explainability required for high-risk operations. 

This research investigates a **hybrid architecture** that uses AI for task understanding and adaptive routing while deterministic policy engines enforce strict operational boundaries and human-in-the-loop escalation.

---

## 3. Research Questions (RQs)
1. **RQ1**: How accurately can the proposed hybrid system classify incoming tasks and identify the correct workflow compared to a rule-only baseline?
2. **RQ2**: Does AI-assisted routing reduce processing time and manual intervention compared with rule-only automation?
3. **RQ3**: Which model strategy provides the optimal trade-off between classification accuracy, processing latency, and resource utilization?
4. **RQ4**: How robust is the system when inputs are incomplete, noisy, or outside the training distribution?
5. **RQ5**: How effectively do confidence thresholds isolate high-risk tasks for human approval without creating excessive review bottlenecks?

---

## 4. Hypotheses
- **H1**: Hybrid AI + rule automation achieves significantly higher routing accuracy than rule-only baselines when processing unstructured inputs.
- **H2**: Confidence-gated AI assistance reduces total human intervention rate while maintaining an overall error rate $< 2\%$.
- **H3**: A lightweight classifier (TF-IDF + Logistic Regression) offers a superior latency-to-accuracy ratio for task routing compared to complex unstructured rules.
- **H4**: Confidence-based escalation prevents invalid auto-executions even when input quality drops by up to $30\%$.

---

## 5. Scope & Non-Goals
### Included Scope (Semester 1):
- End-to-end working prototype for Invoice Processing (primary workflow) and Support Ticket Routing (secondary workflow).
- Document ingestion (PDF, JSON, Form), text extraction, ML task classification, field extraction, policy checks, stateful workflow execution, human approval queue, audit logging, and operations web dashboard.

### Explicit Non-Goals:
- Unrestricted autonomous external system actions without policy constraints.
- Dependency on live external corporate databases or production secrets.
- Full thesis writing (deferred to Semester 2).
