# CEO Cockpit — Product Vision

> **"Your AI chief-of-staff for engineering execution."**
> Not a dashboard. A prediction engine that tells you what's coming, what's at risk, and what to do about it.

---

## The Product Philosophy

### Apple Rule: Fewer features, each perfect.

Every feature earns its place by passing one test: **"Would removing this make a founder notice something is missing?"** If the answer is no, it doesn't ship.

### Future-focused, not past-focused.

Competitors build reporting tools: "You had 47 commits this week."

We build a prediction engine: "Velocity is trending down 15% over 3 weeks. At this pace, next week drops to ~6 PRs. Review pickup time (4.2h avg) is the bottleneck. Option A: split large PRs. Option B: assign second reviewer."

### The brief IS the product.

The AI brief isn't a card on the dashboard. It IS the dashboard. It occupies the top 50% of the screen. Everything below it is supporting evidence.

---

## Technical Architecture (our edge over competitors)

### Multi-model gateway (`model_gateway.py`)

Competitors send everything to one expensive model. We route each task to the OPTIMAL model:

| Task | Model | Cost |
|------|-------|------|
| Pattern detection in metrics | SLM (Haiku / Phi-4) | ~$0.001 |
| Commit classification (AI?) | Regex (no model) | $0.000 |
| CEO brief narrative | Claude Sonnet | ~$0.05 |
| Deep code quality analysis | Claude Opus | ~$0.50 |
| Chat follow-up questions | Claude Sonnet | ~$0.03 |

One file (`model_gateway.py`) handles all LLM calls. Any tool calls the gateway, gateway picks the right model. Single Responsibility Principle.

### Structured output via tool use

LLM returns guaranteed JSON via function calling / tool use. No parsing prose, no "the LLM forgot a field." Dashboard renders structured data directly. This is how production LLM apps work in 2026.

### Prompt chaining (decomposed intelligence)

Instead of one giant prompt, break analysis into reliable stages:

```
Stage 1: Trajectory analysis (SLM — cheap, fast)
  → "Velocity down 15%, commits declining 3 weeks"

Stage 2: Risk identification (SLM — cheap, fast)
  → "auth-service 11 days inactive, stale in 3 days"

Stage 3: Narrative synthesis (Sonnet — smart)
  → Reads Stage 1+2 + benchmarks + quality data
  → Produces full brief with predictions + options
```

Each stage is simpler, more reliable, and cheaper than one massive prompt.

### Deterministic + AI hybrid (four-layer trust)

Layers 1, 2, 4 deterministic. Layer 3 is AI. AI insights always labeled. Founder knows what to trust.

### Future technical roadmap

- Fine-tuned domain SLM for pattern classification (after 100+ customers)
- RAG over historical briefs (after 6+ months of brief history)
- Customer-aggregate benchmarks (anonymized data from all customers)

---

## DORA 2025 Key Insight

- **AI is an amplifier, not a fixer.** Strong teams get better. Struggling teams get worse faster.
- **90% of developers use AI daily.** Near-universal adoption.
- **AI increases throughput BUT increases instability.**
- **7 team archetypes:** from "Harmonious high-achievers" to "Legacy bottleneck."

We track whether AI adoption is HELPING or HURTING.

---

## Four Layers (The Architecture of Trust)

### Layer 1: Truth (deterministic, NO LLM)
- `snapshot_collect` — GitHub data + AI tool detection → snapshots table
- `org_dashboard` — aggregates, scores, rule-based alerts → JSON
- Velocity score: `10 × merged_prs_7d + commits_24h + 0.2 × commits_7d`
- Team health: `100 - (high_alerts × 25) - (warn_alerts × 10)`

### Layer 2: Context (deterministic at runtime)
- `benchmarks.py` — industry percentile data, updated quarterly
- `org_dashboard` adds `context` — "your 8 PRs/dev puts you at top 25%"
- Benchmark lines on velocity chart

### Layer 3: Meaning (LLM-powered — THE PRODUCT)
- `ceo_brief` — predictions + narrative + risks + options + patterns
- `quality_analyze` — code diffs → intelligence score + per-dev assessment + top 3
- Chat — founder asks follow-up questions
- All LLM calls go through `model_gateway.py`

```
🔴 RULE: auth-service stale 14 days             [deterministic, always reliable]
🔵 AI: Review bottleneck will worsen by Friday   [predicted, LLM-generated]
```

### Layer 4: Fun (mixed)
- Repo velocity scores (deterministic formula)
- Top 3 developers (LLM-assessed weekly — not gameable commit counts)

---

## Two Scores

**Velocity** (Layer 1, daily, deterministic): How MUCH is shipping.
**Intelligence** (Layer 3, weekly, AI-assessed): How GOOD is the work.

These can DISAGREE — that's the point.

---

## What We Can and Can't Predict

### V1 (GitHub only) — Engineering health trajectory

| Can predict | How |
|---|---|
| Velocity trajectory | 12-week trend → projected next-week pace |
| Staleness risk | Days since commit + trajectory → "stale by Friday" |
| Review bottleneck forecast | Open PRs ÷ review speed → "8 days to clear queue" |
| AI adoption trajectory | ai_assisted_pct trend → "50% AI-assisted in 6 weeks" |
| Quality trend | Intelligence score over time → "declining 3 weeks = risk" |
| Developer load imbalance | Commit distribution → "80% from 1 person = bus factor" |
| Pattern-based risk | LLM finds: "auth goes quiet → next PR always 900+ lines" |

### V2 (with Linear) — Project delivery prediction

| Will predict | How |
|---|---|
| Feature completion dates | Issues + velocity = Monte Carlo simulation |
| Sprint delivery probability | Planned vs actual completion rates |
| Milestone slip risk | Scope changes + throughput trends |

---

## Scheduling: Newspaper, Not Live Ticker

| Job | Frequency | Cost | LLM? |
|-----|-----------|------|------|
| Collection | 1-2x daily | ~$0 | No |
| Brief + predictions | 1-2x daily | ~$0.10 | Yes (via model_gateway) |
| Deep analysis + top 3 | Weekly | ~$1-2 | Yes (via model_gateway) |

Everything pre-generated. Dashboard loads instantly.

---

## Dashboard Design (5 sections, Apple-level)

### Section 1: AI Brief (hero — 50% of screen)
Predictions + options + top 3 + world context + alerts + patterns (all woven in).
Buttons: `Copy as investor update` / `Regenerate` / `Chat`

### Section 2: Three Health Indicators (compact row)
Velocity ↑↓ + Team Health + AI Adoption ↑↓. Plus Intelligence badge when available.

### Section 3: Velocity Trajectory Chart
12 weeks + projected future (dotted) + benchmark line (dashed). Smooth curves, gradient fill.

### Section 4: Top Contributors (weekly)
🥇🥈🥉 LLM-assessed from code diffs. Not gameable commit counts (Goodhart's Law).

### Section 5: Repo Cards
Mini charts + one-line AI verdict ("Healthy. 3-week streak." or "Quiet 11 days. Stale Friday.")

### Data flow

```
Brief card           → ceo_brief()        → model_gateway → briefs table
Health indicators    → org_dashboard()     → snapshots + benchmarks.py
Velocity chart       → org_dashboard()     → snapshots + projected trend
Top 3 contributors  → quality_analyze()   → model_gateway → quality_assessments
Repo cards + verdict → org_dashboard()     → snapshots + latest brief
```

---

## Database Schema

### Current tables (all ✅ Postgres)
`tracked_repos`, `snapshots`, `ledger_state`, `ledger_events`

### Planned tables
| Table | Purpose | Layer | Step |
|-------|---------|-------|------|
| `briefs` | Pre-generated AI briefs + predictions | L3 | Step 4 |
| `quality_assessments` | Weekly code quality + top 3 devs | L3 | Step 5 |

### org_dashboard output

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
| context object | ✅ Step 3 |
| trends (trajectory) | Dashboard computes from sparklines |

---

## ceo_brief — The Heart of the Product

### What it reads:
org_dashboard + metrics_series + latest quality_assessment + optional web search

### What it produces (structured JSON via tool use):
```json
{
  "summary": "One paragraph: state of engineering team.",
  "predictions": [{"type": "trajectory", "message": "...", "confidence": "high", "basis": "..."}],
  "options": [{"label": "Split large PRs", "impact": "fastest review improvement", "effort": "low"}],
  "top_contributors": [...],
  "world_context": "Industry AI adoption hit 38%. Your team at 22%.",
  "discovered_patterns": [...],
  "repo_verdicts": {"frontend": "Healthy. 3-week streak.", "auth-service": "Quiet 11 days. Stale Friday."},
  "investor_version": "..."
}
```

### Four modes:
facts / balanced / speculative / investor

### Prompt chaining:
Stage 1 (SLM): trajectory + risk detection → Stage 2 (Sonnet): narrative synthesis + options

---

## quality_analyze — Deep Code Intelligence

Reads week's merged PRs + code diffs. Evaluates per-repo (architecture, design, tools, depth, flags) and per-developer (contribution quality). Produces intelligence score (0-100) + top 3 contributors. All via model_gateway.

---

## Build Plan (Apple-pruned)

### ✅ Completed

| Step | What | Date |
|------|------|------|
| Step A | PostgreSQL migration — all 14 tools, SQLite removed | 2026-03-31 |
| Step 1 | org_dashboard tiles: commits_7d, active_devs, team_health | 2026-04-05 |
| Step 2 | AI commit detection (Copilot/Claude/Cursor) in snapshots | 2026-04-05 |
| Step 3 | benchmarks.py + context object in org_dashboard | 2026-04-07 |

### Step 4: model_gateway + ceo_brief ← NEXT

| Sub | What |
|-----|------|
| 4a | Create `model_gateway.py` — unified LLM interface, model routing |
| 4b | Add `briefs` table to models.py |
| 4c | Design LLM prompt — predictions, risks, options, verdicts |
| 4d | Build trajectory analysis (12-week trend → projected next week) |
| 4e | Build risk forecasting (staleness countdown, bottleneck projection) |
| 4f | Build options engine (concrete A/B/C recommendations) |
| 4g | Build repo verdicts (one-line AI assessment per repo) |
| 4h | Four modes: facts / balanced / speculative / investor |
| 4i | Pattern discovery (LLM analyzes time-series for non-obvious patterns) |
| 4j | World context (benchmark highlights + optional web search) |
| 4k | Store in briefs table (pre-generated, loaded instantly) |
| 4l | Test all modes + commit |

### Step 5: quality_analyze + top contributors

| Sub | What |
|-----|------|
| 5a-5j | Quality table, deep prompt, diffs, per-repo + per-dev, intelligence score, top 3, wire into brief |

### Step 6: React Dashboard (Apple-level, includes FastAPI)

| Sub | What |
|-----|------|
| 6a-6k | FastAPI, React+Tailwind, brief hero, tiles, velocity chart with projection, top 3, repo cards with verdict, chat, dark mode |

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

## Competitive Landscape (April 2026)

| Tool | What they do | What we do differently |
|------|-------------|----------------------|
| Jellyfish ($59/dev) | Dashboards + capacity planning | Brief-first predictions + options + multi-model |
| LinearB (Enterprise) | DORA + workflow automation | AI reads actual code, not just counts |
| Allstacks ($400/dev/yr) | ML delivery forecasting | 5 min setup, structured output, prompt chaining |
| Swarmia (Free→paid) | DORA + dev experience surveys | Deep code intelligence + quality scoring |
| Faros AI (Enterprise) | Enterprise DORA + AI impact | We're for startups, 5x cheaper |
| Hivel (India) | Early-stage engineering intelligence | Multi-model gateway, prediction engine |
| **CEO Cockpit** | **Predictions + options + code intelligence** | **Multi-model, structured output, prompt chaining** |

---

## Tech Stack

- **Backend:** Python + FastAPI + FastMCP
- **Database:** PostgreSQL 16 (Docker) — 4 current + 2 planned tables
- **ORM:** SQLAlchemy 2.0
- **AI Gateway:** `model_gateway.py` — routes tasks to optimal model (SLM → frontier)
- **AI Models:** Claude Haiku (classification), Sonnet (narrative), Opus (deep analysis)
- **Frontend:** React (Vite + Tailwind) — planned
- **Benchmarks:** benchmarks.py → LLM-updated → customer-aggregate

---

## What NOT to Do

- Don't show raw numbers without "so what" — every number needs context
- Don't build features that fail the "would they miss it?" test
- Don't report the past — predict the future, give options
- Don't put LLM in Layer 1 — deterministic foundation stays
- Don't rank developers by commit counts (Goodhart's Law)
- Don't show bottom performers — celebrate top 3, never shame
- Don't send everything to one expensive model — use model gateway
- Don't use RAG when structured SQL queries work fine
- Don't fine-tune before you have 100+ customers of training data
- Don't let vision-code drift — documents must match reality