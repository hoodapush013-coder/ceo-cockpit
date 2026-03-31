# CEO Engineering Cockpit

> **"A Startup Execution Console, not a dashboard."**
> Setup in minutes, not weeks. Priced for teams of 5–50, not enterprise bloat.

See [VISION.md](VISION.md) for the full product thesis and V1/V2/V3 roadmap.

---

## What This Is

A tool that turns GitHub activity (and soon Linear milestones) into execution intelligence for startup founders and CTOs. Three layers:

1. **Truth Layer** — deterministic metrics from real GitHub events. Never hallucinated.
2. **Meaning Layer** — LLM-generated narrative: risks, actions, forecasts (always cites signals, always labels speculation).
3. **Fun Layer** — scores, streaks, leaderboards. Team-level health, never surveillance.

---

## Current State (updated 2026-03-31)

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     server.py (MCP server)                │
│                                                          │
│  MCP Tools ──→ db.py (sessions) ──→ models.py (schema)  │
│                       ↓                                  │
│               PostgreSQL 16 (Docker)                     │
│                                                          │
│  GitHub API ←── httpx (async HTTP client)                │
└──────────────────────────────────────────────────────────┘
```

### Files

| File | Job | One-line summary |
|------|-----|-----------------|
| `server.py` | Features | MCP tools + GitHub API calls + scoring logic |
| `models.py` | Schema | SQLAlchemy ORM models (4 tables) |
| `db.py` | Plumbing | Postgres engine, connection pool, session factory |
| `test.py` | Testing | MCP client test harness via SSE |
| `.env` | Secrets | GITHUB_TOKEN + DATABASE_URL (never committed) |

### Database (PostgreSQL 16 in Docker)

| Table | Purpose | Status |
|-------|---------|--------|
| `tracked_repos` | Which repos an org monitors | ✅ Postgres |
| `snapshots` | Time-series activity metrics per repo | ✅ Postgres |
| `ledger_state` | Current execution summary per repo | ✅ Postgres |
| `ledger_events` | Conversation history + verification receipts | ✅ Postgres |

### MCP Tools

| Tool | Purpose | DB |
|------|---------|-----|
| `ping` | Health check | — |
| `list_commits` | Latest commits from GitHub API | — |
| `get_file` | Read file/dir from GitHub API | — |
| `compare` | Diff two Git refs | — |
| `repos_add` | Track a repo for an org | ✅ Postgres |
| `repos_list` | List tracked repos | ✅ Postgres |
| `repos_remove` | Soft-delete a tracked repo | ✅ Postgres |
| `snapshot_collect` | Fetch GitHub metrics, save snapshot | ✅ Postgres |
| `metrics_series` | Time-ordered series for one metric | ✅ Postgres |
| `org_collect` | Collect snapshots for all tracked repos | ✅ Postgres |
| `org_dashboard` | Tiles + repos + leaderboard + alerts | 🔲 SQLite (NEXT) |
| `ledger_get` | Read current repo execution state | ✅ Postgres |
| `ledger_set` | Write/update repo execution state | ✅ Postgres |
| `ledger_record_turn` | Record conversation + GitHub diff | ✅ Postgres |

### Scoring

```
repo_score = 10 × merged_prs_7d + commits_24h + 0.2 × commits_7d
```

### Alerts

- **STALE (warn)**: no commits in 7+ days
- **STALE (high)**: no commits in 14+ days
- **LOW_ENGAGEMENT**: ≤1 active dev AND ≤2 commits in 7 days

---

## Next Steps (in order)

### Step A.5: Finish Postgres Migration
- Migrate `org_dashboard` to Postgres (the biggest tool)
- Remove all SQLite code (import sqlite3, init_ledger_db, LEDGER_DB_PATH)
- Clean up, full test, commit

### Step B: LLM Analyst (`ceo_brief` tool)
- `ceo_brief(org_id, mode="facts|balanced|speculative")`
- Calls `org_dashboard()` → feeds data to LLM → returns narrative
- Swappable LLM provider (Claude, OpenAI, local) via abstraction layer
- Output: summary, risks, actions, forecasts with disclaimers

### Step C: React Dashboard UI
- FastAPI HTTP API (coexists with FastMCP for AI access)
- Dark-mode CEO-grade dashboard
- Tiles + leaderboard + alert feed + AI brief card
- "First 3 minutes" wow factor

### Step D: V1.1 Metrics
- PR cycle time + stage breakdown (coding → pickup → review → merge)
- Time to first review, review latency
- Stale PR count, deploy frequency proxy

### Step E: Linear Integration (V1b)
- Connect Linear API, ingest milestones and issues
- Milestones become the main object (not repos)
- Risk detection across GitHub + Linear

---

## How to Run

### Prerequisites
- Python 3.10+ (managed with `uv`)
- Docker Desktop (for Postgres)

### Setup

```bash
# 1. Install deps
uv sync

# 2. Start Postgres (skip if already running — check with: docker ps)
docker run --name ceo-cockpit-db \
  -e POSTGRES_USER=cockpit \
  -e POSTGRES_PASSWORD=cockpit_dev \
  -e POSTGRES_DB=cockpit \
  -p 5432:5432 \
  -d postgres:16

# 3. Set secrets (create .env if it doesn't exist)
# .env should contain:
# GITHUB_TOKEN=ghp_your_token_here
# DATABASE_URL=postgresql+psycopg2://cockpit:cockpit_dev@localhost:5432/cockpit

# 4. Create tables
uv run python -c "from db import init_db; init_db()"

# 5. Start the MCP server
uv run python server.py
```

### Test

```bash
# In a separate terminal (server must be running)
uv run python test.py
```

### Docker Quick Reference

```bash
docker ps                          # is Postgres running?
docker start ceo-cockpit-db        # restart stopped container
docker logs ceo-cockpit-db         # check Postgres logs
docker exec -it ceo-cockpit-db psql -U cockpit -d cockpit   # interactive SQL
docker exec -it ceo-cockpit-db psql -U cockpit -d cockpit -c "\dt"  # list tables
docker exec -it ceo-cockpit-db psql -U cockpit -d cockpit -c "SELECT * FROM tracked_repos;"
```

---

## Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| Language | Python 3.10+ | AI/data ecosystem, FastAPI, SQLAlchemy |
| Package manager | uv | Fast, modern Python packaging |
| Database | PostgreSQL 16 | Concurrent reads/writes, JSONB, production-grade |
| ORM | SQLAlchemy 2.0 | Type-safe models, connection pooling, DB-portable |
| DB driver | psycopg2-binary | Standard Postgres driver for Python |
| AI protocol | FastMCP (MCP/SSE) | Standardized tool interface for LLMs |
| HTTP client | httpx (async) | GitHub API calls |
| Containerization | Docker | Isolated Postgres, reproducible environments |
| Version control | Git + GitHub | `hoodapush013-coder/ceo-cockpit` |

---

## Git Workflow

```bash
# Before pushing — 3-second sanity check:
git config user.name          # should be: hoodapush013-coder
git remote -v                 # should point to: github.com-hoodapush013-coder:...
git branch                    # should be: main

# SSH host alias ensures pushes go to the right account
# Config lives in ~/.ssh/config under Host github.com-hoodapush013-coder
```

---

## Build Philosophy

Every task follows this structure:
1. **Goal**: what we're building, in plain English
2. **Bigger picture**: where it fits in the system, who calls it, when it runs
3. **Tiny examples**: inputs → outputs
4. **Implement**: minimal working happy path
5. **Harden**: error handling only AFTER it works
6. **Commit**: after each milestone
7. **Update README + VISION**: after every change so next chat knows the state

---

## Learning Journal (System Design & CS Concepts)

Concepts covered while building this project:

**Architecture & System Design:**
- Separation of Concerns — models.py (schema) / db.py (plumbing) / server.py (features)
- Three-layer product model — truth layer / meaning layer / fun layer
- Refactoring — swap internals without changing external API (Liskov Substitution)
- MCP Protocol — standardized tool interface for LLMs (AI-facing door), vs HTTP/FastAPI (human-facing door)
- Connection Pools — reuse database connections instead of open/close per request
- Factory Pattern — sessionmaker configures once, creates many sessions
- LLM as swappable commodity — provider abstraction, AI is a component not the product
- Data ownership — truth layer in YOUR database, AI only narrates what truth layer contains

**Database & ORM:**
- PostgreSQL vs SQLite — server DB vs embedded DB, MVCC concurrency, SERIAL auto-increment
- SQLAlchemy ORM — Base class, Column types/constraints, sessions, query/filter/commit
- CRUD — Create (add), Read (query/filter), Update (change attribute + commit), Delete
- server_default vs default — database clock vs Python clock for timestamps
- Composite Primary Keys — (org_id, repo) together must be unique
- TIMESTAMP WITH TIME ZONE — always store timezone-aware timestamps
- session.refresh() — reload auto-generated fields (id, ts) after commit

**Python Fundamentals:**
- Classes and Objects — blueprints vs instances, __init__, self, __repr__
- Context Managers — `with` guarantees cleanup (sessions, HTTP clients, files)
- Environment Variables — DATABASE_URL pattern, .env files, sensible defaults

**DevOps & Git:**
- Docker — containers vs images, port mapping, isolated environments
- SSH Multi-Account — host aliases in ~/.ssh/config, IdentitiesOnly, per-repo git identity
- Git Workflow — staging → commit → push, .gitignore, meaningful commit messages
- GitHub Integration — Claude Projects can sync repo files for AI-assisted development