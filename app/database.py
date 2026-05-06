import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------------------
# Database URL
# ---------------------------
# Priority:
# 1. Environment variable (for production)
# 2. Local SQLite fallback

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./kitchen.db"
)

# ---------------------------
# Engine Configuration
# ---------------------------

# SQLite needs special handling
is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # required for SQLite + FastAPI
        echo=False
    )
else:
    # Production DB (PostgreSQL / MySQL etc.)
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,   # avoids stale connections
        future=True,
        echo=False
    )

# ---------------------------
# Session Factory
# ---------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ---------------------------
# Base Class
# ---------------------------

Base = declarative_base()

# ---------------------------
# Dependency (FastAPI)
# ---------------------------

def get_db():
    """
    Provides a DB session per request
    Ensures proper cleanup after request completes
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()