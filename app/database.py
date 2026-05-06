import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------------------
# Database URL
# ---------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./kitchen.db"
)

# ---------------------------
# Engine Configuration
# ---------------------------

is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        future=True
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
# Dependency
# ---------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()