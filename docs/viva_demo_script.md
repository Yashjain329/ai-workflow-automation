# Viva Demonstration Script (Week 16 - 7-10 Min Presentation)

## Demo Agenda & Sequence

1. **Problem Statement & Research Goals (45s)**
   - *Speaker*: Introduce the limitation of rule-based RPA under unstructured inputs and explain the proposed hybrid AI + deterministic policy system.

2. **Architecture & Hybrid Policy Engine Overview (1m 30s)**
   - *Visual*: Show `docs/architecture.md` diagram and explain the separation of concerns (AI predicts, policy constrains, workflow engine executes).

3. **Step 1: Automatic Execution Flow - Clean High-Confidence Invoice (1m 30s)**
   - *Action*: Post a standard invoice payload to `/api/jobs`.
   - *Expected Result*: Category identified as `invoice`, vendor/amount extracted, confidence $= 0.96$, auto-approved, DB updated, notification sent, state = `COMPLETED`.

4. **Step 2: Human Escalation Flow - Ambiguous / Medium-Confidence Task (1m 30s)**
   - *Action*: Post an ambiguous purchase request with confidence $= 0.78$ or amount $> \$10,000$.
   - *Expected Result*: Policy triggers escalation. Job enters `APPROVAL_PENDING`.
   - *Action*: Open Dashboard UI (`http://localhost:8000`), navigate to Approval Queue, inspect decision trace, and click **Approve**.
   - *Expected Result*: State transitions to `COMPLETED` and action executes.

5. **Step 3: Fault Tolerance & Failure Injection Handling (1m)**
   - *Action*: Post a malformed document or simulate a connector timeout.
   - *Expected Result*: Retry logic triggers up to 3 attempts, failure logged in `ActionLog`, state transitions to `FAILED` with non-silent error taxonomy.

6. **Step 4: Audit Trail Inspection (1m)**
   - *Action*: Click on a completed run in the Dashboard UI.
   - *Expected Result*: Show full audit trail including raw payload, model outputs, confidence scores, policy rules triggered, and action responses.

7. **Step 5: Experimental Evaluation & Benchmark Findings (1m 30s)**
   - *Visual*: Show benchmark output (`python experiments/run_benchmark.py`).
   - *Key Findings*: Contrast rule-based baseline vs hybrid AI approach across Accuracy, Automation Rate, Rework Rate, and Latency.

8. **Conclusion & Future Directions (45s)**
   - *Speaker*: Summarize key takeaway and outline Semester 2 ablation study plans.
