# AI-Based Intelligent Workflow Automation Platform

> **Dissertation & Implementation Project (v1.0)**
> *Design, Development, and Experimental Evaluation of an AI-Driven Intelligent Workflow Automation System for Adaptive Task Processing*

---

## 📌 Project Overview

This platform provides an end-to-end intelligent workflow automation framework combining **deterministic policy enforcement** with **machine-learning task understanding and routing**. 

### Key Capabilities:
- **Multi-Format Ingestion**: Supports JSON, Form payloads, raw text, and PDF document parsing.
- **Task Classification**: Baseline rule mapping + ML classifier (TF-IDF + Logistic Regression) for automatic document/request categorization.
- **Structured Field Extraction**: Extracts key operational entities (vendor, invoice amount, date, urgency, category).
- **Hybrid Decision Engine**: Evaluates ML prediction confidence against deterministic business policies:
  - $\text{Confidence} \ge 0.90$ $\rightarrow$ **Auto-Execute** workflow.
  - $0.70 \le \text{Confidence} < 0.90$ $\rightarrow$ **Escalate to Human Approval Queue**.
  - $\text{Confidence} < 0.70$ or Policy Violation $\rightarrow$ **Reject / Manual Intervention**.
- **Stateful Workflow Engine**: Full state machine (`RECEIVED` $\rightarrow$ `VALIDATING` $\rightarrow$ `CLASSIFIED` $\rightarrow$ `EXTRACTED` $\rightarrow$ `DECIDING` $\rightarrow$ `APPROVAL_PENDING` $\rightarrow$ `EXECUTING` $\rightarrow$ `COMPLETED` / `FAILED` $\rightarrow$ `AUDITED`).
- **Interactive Operations Dashboard**: Live web UI monitoring active jobs, throughput, latency, failure taxonomy, and human review actions.
- **Reproducible Evaluation & Testing**: Complete benchmark suite and `pytest` suite covering 10 failure injection scenarios.

---

## 📁 Repository Structure

```text
ai-workflow-automation/
├── backend/
│   ├── api/             # FastAPI REST Endpoints (jobs, approvals, metrics)
│   ├── connectors/      # DB Update & Notification connectors
│   ├── models/          # DB schemas, ML classifier, NER field extractor
│   ├── policy/          # Business rules & hybrid decision engine
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Ingestion & PDF parser service
│   ├── workflow/        # State machine & workflow orchestrator
│   ├── config.py        # Environment configuration
│   ├── database.py      # SQLAlchemy setup
│   └── main.py          # FastAPI application entrypoint
├── docs/                # Research framing, literature matrix, requirements, demo script
├── frontend/            # Operations Dashboard & Human Approval UI (HTML/JS/Tailwind)
├── data/                # Synthetic training, validation, and test datasets
├── experiments/         # Benchmark runners & ML model evaluation scripts
├── scripts/             # Dataset generation tools
├── tests/               # Automated pytest suite
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

### 3. Run Automated Tests
```bash
pytest tests/ -v
```

### 4. Run Model Evaluation & Benchmark Script
```bash
python experiments/run_benchmark.py
```

### 5. Launch Application & Operations Dashboard
```bash
uvicorn backend.main:app --reload --port 8000
```
Open your browser and navigate to:
- **Operations Dashboard & Approval Queue UI**: `http://localhost:8000/`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`
