# AI-Based Intelligent Workflow Automation Platform

> **Dissertation & Research Implementation Project**  
> *Design, Development, and Experimental Evaluation of an AI-Driven Intelligent Workflow Automation System for Adaptive Task Processing*

[![Release](https://img.shields.io/badge/Release-v1.0--semester1-blue.svg)](https://github.com/Yashjain329/ai-workflow-automation)
[![Tests](https://img.shields.io/badge/Tests-14%20Passed-brightgreen.svg)](tests/)
[![Deployment](https://img.shields.io/badge/Live%20Demo-Netlify-00ad9f.svg)](https://aiworkflowautomation.netlify.app/)

---

## 📌 Project Overview

This platform provides an end-to-end intelligent workflow automation framework combining **deterministic policy enforcement** with **machine-learning task understanding and routing**. 

### Key Capabilities:
- **Multi-Format Ingestion**: Supports JSON, Form payloads, raw text, and PDF document parsing.
- **Task Classification**: Trained `scikit-learn` Pipeline (`TfidfVectorizer` + `LogisticRegression`) with persisted model artifact (`tfidf_logreg_model.pkl`) + rule-based baseline comparator.
- **Structured Field Extraction**: Extracts key operational entities (vendor, invoice amount, date, urgency, category) with field-level confidence scores.
- **Hybrid Decision Engine**: Evaluates ML prediction confidence against deterministic business policies:
  - $\text{Confidence} \ge 0.90$ & Low Risk $\rightarrow$ **Auto-Execute** workflow.
  - $0.70 \le \text{Confidence} < 0.90$ or Policy Flag $\rightarrow$ **Escalate to Human Approval Queue**.
  - $\text{Confidence} < 0.70$ or High Risk $\rightarrow$ **Reject / Manual Intervention**.
- **Stateful Workflow Engine**: Full 8-state machine (`RECEIVED` $\rightarrow$ `VALIDATING` $\rightarrow$ `CLASSIFIED` $\rightarrow$ `EXTRACTED` $\rightarrow$ `DECIDING` $\rightarrow$ `APPROVAL_PENDING` $\rightarrow$ `EXECUTING` $\rightarrow$ `COMPLETED` / `FAILED` $\rightarrow$ `AUDITED`).
- **Interactive Operations Dashboard**: Live web UI monitoring active jobs, throughput, latency, failure taxonomy, and human review actions. Live on Netlify: [https://aiworkflowautomation.netlify.app/](https://aiworkflowautomation.netlify.app/).
- **Three-Way Research Baseline**: Empirical evaluation comparing **Rule-Only** vs. **AI-Only** vs. **Proposed Hybrid AI + Policy**.
- **Controlled Robustness Suite**: Evaluates degradation under clean vs. 10%, 20%, 30% noise and incomplete inputs.

---

## 📁 Repository Structure

```text
ai-workflow-automation/
├── backend/
│   ├── api/             # FastAPI REST Endpoints (jobs, approvals, metrics)
│   ├── connectors/      # DB Update & Notification connectors with SHA-256 idempotency
│   ├── models/          # DB schemas, ML classifier (TF-IDF + LogReg), entity extractor
│   ├── policy/          # Business rules & hybrid decision engine
│   ├── schemas/         # Pydantic v2 schemas
│   ├── services/        # Ingestion & PDF parser service
│   ├── workflow/        # State machine & workflow orchestrator
│   ├── config.py        # Environment configuration & thresholds
│   ├── database.py      # SQLAlchemy setup
│   └── main.py          # FastAPI application entrypoint
├── docs/                # Research framing, literature matrix, requirements, architecture, logs
├── frontend/            # Operations Dashboard & Human Approval UI (HTML/JS/Tailwind)
├── data/                # Master Plan benchmark dataset (train: 210, val: 45, test: 45)
├── experiments/         # 5-Layer benchmark, 3-way baseline comparator, robustness suite
├── scripts/             # Dataset generation and deterministic model training tools
├── tests/               # 14 automated pytest suites (Unit, API, State, Failure, Reliability)
├── .env.example         # Environment template
├── CHANGELOG.md         # Release history
├── netlify.toml         # Netlify CI/CD deployment configuration
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Benchmark Dataset
```bash
python scripts/generate_dataset.py
```

### 3. Train Machine Learning Model
```bash
python scripts/train_model.py
```

### 4. Run Automated Test Suite (14 Tests)
```bash
pytest tests/ -v
```

### 5. Run Experimental Research Harnesses
```bash
# 5-Layer Benchmark Evaluation (Exports CSV/JSON to experiments/results/)
python experiments/run_benchmark.py

# Three-Way Comparison: Rule-Only vs. AI-Only vs. Hybrid AI + Policy
python experiments/compare_baselines.py

# Controlled Robustness Study: 0%, 10%, 20%, 30% Noise Perturbations
python experiments/test_robustness.py
```

### 6. Launch Application & Operations Dashboard
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
Open your browser to:
- **Operations Dashboard & Approval Queue UI**: `http://localhost:8000/` (or live on Netlify: `https://aiworkflowautomation.netlify.app/`)
- **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`
