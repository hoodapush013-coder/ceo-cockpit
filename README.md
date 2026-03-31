# CEO Engineering Cockpit

> **"Your AI chief-of-staff for engineering execution."**
> Brief-first. Benchmark-aware. AI that discovers what nobody programmed. Setup in 5 minutes.

See [VISION.md](VISION.md) for the full product thesis, dashboard design spec, competitive analysis, and V1/V2/V3 roadmap.

---

## What This Is

An AI-native tool that turns GitHub activity into execution intelligence for startup founders. What no competitor gives small teams:

1. **AI briefs, not dashboards** — a paragraph that says what shipped, what slipped, what to do
2. **World context** — how you compare to industry benchmarks and AI adoption trends
3. **Emergent pattern discovery** — AI finds patterns nobody programmed ("your velocity drops 35% every Thursday")
4. **Investor updates** — one click generates a draft to edit and forward

Four layers:

| Layer | What | Example |
|-------|------|---------|
| Truth | Deterministic metrics from GitHub | "47 commits, 8 PRs merged this week" |
| Context | Industry benchmarks + AI detection | "Top 25% for team size. 38% AI-assisted (avg: 30%)" |
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
│  ceo_brief ──→ org_dashboard + time-series + web_search            │
│            ──→ LLM: narrative + pattern discovery + priority picks  │
│  FastAPI HTTP ──→ React Dashboard (brief-first, Apple-level UX)    │
└────────────────────────────────────────────────────────────────────┘
```

### Files

| File | Job | Summary |
|------|-----|---------|
| `server.py` | Features | MCP tools + GitHub API + scoring + alerts |
| `models.py` | Schema | SQLAlchemy ORM (4 tables) |
| `db.py` | Plumbing | Postgres engine, pool, sessions |
| `test.py` | Testing | MCP client harness via SSE |
| `.env` | Secrets | GITHUB_TOKEN + DATABASE_URL |
| `benchmarks.py` | Context | Industry benchmark data (PLANNED) |

### Database (PostgreSQL 16 in Docker)

| Table | Purpose | Status |
|-------|---------|--------|
| `tracked_repos` | Which repos an org monitors | ✅ Postgres |
| `snapshots` | Time-series metrics per repo | ✅ Postgres |
| `ledger_state` | Execution summary per repo | ✅ Postgres |
| `ledger_events` | Conversation history | ✅ Postgres |

### MCP Tools → Dashboard Mapping

| Tool | DB | Feeds |
|------|-----|-------|
| `repos_add/list/remove` | ✅ | Setup |
| `snapshot_collect` | ✅ | Snapshots + AI commit detection |
| `metrics_series` | ✅ | Time-series for pattern discovery |
| `org_collect` | ✅ | Batch collection |
| `org_dashboard` | 🔧 Migrating | Tiles, context, repos, alerts, leaderboard |
| `ledger_get/set/record_turn` | ✅ | Execution state |
| `ceo_brief` | 🔲 Step B | Brief card, patterns card, investor update |

### Scoring

```
repo_score    = 10 × merged_prs_7d + commits_24h + 0.2 × commits_7d
team_health   = max(0, 100 - (high_alerts × 25) - (warn_alerts × 10))
ai_assisted%  = ai_commits_7d / total_commits_7d × 100
```

---

## Next Steps

### Step A.5: Finish Postgres Migration + AI Detection
- Migrate `org_dashboard` to Postgres (last SQLite tool)
- Remove all SQLite code
- Add AI-assisted commit detection to `snapshot_collect`

### Step B: LLM Analyst (`ceo_brief`)
- `ceo_brief(org_id, mode="facts|balanced|speculative|investor")`
- Calls `org_dashboard()` + `metrics_series()` for full history
- Optional web search for external intelligence
- LLM generates: narrative + emergent patterns + priority benchmarks
- Investor mode reformats for forwarding

### Step B.5: Context Layer (`benchmarks.py`)
- Industry data from DORA + research
- `org_dashboard` returns percentile rankings and context object
- Team health, trends, AI adoption metrics
- LLM picks which benchmarks matter this week (dynamic, not static)

### Step C: React Dashboard (Apple-level UX)
- FastAPI HTTP API layer
- Brief card (hero) → tiles with benchmarks → velocity line chart → AI patterns card → alerts → repos + leaderboard
- Smooth line charts (tension 0.4, gradient fill, no point markers)
- Mini line charts on repo cards (12-point curves colored by health)
- Dark mode default, mobile-responsive
- "Copy as investor update" button

### Step D: V1.1 Metrics
- PR cycle time, review speed (benchmarked)
- Deploy frequency proxy, AI adoption trend over time

### Step E: Linear Integration (V1b)

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

1. Goal in plain English → 2. Bigger picture → 3. Tiny examples → 4. Implement happy path → 5. Harden → 6. Commit → 7. Update docs

---

## Learning Journal

### Architecture & System Design
- Four-layer model: truth / context / meaning / fun
- Brief-first design: narrative as primary product, dashboard as drill-down
- Progressive disclosure: headline → numbers → comparison → detail
- Single source of truth: org_dashboard feeds both UI and LLM
- Rule-based vs emergent intelligence: hardcoded alerts vs LLM-discovered patterns
- Dynamic benchmark selection: AI picks what's relevant this week
- Read-heavy aggregation: dashboards join tables + compute
- "One concern per change": migrate first, improve later
- MCP (AI door) vs FastAPI (human door)
- Connection pools, factory pattern, separation of concerns

### Context Layer (unique competitive advantage)
- Industry benchmarking: team metrics vs published research
- AI tool detection: Copilot/Cursor patterns in commit trailers
- External intelligence: web search for framework releases, trends
- Percentile computation: raw numbers → meaningful rankings
- Emergent pattern discovery: LLM analyzes full time-series for non-obvious patterns
- Dynamic relevance: LLM decides which benchmarks matter this week
- Benchmark lifecycle: hardcoded → web-updated → customer-aggregate

### Dashboard Design (Apple principles)
- Remove everything unnecessary, make what remains feel alive
- Line charts over bar charts (trajectory over snapshot)
- Smooth curves (tension 0.4), gradient fills, no point markers until hover
- Typography: tight letter-spacing on headlines, generous line-height on body
- Two font weights only: regular (400) and medium (500)
- Every chart must answer a specific question or be removed
- Dark mode default, generous whitespace

### Database & ORM
- PostgreSQL vs SQLite, SQLAlchemy ORM, CRUD
- server_default vs default, composite primary keys
- TIMESTAMP WITH TIME ZONE, session.refresh()
- N+1 query avoidance

### Product & Business
- Numbers without context = noise. Context transforms data into insight.
- Investor update as viral loop: make users look smart to their investors
- 5-minute setup test: every extra step loses customers
- Pricing as positioning: free + $12/dev = "for startups"
- Emergent AI as moat: competitors can copy features, not accumulated intelligence
- Data over time is the competitive advantage: more history = better patterns

### Python & DevOps
- Classes/objects, context managers, env vars, lists vs dicts vs objects
- Docker, SSH multi-account, Git workflow