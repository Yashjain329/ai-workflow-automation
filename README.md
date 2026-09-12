# AI-Based Intelligent Workflow Automation Platform

> **Dissertation & Research Implementation Project**  
> *Design, Development, and Experimental Evaluation of an AI-Driven Intelligent Workflow Automation System for Adaptive Task Processing*

[![Release](https://img.shields.io/badge/Release-v2.0--enhanced-green.svg)](https://github.com/Yashjain329/ai-workflow-automation)
[![Tests](https://img.shields.io/badge/Tests-18%20Passed-brightgreen.svg)](tests/)
[![Deployment](https://img.shields.io/badge/Live%20Demo-Netlify-00ad9f.svg)](https://aiworkflowautomation.netlify.app/)
[![Enhancements](https://img.shields.io/badge/Enhancements-4--Phase-blue.svg)](docs/specs/ENHANCEMENT_ROADMAP.md)

---

## 📌 Project Overview

This platform provides an end-to-end intelligent workflow automation framework combining **deterministic policy enforcement** with **machine-learning task understanding and routing**. 

### Key Capabilities:
- **Multi-Format Ingestion**: Supports JSON, Form payloads, raw text, and PDF document parsing.
- **Task Classification**: Trained `scikit-learn` Pipeline (`TfidfVectorizer` + `LogisticRegression`) with persisted model artifact (`tfidf_logreg_model.pkl`) + rule-based baseline comparator.
- **Structured Field Extraction**: Extracts key operational entities (vendor, invoice amount, date, urgency, category) with field-level confidence scores.
- **Hybrid Decision Engine**: Evaluates ML prediction confidence against deterministic business policies:
  - $\\text{Confidence} \\ge 0.90$ & Low Risk $\\rightarrow$ **Auto-Execute** workflow.
  - $0.70 \\le \\text{Confidence} < 0.90$ or Policy Flag $\\rightarrow$ **Escalate to Human Approval Queue**.
  - $\\text{Confidence} < 0.70$ or High Risk $\\rightarrow$ **Reject / Manual Intervention**.
- **Stateful Workflow Engine**: Full 8-state machine (`RECEIVED` $\\rightarrow$ `VALIDATING` $\\rightarrow$ `CLASSIFIED` $\\rightarrow$ `EXTRACTED` $\\rightarrow$ `DECIDING` $\\rightarrow$ `APPROVAL_PENDING` $\\rightarrow$ `EXECUTING` $\\rightarrow$ `COMPLETED` / `FAILED` $\\rightarrow$ `AUDITED`).
- **Interactive Operations Dashboard**: Live web UI monitoring active jobs, throughput, latency, failure taxonomy, and human review actions. Live on Netlify: [https://aiworkflowautomation.netlify.app/](https://aiworkflowautomation.netlify.app/).
- **Three-Way Research Baseline**: Empirical evaluation comparing **Rule-Only** vs. **AI-Only** vs. **Proposed Hybrid AI + Policy**.
- **Controlled Robustness Suite**: Evaluates degradation under clean vs. 10%, 20%, 30% noise and incomplete inputs.
- **Enhanced Monitoring & Observability**: Model drift detection, performance metrics, and real-time analytics.
- **Scalable Architecture**: Asynchronous processing with Celery/Redis for high-load scenarios.
- **Modern Frontend Experience**: React/Vite-based dashboard with real-time WebSocket updates.

---