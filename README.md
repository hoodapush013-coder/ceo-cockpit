# CEO Engineering Cockpit

> **"Your AI chief-of-staff for engineering execution."**
> Brief-first. Benchmark-aware. AI that discovers what nobody programmed. Setup in 5 minutes.

See [VISION.md](VISION.md) for the full product thesis, dashboard design spec, competitive analysis, and build plan.

---

## What This Is

An AI-native tool that turns GitHub activity into execution intelligence for startup founders. Four layers:

| Layer | What | LLM? | Example |
|-------|------|------|---------|
| Truth | Deterministic metrics from GitHub | No | "47 commits, 8 PRs merged" |
| Context | Benchmarks + AI detection | No | "Top 25% for team size. 38% AI-assisted" |
| Meaning | AI narrative + code quality analysis | Yes | "Auth stuck. Thursday dip detected. Intelligence: 72" |
| Fun | Scores, streaks, leaderboard | No | "Frontend on a 3-week shipping streak" |

**The golden rule:** Layers 1, 2, 4 are deterministic (same input = same output, always). Layer 3 is where AI lives. AI interprets the data but never replaces it. If a deterministic number changes, the data changed. If an AI insight changes, the AI thought differently. Both are clearly labeled so the founder knows what to trust.

**Two scores:**
- **Velocity** (Layer 1, daily, deterministic): How MUCH is the team shipping?
- **Intelligence** (Layer 3, weekly, AI-assessed): How GOOD is the work?

These can disagree — that's the point. Velocity 128 + Intelligence 45 = "Shipping fast but building fragile software."

**Scheduling: newspaper, not live ticker.** Everything is pre-computed and stored. The founder opens the dashboard and it's already there. No loading spinners, no waiting for LLM. Like opening a newspaper, not refreshing a stock ticker.

---

## Current State (updated 2026-04-01)

### Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          server.py (MCP server)                            │
│                                                                            │
│  LAYER 1 (deterministic, NO LLM):                                         │
│    snapshot_collect → counts metrics → snapshots table                     │
│    org_dashboard → aggregates, scores (formula), rule alerts → response    │
│                                                                            │
│  LAYER 2 (deterministic, NO LLM):                                         │
│    benchmarks.py → industry data → org_dashboard adds context (PLANNED)    │
│                                                                            │
│  LAYER 3 (LLM-powered, pre-generated + stored):                           │
│    ceo_brief → narrative + patterns → briefs table (PLANNED)               │
│    quality_analyze → code diffs + LLM → quality_assessments table (PLANNED)│
│                                                                            │
│  LAYER 4 (deterministic, NO LLM):                                         │
│    Velocity scores, leaderboard, streaks → from Layer 1 data               │
│                                                                            │
│  Database: PostgreSQL 16 (Docker) ←→ SQLAlchemy ORM                        │
│  GitHub API ←── httpx (async HTTP client)                                  │
├────────────────────────────────────────────────────────────────────────────┤
│  FUTURE:                                                                   │
│  FastAPI HTTP ──→ React Dashboard (brief-first, Apple-level UX)            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Three job frequencies (newspaper model)

| Job | Frequency | Cost | LLM? | Tool |
|-----|-----------|------|------|------|
| Light collection | 1-2x daily | ~$0 | No | `org_collect` → `snapshot_collect` |
| Brief generation | 1-2x daily | ~$0.10 | Yes | `ceo_brief` → stored in `briefs` table |
| Deep analysis | Weekly | ~$1-2 | Yes | `quality_analyze` → stored in `quality_assessments` |

### Files

| File | Job | Status |
|------|-----|--------|
| `server.py` | MCP tools + GitHub API + scoring + alerts | ✅ Active |
| `models.py` | SQLAlchemy ORM (4 tables, 2 planned) | ✅ Active |
| `db.py` | Postgres engine, pool, sessions | ✅ Active |
| `test.py` | MCP client harness via SSE | ✅ Active |
| `.env` | GITHUB_TOKEN + DATABASE_URL | ✅ Active |
| `benchmarks.py` | Industry benchmark data | 🔲 Step 3 |

### Database

**Current tables (all ✅ Postgres):**

| Table | Purpose | Layer |
|-------|---------|-------|
| `tracked_repos` | Which repos an org monitors | Setup |
| `snapshots` | Time-series activity metrics per repo | L1 |
| `ledger_state` | Execution summary per repo | L1 |
| `ledger_events` | Conversation history | L1 |

**Planned tables:**

| Table | Purpose | Layer | Step |
|-------|---------|-------|------|
| `briefs` | Pre-generated AI narratives per org | L3 | Step 4 |
| `quality_assessments` | Weekly code quality analysis per repo | L3 | Step 5 |

### MCP Tools

| Tool | Layer | Status | Feeds |
|------|-------|--------|-------|
| `ping` | — | ✅ | — |
| `list_commits` | — | ✅ | — |
| `get_file` | — | ✅ | — |
| `compare` | — | ✅ | Used by quality_analyze (Step 5) |
| `repos_add` | Setup | ✅ | — |
| `repos_list` | Setup | ✅ | — |
| `repos_remove` | Setup | ✅ | — |
| `snapshot_collect` | L1 | ✅ (AI detection: Step 2) | snapshots table |
| `metrics_series` | L1 | ✅ | Time-series for ceo_brief discovery |
| `org_collect` | L1 | ✅ | Triggers snapshot_collect for all repos |
| `org_dashboard` | L1+L2 | ⚠️ 3 tile fields missing (Step 1) | Dashboard tiles, repos, alerts, leaderboard |
| `ledger_get` | L1 | ✅ | Execution state |
| `ledger_set` | L1 | ✅ | Execution state |
| `ledger_record_turn` | L1 | ✅ | Execution state |
| `ceo_brief` | L3 | 🔲 Step 4 | Brief card, patterns card, investor update |
| `quality_analyze` | L3 | 🔲 Step 5 | Intelligence score, code quality insights |

### org_dashboard tiles — what's there vs what's needed

| Field | Layer | In output? | Step |
|-------|-------|-----------|------|
| repos_tracked | L1 | ✅ Yes | — |
| commits_24h_total | L1 | ✅ Yes | — |
| commits_7d_total | L1 | ⚠️ Computed not returned | Step 1a |
| merged_prs_7d_total | L1 | ✅ Yes | — |
| active_devs_total | L1 | ❌ Not computed | Step 1b |
| activity_score_total | L1 | ✅ Yes | — |
| team_health_score | L1 | ❌ Not computed | Step 1c |
| ai_assisted_pct | L1 | ❌ Needs AI detection | Step 2 |
| last_collection_ts | L1 | ✅ Yes | — |
| trends | L2 | ❌ Needs historical comparison | Step 3 |
| context object | L2 | ❌ Needs benchmarks.py | Step 3 |

### Scoring (Layer 1, deterministic)

```
velocity_score  = 10 × merged_prs_7d + commits_24h + 0.2 × commits_7d
team_health     = max(0, 100 - (high_alerts × 25) - (warn_alerts × 10))  ← Step 1c
ai_assisted_pct = ai_commits_7d / total_commits_7d × 100                 ← Step 2
```

### Alerts

**Rule-based (Layer 1, deterministic, always reliable):**
- 🔴 **STALE (high)**: no commits in 14+ days
- 🟡 **STALE (warn)**: no commits in 7+ days
- 🟡 **LOW_ENGAGEMENT**: ≤1 active dev AND ≤2 commits in 7d

**AI-discovered (Layer 3, from ceo_brief, labeled as AI):**
- 🔵 Emergent patterns, trends, risks (generated weekly, not hardcoded)

---

## Build Plan (Micro-Steps)

### ✅ Completed

| Step | What | Date |
|------|------|------|
| Task 12 | Leaderboard + alerts | Done |
| Step A | PostgreSQL migration — all 14 tools, SQLite removed | 2026-03-31 |

### Step 1: org_dashboard tile fixes ← CURRENT

| Sub | What |
|-----|------|
| 1a | Add `commits_7d_total` to tiles (already computed, missing from dict) |
| 1b | Add `active_devs_total` (new accumulator + tiles) |
| 1c | Add `team_health_score` (count alerts, apply formula, add to tiles) |
| 1d | Test + commit (health should be 65 for test data) |

### Step 2: AI commit detection

| Sub | What |
|-----|------|
| 2a | Learn GitHub commit trailer format |
| 2b | Add Copilot/Cursor pattern scanning to snapshot_collect |
| 2c | Add `ai_assisted_commits` to metrics_json |
| 2d | Add `ai_assisted_pct` to org_dashboard tiles |
| 2e | Test + commit |

### Step 3: benchmarks.py + context

| Sub | What |
|-----|------|
| 3a | Create benchmarks.py with DORA + research data |
| 3b | Percentile functions (team-size-adjusted) |
| 3c | Add `context` object to org_dashboard |
| 3d | Add `trends` to tiles |
| 3e | Test + commit |

### Step 4: ceo_brief + briefs table

| Sub | What |
|-----|------|
| 4a | Add `briefs` table to models.py |
| 4b | Design LLM prompt |
| 4c | Build ceo_brief tool |
| 4d | facts / balanced / speculative modes |
| 4e | Emergent pattern discovery |
| 4f | Investor update mode |
| 4g | Dynamic benchmark selection |
| 4h | External intelligence (web search) |
| 4i | Store in briefs table |
| 4j | Test + commit |

### Step 5: quality_analyze + quality_assessments table

| Sub | What |
|-----|------|
| 5a | Add `quality_assessments` table to models.py |
| 5b | Design quality analysis LLM prompt |
| 5c | Build quality_analyze (reads week's merged PRs + diffs) |
| 5d | LLM evaluates: architecture, design, tools, depth, flags |
| 5e | Intelligence score (0-100) per repo |
| 5f | Store in quality_assessments |
| 5g | Wire into org_dashboard output |
| 5h | Update ceo_brief to reference quality data |
| 5i | Test + commit |

### Step 6: FastAPI HTTP layer

| Sub | What |
|-----|------|
| 6a | FastAPI alongside MCP |
| 6b | GET /api/dashboard |
| 6c | GET /api/brief |
| 6d | POST /api/brief/regenerate |
| 6e | CORS + test + commit |

### Step 7: React Dashboard

| Sub | What |
|-----|------|
| 7a | Vite + React + Tailwind |
| 7b | Brief card (hero, pre-loaded) |
| 7c | Tiles with benchmark lines |
| 7d | Velocity line chart (smooth, gradient, benchmark dashed line) |
| 7e | Intelligence score badge |
| 7f | AI patterns card |
| 7g | Rule alerts bar (separate from AI insights) |
| 7h | Repo cards with mini charts + IQ badge |
| 7i | Leaderboard |
| 7j | Dark mode + responsive |
| 7k | "Copy as investor update" |
| 7l | Polish + commit |

### Step 8: V1.1 Metrics

| Sub | What |
|-----|------|
| 8a | PR cycle time |
| 8b | Time to first review |
| 8c | Deploy frequency proxy |
| 8d | New rule alerts: review bottleneck, large PR |
| 8e | Add to benchmarks.py |
| 8f | Test + commit |

### Future

- Step 9: Linear integration (V1b)
- Step 10: Slack + CI/CD (V2)
- Step 11: Autonomous execution (V3)

---

## How to Run

```bash
uv sync
docker run --name ceo-cockpit-db \
  -e POSTGRES_USER=cockpit -e POSTGRES_PASSWORD=cockpit_dev \
  -e POSTGRES_DB=cockpit -p 5432:5432 -d postgres:16

# .env: GITHUB_TOKEN=ghp_... and DATABASE_URL=postgresql+psycopg2://cockpit:cockpit_dev@localhost:5432/cockpit

uv run python -c "from db import init_db; init_db()"
uv run python server.py

# Separate terminal:
SAMPLE_REPOS="octocat/Hello-World:Hello,psf/requests:Requests" uv run python test.py
```

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.10+ |
| Database | PostgreSQL 16 (Docker) |
| ORM | SQLAlchemy 2.0 |
| AI protocol | FastMCP (MCP/SSE) |
| HTTP | httpx (async) |
| Container | Docker |
| Git | `hoodapush013-coder/ceo-cockpit` |

---

## Build Philosophy

1. Goal in plain English
2. Bigger picture: who calls it, when, why, which layer
3. Tiny examples: inputs → outputs
4. Questions first: understand before coding
5. Implement happy path
6. Harden (error handling AFTER it works)
7. Test + commit
8. Update README + VISION (ground truth, never drift)

---

## Learning Journal

### Architecture & System Design
- Four-layer model: truth / context / meaning / fun
- The golden rule: Layers 1, 2, 4 deterministic. Layer 3 is AI.
- Thermometer vs doctor: data layer measures, AI layer interprets
- Two-score system: velocity (how much) vs intelligence (how good)
- Newspaper model: pre-compute and store, never make the user wait
- Three job frequencies: light (daily), brief (daily), deep (weekly)
- Brief-first design: narrative as product, dashboard as drill-down
- Single source of truth: org_dashboard feeds both UI and LLM
- Rule-based alerts (reliable) vs AI insights (smart) — labeled differently
- Ground truth audits: docs must match code reality at all times
- Vision-code drift: the #1 cause of lost engineering teams
- API-first development: get data contract right, then build UI
- Pre-generated storage: LLM output stored in tables, loaded instantly

### Database & Data Flow
- Accumulator pattern: initialize before loop, sum inside loop, use after loop
- Running maximum: track best/latest as you iterate
- Derived metrics: values computed from other computed values (health from alerts)
- Safe dict access: .get("key", default) vs ["key"] (KeyError prevention)
- isinstance checks: defensive programming against type mismatches
- Negative indexing: [-1] for last element, check empty first
- Ternary expressions: `value if condition else fallback`
- Truthiness: empty list is False, non-empty is True
- `continue` keyword: skip rest of loop iteration
- Generator expressions: `sum(1 for x in list if condition)`
- Why keys might be missing: schema evolution (new fields in new snapshots, old snapshots don't have them)
- N+1 query avoidance, session.refresh(), composite primary keys

### Product & Business
- Numbers without context = noise. Context transforms data into insight.
- Velocity and intelligence can DISAGREE — that's the point
- Investor update as viral loop
- 5-minute setup test
- Pricing as positioning: free + $12/dev = "for startups"
- Cost math: $60 revenue vs $12 AI cost = 80% margin
- Data over time is the moat: more history = better patterns

### Python & DevOps
- Single = (assign) vs double == (compare)
- Colon after if/for/while/def
- Variable name consistency (typos create new variables)
- Docker, SSH multi-account, Git workflow