# Monitoring Enhancement Specification

## Objective
Add model drift detection and performance metrics to monitor the health and effectiveness of the deployed machine learning models and the overall system.

## Current State
- The system currently logs predictions, decisions, and workflow steps to the database.
- There is no active monitoring of model performance over time (e.g., accuracy, confidence distribution) or detection of data drift.

## Proposed Changes
1. **Model Performance Metrics**:
   - Periodically compute and log key metrics (e.g., accuracy, precision, recall, F1) for the ML classifier if ground truth becomes available (e.g., from human-approved jobs).
   - Track the distribution of prediction confidences and outcomes (auto-approved, human-approved, rejected) to detect shifts.

2. **Data Drift Detection**:
   - Monitor the input data (normalized text) for changes in distribution that might indicate drift.
   - Use simple statistical tests (e.g., Kolmogorov-Smirnov for feature distributions) or more advanced methods if needed.

3. **System Performance Metrics**:
   - Track latency at each stage of the workflow (ingestion, classification, extraction, decision, execution).
   - Monitor throughput (jobs per minute/hour) and error rates.

4. **Alerting and Visualization**:
   - Expose metrics via an endpoint (e.g., `/metrics`) in Prometheus format or similar.
   - Integrate with the existing frontend dashboard to show real-time metrics and alerts.
   - Set up alerts for significant drifts or performance degradation.

## Implementation Plan
1. **Extend the Database Schema**:
   - Add tables for storing model performance metrics and drift metrics over time.
   - Alternatively, use an external time-series database (e.g., Prometheus) for metrics.

2. **Modify the Workflow Engine**:
   - After a job reaches a state where ground truth is available (e.g., after human approval or auto-execution with verification), compute and store performance metrics.
   - For drift detection, periodically sample recent input data and compare to a baseline (e.g., training data distribution).

3. **Create a Monitoring Service**:
   - A background service that periodically computes metrics and checks for drift.
   - Alternatively, compute metrics on-demand or as part of the workflow for simplicity.

4. **Update the Frontend Dashboard**:
   - Add new panels to show model performance, drift metrics, and system health.

5. **Expose Metrics Endpoint**:
   - Add a `/metrics` endpoint to the FastAPI app that returns metrics in a standard format.

## Files to Modify
- `backend/database.py`: Add new tables for metrics.
- `backend/workflow/engine.py`: Hook to compute and store metrics after job completion.
- `backend/monitoring.py`: New file for monitoring logic.
- `backend/main.py`: Add the `/metrics` endpoint and start background monitoring service if applicable.
- `frontend/index.html` and `frontend/app.js`: Update dashboard to show new metrics.

## Validation
- Unit tests for the new monitoring logic.
- Integration tests to ensure metrics are collected and stored correctly.
- Verify that the dashboard displays the new metrics.
- Test that alerts are triggered appropriately in simulated drift scenarios.

## References
- [Prometheus Client for Python](https://github.com/prometheus/client_python)
- [WhyLabs or Evidently AI for drift detection](https://www.evidentlyai.com/)