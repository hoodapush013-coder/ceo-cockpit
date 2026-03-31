# CEO Cockpit — Product Vision

> **"Your AI chief-of-staff for engineering execution."**
> Not another dashboard. An intelligence system that tells you what's happening, how you compare, what nobody else noticed, and what to do about it.

---

## The Problem Nobody Has Solved

Every engineering intelligence platform in 2026 — Jellyfish, LinearB, Swarmia, Allstacks — is built for VPs of Engineering at 200-person companies. They show dashboards full of DORA metrics. They take weeks to set up. They require Jira. They only show YOUR numbers in isolation.

**Nobody is building for the founder. Nobody is giving small teams world context. And nobody's AI is discovering patterns that no human programmed.**

CEO Cockpit does all three.

---

## Four Layers (The Architecture of Trust)

### Layer 1: Truth (deterministic, never hallucinated)
Raw metrics from GitHub/Linear APIs. Commits, PRs, reviews, milestones. Time-series snapshots in YOUR database. Transparent scoring formulas.

### Layer 2: Context (benchmarking + external intelligence)
Your metrics compared against industry benchmarks (DORA, 800K+ PR studies). AI tool adoption detection. Relevant framework releases and industry trends. Percentile rankings: "Top 25% for your team size."

### Layer 3: Meaning (AI-generated intelligence)
**Narrative mode** — LLM reads truth + context and generates a weekly brief. Every claim cites its source. Speculation is labeled. Modes: facts / balanced / speculative / investor.

**Discovery mode** — LLM receives full time-series history and discovers patterns nobody programmed:
- "Your commit velocity drops 35% every Thursday"
- "PRs under 200 lines get reviewed 3x faster on your team"
- "frontend-app and backend-api always slow down together — possible hidden dependency"

**Dynamic benchmark selection** — LLM decides WHICH benchmarks are most relevant this week based on the data.

### Layer 4: Fun (team motivation, never surveillance)
Scores, streaks, team leaderboard (never individual). "Shipped this week" celebrations. Gamification that drives healthy behavior.

---

## How It's Different

| | Competitors | CEO Cockpit |
|---|---|---|
| Primary product | Dashboard with charts | AI brief with narrative |
| Intelligence | Hardcoded rules | AI discovers emergent patterns |
| Context | Your numbers in isolation | Your numbers vs the world |
| Benchmarks | Static DORA tiers | LLM picks what's relevant this week |
| AI detection | Basic or none | Copilot/Cursor commit detection + trend |
| Setup | Days to weeks | 5 minutes |
| Pricing | $59/dev/mo+ | Free → $12/dev/mo |
| Team size | 50+ engineers | 4-25 engineers |
| Surveillance | Often individual metrics | Never. Team-level only. |

---

## Dashboard Design

### Design philosophy: Apple-level useful beauty

Remove everything unnecessary. Make what remains feel alive. Smooth line charts over bar charts (trajectory over snapshot). Generous whitespace. Typography that breathes. Dark mode by default.

### Visual hierarchy (top to bottom)

**1. AI brief card (hero)** — Weekly narrative integrating all four layers. Tags: `AI DISCOVERED` (emergent patterns), `WORLD` (external intelligence). Buttons: "Copy as investor update" / "Regenerate" / "Full brief"

**2. Status tiles (4 cards)** — Commits 7d, PRs merged 7d, AI-assisted %, Team health. Each: value + delta + benchmark line.

**3. Velocity chart** — 12-week smooth line chart. Switchable: commits / PRs / score. Gradient fill, no point markers, points on hover.

**4. AI-discovered patterns card** — Emergent insights from time-series analysis. Color dots: green (positive), amber (risk), blue (trend). NOT hardcoded — generated fresh each week.

**5. Alerts** — Conditional. Color-coded with benchmark context.

**6. Repo cards + Leaderboard** — Cards with mini line charts (health-colored curves). Leaderboard sidebar with score bars.

### Data flow

```
Dashboard element         → MCP tool             → Sources
────────────────────────────────────────────────────────────
AI brief + patterns       → ceo_brief()          → org_dashboard + metrics_series + web + LLM
Status tiles + benchmarks → org_dashboard()      → tracked_repos + snapshots + benchmarks.py
Velocity chart            → org_dashboard()      → snapshots (sparklines)
Alerts                    → org_dashboard()      → tracked_repos + snapshots + benchmarks.py
Repo cards + mini charts  → org_dashboard()      → tracked_repos + snapshots
Leaderboard               → org_dashboard()      → tracked_repos + snapshots
```

Key: `org_dashboard` = single source of truth. `ceo_brief` adds intelligence. Dashboard calls both.

### org_dashboard output (target schema)

```json
{
  "tiles": {
    "repos_tracked": 5,
    "commits_24h_total": 12,
    "commits_7d_total": 47,
    "merged_prs_7d_total": 8,
    "active_devs_total": 6,
    "activity_score_total": 127.4,
    "team_health_score": 82,
    "ai_assisted_pct": 38.0,
    "last_collection_ts": "...",
    "trends": { "commits_7d_delta_pct": 18.0, "..." }
  },
  "context": {
    "velocity_percentile": 75,
    "ai_adoption_industry_avg": 30.0,
    "review_speed_percentile": 40
  },
  "repos": [ "..." ],
  "leaderboard": [ "..." ],
  "alerts": [ "..." ]
}
```

**Current vs target status of each field:**

| Field | Status | Step |
|-------|--------|------|
| repos_tracked | ✅ In output | — |
| commits_24h_total | ✅ In output | — |
| commits_7d_total | ⚠️ Computed but not in output | Step 1a |
| merged_prs_7d_total | ✅ In output | — |
| active_devs_total | ❌ Not computed | Step 1b |
| activity_score_total | ✅ In output | — |
| team_health_score | ❌ Not computed | Step 1c |
| ai_assisted_pct | ❌ Needs AI detection first | Step 2 |
| last_collection_ts | ✅ In output | — |
| trends | ❌ Needs historical comparison | Step 3 |
| context object | ❌ Needs benchmarks.py | Step 3 |

---

## Customer Journey

1. Marketing page → "Start free"
2. GitHub OAuth → read-only access
3. Pick 3-5 repos → checkboxes
4. "Collecting first snapshot..." → 30-60 seconds
5. Dashboard with brief + benchmarks + first AI insight
6. "How did it know that?" → hooked
7. "Copy as investor update" → forward to investors
8. Investor: "What tool is this?" → organic referral

Steps 1-5: under 5 minutes.

---

## Context Layer: Implementation

### Source 1: AI tool detection (commit metadata) — Step 2
Scan commit trailers for `Co-authored-by: copilot`, Cursor patterns. New metric: `ai_assisted_commits_7d`. Zero new API calls.

### Source 2: Industry benchmarks (`benchmarks.py`) — Step 3
Hardcoded from DORA + research. Percentile functions. `org_dashboard` compares and returns rankings.

### Source 3: External intelligence (web search in `ceo_brief`) — Step 4
Brief generation searches for framework releases, AI tool updates. One nugget per brief, tagged as external.

### Source 4: Emergent discovery (LLM on time-series) — Step 4
Full 12-week history fed to LLM. Discovers patterns, correlations, anomalies. Powers the "AI patterns" dashboard card.

---

## Build Plan (Micro-Steps)

### ✅ COMPLETED

| Step | What | Date |
|------|------|------|
| Task 12 | Leaderboard + alerts in org_dashboard | Done |
| Step A | PostgreSQL migration — all 14 tools on Postgres, SQLite removed | 2026-03-31 |

### CURRENT: Layer 1 (Truth) completion

**Step 1: org_dashboard tile fixes** ← CURRENT
- 1a. Add `commits_7d_total` to tiles output (already computed, just missing from dict)
- 1b. Add `active_devs_total` accumulator + output
- 1c. Add `team_health_score` computation (from alert counts)
- 1d. Test, verify all 8 tile fields present, commit

### NEXT: Layer 2 (Context) build

**Step 2: AI commit detection in snapshot_collect**
- 2a. Understand GitHub commit trailer format
- 2b. Add AI pattern scanning to snapshot_collect (Copilot/Cursor)
- 2c. Add `ai_assisted_commits` to metrics_json
- 2d. Add `ai_assisted_pct` to org_dashboard tiles
- 2e. Test, commit

**Step 3: benchmarks.py + org_dashboard context enrichment**
- 3a. Create benchmarks.py with DORA + research data
- 3b. Add percentile computation functions (team-size-adjusted)
- 3c. Import in org_dashboard, add `context` object to output
- 3d. Add `trends` to tiles (week-over-week deltas from historical snapshots)
- 3e. Test, commit

### THEN: Layer 3 (Meaning) build

**Step 4: ceo_brief tool**
- 4a. Design LLM prompt structure (system prompt + data template)
- 4b. Build ceo_brief tool (calls org_dashboard + metrics_series)
- 4c. Add facts/balanced/speculative modes
- 4d. Add discovery mode (time-series → LLM → emergent patterns)
- 4e. Add investor update mode
- 4f. Add dynamic benchmark selection (LLM picks priority comparisons)
- 4g. Add external intelligence (optional web search)
- 4h. Test all modes, commit

### THEN: Layer 4 (Fun) + Dashboard

**Step 5: FastAPI HTTP layer**
- 5a. Add FastAPI app alongside MCP server
- 5b. Create GET /api/dashboard (calls org_dashboard)
- 5c. Create GET /api/brief (calls ceo_brief)
- 5d. CORS config for React frontend
- 5e. Test, commit

**Step 6: React Dashboard (Apple-level UX)**
- 6a. Project setup (Vite + React + Tailwind)
- 6b. Brief card component (hero)
- 6c. Tiles row with benchmark lines
- 6d. Velocity line chart (Chart.js, smooth curves, gradient fill)
- 6e. AI patterns card (dynamic from ceo_brief)
- 6f. Alerts bar (conditional)
- 6g. Repo cards with mini line charts
- 6h. Leaderboard sidebar
- 6i. Dark mode + responsive
- 6j. "Copy as investor update" button
- 6k. Polish, test, commit

**Step 7: V1.1 Metrics**
- 7a. PR cycle time from GitHub API
- 7b. Time to first review
- 7c. Deploy frequency proxy
- 7d. AI adoption trend over time
- 7e. Add to benchmarks.py comparisons
- 7f. Test, commit

### FUTURE

**Step 8:** Linear integration (V1b)
**Step 9:** Slack + CI/CD (V2)
**Step 10:** Autonomous execution (V3)

---

## Competitive Landscape (March 2026)

| Tool | Pricing | Our edge |
|------|---------|----------|
| Jellyfish | $59/dev/mo | 5x cheaper + AI discovery + world context |
| LinearB | Enterprise | Narrative + emergent patterns for small teams |
| Swarmia | Free → paid | Brief-first + pattern discovery + benchmarks |
| Allstacks | $400/dev/yr | 5 min setup + AI detection + dynamic context |
| **CEO Cockpit** | **Free → $12** | **AI intelligence, not just metrics** |

---

## Tech Stack

- **Backend:** Python + FastAPI + FastMCP
- **Database:** PostgreSQL 16 (Docker)
- **ORM:** SQLAlchemy 2.0
- **AI:** Model gateway — swappable LLM providers
- **Frontend:** React (Vite) — planned
- **Benchmarks:** benchmarks.py (hardcoded → web-updated → customer-aggregate)

---

## What NOT to Do

- Don't hardcode all insights — let the AI discover patterns
- Don't show all benchmarks equally — let the AI pick what matters this week
- Don't use bar charts when line charts tell the story better
- Don't show individual developer rankings — ever
- Don't make setup take more than 5 minutes
- Don't build a dashboard and call it done — the intelligence is the product