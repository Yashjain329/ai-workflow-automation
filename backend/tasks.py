"""
Celery tasks for the AI-Based Intelligent Workflow Automation Platform.
This module contains long-running operations that are offloaded to background workers.
"""
from celery import Celery
from backend.config import settings

# Initialize Celery
celery_app = Celery(
    "workflow_automation",
    broker=settings.BROKER_URL,
    backend=settings.RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer=settings.TASK_SERIALIZER,
    result_serializer=settings.RESULT_SERIALIZER,
    accept_content=settings.ACCEPT_CONTENT,
    timezone=settings.TIMEZONE,
    enable_utc=settings.ENABLE_UTC,
)

# Import the modules that contain the long-running operations
# We'll import them inside the tasks to avoid circular imports


@celery_app.task(bind=True)
def process_workflow_job(self, job_id: int):
    """
    Process a workflow job in the background.
    This replaces the synchronous WorkflowEngine.process_job method.
    """
    from backend.workflow_engine import WorkflowEngine
    from backend.database import SessionLocal
    
    db = SessionLocal()
    try:
        engine = WorkflowEngine(db)
        result = engine.process_job(job_id)
        return result
    finally:
        db.close()


@celery_app.task(bind=True)
def execute_database_connector_action(self, connector_id: int, action_params: dict):
    """
    Execute a database connector action in the background.
    """
    from backend.connectors.database_connector import DatabaseConnector
    from backend.database import SessionLocal
    
    db = SessionLocal()
    try:
        connector = DatabaseConnector(db, connector_id)
        result = connector.execute_action(action_params)
        return result
    finally:
        db.close()


@celery_app.task(bind=True)
def send_notification(self, notification_id: int, message: str, recipient: str):
    """
    Send a notification in the background.
    """
    from backend.connectors.notification_connector import NotificationConnector
    from backend.database import SessionLocal
    
    db = SessionLocal()
    try:
        connector = NotificationConnector(db)
        result = connector.send_notification(notification_id, message, recipient)
        return result
    finally:
        db.close()


# Add more tasks as needed for other long-running operations