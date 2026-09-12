from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.monitoring import MonitoringService, collect_metrics
from backend.models.monitoring_models import (
    ModelPerformanceMetrics, DataDriftMetrics, SystemPerformanceMetrics
)
from backend.config import settings

router = APIRouter(
    prefix="/monitoring",
    tags=["monitoring"],
    responses={404: {"description": "Not found"}},
)

@router.post("/collect", status_code=202)
def trigger_metrics_collection(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Trigger a monitoring metrics collection cycle in the background.
    """
    if not settings.METRICS_COLLECTION_ENABLED:
        raise HTTPException(status_code=400, detail="Metrics collection is disabled")
    
    background_tasks.add_task(collect_metrics)
    return {"message": "Metrics collection triggered in background"}

@router.get("/model-performance")
def get_model_performance_metrics(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Retrieve the latest model performance metrics.
    """
    metrics = db.query(ModelPerformanceMetrics).order_by(
        ModelPerformanceMetrics.timestamp.desc()
    ).limit(limit).all()
    return metrics

@router.get("/system-performance")
def get_system_performance_metrics(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Retrieve the latest system performance metrics.
    """
    metrics = db.query(SystemPerformanceMetrics).order_by(
        SystemPerformanceMetrics.timestamp.desc()
    ).limit(limit).all()
    return metrics

@router.get("/data-drift")
def get_data_drift_metrics(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Retrieve the latest data drift metrics.
    """
    metrics = db.query(DataDriftMetrics).order_by(
        DataDriftMetrics.timestamp.desc()
    ).limit(limit).all()
    return metrics

@router.get("/metrics")
def get_all_latest_metrics(db: Session = Depends(get_db)):
    """
    Get the latest of each type of metric for monitoring dashboards.
    """
    import datetime
    latest_model_perf = db.query(ModelPerformanceMetrics).order_by(
        ModelPerformanceMetrics.timestamp.desc()
    ).first()
    
    latest_system_perf = db.query(SystemPerformanceMetrics).order_by(
        SystemPerformanceMetrics.timestamp.desc()
    ).first()
    
    latest_data_drift = db.query(DataDriftMetrics).order_by(
        DataDriftMetrics.timestamp.desc()
    ).first()
    
    return {
        "model_performance": [m.__dict__ for m in [latest_model_perf]] if latest_model_perf else [],
        "system_performance": [m.__dict__ for m in [latest_system_perf]] if latest_system_perf else [],
        "data_drift": [m.__dict__ for m in [latest_data_drift]] if latest_data_drift else [],
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }