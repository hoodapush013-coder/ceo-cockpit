# CEO Engineering Cockpit

> **"Your AI chief-of-staff for engineering execution."**
> Predicts risks. Shows options. Reads actual code. Setup in 5 minutes.

See [VISION.md](VISION.md) for the full product thesis, dashboard design, and build plan.

---

## What This Is

A prediction engine for startup founders managing small engineering teams (4-25 engineers). Not a metrics dashboard — an AI that tells you what's coming, what's at risk, and what to do about it.

**Apple philosophy:** Fewer features, each perfect.

**Future-focused:** Predicts velocity trajectory, staleness risk, bottleneck forecasts. Gives OPTIONS, not just observations.

**The brief IS the product.** 50% of the dashboard. Everything else is supporting evidence.

**Multi-model architecture:** Routes each task to the optimal model — SLM for classification, frontier model for narrative. Same quality as competitors, 75% less cost.

### Four Layers

| Layer | What | LLM? |
|-------|------|------|
| Truth | Deterministic GitHub metrics | No |
| Context | Benchmarks, "vs world" comparisons | No (runtime) |
| Meaning | Brief + predictions + options + code intelligence | Yes (via model_gateway) |
| Fun | Scores, top 3 devs (LLM-assessed weekly) | Partial |

### Two Scores
- **Velocity** (L1, daily): How MUCH — deterministic formula
- **Intelligence** (L3, weekly): How GOOD — AI reads actual code diffs

---

## Current State (updated 2026-04-07)

### Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          server.py (MCP server)                            │
│                                                                            │
│  LAYER 1 (deterministic):                                                  │
│    snapshot_collect → metrics + AI detection → snapshots table             │
│    org_dashboard → aggregates, scores, alerts, tiles, context → JSON      │
│                                                                            │
│  LAYER 2 (deterministic at runtime):                                       │
│    benchmarks.py → DORA percentile comparisons → context in org_dashboard │
│                                                                            │
│  LAYER 3 (LLM via model_gateway — THE PRODUCT):                           │
│    model_gateway.py → routes to optimal model (PLANNED — Step 4)          │
│    ceo_brief → predictions + risks + options → briefs table (PLANNED)     │
│    quality_analyze → diffs → intelligence + top 3 (PLANNED)               │
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
| `benchmarks.py` | ✅ DORA percentile comparisons |
| `model_gateway.py` | 🔲 Step 4 — unified LLM interface |

### Database

**Live:** `tracked_repos`, `snapshots`, `ledger_state`, `ledger_events`
**Planned:** `briefs` (Step 4), `quality_assessments` (Step 5)

### org_dashboard tiles — all complete

repos_tracked ✅, commits_24h_total ✅, commits_7d_total ✅, merged_prs_7d_total ✅, active_devs_total ✅, activity_score_total ✅, team_health_score ✅, ai_assisted_total ✅, ai_assisted_pct ✅, last_collection_ts ✅, context ✅

### Scoring (deterministic)

```
velocity_score  = 10 × merged_prs_7d + commits_24h + 0.2 × commits_7d
team_health     = max(0, 100 - (high_alerts × 25) - (warn_alerts × 10))
ai_assisted_pct = ai_assisted_total / max(commits_7d_total, 1) × 100
```

---

## Build Plan

### ✅ Completed

| Step | What | Date |
|------|------|------|
| Step A | PostgreSQL migration | 2026-03-31 |
| Step 1 | org_dashboard tiles: commits_7d, active_devs, team_health | 2026-04-05 |
| Step 2 | AI commit detection (Copilot/Claude/Cursor) | 2026-04-05 |
| Step 3 | benchmarks.py + context object (DORA percentiles) | 2026-04-07 |

### Step 4: model_gateway + ceo_brief ← NEXT

| Sub | What |
|-----|------|
| 4a | `model_gateway.py` — unified LLM interface, model routing |
| 4b | `briefs` table in models.py |
| 4c-4l | LLM prompt, trajectory, risk forecast, options, verdicts, 4 modes, patterns, world context, store, test |

### Step 5: quality_analyze + top contributors
### Step 6: React Dashboard (includes FastAPI)
### Step 7: V1.1 Metrics (PR cycle time, time to first review)

### Future (V2+)
- Step 8: Linear → delivery predictions
- Step 9: Slack + CI/CD
- Step 10: DORA team archetypes
- Step 11: Autonomous execution

---

## Dashboard (5 sections)

1. **Brief (hero, 50%)** — predictions + options + top 3 + world context + alerts + patterns
2. **Three health tiles** — velocity ↑↓ + team health + AI adoption ↑↓
3. **Velocity trajectory chart** — 12 weeks + projected future (dotted) + benchmark line
4. **Top 3 contributors** — LLM-assessed from code diffs, weekly
5. **Repo cards** — mini charts + one-line AI verdict

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
| AI Gateway | model_gateway.py — SLM → frontier routing (planned) |
| AI Models | Claude Haiku (classify), Sonnet (narrative), Opus (deep analysis) |
| Frontend | React + Vite + Tailwind (planned) |
| Git | `hoodapush013-coder/ceo-cockpit` |

---

## Learning Journal

### Product Philosophy
- Apple rule: fewer features, each perfect. "Would removing this make a founder notice?"
- Future-focused: predict, don't report. Give options, not observations.
- Brief IS the product — not a card on the dashboard
- Every number needs a "so what" — never raw data alone
- V1 predicts pace + risk. V2 predicts delivery dates. Be honest about the boundary.

### Architecture & System Design
- **Separation of Concerns / Single Responsibility Principle (SRP):** every file does ONE job. If you need "and" to describe it, split it. First letter of SOLID.
- **Data-driven design:** behavior defined by data structures, not hardcoded logic. Adding a new metric = adding one dict entry, not writing a new function. Most powerful pattern in software.
- **Multi-model gateway:** route each task to the optimal model. SLM for classification, frontier for narrative. Same quality, 75% less cost.
- **Structured output:** use tool use / function calling for guaranteed JSON. No parsing prose.
- **Prompt chaining:** decompose complex analysis into stages. Each stage simpler, cheaper, more reliable.
- Four layers: truth / context / meaning / fun
- Golden rule: Layers 1, 2, 4 deterministic. Layer 3 is AI.
- Two scores: velocity (how much) vs intelligence (how good)
- Newspaper model: pre-compute, never make user wait
- Rule alerts (reliable) vs AI predictions (smart) — labeled differently
- Constants at module level (AI_PATTERNS), not inside functions
- Import system: Python executes module once, caches it, shares across importers

### Recognition vs Surveillance (Goodhart's Law)
- Quantitative rankings get GAMED — Goodhart's Law
- LLM-assessed quality recognition — reads actual code, can't be gamed
- Top 3 only, never bottom performers

### DORA 2025 Insights
- AI amplifies, doesn't fix
- 90% adoption, 30% don't trust AI output
- AI increases throughput AND instability
- 7 team archetypes
- Lead time: coding → pickup (92%!) → review → deploy
- 5th metric: rework rate

### What NOT to use (and why)
- RAG: our data is structured in Postgres. SQL queries work. RAG adds complexity for zero benefit. Maybe V3 for historical brief search.
- Fine-tuned SLM: need 100+ customers of training data first. V2/V3.
- Vector database: same reasoning as RAG. Postgres is perfect for structured data.

### Database & Python
- Accumulator pattern, safe dict access (.get), isinstance checks
- Division by zero guard: max(divisor, 1)
- Schema evolution: old snapshots lack new keys
- = vs ==, colon after blocks, .lower() returns new string (immutable)
- "text" in string (quotes!), break to avoid double-counting
- snake_case variables, ALL_CAPS constants
- Restart server after code changes

### Business
- 5-minute setup test
- $60 revenue vs $12 AI cost = 80% margin
- Investor update viral loop + dev recognition viral loop
- Only Indian competitor: Hivel (early stage)
- YC viable: AI + B2B SaaS, dev tools category
- Bootstrap viable: 100 teams × $12/dev = $9,600/mo on $200/mo infra