# CEO Cockpit — Product Vision

> **"Your AI chief-of-staff for engineering execution."**
> Not a dashboard. A prediction engine that tells you what's coming, what's at risk, and what to do about it.

---

## The Product Philosophy

### Apple Rule: Fewer features, each perfect.

Every feature earns its place by passing one test: **"Would removing this make a founder notice something is missing?"** If the answer is no, it doesn't ship.

We don't build 30 metrics. We build 4 that matter, done insanely well. We don't show raw numbers — every number has a "so what" attached. We don't report the past — we predict the future and give options.

### Future-focused, not past-focused.

Competitors build reporting tools: "You had 47 commits this week."

We build a prediction engine: "Velocity is trending down 15% over 3 weeks. At this pace, next week drops to ~6 PRs. Review pickup time (4.2h avg) is the bottleneck. Option A: split large PRs. Option B: assign second reviewer."

The dashboard is about what's COMING and what to DO, not what already happened. Present data exists only to support future predictions.

### The brief IS the product.

The AI brief isn't a card on the dashboard. It IS the dashboard. It occupies the top 50% of the screen. Everything below it — tiles, chart, repo cards — is supporting evidence for the brief's claims. If you only read the brief and nothing else, you have complete understanding of your engineering team.

---

## DORA 2025 Key Insight

- **AI is an amplifier, not a fixer.** Strong teams get better. Struggling teams get worse faster.
- **90% of developers use AI daily.** Near-universal adoption.
- **AI increases throughput BUT increases instability.** Speed without stability = accelerated chaos.
- **7 team archetypes:** from "Harmonious high-achievers" to "Legacy bottleneck."

We don't just track AI adoption. We track whether it's HELPING or HURTING.

---

## Four Layers (The Architecture of Trust)

### The Golden Rule

**Layers 1, 2, and 4 are DETERMINISTIC.** Same input = same output. This is what the founder trusts.

**Layer 3 is where AI lives.** It interprets, predicts, and recommends — but never replaces the deterministic foundation. Layer 3 is the star of the product, but it stands on Layer 1's truth.

### Layer 1: Truth (deterministic, NO LLM)
- `snapshot_collect` — GitHub data + AI tool detection → snapshots table
- `org_dashboard` — aggregates, scores, rule-based alerts → JSON
- Velocity score: `10 × merged_prs_7d + commits_24h + 0.2 × commits_7d`
- Team health: `100 - (high_alerts × 25) - (warn_alerts × 10)`

### Layer 2: Context (deterministic at runtime)
- `benchmarks.py` — industry percentile data, updated quarterly (LLM reads latest research)
- `org_dashboard` adds `context` — "your 8 PRs/dev puts you at top 25%"
- Benchmark lines on velocity chart

### Layer 3: Meaning (LLM-powered — THE PRODUCT)
- `ceo_brief` — prediction + narrative + risks + options + pattern discovery
- `quality_analyze` — code diffs → intelligence score + per-developer assessment + top 3
- Chat — founder asks follow-up questions about the brief

Two types of output, labeled differently:
```
🔴 RULE: auth-service stale 14 days             [deterministic, always reliable]
🔵 AI: Review bottleneck will worsen by Friday   [predicted, LLM-generated]
```

### Layer 4: Fun (mixed)
- Repo velocity scores (deterministic formula)
- Top 3 developers (LLM-assessed weekly from quality_analyze — not gameable commit counts)

---

## Two Scores

**Velocity** (Layer 1, daily, deterministic): How MUCH is shipping.
**Intelligence** (Layer 3, weekly, AI-assessed): How GOOD is the work.

These can DISAGREE — that's the point:
- Velocity 128 + Intelligence 45 = "Shipping fast but building fragile"
- Velocity 20 + Intelligence 90 = "Slow week but architecturally excellent"

---

## What We Can and Can't Predict (Honesty)

### V1 (GitHub only) — Engineering health trajectory

| Can predict | How |
|---|---|
| Velocity trajectory | 12-week trend → projected next-week pace |
| Staleness risk | Days since commit + trajectory → "stale by Friday" |
| Review bottleneck forecast | Open PRs ÷ review speed → "8 days to clear queue" |
| AI adoption trajectory | ai_assisted_pct trend → "50% AI-assisted in 6 weeks" |
| Quality trend | Intelligence score over time → "declining 3 weeks = risk" |
| Developer load imbalance | Commit distribution → "80% from 1 person = bus factor" |
| Pattern-based risk | LLM finds: "auth goes quiet → next PR is always 900+ lines" |

### V2 (with Linear) — Project delivery prediction

| Will predict | How |
|---|---|
| Feature completion dates | Issues + velocity = Monte Carlo simulation |
| Sprint delivery probability | Planned vs actual completion rates |
| Milestone slip risk | Scope changes + throughput trends |
| Scope creep detection | Planned vs unplanned work ratio |

V1 predictions are about PACE and RISK. V2 predictions are about DELIVERY DATES. Both are valuable. We ship V1 predictions so well that founders don't notice what's missing until V2 arrives.

---

## Scheduling: Newspaper, Not Live Ticker

| Job | Frequency | Cost | LLM? |
|-----|-----------|------|------|
| Collection | 1-2x daily | ~$0 | No |
| Brief + predictions | 1-2x daily | ~$0.10 | Yes, pre-stored in `briefs` table |
| Deep analysis + top 3 | Weekly | ~$1-2 | Yes, stored in `quality_assessments` table |

Everything pre-generated. Dashboard loads instantly. Founder never waits for LLM.

---

## Dashboard Design (5 sections, Apple-level)

### Design principles

- Brief IS the dashboard (top 50% of screen)
- No separate alerts section (woven into brief)
- No separate patterns card (woven into brief)
- No leaderboard sidebar (folded into repo cards)
- Every number has a "so what" — never raw numbers alone
- Velocity chart projects INTO THE FUTURE (dotted line)
- Dark mode default, generous whitespace, smooth curves
- Beautiful enough to screenshot for investors

### Section 1: AI Brief (hero — 50% of screen)

Pre-generated, loads instantly. Contains:
- What shipped this week (with quality assessment)
- PREDICTIONS: velocity trajectory, risk forecasts, bottleneck warnings
- OPTIONS: concrete actions the founder can take (A/B/C choices)
- Top 3 contributors with plain-English description of their best work
- World context: benchmark comparisons, industry trends
- Rule-based alerts (woven in, not a separate section)
- AI-discovered patterns (woven in, not a separate section)

Buttons: `Copy as investor update` / `Regenerate` / `Chat`

### Section 2: Three Health Indicators (compact row)

| Indicator | What | Shows |
|---|---|---|
| Velocity | How much is shipping | Score + ↑↓ arrow + "top X%" |
| Team Health | Rule-based health | Score + alert count |
| AI Adoption | AI tool usage | Percentage + ↑↓ + "avg 30%" |

Plus Intelligence Score badge when available (from weekly analysis).

3-4 compact cards. NOT 10 tiles with raw numbers.

### Section 3: Velocity Trajectory Chart

Smooth line chart (12 weeks) with:
- Gradient fill, health-colored curve
- **PROJECTED trajectory** extending forward as a dotted line
- Industry median as horizontal dashed benchmark line
- Switchable: velocity score / commits / PRs

The chart SHOWS THE FUTURE. If the trend is declining, the founder sees the dotted line going down before it happens.

### Section 4: Top Contributors (weekly)

```
🥇 Alice — Observer pattern for state management (high architectural impact)
🥈 Bob — Auth refactor, reduced coupling by 40% (quality improvement)
🥉 Charlie — Solved caching race condition (hard problem)

Last analyzed: Sunday  •  Intelligence: 72/100
```

LLM-assessed from code diffs. Not gameable commit counts (Goodhart's Law).

### Section 5: Repo Cards

Each card shows:
- Name + velocity pill (green/amber/red)
- Intelligence badge when available
- Smooth mini line chart (12 data points)
- **One-line AI verdict** (from the brief): "Healthy. 3-week streak." or "Quiet 11 days. Stale Friday."

No separate leaderboard. The cards ARE the leaderboard, ordered by velocity.

### Data flow (simplified)

```
Brief card           → ceo_brief()        → briefs table (pre-generated)
Health indicators    → org_dashboard()     → snapshots + benchmarks.py
Velocity chart       → org_dashboard()     → snapshots (sparklines) + projected trend
Top 3 contributors  → quality_analyze()   → quality_assessments table
Repo cards + verdict → org_dashboard()     → snapshots + latest brief (for verdict text)
```

---

## Database Schema

### Current tables (all ✅ Postgres)

| Table | Purpose | Layer |
|-------|---------|-------|
| `tracked_repos` | Which repos to monitor | Setup |
| `snapshots` | Time-series metrics per repo | L1 |
| `ledger_state` | Execution summary per repo | L1 |
| `ledger_events` | Conversation history | L1 |

### Planned tables

| Table | Purpose | Layer | Step |
|-------|---------|-------|------|
| `briefs` | Pre-generated AI briefs + predictions | L3 | Step 4 |
| `quality_assessments` | Weekly code quality + top 3 devs | L3 | Step 5 |

### org_dashboard output

| Field | Status | Layer |
|-------|--------|-------|
| repos_tracked | ✅ | L1 |
| commits_24h_total | ✅ | L1 |
| commits_7d_total | ✅ | L1 |
| merged_prs_7d_total | ✅ | L1 |
| active_devs_total | ✅ | L1 |
| activity_score_total | ✅ | L1 |
| team_health_score | ✅ | L1 |
| ai_assisted_total | ✅ | L1 |
| ai_assisted_pct | ✅ | L1 |
| last_collection_ts | ✅ | L1 |
| trends (with trajectory) | 🔲 Step 3 | L2 |
| context object | 🔲 Step 3 | L2 |

---

## ceo_brief — The Heart of the Product

This tool is where 80% of the product's value lives. The LLM prompt must be designed with extreme care.

### What ceo_brief reads:
- `org_dashboard()` — current metrics + alerts + benchmarks
- `metrics_series()` — 12+ weeks of historical data for trajectory analysis
- Latest `quality_assessment` — intelligence score + per-dev analysis
- Optional web search — framework releases, industry trends

### What ceo_brief produces:

```json
{
  "summary": "One paragraph: the state of your engineering team.",
  "predictions": [
    {
      "type": "trajectory",
      "message": "Velocity trending down 15% over 3 weeks. Next week: ~6 PRs.",
      "confidence": "high",
      "basis": "12-week linear regression on merged_prs_7d"
    },
    {
      "type": "risk",
      "message": "auth-service hits stale threshold Friday at current pace.",
      "confidence": "high",
      "basis": "11 days inactive, 14-day threshold in 3 days"
    }
  ],
  "options": [
    {
      "label": "Split large PRs",
      "impact": "Fastest review turnaround improvement",
      "effort": "low"
    },
    {
      "label": "Assign second reviewer for auth-service",
      "impact": "Reduces review bottleneck by ~50%",
      "effort": "medium"
    }
  ],
  "top_contributors": [...],
  "world_context": "Industry AI adoption hit 38%. Your team at 22%, up 3 pts.",
  "discovered_patterns": [...],
  "repo_verdicts": {
    "frontend": "Healthy. 3-week shipping streak.",
    "auth-service": "Quiet 11 days. Stale Friday."
  },
  "investor_version": "..."
}
```

### Four modes:
- `facts` — just data, no speculation
- `balanced` — data + predictions + options (default)
- `speculative` — deeper pattern analysis, longer horizon
- `investor` — professional tone, forward-ready, highlights growth

---

## quality_analyze — Deep Code Intelligence

### What it reads:
Week's merged PRs via GitHub API → code diffs via `compare` tool.

### What it evaluates per repo:
- Architecture decisions: clean patterns or spaghetti?
- Design quality: separation of concerns? proper abstractions?
- Tool choices: right tools? latest versions?
- Engineering depth: hard problems or boilerplate?
- Flags: deprecated libraries, no tests on critical path

### What it evaluates per developer:
- What did each contributor actually build?
- Quality and impact of their specific commits/PRs
- Who made the most impactful engineering contributions?

### What it produces:
- Intelligence score (0-100) per repo
- Top 3 contributors across org with plain-English descriptions
- Specific, actionable recommendations (not generic advice)
- Stored in `quality_assessments` table

---

## Build Plan (Apple-pruned)

### ✅ Completed

| Step | What | Date |
|------|------|------|
| Step A | PostgreSQL migration — all 14 tools, SQLite removed | 2026-03-31 |
| Step 1 | org_dashboard tiles: commits_7d, active_devs, team_health | 2026-04-05 |
| Step 2 | AI commit detection (Copilot/Claude/Cursor) in snapshots | 2026-04-05 |

### Step 3: benchmarks.py + context ← CURRENT

| Sub | What |
|-----|------|
| 3a | Create benchmarks.py with DORA + research percentile data |
| 3b | Percentile computation functions (benchmarks.py does the per-dev division) |
| 3c | Add `context` object to org_dashboard (inline benchmark comparisons) |
| 3d | Add trajectory arrows to tiles (current value vs previous snapshot) |
| 3e | Test + commit |

### Step 4: ceo_brief (THE PRODUCT — deep investment)

| Sub | What |
|-----|------|
| 4a | Add `briefs` table to models.py |
| 4b | Design LLM prompt — predictions, risks, options, verdicts (not just summary) |
| 4c | Build trajectory analysis (12-week trend → projected next week) |
| 4d | Build risk forecasting (staleness countdown, bottleneck projection) |
| 4e | Build options engine (concrete A/B/C recommendations) |
| 4f | Build repo verdicts (one-line AI assessment per repo) |
| 4g | Four modes: facts / balanced / speculative / investor |
| 4h | Pattern discovery (LLM analyzes time-series for non-obvious patterns) |
| 4i | World context (benchmark highlights + optional web search) |
| 4j | Store in briefs table (pre-generated, loaded instantly) |
| 4k | Test all modes + commit |

### Step 5: quality_analyze + top contributors

| Sub | What |
|-----|------|
| 5a | Add `quality_assessments` table to models.py |
| 5b | Design quality prompt (deep, specific, educational — not generic) |
| 5c | Build quality_analyze (reads week's PRs + diffs) |
| 5d | Per-repo: architecture, design, tools, depth, flags |
| 5e | Per-developer: contribution quality assessment |
| 5f | Intelligence score (0-100) per repo |
| 5g | Top 3 contributors across org |
| 5h | Store in quality_assessments |
| 5i | Wire latest intelligence score + top 3 into brief |
| 5j | Test + commit |

### Step 6: React Dashboard (Apple-level UX — includes FastAPI)

| Sub | What |
|-----|------|
| 6a | FastAPI HTTP endpoints: /api/dashboard, /api/brief, /api/brief/regenerate |
| 6b | Vite + React + Tailwind setup |
| 6c | Brief card (hero, 50% of screen, pre-loaded from briefs table) |
| 6d | Three health indicator tiles (velocity ↑↓, health, AI adoption ↑↓) |
| 6e | Velocity trajectory chart (smooth line + projected future + benchmark line) |
| 6f | Top 3 contributors card |
| 6g | Repo cards with mini charts + one-line AI verdict |
| 6h | Chat interface for brief follow-up questions |
| 6i | Dark mode, responsive, generous whitespace |
| 6j | "Copy as investor update" button |
| 6k | Polish until it's beautiful enough to screenshot |

### Step 7: V1.1 Metrics (focused — only what drives predictions)

| Sub | What |
|-----|------|
| 7a | PR cycle time (4 stages: coding → pickup → review → deploy) |
| 7b | Time to first review (the biggest bottleneck — feeds predictions) |
| 7c | Add to benchmarks.py + ceo_brief predictions |
| 7d | Test + commit |

### Future (V2+)

- **Step 8:** Linear integration → project delivery predictions (Monte Carlo)
- **Step 9:** Slack + CI/CD → deploy frequency, notification workflows
- **Step 10:** DORA team archetype classification
- **Step 11:** Autonomous execution — bounded autonomy, slip simulation

---

## Competitive Landscape (April 2026)

| Tool | What they do | What we do differently |
|------|-------------|----------------------|
| Jellyfish ($59/dev) | Dashboards + capacity planning | Brief-first predictions + options |
| LinearB (Enterprise) | DORA + workflow automation + Monte Carlo | AI reads actual code, not just counts |
| Allstacks ($400/dev/yr) | ML delivery forecasting | 5 min setup, AI-assessed dev recognition |
| Swarmia (Free→paid) | DORA + developer experience surveys | Deep code intelligence + quality scoring |
| Faros AI (Enterprise) | Enterprise DORA + AI impact | We're for startups, 5x cheaper |
| Hivel (India) | Early-stage engineering intelligence | Prediction engine, not reporting tool |
| **CEO Cockpit** | **Predictions + options + intelligence** | **Only product that reads code, predicts risks, and gives options** |

---

## Tech Stack

- **Backend:** Python + FastAPI + FastMCP
- **Database:** PostgreSQL 16 (Docker) — 4 current + 2 planned tables
- **ORM:** SQLAlchemy 2.0
- **AI:** Model gateway — swappable LLM providers
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
- Don't make the dashboard look like 2000s enterprise software
- Don't add more metrics when existing ones aren't perfect yet
- Don't promise project delivery dates without Linear data (V2)
- Don't let vision-code drift — documents must match reality