import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger("app.database")

Base = declarative_base()

def get_engine():
    try:
        # Try primary engine (e.g., MySQL)
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        # Test connection
        with engine.connect() as conn:
            pass
        logger.info(f"Connected to primary database: {settings.DATABASE_URL.split('@')[-1]}")
        return engine
    except Exception as e:
        if settings.USE_SQLITE_FALLBACK_IF_MYSQL_UNAVAILABLE:
            logger.warning(f"Could not connect to primary MySQL database ({e}). Falling back to SQLite: {settings.SQLITE_FALLBACK_URL}")
            fallback_engine = create_engine(
                settings.SQLITE_FALLBACK_URL,
                connect_args={"check_same_thread": False}
            )
            return fallback_engine
        else:
            raise e

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
