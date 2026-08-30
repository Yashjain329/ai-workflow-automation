# Changelog

All notable changes to the **AI-Based Intelligent Workflow Automation Platform** will be documented in this file.

---

## [1.0.0-semester1] - 2026-08-30

### 🚀 Added
- **Core Architecture**: Modular 8-stage state machine (`RECEIVED` $\rightarrow$ `VALIDATING` $\rightarrow$ `CLASSIFIED` $\rightarrow$ `EXTRACTED` $\rightarrow$ `DECIDING` $\rightarrow$ `APPROVAL_PENDING` $\rightarrow$ `EXECUTING` $\rightarrow$ `COMPLETED`/`FAILED` $\rightarrow$ `AUDITED`).
- **Machine Learning Engine**: Trained `scikit-learn` `TfidfVectorizer` + `LogisticRegression` classification pipeline with model artifact persistence (`tfidf_logreg_model.pkl`).
- **Baseline Comparators**: Rule-Only keyword baseline (`RuleOnlyClassifier`) and AI-Only experimental group.
- **Structured Entity Extraction**: Regex and pattern-based entity extraction for amounts, vendors, invoice numbers, departments, and urgency with field-level confidence scores.
- **Hybrid Decisioning**: Safety-gated policy engine integrating AI prediction confidence with deterministic business rules.
- **Connectors**: Database ledger updater with SHA-256 idempotency request hashing and notification simulator with retry logic.
- **Human Approval Queue**: REST endpoints and state handlers for manual escalation review (`APPROVED` / `REJECTED`).
- **Web Operations Dashboard**: Interactive Tailwind/JS UI with live polling, metrics overview cards, active job table, and decision inspection modals.
- **Research Benchmark Harness**: 5-layer evaluator outputting `classification_metrics.csv`, `confusion_matrix.csv`, and `experiment_manifest.json`.
- **Three-Way Comparison Harness**: Automated experimental suite comparing Rule-Only vs. AI-Only vs. Hybrid AI + Policy approaches (`compare_baselines.py`).
- **Robustness Testing Suite**: Perturbation generator testing clean vs. 10%, 20%, 30% noise, incomplete, and ambiguous inputs (`test_robustness.py`).
- **Automated Test Suite**: 15+ automated pytest modules verifying policy rules, state transitions, API endpoints, failure scenarios, and idempotency.
- **Cloud & Deployment**: `netlify.toml` continuous deployment integration on GitHub, public deployment at `https://aiworkflowautomation.netlify.app/`.
