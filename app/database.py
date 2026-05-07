import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------------------
# Database URL (MANDATORY)
# ---------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("❌ DATABASE_URL not set. Render env variable check kar.")

# 🔥 FIX: Render sometimes gives 'postgres://' instead of correct driver
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg2://"
    )

# ---------------------------
# Engine Configuration
# ---------------------------

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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
