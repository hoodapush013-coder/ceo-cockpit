"""Database connection and session management for CEO Cockpit.

This module is the ONLY place that knows how to connect to the database.
Everything else (models, tools, API) imports from here.

Key concepts:
    engine       — the connection pool to Postgres
    SessionLocal — a factory that creates new sessions (shopping carts)
    get_session  — a helper that tools use to get a session
    init_db      — creates all tables from our models
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Import Base so we can call create_all() to build tables
from models import Base

# Load .env so DATABASE_URL can live alongside GITHUB_TOKEN
load_dotenv()

# ---------------------------------------------------------------------------
# Database URL
# ---------------------------------------------------------------------------
# Format: postgresql+psycopg2://user:password@host:port/dbname
#
# We read from environment so the same code works everywhere:
#   - Local dev:   DATABASE_URL=postgresql+psycopg2://cockpit:cockpit_dev@localhost:5432/cockpit
#   - Production:  DATABASE_URL=postgresql+psycopg2://prod_user:secret@db.example.com:5432/prod_db
#   - Testing:     DATABASE_URL=postgresql+psycopg2://test:test@localhost:5432/test_db

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://cockpit:cockpit_dev@localhost:5432/cockpit",
)

# ---------------------------------------------------------------------------
# Engine — the connection pool
# ---------------------------------------------------------------------------
# echo=True prints every SQL statement SQLAlchemy generates.
# GREAT for learning. Turn it off in production (echo=False).

engine = create_engine(
    DATABASE_URL,
    echo=True,           # prints SQL to console — remove in production
    pool_size=5,         # keep 5 connections warm
    max_overflow=10,     # allow up to 10 more under load (then wait)
    pool_pre_ping=True,  # check if connection is alive before using it
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
# sessionmaker returns a CLASS, not an instance.
# Each time you call SessionLocal(), you get a NEW session (shopping cart).
#
# autocommit=False  → you must explicitly commit (safer, no accidental saves)
# autoflush=False   → don't auto-sync Python objects to DB until you say so
#                     (gives you full control over when SQL is sent)

SessionLocal = sessionmaker(
    bind=engine,         # "use this engine's connection pool"
    autocommit=False,
    autoflush=False,
)


# ---------------------------------------------------------------------------
# Helper: get a session (what tools will use)
# ---------------------------------------------------------------------------

def get_session():
    """Create and return a new database session.

    Usage in tools:
        session = get_session()
        try:
            # do queries...
            session.commit()
        finally:
            session.close()

    Or better, with a context manager:
        with SessionLocal() as session:
            # do queries...
            session.commit()
    """
    return SessionLocal()


# ---------------------------------------------------------------------------
# Helper: create all tables
# ---------------------------------------------------------------------------

def init_db():
    """Create all tables defined in models.py if they don't exist.

    This replaces your old init_ledger_db() function.
    Instead of raw CREATE TABLE SQL strings, we let SQLAlchemy
    generate the DDL from our Python model classes.

    Safe to call multiple times — CREATE TABLE IF NOT EXISTS.
    """
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database tables created/verified at: {DATABASE_URL}")