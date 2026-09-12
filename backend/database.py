from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import settings

# SQLite configuration requires connect_args check
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base will be imported from the models or defined here? We'll keep it here but note that the models will import it.
# To avoid circular import, we will define Base here and have the models import it from this module.
# But then the models importing this module is okay because we are not importing the models in this module.
from sqlalchemy.orm import declarative_base
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()