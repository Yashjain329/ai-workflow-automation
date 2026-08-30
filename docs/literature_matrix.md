# Literature Review Matrix (Week 2)

| Paper / Theme | Problem Studied | Methodology | Key Findings / Trade-offs | Takeaway for Current System |
| :--- | :--- | :--- | :--- | :--- |
| **Workflow Automation / RPA** | Rule brittleness under semi-structured inputs | Rule-based decision tables | High accuracy on structured data, but 0% resilience on schema changes. | Establish deterministic baseline rules for control comparison. |
| **Intelligent Process Automation (IPA)** | Task classification & routing in enterprise systems | Naive Bayes + SVM classifiers | ML routing reduces manual handling by up to 60%. | Use ML classifiers to dynamically determine task routes. |
| **Document Intelligence** | Extracting entities from invoices & receipts | Regex + NER sequence labeling | High precision on standard keys; struggles on ambiguous labels. | Combine template regex with fallback confidence scoring. |
| **Human-in-the-loop AI** | Uncertainty estimation in automated decisions | Confidence thresholding & escalation queues | Thresholding at 0.85-0.90 optimizes precision while capping review load. | Implement dual-threshold escalation (Auto, Review, Reject). |
| **Workflow Orchestration** | State tracking, idempotency, and retries | Stateful state machine & audit log | Distributed state requires atomic logs to prevent duplicate executions. | Use explicit state transition table and audit log tables. |
| **Evaluation Metrics in IPA** | Measuring operational vs ML quality | F1-Score, Automation Rate, Rework Rate, Latency | Accuracy alone is insufficient; automation rate + failure rate define utility. | Evaluate system using Automation Rate, Latency, and Error Rate. |
