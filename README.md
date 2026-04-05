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
| Context | Benchmarks + AI detection | No (runtime) | "Top 25% for team size. 38% AI-assisted" |
| Meaning | AI narrative + code quality + dev recognition | Yes | "Auth stuck. Alice built great observer pattern. IQ: 72" |
| Fun | Scores, streaks, repo leaderboard, top 3 devs | Partial | Repo scores deterministic, dev recognition LLM-assessed |

**The golden rule:** Layers 1, 2 deterministic. Layer 3 is AI. Layer 4 mixes both (repo scores = formula, developer top 3 = LLM-assessed weekly).

**Two scores:** Velocity (L1, daily, deterministic: how MUCH) + Intelligence (L3, weekly, AI: how GOOD).

**Developer recognition:** Weekly top 3 contributors based on LLM's assessment of actual code quality — not commit counts (Goodhart's Law: gameable metrics create bad incentives). Shows only top 3, never bottom performers. Celebrates excellence.

**Scheduling: newspaper, not live ticker.** Pre-computed and stored. Dashboard loads instantly.

**DORA 2025:** AI is an amplifier, not a fixer. 90% use AI. AI increases throughput BUT instability. We track both.

---

## Current State (updated 2026-04-05)

### Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          server.py (MCP server)                            │
│                                                                            │
│  LAYER 1 (deterministic, NO LLM):                                         │
│    snapshot_collect → metrics + AI detection → snapshots table             │
│    org_dashboard → aggregates, scores, alerts, tiles (10 fields) → JSON   │
│                                                                            │
│  LAYER 2 (deterministic at runtime, NO LLM at runtime):                   │
│    benchmarks.py → industry data → org_dashboard adds context (PLANNED)    │
│                                                                            │
│  LAYER 3 (LLM-powered, pre-generated + stored):                           │
│    ceo_brief → narrative + patterns → briefs table (PLANNED)               │
│    quality_analyze → diffs + LLM → intelligence score + top 3 (PLANNED)   │
│                                                                            │
│  LAYER 4 (mixed):                                                          │
│    Velocity scores, repo leaderboard (deterministic)                       │
│    Top 3 contributors (from quality_analyze, LLM-assessed weekly)          │
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
| Brief generation | 1-2x daily | ~$0.10 | Yes | `ceo_brief` → `briefs` table |
| Deep analysis | Weekly | ~$1-2 | Yes | `quality_analyze` → `quality_assessments` (includes top 3) |

### Files

| File | Job | Status |
|------|-----|--------|
| `server.py` | MCP tools + GitHub API + scoring + alerts + AI detection | ✅ Active |
| `models.py` | SQLAlchemy ORM (4 tables, 2 planned) | ✅ Active |
| `db.py` | Postgres engine, pool, sessions | ✅ Active |
| `test.py` | MCP client harness via SSE | ✅ Active |
| `.env` | GITHUB_TOKEN + DATABASE_URL | ✅ Active |
| `benchmarks.py` | Industry benchmark data | 🔲 Step 3 |

### Database

**Current (all ✅ Postgres):** `tracked_repos`, `snapshots`, `ledger_state`, `ledger_events`

**Planned:** `briefs` (Step 4), `quality_assessments` (Step 5 — includes per-dev assessments)

### MCP Tools

| Tool | Layer | Status |
|------|-------|--------|
| `ping` | — | ✅ |
| `list_commits` / `get_file` / `compare` | — | ✅ |
| `repos_add/list/remove` | Setup | ✅ |
| `snapshot_collect` | L1 | ✅ + AI detection |
| `metrics_series` | L1 | ✅ |
| `org_collect` | L1 | ✅ |
| `org_dashboard` | L1+L2 | ✅ tiles done, context pending (Step 3) |
| `ledger_get/set/record_turn` | L1 | ✅ |
| `ceo_brief` | L3 | 🔲 Step 4 |
| `quality_analyze` | L3 | 🔲 Step 5 (includes per-dev assessment) |

### org_dashboard tiles — current status

| Field | Status |
|-------|--------|
| repos_tracked | ✅ |
| commits_24h_total | ✅ |
| commits_7d_total | ✅ Step 1 |
| merged_prs_7d_total | ✅ |
| active_devs_total | ✅ Step 1 |
| activity_score_total | ✅ |
| team_health_score | ✅ Step 1 |
| ai_assisted_total | ✅ Step 2 |
| ai_assisted_pct | ✅ Step 2 |
| last_collection_ts | ✅ |
| trends | 🔲 Step 3 |
| context object | 🔲 Step 3 |

### Scoring (Layer 1, deterministic)

```
velocity_score  = 10 × merged_prs_7d + commits_24h + 0.2 × commits_7d
team_health     = max(0, 100 - (high_alerts × 25) - (warn_alerts × 10))
ai_assisted_pct = ai_assisted_total / max(commits_7d_total, 1) × 100
```

### Alerts & Recognition

**Rule-based alerts (L1):** 🔴 Stale 14d+ / 🟡 Stale 7d+ / 🟡 Low engagement
**AI-discovered insights (L3):** 🔵 Emergent patterns from ceo_brief (Step 4)
**Developer recognition (L3):** 🥇🥈🥉 Top 3 contributors from quality_analyze (Step 5)

---

## Build Plan

### ✅ Completed

| Step | What | Date |
|------|------|------|
| Task 12 | Leaderboard + alerts | Done |
| Step A | PostgreSQL migration — all 14 tools, SQLite removed | 2026-03-31 |
| Step 1 | org_dashboard tiles: commits_7d, active_devs, team_health | 2026-04-05 |
| Step 2 | AI commit detection (Copilot/Claude/Cursor) in snapshots | 2026-04-05 |

### Step 3: benchmarks.py + context ← CURRENT

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
| 4a-4j | LLM prompt, narrative, patterns, investor mode, web search, store |

### Step 5: quality_analyze + quality_assessments

| Sub | What |
|-----|------|
| 5a-5k | Quality prompt, diffs, intelligence score, per-dev assessment, top 3, store, wire |

### Step 6: FastAPI HTTP layer
### Step 7: React Dashboard (includes top 3 contributors card)

### Step 8: V1.1 Metrics

Lead time: coding → pickup (92%!) → review → deploy. DORA 5th metric: rework rate.

| Sub | What |
|-----|------|
| 8a-8h | PR cycle time, first review, deploy freq, rework rate, AI instability, alerts |

### Future

- Step 9: Linear (V1b) / Step 10: Slack+CI/CD (V2) / Step 11: DORA archetypes (V2) / Step 12: Autonomous (V3)

---

## How to Run

```bash
uv sync
docker run --name ceo-cockpit-db \
  -e POSTGRES_USER=cockpit -e POSTGRES_PASSWORD=cockpit_dev \
  -e POSTGRES_DB=cockpit -p 5432:5432 -d postgres:16
# .env: GITHUB_TOKEN + DATABASE_URL
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

1. Goal in plain English → 2. Bigger picture (who/when/why/which layer) → 3. Examples → 4. Questions first → 5. Implement → 6. Harden → 7. Test + commit → 8. Update docs

---

## Learning Journal

### Architecture & System Design
- Four-layer model: truth / context / meaning / fun
- The golden rule: Layers 1, 2 deterministic. Layer 3 is AI. Layer 4 mixes both.
- Thermometer vs doctor: data layer measures, AI layer interprets
- Two-score system: velocity (how much) vs intelligence (how good)
- Newspaper model: pre-compute and store, never make user wait
- Single source of truth: org_dashboard feeds both UI and LLM
- Rule alerts (reliable) vs AI insights (smart) — labeled differently
- Ground truth audits: docs must match code reality
- API-first: data contract right, then build UI
- Constants at module level (AI_PATTERNS), not inside functions

### Recognition vs Surveillance (Goodhart's Law)
- Quantitative rankings (commit counts, lines of code) get GAMED
- Goodhart's Law: "When a measure becomes a target, it ceases to be a good measure"
- Solution: LLM-assessed quality recognition — reads actual code, can't be gamed
- Show top 3 contributors (celebrate excellence), never bottom performers (don't shame)
- Recognition based on engineering QUALITY, not typing QUANTITY

### DORA 2025 Insights
- AI amplifies, doesn't fix — strong teams get better, weak get worse
- 90% adoption, 30% don't trust AI output
- AI increases throughput AND instability — track both
- 7 team archetypes: "Harmonious high-achievers" to "Legacy bottleneck"
- Lead time: coding → pickup (92%!) → review → deploy
- 5th metric: rework rate (2024)
- Speed without stability = accelerated chaos

### Database & Data Flow
- Accumulator pattern, running maximum, derived metrics
- Safe dict access: .get(), isinstance checks
- Negative indexing, ternary, truthiness, continue, break
- Generator expressions: sum(1 for x in list if condition)
- Division by zero guard: max(divisor, 1)
- Schema evolution: old snapshots lack new keys

### Python Fundamentals
- = (assign) vs == (compare), colon after blocks
- .lower() returns new string (immutable), "text" in string (quotes!)
- snake_case variables, ALL_CAPS constants
- Restart server after code changes

### Product & Business
- Numbers without context = noise
- Velocity and intelligence can disagree — that's the point
- Investor update as viral loop
- Dev sees name in top 3 → motivated → tells friends (second viral loop)
- 5-minute setup test, $60 revenue vs $12 AI cost = 80% margin
- Data over time is the moat
- Vision-code drift: #1 cause of lost teams