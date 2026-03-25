"""SQLAlchemy ORM models for CEO Cockpit.

This module defines the shape of every table in our database.
It is the SINGLE SOURCE OF TRUTH for our data schema.
If you want to know what a tracked_repo looks like, you look here.
Not in SQL strings, not in migration scripts — here.

Tables:
    TrackedRepo  — which repos an org is monitoring
    Snapshot     — time-series activity metrics per repo
    LedgerState  — current per-repo execution summary
    LedgerEvent  — historical conversation turns + verification receipts
"""

from sqlalchemy import (
    Column,         # defines a column in a table
    Integer,        # whole numbers (1, 2, 3)
    String,         # short text (repo names, org IDs)
    Text,           # long text (JSON blobs, summaries)
    Boolean,        # True/False
    DateTime,       # timestamps
    func,           # database functions like NOW()
)
from sqlalchemy.orm import DeclarativeBase


# ---------------------------------------------------------------------------
# Base class — every model inherits from this
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """Base class for all ORM models.

    Think of this as the 'school' that all our tables are enrolled in.
    When we call Base.metadata.create_all(engine), it creates SQL tables
    for every class that inherits from Base.
    """
    pass


# ---------------------------------------------------------------------------
# Table: tracked_repos
# ---------------------------------------------------------------------------

class TrackedRepo(Base):
    """Which repos an org dashboard should track.

    Composite primary key: (org_id, repo) — because the same repo
    could theoretically be tracked by multiple orgs.

    Maps to your current SQLite table:
        CREATE TABLE tracked_repos (
            org_id TEXT NOT NULL,
            repo TEXT NOT NULL,
            display_name TEXT,
            is_tracked INTEGER NOT NULL DEFAULT 1,
            added_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (org_id, repo)
        )
    """
    __tablename__ = "tracked_repos"

    # --- Primary key (composite: org_id + repo together must be unique) ---
    org_id       = Column(String, primary_key=True)
    repo         = Column(String, primary_key=True)

    # --- Data columns ---
    display_name = Column(String, nullable=True)           # can be NULL (optional)
    is_tracked   = Column(Boolean, nullable=False, default=True)  # Python fills in True
    added_at     = Column(DateTime(timezone=True), server_default=func.now())  # Postgres fills in timestamp

    def __repr__(self):
        """How this object looks when you print() it. Useful for debugging."""
        return f"<TrackedRepo org={self.org_id} repo={self.repo} tracked={self.is_tracked}>"


# ---------------------------------------------------------------------------
# Table: snapshots
# ---------------------------------------------------------------------------

class Snapshot(Base):
    """Time-stamped activity metrics for a single repo.

    Each row is one 'photograph' of a repo's health at a point in time.
    The metrics_json column holds the actual numbers (commits, PRs, etc.)
    as a JSON string. In V2, this becomes Postgres JSONB for direct querying.

    Maps to your current SQLite table:
        CREATE TABLE snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT NOT NULL,
            ts TEXT NOT NULL DEFAULT (datetime('now')),
            metrics_json TEXT NOT NULL
        )
    """
    __tablename__ = "snapshots"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    repo         = Column(String, nullable=False)
    ts           = Column(DateTime(timezone=True), server_default=func.now())
    metrics_json = Column(Text, nullable=False)  # JSON string; becomes JSONB in V2

    def __repr__(self):
        return f"<Snapshot id={self.id} repo={self.repo} ts={self.ts}>"


# ---------------------------------------------------------------------------
# Table: ledger_state
# ---------------------------------------------------------------------------

class LedgerState(Base):
    """Current execution summary for a repo.

    This is the 'current state' — what we know right now about a repo's
    situation, constraints, and next steps. Updated on each conversation turn.

    Maps to your current SQLite table:
        CREATE TABLE ledger_state (
            repo TEXT PRIMARY KEY,
            summary TEXT NOT NULL,
            constraints TEXT NOT NULL,
            next_steps TEXT NOT NULL,
            last_verified_sha TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """
    __tablename__ = "ledger_state"

    repo              = Column(String, primary_key=True)
    summary           = Column(Text, nullable=False)
    constraints       = Column(Text, nullable=False)
    next_steps        = Column(Text, nullable=False)
    last_verified_sha = Column(String, nullable=True)
    updated_at        = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<LedgerState repo={self.repo} sha={self.last_verified_sha}>"


# ---------------------------------------------------------------------------
# Table: ledger_events
# ---------------------------------------------------------------------------

class LedgerEvent(Base):
    """Historical conversation turns and verification receipts.

    Every time the system records a conversation turn about a repo,
    it creates one of these rows. This is the audit trail — 'what did
    we say, when, and what was the GitHub state at that moment?'

    Maps to your current SQLite table:
        CREATE TABLE ledger_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT NOT NULL,
            ts TEXT NOT NULL DEFAULT (datetime('now')),
            user_text TEXT NOT NULL,
            assistant_text TEXT NOT NULL,
            head_sha TEXT,
            base_sha TEXT,
            diff_json TEXT,
            verification_note TEXT
        )
    """
    __tablename__ = "ledger_events"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    repo              = Column(String, nullable=False)
    ts                = Column(DateTime(timezone=True), server_default=func.now())
    user_text         = Column(Text, nullable=False)
    assistant_text    = Column(Text, nullable=False)
    head_sha          = Column(String, nullable=True)
    base_sha          = Column(String, nullable=True)
    diff_json         = Column(Text, nullable=True)       # JSON string of changed files
    verification_note = Column(Text, nullable=True)

    def __repr__(self):
        return f"<LedgerEvent id={self.id} repo={self.repo} ts={self.ts}>"