# CEO Engineering Cockpit

> **"Your AI chief-of-staff for engineering execution."**
> Predicts risks. Shows options. Reads actual code. Setup in 5 minutes.

See [VISION.md](VISION.md) for the full product thesis, dashboard design, and build plan.

---

## What This Is

A prediction engine for startup founders managing small engineering teams (4-25 engineers). Not a metrics dashboard — an AI that tells you what's coming, what's at risk, and what to do about it.

**Apple philosophy:** Fewer features, each perfect. Every feature passes one test: "Would removing this make a founder notice?"

**Future-focused:** The brief doesn't say "you had 47 commits." It says "velocity is trending down 15%. At this pace, next week drops to ~6 PRs. Review pickup time is the bottleneck. Option A: split large PRs. Option B: assign second reviewer."

**The brief IS the product.** It occupies 50% of the dashboard. Everything else is supporting evidence.

### Four Layers

| Layer | What | LLM? |
|-------|------|------|
| Truth | Deterministic GitHub metrics | No |
| Context | Benchmarks, "vs world" comparisons | No (runtime) |
| Meaning | Brief + predictions + options + code intelligence | Yes (THE PRODUCT) |
| Fun | Scores, top 3 devs (LLM-assessed, not commit counts) | Partial |

### Two Scores
- **Velocity** (L1, daily): How MUCH is shipping — deterministic formula
- **Intelligence** (L3, weekly): How GOOD is the work — AI reads actual code diffs

### What V1 Predicts (GitHub only)
Velocity trajectory, staleness risk, review bottleneck forecast, AI adoption trend, quality trend, developer load imbalance, pattern-based risk

### What V2 Predicts (with Linear)
Feature completion dates, sprint delivery probability, milestone slip risk, scope creep detection

---

## Current State (updated 2026-04-05)

### Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          server.py (MCP server)                            │
│                                                                            │
│  LAYER 1 (deterministic):                                                  │
│    snapshot_collect → metrics + AI detection → snapshots table             │
│    org_dashboard → aggregates, scores, alerts, tiles (10 fields)          │
│                                                                            │
│  LAYER 2 (deterministic at runtime):                                       │
│    benchmarks.py → percentile comparisons (PLANNED — Step 3)              │
│                                                                            │
│  LAYER 3 (LLM — THE PRODUCT):                                             │
│    ceo_brief → predictions + risks + options → briefs table (PLANNED)     │
│    quality_analyze → code diffs → intelligence + top 3 (PLANNED)          │
│                                                                            │
│  Database: PostgreSQL 16 ←→ SQLAlchemy ORM                                 │
│  GitHub API ←── httpx (async)                                              │
├────────────────────────────────────────────────────────────────────────────┤
│  FastAPI HTTP + React Dashboard (PLANNED)                                  │
└────────────────────────────────────────────────────────────────────────────┘
```

### Files

| File | Status |
|------|--------|
| `server.py` | ✅ MCP tools + GitHub API + scoring + alerts + AI detection |
| `models.py` | ✅ SQLAlchemy ORM (4 tables, 2 planned) |
| `db.py` | ✅ Postgres engine + sessions |
| `test.py` | ✅ MCP client harness |
| `benchmarks.py` | 🔲 Step 3 |

### Database

**Live:** `tracked_repos`, `snapshots`, `ledger_state`, `ledger_events`
**Planned:** `briefs` (Step 4), `quality_assessments` (Step 5)

### org_dashboard tiles

All 10 fields complete: repos_tracked, commits_24h_total, commits_7d_total, merged_prs_7d_total, active_devs_total, activity_score_total, team_health_score, ai_assisted_total, ai_assisted_pct, last_collection_ts

Pending: `trends` + `context` (Step 3)

### Scoring (deterministic)

```
velocity_score  = 10 × merged_prs_7d + commits_24h + 0.2 × commits_7d
team_health     = max(0, 100 - (high_alerts × 25) - (warn_alerts × 10))
ai_assisted_pct = ai_assisted_total / max(commits_7d_total, 1) × 100
```

---

## Build Plan (Apple-pruned — 7 steps, not 12)

### ✅ Completed

| Step | What | Date |
|------|------|------|
| Step A | PostgreSQL migration | 2026-03-31 |
| Step 1 | org_dashboard tiles: commits_7d, active_devs, team_health | 2026-04-05 |
| Step 2 | AI commit detection (Copilot/Claude/Cursor) | 2026-04-05 |

### Step 3: benchmarks.py + context ← CURRENT

| Sub | What |
|-----|------|
| 3a | benchmarks.py with DORA + research percentile data |
| 3b | Percentile functions (benchmarks.py does per-dev division) |
| 3c | `context` object in org_dashboard |
| 3d | Trajectory arrows (current vs previous) |
| 3e | Test + commit |

### Step 4: ceo_brief — THE PRODUCT

| Sub | What |
|-----|------|
| 4a-4k | Briefs table, LLM prompt, trajectory analysis, risk forecasting, options engine, repo verdicts, 4 modes, pattern discovery, world context, pre-store |

### Step 5: quality_analyze + top contributors

| Sub | What |
|-----|------|
| 5a-5j | Quality table, deep prompt, code diffs, per-repo + per-dev assessment, intelligence score, top 3, wire into brief |

### Step 6: React Dashboard (Apple-level, includes FastAPI)

| Sub | What |
|-----|------|
| 6a-6k | FastAPI, React+Tailwind, brief hero card, 3 health tiles, velocity chart with projection, top 3, repo cards with AI verdict, chat, dark mode, investor update button |

### Step 7: V1.1 Metrics (focused)

| Sub | What |
|-----|------|
| 7a-7d | PR cycle time (4 stages), time to first review, add to benchmarks + brief |

### Future (V2+)

- Step 8: Linear → delivery predictions (Monte Carlo)
- Step 9: Slack + CI/CD
- Step 10: DORA team archetypes
- Step 11: Autonomous execution

---

## Dashboard (5 sections)

1. **Brief (hero, 50%)** — predictions + options + top 3 + world context + alerts (woven in) + patterns (woven in)
2. **Three health tiles** — velocity ↑↓ + team health + AI adoption ↑↓
3. **Velocity trajectory chart** — 12 weeks + projected future (dotted) + benchmark line (dashed)
4. **Top 3 contributors** — LLM-assessed from code diffs, weekly
5. **Repo cards** — mini charts + one-line AI verdict ("Healthy. 3-week streak." or "Quiet 11 days. Stale Friday.")

No separate alerts section. No separate patterns card. No leaderboard sidebar. Brief contains everything.

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

| What | Tool |
|------|------|
| Language | Python 3.10+ |
| Database | PostgreSQL 16 (Docker) |
| ORM | SQLAlchemy 2.0 |
| MCP | FastMCP (SSE) |
| HTTP | httpx (async), FastAPI (planned) |
| Frontend | React + Vite + Tailwind (planned) |
| Git | `hoodapush013-coder/ceo-cockpit` |

---

## Learning Journal

### Product Philosophy
- Apple rule: fewer features, each perfect. "Would removing this make a founder notice?"
- Future-focused: predict, don't report. Give options, not just observations.
- Brief IS the product — not a card on the dashboard
- Every number needs a "so what" — never raw data without context
- V1 predicts pace + risk. V2 predicts delivery dates. Be honest about the boundary.

### Architecture & System Design
- Four layers: truth / context / meaning / fun
- Golden rule: Layers 1, 2, 4 deterministic. Layer 3 is AI.
- Thermometer vs doctor: data measures, AI interprets
- Two scores: velocity (how much) vs intelligence (how good)
- Newspaper model: pre-compute, never make user wait
- Rule alerts (reliable) vs AI predictions (smart) — labeled differently

### Recognition vs Surveillance (Goodhart's Law)
- Quantitative rankings get GAMED — Goodhart's Law
- LLM-assessed quality recognition — reads actual code, can't be gamed
- Top 3 only, never bottom performers
- Developer sees name → motivated → tells friends (second viral loop)

### DORA 2025 Insights
- AI amplifies, doesn't fix
- 90% adoption, 30% don't trust AI output
- AI increases throughput AND instability
- 7 team archetypes
- Lead time: coding → pickup (92%!) → review → deploy
- 5th metric: rework rate

### Database & Python
- Accumulator pattern, safe dict access (.get), isinstance checks
- Division by zero guard: max(divisor, 1)
- Schema evolution: old snapshots lack new keys
- = vs ==, colon after blocks, .lower() returns new string (immutable)
- "text" in string (quotes!), break to avoid double-counting
- snake_case variables, ALL_CAPS constants
- Restart server after code changes
- Constants at module level, not inside functions

### Business
- 5-minute setup test
- $60 revenue vs $12 AI cost = 80% margin
- Investor update as viral loop, dev recognition as second viral loop
- Only Indian competitor: Hivel (early stage)
- YC viable: AI + B2B SaaS, dev tools category
- Bootstrap viable: 100 teams × $12/dev = $9,600/mo on $200/mo infra