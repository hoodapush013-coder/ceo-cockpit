# CEO Engineering Cockpit

> **"Your AI chief-of-staff for engineering execution."**
> Brief-first. Benchmark-aware. AI that discovers what nobody programmed. Setup in 5 minutes.

See [VISION.md](VISION.md) for the full product thesis, dashboard design spec, competitive analysis, and build plan.

---

## What This Is

An AI-native tool that turns GitHub activity into execution intelligence for startup founders. Four layers:

| Layer | What | Example |
|-------|------|---------|
| Truth | Deterministic metrics from GitHub | "47 commits, 8 PRs merged this week" |
| Context | Benchmarks + AI detection | "Top 25% for team size. 38% AI-assisted (avg: 30%)" |
| Meaning | AI narrative + emergent discovery | "Auth is stuck. Thursday velocity dip detected." |
| Fun | Scores, streaks, team leaderboard | "Frontend on a 3-week shipping streak" |

---

## Current State (updated 2026-03-31)

### Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                     server.py (MCP server)                         │
│                                                                    │
│  MCP Tools ──→ db.py (sessions) ──→ models.py (schema)            │
│                       ↓                                            │
│               PostgreSQL 16 (Docker)                               │
│  GitHub API ←── httpx (async HTTP client)                          │
├────────────────────────────────────────────────────────────────────┤
│  PLANNED:                                                          │
│  benchmarks.py ──→ industry data (DORA, 800K+ PRs research)       │
│  ceo_brief ──→ org_dashboard + time-series + web_search + LLM     │
│  FastAPI HTTP ──→ React Dashboard (brief-first, Apple-level UX)    │
└────────────────────────────────────────────────────────────────────┘
```

### Files

| File | Job | Summary | Status |
|------|-----|---------|--------|
| `server.py` | Features | MCP tools + GitHub API + scoring + alerts | ✅ Active |
| `models.py` | Schema | SQLAlchemy ORM (4 tables) | ✅ Active |
| `db.py` | Plumbing | Postgres engine, pool, sessions | ✅ Active |
| `test.py` | Testing | MCP client harness via SSE | ✅ Active |
| `.env` | Secrets | GITHUB_TOKEN + DATABASE_URL | ✅ Active |
| `benchmarks.py` | Context | Industry benchmark data | 🔲 Step 3 |

### Database (PostgreSQL 16 in Docker)

| Table | Purpose | Status |
|-------|---------|--------|
| `tracked_repos` | Which repos an org monitors | ✅ Postgres |
| `snapshots` | Time-series metrics per repo | ✅ Postgres |
| `ledger_state` | Execution summary per repo | ✅ Postgres |
| `ledger_events` | Conversation history | ✅ Postgres |

### MCP Tools

| Tool | DB | Status | Feeds |
|------|-----|--------|-------|
| `ping` | — | ✅ | — |
| `list_commits` | — | ✅ | — |
| `get_file` | — | ✅ | — |
| `compare` | — | ✅ | — |
| `repos_add` | ✅ Postgres | ✅ | Setup |
| `repos_list` | ✅ Postgres | ✅ | Setup |
| `repos_remove` | ✅ Postgres | ✅ | Setup |
| `snapshot_collect` | ✅ Postgres | ✅ (AI detection: Step 2) | Snapshots |
| `metrics_series` | ✅ Postgres | ✅ | Time-series for discovery |
| `org_collect` | ✅ Postgres | ✅ | Batch collection |
| `org_dashboard` | ✅ Postgres | ⚠️ Missing 3 tile fields (Step 1) | Tiles, repos, alerts, leaderboard |
| `ledger_get` | ✅ Postgres | ✅ | Execution state |
| `ledger_set` | ✅ Postgres | ✅ | Execution state |
| `ledger_record_turn` | ✅ Postgres | ✅ | Execution state |
| `ceo_brief` | — | 🔲 Step 4 | Brief card, patterns, investor update |

### org_dashboard tiles — what's there vs what's needed

| Field | In output? | Step |
|-------|-----------|------|
| repos_tracked | ✅ Yes | — |
| commits_24h_total | ✅ Yes | — |
| commits_7d_total | ⚠️ Computed but not returned | Step 1a |
| merged_prs_7d_total | ✅ Yes | — |
| active_devs_total | ❌ Not computed | Step 1b |
| activity_score_total | ✅ Yes | — |
| team_health_score | ❌ Not computed | Step 1c |
| ai_assisted_pct | ❌ Needs AI detection | Step 2 |
| last_collection_ts | ✅ Yes | — |
| trends | ❌ Needs historical comparison | Step 3 |
| context object | ❌ Needs benchmarks.py | Step 3 |

### Scoring

```
repo_score    = 10 × merged_prs_7d + commits_24h + 0.2 × commits_7d
team_health   = max(0, 100 - (high_alerts × 25) - (warn_alerts × 10))  ← Step 1c
ai_assisted%  = ai_commits_7d / total_commits_7d × 100                 ← Step 2
```

### Alerts

- **STALE (high)**: no commits in 14+ days
- **STALE (warn)**: no commits in 7+ days
- **LOW_ENGAGEMENT**: ≤1 active dev AND ≤2 commits in 7d

---

## Build Plan (Micro-Steps)

### ✅ Completed

| Step | What | Date |
|------|------|------|
| Task 12 | Leaderboard + alerts | Done |
| Step A | PostgreSQL migration — all 14 tools, SQLite removed | 2026-03-31 |

### Step 1: org_dashboard tile fixes ← CURRENT

Complete the Truth Layer by adding missing fields to org_dashboard output.

| Sub-step | What | Change |
|----------|------|--------|
| 1a | Add `commits_7d_total` to tiles | Already computed, just add to tiles dict |
| 1b | Add `active_devs_total` | New accumulator + add to tiles dict |
| 1c | Add `team_health_score` | Count alerts by level, compute health score |
| 1d | Test + commit | Verify all 8 tile fields present |

### Step 2: AI commit detection in snapshot_collect

Add Layer 2 (Context) data collection.

| Sub-step | What |
|----------|------|
| 2a | Learn GitHub commit trailer format |
| 2b | Add Copilot/Cursor pattern scanning to snapshot_collect |
| 2c | Add `ai_assisted_commits` to metrics_json |
| 2d | Add `ai_assisted_pct` to org_dashboard tiles |
| 2e | Test + commit |

### Step 3: benchmarks.py + context enrichment

Build the comparison engine.

| Sub-step | What |
|----------|------|
| 3a | Create benchmarks.py with DORA + research data |
| 3b | Add percentile computation functions |
| 3c | Add `context` object to org_dashboard output |
| 3d | Add `trends` to tiles (week-over-week deltas) |
| 3e | Test + commit |

### Step 4: ceo_brief tool

Build Layer 3 (Meaning) — the AI intelligence engine.

| Sub-step | What |
|----------|------|
| 4a | Design LLM prompt structure |
| 4b | Build ceo_brief tool (calls org_dashboard + metrics_series) |
| 4c | Add facts/balanced/speculative modes |
| 4d | Add discovery mode (emergent pattern detection) |
| 4e | Add investor update mode |
| 4f | Add dynamic benchmark selection |
| 4g | Add external intelligence (optional web search) |
| 4h | Test all modes + commit |

### Step 5: FastAPI HTTP layer

Serve the React dashboard.

| Sub-step | What |
|----------|------|
| 5a | Add FastAPI alongside MCP server |
| 5b | GET /api/dashboard (calls org_dashboard) |
| 5c | GET /api/brief (calls ceo_brief) |
| 5d | CORS config + test + commit |

### Step 6: React Dashboard

Apple-level UX. Brief-first layout.

| Sub-step | What |
|----------|------|
| 6a | Vite + React + Tailwind setup |
| 6b | Brief card (hero) |
| 6c | Tiles row with benchmark lines |
| 6d | Velocity line chart (smooth curves) |
| 6e | AI patterns card |
| 6f | Alerts bar |
| 6g | Repo cards with mini line charts |
| 6h | Leaderboard sidebar |
| 6i | Dark mode + responsive |
| 6j | "Copy as investor update" button |
| 6k | Polish + commit |

### Step 7: V1.1 Metrics

| Sub-step | What |
|----------|------|
| 7a | PR cycle time |
| 7b | Time to first review |
| 7c | Deploy frequency proxy |
| 7d | AI adoption trend over time |
| 7e | Add to benchmarks.py |
| 7f | Test + commit |

### Future

- Step 8: Linear integration (V1b)
- Step 9: Slack + CI/CD (V2)
- Step 10: Autonomous execution (V3)

---

## How to Run

```bash
# 1. Install deps
uv sync

# 2. Start Postgres
docker run --name ceo-cockpit-db \
  -e POSTGRES_USER=cockpit -e POSTGRES_PASSWORD=cockpit_dev \
  -e POSTGRES_DB=cockpit -p 5432:5432 -d postgres:16

# 3. Set secrets in .env:
# GITHUB_TOKEN=ghp_your_token_here
# DATABASE_URL=postgresql+psycopg2://cockpit:cockpit_dev@localhost:5432/cockpit

# 4. Create tables
uv run python -c "from db import init_db; init_db()"

# 5. Start server
uv run python server.py

# 6. Test (separate terminal)
SAMPLE_REPOS="octocat/Hello-World:Hello,psf/requests:Requests" uv run python test.py
```

### Docker

```bash
docker ps                          # running?
docker start ceo-cockpit-db        # restart
docker exec -it ceo-cockpit-db psql -U cockpit -d cockpit  # SQL shell
```

---

## Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| Language | Python 3.10+ | AI/data ecosystem |
| Database | PostgreSQL 16 | JSONB, concurrent, production |
| ORM | SQLAlchemy 2.0 | Type-safe, pooling |
| AI protocol | FastMCP (MCP/SSE) | LLM tool interface |
| HTTP | httpx (async) | GitHub API |
| Container | Docker | Isolated Postgres |
| Git | `hoodapush013-coder/ceo-cockpit` | SSH multi-account |

---

## Build Philosophy

1. Goal in plain English
2. Bigger picture: who calls it, when, why
3. Tiny examples: inputs → outputs
4. Implement happy path
5. Harden (error handling AFTER it works)
6. Test + commit
7. Update README + VISION (ground truth, never drift)

---

## Learning Journal

### Architecture & System Design
- Four-layer model: truth / context / meaning / fun
- Brief-first design: narrative as product, dashboard as drill-down
- Progressive disclosure: headline → numbers → comparison → detail
- Single source of truth: org_dashboard feeds both UI and LLM
- Rule-based vs emergent intelligence: hardcoded alerts vs LLM discovery
- Read-heavy aggregation: dashboards join tables + compute derived values
- "One concern per change": migrate first, improve later
- Ground truth audits: docs must match code reality at all times
- MCP (AI door) vs FastAPI (human door)
- Connection pools, factory pattern, separation of concerns

### Context Layer (competitive advantage)
- Industry benchmarking: team metrics vs published research
- AI tool detection: Copilot/Cursor patterns in commit trailers
- External intelligence: web search for framework releases, trends
- Emergent pattern discovery: LLM analyzes full time-series
- Dynamic relevance: LLM picks which benchmarks matter this week
- Benchmark lifecycle: hardcoded → web-updated → customer-aggregate

### Dashboard Design (Apple principles)
- Remove everything unnecessary, make what remains feel alive
- Line charts over bar charts (trajectory over snapshot)
- Smooth curves (tension 0.4), gradient fills
- Two font weights: regular (400) and medium (500)
- Every chart must answer a specific question or be removed
- Dark mode default, generous whitespace

### Database & ORM
- PostgreSQL vs SQLite, SQLAlchemy ORM, CRUD
- Composite primary keys, TIMESTAMP WITH TIME ZONE
- N+1 query avoidance, session.refresh()
- Accumulators, running maximums, safe dict access (.get)
- Negative indexing ([-1]), ternary expressions, truthiness
- Generator expressions with sum()

### Product & Business
- Numbers without context = noise
- Investor update as viral loop
- 5-minute setup test
- Pricing as positioning: free + $12/dev = "for startups"
- Data over time is the moat: more history = better patterns
- Vision-code drift: documents must always match reality

### Python & DevOps
- Classes/objects, context managers, env vars
- Lists vs dicts vs objects
- Docker, SSH multi-account, Git workflow
- The `continue` keyword in loops