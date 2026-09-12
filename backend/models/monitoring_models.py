import datetime
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base

class ModelPerformanceMetrics(Base):
    __tablename__ = "model_performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Model identification
    model_version = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # e.g., "TF-IDF-LogReg", "RuleOnly"
    
    # Performance metrics (when ground truth is available)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    # Confidence distribution metrics
    avg_confidence = Column(Float, nullable=True)
    confidence_std = Column(Float, nullable=True)
    high_confidence_count = Column(Integer, nullable=True)  # >= 0.9
    medium_confidence_count = Column(Integer, nullable=True)  # 0.7-0.9
    low_confidence_count = Column(Integer, nullable=True)   # < 0.7
    
    # Prediction counts by category
    invoice_predictions = Column(Integer, nullable=True)
    service_request_predictions = Column(Integer, nullable=True)
    unknown_predictions = Column(Integer, nullable=True)
    
    # Sample size
    sample_size = Column(Integer, nullable=True)
    
    # Computation metadata
    computation_time_ms = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<ModelPerformanceMetrics(id={self.id}, model_version='{self.model_version}', timestamp='{self.timestamp}', accuracy={self.accuracy})>"

class DataDriftMetrics(Base):
    __tablename__ = "data_drift_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Drift detection results
    drift_detected = Column(Boolean, nullable=False)
    drift_score = Column(Float, nullable=True)  # Overall drift score (0-1)
    
    # Feature-level drift (stored as JSON for flexibility)
    feature_drift_scores = Column(JSON, nullable=True)  # e.g., {"text_length": 0.2, "keyword_density": 0.5}
    
    # Statistical test results
    ks_test_p_value = Column(Float, nullable=True)  # Kolmogorov-Smirnov test p-value
    chi_square_p_value = Column(Float, nullable=True)  # Chi-square test for categorical features
    
    # Reference and current sample info
    reference_period_start = Column(DateTime, nullable=True)
    reference_period_end = Column(DateTime, nullable=True)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    
    sample_size_reference = Column(Integer, nullable=True)
    sample_size_current = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<DataDriftMetrics(id={self.id}, timestamp='{self.timestamp}', drift_detected={self.drift_detected}, drift_score={self.drift_score})>"

class SystemPerformanceMetrics(Base):
    __tablename__ = "system_performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Workflow throughput
    jobs_processed_per_minute = Column(Float, nullable=True)
    jobs_completed_per_minute = Column(Float, nullable=True)
    jobs_failed_per_minute = Column(Float, nullable=True)
    jobs_pending_approval = Column(Integer, nullable=True)
    
    # Latency metrics (in milliseconds)
    avg_latency_total = Column(Float, nullable=True)
    avg_latency_ingestion = Column(Float, nullable=True)
    avg_latency_classification = Column(Float, nullable=True)
    avg_latency_extraction = Column(Float, nullable=True)
    avg_latency_decision = Column(Float, nullable=True)
    avg_latency_execution = Column(Float, nullable=True)
    
    # Success rates
    automation_rate = Column(Float, nullable=True)  # Percentage of jobs auto-approved
    escalation_rate = Column(Float, nullable=True)  # Percentage escalated to human
    failure_rate = Column(Float, nullable=True)     # Percentage failed
    
    # Error metrics
    error_count_total = Column(Integer, nullable=True)
    error_count_database = Column(Integer, nullable=True)
    error_count_notification = Column(Integer, nullable=True)
    error_count_validation = Column(Integer, nullable=True)
    
    # Retry metrics
    avg_retry_count = Column(Float, nullable=True)
    max_retry_count = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<SystemPerformanceMetrics(id={self.id}, timestamp='{self.timestamp}', jobs_processed_per_minute={self.jobs_processed_per_minute}, automation_rate={self.automation_rate})>"