# CEO Cockpit — Product Vision

> **"Your AI chief-of-staff for engineering execution."**
> Not another dashboard. An intelligence system that tells you what's happening, how you compare, what nobody else noticed, and what to do about it.

---

## The Problem Nobody Has Solved

Every engineering intelligence platform in 2026 — Jellyfish, LinearB, Swarmia, Allstacks — is built for VPs of Engineering at 200-person companies. They show real-time dashboards full of DORA metrics. They take weeks to set up. They require Jira. They only show YOUR numbers in isolation.

**Nobody is building for the founder. Nobody is giving small teams world context. And nobody's AI is discovering patterns that no human programmed.**

CEO Cockpit does all three.

---

## Four Layers (The Architecture of Trust)

### The Golden Rule

**Layers 1, 2, and 4 are DETERMINISTIC — no LLM, same input always produces same output.** This is the foundation the founder trusts. If a number changes, it's because the data changed, not because the AI had a different opinion.

**Layer 3 is where AI lives.** It INTERPRETS the deterministic data but never REPLACES it. AI insights are always labeled as AI-generated and always cite which Layer 1/2 data they're based on.

Think of it like a hospital: the thermometer (Layer 1) reads 38.5°C every time. The doctor (Layer 3) interprets what that means. If you make the thermometer guess the diagnosis, you've built a bad thermometer AND a bad doctor.

### Layer 1: Truth (deterministic, NO LLM)

Raw metrics from GitHub/Linear APIs. Commits, PRs, reviews, milestones. Time-series snapshots stored in YOUR database. Scoring formulas are fixed and transparent — the founder can look at any number and know exactly why it is what it is.

What lives here:
- `snapshot_collect` — fetches GitHub data, counts metrics, stores in snapshots table
- `org_dashboard` — aggregates snapshots, computes velocity scores (fixed formula), generates rule-based alerts
- Velocity score: `10 × merged_prs_7d + commits_24h + 0.2 × commits_7d`
- Rule-based alerts: "no commits in 14 days" = stale. Always. No AI opinion needed.
- Team health score: `100 - (high_alerts × 25) - (warn_alerts × 10)`. Computed from rule-based alert counts.

### Layer 2: Context (deterministic, NO LLM)

Your metrics compared against published industry benchmarks. Percentile rankings computed from research data (DORA, CodePulse 800K+ PR study). AI tool adoption rates from commit metadata detection.

What lives here:
- `benchmarks.py` — hardcoded industry data, percentile computation functions
- `org_dashboard` adds a `context` object — "your 8 PRs/week puts you at percentile 75 for 6-person teams"
- Benchmark lines on charts — horizontal dashed line at industry median on velocity chart

These numbers are deterministic because they compare YOUR deterministic data against FIXED reference data. Percentile 75 means the same thing every time for the same input.

### Layer 3: Meaning (LLM-powered, always attributed)

This is where AI intelligence lives. It reads Layer 1 + 2 data and produces insights that no formula could generate. Every AI claim cites its source data. Speculation is always labeled.

What lives here:
- `ceo_brief` — reads org_dashboard data + time-series history, LLM generates narrative brief
- `quality_analyze` — reads actual code diffs, LLM evaluates architecture/design/tool choices
- Emergent pattern discovery — LLM finds patterns nobody programmed ("Thursday velocity dip")
- Dynamic benchmark selection — LLM decides which comparisons matter most THIS week
- External intelligence — optional web search for framework releases, industry trends

Two types of AI output appear on the dashboard, labeled differently:

```
🔴 ALERT: auth-service — no commits in 14 days        [RULE — Layer 1, always reliable]
🟡 ALERT: low engagement — 1 dev, 2 commits           [RULE — Layer 1, always reliable]
🔵 AI INSIGHT: PR sizes growing 20% week-over-week    [AI — Layer 3, discovered pattern]
🔵 AI INSIGHT: Thursday velocity dip detected          [AI — Layer 3, discovered pattern]
```

Founders trust both but for different reasons: rules are reliable, AI insights are smart.

### Layer 4: Fun (deterministic, NO LLM)

Scores, streaks, team leaderboard (never individual). "Shipped this week" celebrations. Computed from Layer 1 data using fixed formulas.

---

## Two Scores (Velocity + Intelligence)

### Velocity Score (Layer 1, deterministic, updated daily)

Measures HOW MUCH the team is shipping. Formula-based, same input = same output.

```
velocity = 10 × merged_prs_7d + commits_24h + 0.2 × commits_7d
```

A repo can have velocity 200 and still be doing bad work (panicked bug fixes, boilerplate). Velocity answers: "Is the team active?"

### Intelligence Score (Layer 3, AI-assessed, updated weekly)

Measures HOW GOOD the work is. LLM reads the actual code diffs and evaluates:
- Architecture decisions: Did they introduce clean patterns? Or add spaghetti?
- Design quality: Separation of concerns? Tight coupling? Proper abstractions?
- Tool choices: Using the right tools? Latest versions? Falling behind?
- Engineering depth: Solving hard problems? Or just shipping boilerplate?
- Flags: Anything genuinely concerning (e.g., using a deprecated library, no tests on critical path)

These two scores can DISAGREE, and that's the point:
- Velocity 128 + Intelligence 45 = "Shipping fast but building fragile software"
- Velocity 20 + Intelligence 90 = "Slow week but the work is architecturally excellent"
- Velocity 100 + Intelligence 80 = "Healthy — shipping good work at good pace"

---

## Scheduling Philosophy: Newspaper, Not Live Ticker

Competitors brag about "real-time dashboards." But who refreshes a dashboard every 10 minutes? A micromanager, not a founder. CEO Cockpit is a newspaper — the picture is ready when you open it.

### Three frequencies, three cost tiers

| Job | Frequency | Cost | LLM? | What it does |
|-----|-----------|------|------|-------------|
| Light collection | 1-2x daily | ~$0 | No | snapshot_collect for each repo. Counts commits, PRs, devs, AI-assisted commits. Stores in snapshots table. |
| Brief generation | 1-2x daily | ~$0.10 | Yes | ceo_brief reads snapshots + latest quality assessment + benchmarks. LLM generates narrative + discovers patterns. Pre-generated and STORED — founder never waits. |
| Deep analysis | Weekly | ~$1-2 | Yes | quality_analyze reads the week's merged PRs and code diffs. LLM evaluates architecture, design, tool choices. Produces intelligence score. Stores in quality_assessments table. |

**Cost math:** 5 devs × $12/month = $60 revenue. AI costs: ~$6 briefs + ~$6 quality = $12/month. Margin: 80%. Healthy.

**Pricing lever:** Customers can choose daily deep analysis by paying more. Default is weekly.

### Pre-generated briefs

The brief is generated 1-2x daily by `ceo_brief` and STORED in a `briefs` table. When the founder opens the dashboard, the brief is already there — no loading spinner, no "generating..." message, no 45-second wait. It loads as fast as any other data.

If the founder wants a fresh brief, they click "Regenerate" — but that's optional, not the default experience.

---

## Dashboard Design

### Design philosophy: Apple-level useful beauty

Remove everything unnecessary. Make what remains feel alive. Smooth line charts (trajectory, not snapshot). Generous whitespace. Dark mode default. The dashboard is the DRILL-DOWN, not the primary product — the brief is.

### Visual hierarchy (top to bottom)

**1. AI brief card (hero — pre-generated, loads instantly)**

Weekly narrative integrating all four layers. Pre-generated and stored. Two special tag types:

- `RULE ALERT` — deterministic rule-based alerts (reliable, always correct)
- `AI DISCOVERED` — emergent patterns from time-series analysis (smart, may vary)
- `WORLD` — external intelligence from framework releases, industry trends

Buttons: "Copy as investor update" / "Regenerate" / "Full brief"

**2. Status tiles (4 cards with benchmark context)**

| Tile | Source | Layer | Benchmark line |
|------|--------|-------|----------------|
| Commits (7d) | org_dashboard tiles | L1 | "Top 25% for 6-person teams" (L2) |
| PRs merged (7d) | org_dashboard tiles | L1 | "Median: 5 for your size" (L2) |
| AI-assisted code | org_dashboard tiles | L1 | "Industry avg: 30%" (L2) |
| Team health | org_dashboard tiles | L1 | "2 rule alerts active" |

Plus when available:
| Intelligence score | quality_assessments | L3 | "Last analyzed: Sunday" |
| Velocity score | org_dashboard tiles | L1 | — |

**3. Velocity chart (smooth line, 12 weeks)**

Line chart with gradient fill. Switchable: commits / PRs / score. Industry median shown as horizontal dashed benchmark line (Layer 2 data on the chart). This is the chart founders screenshot for investors.

**4. AI-discovered patterns card (Layer 3, from ceo_brief)**

Emergent insights generated by LLM analyzing full time-series. NOT hardcoded rules.

- 🟢 Green dot: positive pattern ("PRs under 200 lines get reviewed 3x faster on your team")
- 🟡 Amber dot: risk ("auth-service goes quiet → next PR always 900+ lines")
- 🔵 Blue dot: trend ("Copilot adoption 22% → 38% in 6 weeks")

Tags: `Pattern` / `Risk` / `Trend`

**5. Rule-based alerts (Layer 1, conditional)**

Only appears when rule-based alerts exist. Color-coded:
- 🔴 High: stale 14+ days
- 🟡 Warn: stale 7+ days, low engagement

With benchmark context from Layer 2: "No commits in 14 days (industry benchmark: stale after 7)"

**6. Repo cards (left ~70%) + Leaderboard (right ~30%)**

Each repo card:
- Name + velocity pill (green/amber/red with score)
- Intelligence score badge when available ("IQ: 72" or "IQ: pending")
- Smooth mini line chart (12 data points, health-colored curve)
- One-line stats: commits, PRs, devs, last activity

Leaderboard: repos ranked by velocity score with visual bars.

### Data flow

```
Dashboard element         → Source tool           → Data layer → Storage
──────────────────────────────────────────────────────────────────────────
AI brief (pre-generated)  → ceo_brief()           → Layer 3    → briefs table
AI patterns card          → ceo_brief()           → Layer 3    → briefs table (patterns in brief_json)
Intelligence score        → quality_analyze()     → Layer 3    → quality_assessments table
Status tiles              → org_dashboard()       → Layer 1+2  → snapshots + benchmarks.py
Velocity chart            → org_dashboard()       → Layer 1+2  → snapshots (sparklines)
Benchmark lines on chart  → org_dashboard()       → Layer 2    → benchmarks.py
Rule-based alerts         → org_dashboard()       → Layer 1    → snapshots (computed)
Repo cards + mini charts  → org_dashboard()       → Layer 1    → snapshots
Leaderboard               → org_dashboard()       → Layer 1    → snapshots
Investor update button    → ceo_brief(investor)   → Layer 3    → briefs table
```

**Key principle:** org_dashboard provides Layer 1+2 data (truth + context). ceo_brief provides Layer 3 intelligence (narrative + patterns). quality_analyze provides Layer 3 deep analysis (intelligence score). The React dashboard calls ALL THREE and assembles the view. Each loads from pre-computed storage — the founder never waits for LLM.

---

## Database Schema

### Current tables (all ✅ working in Postgres)

| Table | Purpose | Layer |
|-------|---------|-------|
| `tracked_repos` | Which repos an org monitors | Setup |
| `snapshots` | Time-series activity metrics per repo | Layer 1 |
| `ledger_state` | Current execution summary per repo | Layer 1 |
| `ledger_events` | Conversation history + verification | Layer 1 |

### New tables (planned)

| Table | Purpose | Layer | Step |
|-------|---------|-------|------|
| `briefs` | Pre-generated AI briefs per org | Layer 3 | Step 4 |
| `quality_assessments` | Weekly code quality analysis per repo | Layer 3 | Step 5 |

**`briefs` table schema:**
- `id` — unique row identifier
- `org_id` — which organization
- `mode` — facts / balanced / speculative / investor
- `brief_json` — full structured output (narrative + discovered patterns + priority benchmarks)
- `created_at` — when generated

**`quality_assessments` table schema:**
- `id` — unique row identifier
- `org_id` — which organization
- `repo` — which repo (one row per repo per week)
- `week_start` — which week this covers (e.g., "2026-03-24")
- `intelligence_score` — AI quality score (0-100)
- `analysis_json` — full LLM output (architecture decisions, tool choices, flags, recommendations)
- `created_at` — when generated

### org_dashboard output — current vs target

| Field | Status | Layer | Step |
|-------|--------|-------|------|
| repos_tracked | ✅ In output | L1 | — |
| commits_24h_total | ✅ In output | L1 | — |
| commits_7d_total | ⚠️ Computed but not returned | L1 | Step 1a |
| merged_prs_7d_total | ✅ In output | L1 | — |
| active_devs_total | ❌ Not computed | L1 | Step 1b |
| activity_score_total | ✅ In output | L1 | — |
| team_health_score | ❌ Not computed | L1 | Step 1c |
| ai_assisted_pct | ❌ Needs AI detection | L1 | Step 2 |
| last_collection_ts | ✅ In output | L1 | — |
| trends | ❌ Needs historical comparison | L2 | Step 3 |
| context object | ❌ Needs benchmarks.py | L2 | Step 3 |

---

## Context Layer (Layer 2): Implementation

### Source 1: AI tool detection (commit metadata) — Step 2
Scan commit trailers for `Co-authored-by: copilot`, Cursor patterns. New metric: `ai_assisted_commits_7d`. Zero new API calls — we already fetch commit data.

### Source 2: Industry benchmarks (`benchmarks.py`) — Step 3
Hardcoded from DORA research and CodePulse (803K+ PRs). Percentile functions adjusted for team size. `org_dashboard` compares team metrics against benchmarks and returns percentile rankings in a `context` object.

Benchmark lifecycle: hardcoded (V1) → web-updated (V2) → computed from anonymized customer data (V3).

### Source 3: Benchmark lines on charts — Step 7 (dashboard)
Industry median shown as horizontal dashed line on the velocity chart. Visual "am I above or below average?" at a glance.

---

## Meaning Layer (Layer 3): Implementation

### ceo_brief — narrative intelligence (1-2x daily)

Reads: `org_dashboard()` data + `metrics_series()` history + latest `quality_assessment` + optional web search.

LLM generates:
- What shipped, what slipped, what's at risk
- Emergent pattern discovery (time-series analysis → non-obvious patterns)
- Dynamic benchmark selection (LLM picks most relevant comparisons this week)
- External intelligence nugget (framework release, industry trend)
- Investor update variant (same data, professional tone, forward-ready)

Result stored in `briefs` table. Dashboard loads it instantly.

Four modes: `facts` / `balanced` / `speculative` / `investor`

### quality_analyze — deep code intelligence (weekly)

Reads: Week's merged PRs via GitHub API → code diffs via `compare` tool.

LLM evaluates per repo:
- Architecture decisions: clean patterns or spaghetti?
- Design quality: separation of concerns? proper abstractions?
- Tool choices: right tools? latest versions? falling behind?
- Engineering depth: hard problems or boilerplate?
- Flags: deprecated libraries, no tests on critical path, misuse of tools

Produces: intelligence score (0-100) + detailed analysis.

Result stored in `quality_assessments` table (one row per repo per week).

---

## Customer Journey

1. Marketing page → "Start free"
2. GitHub OAuth → read-only access
3. Pick 3-5 repos → checkboxes
4. "Collecting first snapshot..." → 30-60 seconds
5. Dashboard with brief + velocity metrics + benchmark comparisons
6. One week later: first intelligence score + AI-discovered patterns
7. "How did it know our Thursday pattern?" → hooked
8. "Copy as investor update" → forward to investors
9. Investor: "What tool is this?" → organic referral

Steps 1-5: under 5 minutes. Intelligence score arrives after first weekly analysis.

---

## Build Plan (Micro-Steps)

### ✅ Completed

| Step | What | Date |
|------|------|------|
| Task 12 | Leaderboard + alerts | Done |
| Step A | PostgreSQL migration — all 14 tools, SQLite removed | 2026-03-31 |

### Step 1: org_dashboard tile fixes ← CURRENT

Complete Layer 1 output. No new files, no new infrastructure.

| Sub | What | Detail |
|-----|------|--------|
| 1a | `commits_7d_total` in tiles | Already computed in loop, just add to tiles dict |
| 1b | `active_devs_total` in tiles | New accumulator before loop, sum inside loop, add to dict |
| 1c | `team_health_score` in tiles | Count rule-based alerts after loop, apply formula, add to dict |
| 1d | Test + commit | Verify all 8 tile fields. Health should be 65 for test data. |

### Step 2: AI commit detection in snapshot_collect

Layer 1 data collection enhancement. No LLM.

| Sub | What |
|-----|------|
| 2a | Learn GitHub commit trailer format |
| 2b | Add Copilot/Cursor pattern scanning to snapshot_collect |
| 2c | Add `ai_assisted_commits` to metrics_json |
| 2d | Add `ai_assisted_pct` to org_dashboard tiles |
| 2e | Test + commit |

### Step 3: benchmarks.py + context enrichment

Layer 2 build. Deterministic comparison engine.

| Sub | What |
|-----|------|
| 3a | Create benchmarks.py with DORA + research data |
| 3b | Percentile computation functions (team-size-adjusted) |
| 3c | Add `context` object to org_dashboard output |
| 3d | Add `trends` to tiles (week-over-week deltas from snapshots) |
| 3e | Test + commit |

### Step 4: ceo_brief tool + briefs table

Layer 3 narrative intelligence.

| Sub | What |
|-----|------|
| 4a | Add `briefs` table to models.py |
| 4b | Design LLM prompt (system prompt + data template) |
| 4c | Build ceo_brief tool (reads org_dashboard + metrics_series) |
| 4d | Add facts / balanced / speculative modes |
| 4e | Add emergent pattern discovery (time-series → LLM) |
| 4f | Add investor update mode |
| 4g | Add dynamic benchmark selection |
| 4h | Add external intelligence (optional web search) |
| 4i | Store result in briefs table |
| 4j | Test all modes + commit |

### Step 5: quality_analyze tool + quality_assessments table

Layer 3 deep code intelligence.

| Sub | What |
|-----|------|
| 5a | Add `quality_assessments` table to models.py |
| 5b | Design quality analysis LLM prompt |
| 5c | Build quality_analyze tool (reads week's PRs via GitHub API + compare) |
| 5d | LLM evaluates: architecture, design, tool choices, depth, flags |
| 5e | Compute intelligence score (0-100) per repo |
| 5f | Store in quality_assessments table |
| 5g | Wire latest intelligence score into org_dashboard output |
| 5h | Update ceo_brief to read and reference quality data |
| 5i | Test + commit |

### Step 6: FastAPI HTTP layer

Serve the React dashboard.

| Sub | What |
|-----|------|
| 6a | Add FastAPI app alongside MCP server |
| 6b | GET /api/dashboard (calls org_dashboard + reads latest brief + latest quality) |
| 6c | GET /api/brief (returns pre-generated brief from briefs table) |
| 6d | POST /api/brief/regenerate (triggers fresh brief generation) |
| 6e | CORS config for React frontend |
| 6f | Test + commit |

### Step 7: React Dashboard (Apple-level UX)

| Sub | What |
|-----|------|
| 7a | Vite + React + Tailwind setup |
| 7b | Brief card (hero, pre-loaded from briefs table) |
| 7c | Tiles row with benchmark lines |
| 7d | Velocity line chart (Chart.js, smooth curves, gradient fill, benchmark dashed line) |
| 7e | Intelligence score badge (with "last analyzed" note) |
| 7f | AI patterns card (from pre-generated brief) |
| 7g | Rule-based alerts bar (red/yellow, separate from AI insights) |
| 7h | Repo cards with mini line charts + intelligence badge |
| 7i | Leaderboard sidebar |
| 7j | Dark mode + responsive |
| 7k | "Copy as investor update" button |
| 7l | Polish + commit |

### Step 8: V1.1 Metrics

| Sub | What |
|-----|------|
| 8a | PR cycle time from GitHub API |
| 8b | Time to first review |
| 8c | Deploy frequency proxy |
| 8d | New rule-based alerts: review bottleneck, large PR |
| 8e | Add to benchmarks.py comparisons |
| 8f | Test + commit |

### Future

- Step 9: Linear integration (V1b)
- Step 10: Slack + CI/CD (V2)
- Step 11: Autonomous execution (V3)

---

## Competitive Landscape (March 2026)

| Tool | Pricing | Our edge |
|------|---------|----------|
| Jellyfish | $59/dev/mo | 5x cheaper, AI discovery, world context, intelligence score |
| LinearB | Enterprise | Brief-first, emergent patterns, code quality AI for small teams |
| Swarmia | Free → paid | Two-score system (velocity + intelligence), deep code analysis |
| Allstacks | $400/dev/yr | 5 min setup, AI commit detection, pre-generated briefs |
| **CEO Cockpit** | **Free → $12** | **Deterministic truth + AI intelligence, newspaper not ticker** |

---

## Tech Stack

- **Backend:** Python + FastAPI + FastMCP
- **Database:** PostgreSQL 16 (Docker) — 6 tables (4 current + 2 planned)
- **ORM:** SQLAlchemy 2.0
- **AI:** Model gateway — swappable LLM providers. Cheap model for classification, strong model for quality analysis.
- **Frontend:** React (Vite) — planned
- **Benchmarks:** benchmarks.py (hardcoded → web-updated → customer-aggregate)

---

## What NOT to Do

- Don't put LLM in Layer 1 — deterministic foundation must stay deterministic
- Don't make the dashboard real-time — newspaper model, not live ticker
- Don't hardcode all insights — let the AI discover patterns
- Don't show all benchmarks equally — let the AI pick what matters this week
- Don't show individual developer rankings — ever
- Don't make setup take more than 5 minutes
- Don't confuse velocity (how much) with intelligence (how good)
- Don't let vision-code drift — documents must match reality at all times