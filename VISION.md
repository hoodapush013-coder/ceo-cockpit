# CEO Cockpit — Product Vision

> **"Your AI chief-of-staff for engineering execution."**
> Not another dashboard. An intelligence system that tells you what's happening, how you compare, what nobody else noticed, and what to do about it.

---

## The Problem Nobody Has Solved

Every engineering intelligence platform in 2026 — Jellyfish, LinearB, Swarmia, Allstacks — is built for VPs of Engineering at 200-person companies. They show real-time dashboards full of DORA metrics. They take weeks to set up. They require Jira. They only show YOUR numbers in isolation.

**Nobody is building for the founder. Nobody is giving small teams world context. And nobody's AI is discovering patterns that no human programmed.**

CEO Cockpit does all three.

---

## DORA 2025 Key Insight (shapes everything we build)

The 2025 DORA "State of AI-assisted Software Development" report (5,000 professionals surveyed) found:

- **AI is an amplifier, not a fixer.** Strong teams get better. Struggling teams get worse faster.
- **90% of developers use AI daily.** AI adoption is near-universal.
- **AI increases throughput BUT increases instability.** Speed without stability = accelerated chaos.
- **7 team archetypes** identified: from "Harmonious high-achievers" to "Legacy bottleneck."
- **AI doesn't replace code review — it makes code review MORE critical.**

**What this means for our product:** We don't just track AI adoption percentage. We track whether that adoption is HELPING or HURTING. If ai_assisted_pct is going up but intelligence_score is going down, the brief says: "AI may be amplifying existing code quality issues."

---

## Four Layers (The Architecture of Trust)

### The Golden Rule

**Layers 1, 2, and 4 are DETERMINISTIC — no LLM, same input always produces same output.**

**Layer 3 is where AI lives.** It INTERPRETS the deterministic data but never REPLACES it.

Thermometer (Layer 1) reads 38.5°C every time. Doctor (Layer 3) interprets what that means.

### Layer 1: Truth (deterministic, NO LLM)

Raw metrics from GitHub/Linear APIs. Scoring formulas are fixed and transparent.

- `snapshot_collect` — fetches GitHub data, counts metrics, detects AI tool trailers
- `org_dashboard` — aggregates, computes velocity scores (fixed formula), generates rule-based alerts
- Velocity score: `10 × merged_prs_7d + commits_24h + 0.2 × commits_7d`
- Team health score: `100 - (high_alerts × 25) - (warn_alerts × 10)`
- AI-assisted commit detection: Copilot, Claude Code, Cursor patterns

### Layer 2: Context (deterministic at runtime, NO LLM at runtime)

Your metrics compared against published industry benchmarks. LLM used ONLY to periodically UPDATE benchmark data (quarterly, reading latest research). At runtime: pure math.

- `benchmarks.py` — industry data, percentile functions
- `org_dashboard` adds `context` object — percentile rankings
- Benchmark lines on velocity chart — industry median as dashed line

Benchmark lifecycle: hardcoded (V1) → LLM-updated from research (V2) → customer-aggregate (V3).

### Layer 3: Meaning (LLM-powered, always attributed)

Two types of AI output, labeled differently on dashboard:

```
🔴 ALERT: auth-service — no commits in 14 days        [RULE — Layer 1, always reliable]
🟡 ALERT: low engagement — 1 dev, 2 commits           [RULE — Layer 1, always reliable]
🔵 AI INSIGHT: PR sizes growing 20% week-over-week    [AI — Layer 3, discovered pattern]
🔵 AI INSIGHT: Thursday velocity dip detected          [AI — Layer 3, discovered pattern]
```

What lives here:
- `ceo_brief` — narrative + pattern discovery + investor update + dynamic benchmark selection
- `quality_analyze` — reads code diffs, evaluates architecture/design/tools, produces intelligence score, identifies top contributor work
- Chat about the brief — founder asks follow-up questions

### Layer 4: Fun (deterministic scores, LLM-assessed recognition)

**Repo-level (deterministic):** Velocity scores, streaks, team leaderboard.

**Developer recognition (LLM-assessed, weekly):** Top 3 contributors highlighted based on the weekly `quality_analyze` deep dive. The LLM reads actual code diffs and identifies WHO made the most impactful engineering contributions — not who typed the most keystrokes.

This is NOT a leaderboard of commit counts (which is gameable and encourages busywork). It's recognition of genuine engineering excellence: "Alice introduced a clean observer pattern that decoupled the auth module. Bob refactored 3 legacy endpoints, reducing complexity by 40%."

**Why LLM-assessed, not formula-based:** Any quantitative ranking (commits, PRs, lines of code) gets gamed. This is Goodhart's Law: "When a measure becomes a target, it ceases to be a good measure." The LLM sees through gaming because it reads the ACTUAL CODE, not just counts.

---

## How It's Different

| | Competitors | CEO Cockpit |
|---|---|---|
| Primary product | Dashboard with charts | AI brief with narrative |
| Intelligence | Hardcoded rules | AI discovers emergent patterns |
| Context | Your numbers in isolation | Your numbers vs the world |
| Benchmarks | Static DORA tiers | LLM picks what's relevant this week |
| AI detection | Basic or none | Copilot/Cursor/Claude detection + trend |
| Developer recognition | Commit count leaderboards (gameable) | LLM-assessed quality contributions (weekly top 3) |
| Setup | Days to weeks | 5 minutes |
| Pricing | $59/dev/mo+ | Free → $12/dev/mo |

---

## Two Scores (Velocity + Intelligence)

### Velocity Score (Layer 1, deterministic, updated daily)
How MUCH is shipping. `10 × merged_prs_7d + commits_24h + 0.2 × commits_7d`

### Intelligence Score (Layer 3, AI-assessed, updated weekly)
How GOOD is the work. LLM reads code diffs and evaluates:
- Architecture decisions, design quality, tool choices
- Engineering depth vs boilerplate
- Per-developer contribution quality (feeds top 3 recognition)
- Flags: deprecated libraries, no tests, misuse of tools

These can DISAGREE — that's the point:
- Velocity 128 + Intelligence 45 = "Shipping fast but building fragile"
- Velocity 20 + Intelligence 90 = "Slow week but architecturally excellent"

---

## Scheduling Philosophy: Newspaper, Not Live Ticker

| Job | Frequency | Cost | LLM? | What |
|-----|-----------|------|------|------|
| Light collection | 1-2x daily | ~$0 | No | snapshot_collect: counts + AI detection |
| Brief generation | 1-2x daily | ~$0.10 | Yes | ceo_brief: narrative + patterns. Stored in `briefs` table. |
| Deep analysis | Weekly | ~$1-2 | Yes | quality_analyze: diffs → intelligence score + top contributors. Stored in `quality_assessments` table. |

---

## Dashboard Design

### Design philosophy: Apple-level useful beauty

Remove everything unnecessary. Make what remains feel alive. Smooth line charts. Generous whitespace. Dark mode default. Brief is the product, dashboard is the drill-down.

### Visual hierarchy (top to bottom)

**1. AI brief card (hero — pre-generated, loads instantly)**

Tags: `RULE ALERT` / `AI DISCOVERED` / `WORLD`
Buttons: "Copy as investor update" / "Regenerate" / "Full brief"

**2. Status tiles (4-6 cards with benchmark context)**

| Tile | Layer | Benchmark |
|------|-------|-----------|
| Commits (7d) | L1 | "Top 25% for 6-person teams" (L2) |
| PRs merged (7d) | L1 | "Median: 5 for your size" (L2) |
| AI-assisted code | L1 | "Industry avg: 30%" (L2) |
| Team health | L1 | "2 rule alerts active" |
| Intelligence score | L3 | "Last analyzed: Sunday" (when available) |

**3. Velocity chart (smooth line, 12 weeks)**

Gradient fill, switchable metrics, industry median dashed line. The chart founders screenshot for investors.

**4. Top contributors (Layer 3, weekly, from quality_analyze)**

Top 3 developers who made the most impactful engineering contributions this week. NOT based on commit counts — based on the LLM's assessment of actual code quality, architecture decisions, and problem difficulty.

Example card:
```
🥇 Alice — Introduced observer pattern for state management (high architectural impact)
🥈 Bob — Refactored auth module, reduced coupling by 40% (quality improvement)
🥉 Charlie — Solved complex caching race condition (hard problem)
```

Shows only top 3, never bottom performers. Celebrates excellence without shaming anyone. Updated weekly with the deep analysis. Shows "Top contributors last updated: Sunday" between analyses.

**5. AI-discovered patterns card (Layer 3, from ceo_brief)**

Emergent insights. 🟢 Pattern / 🟡 Risk / 🔵 Trend. NOT hardcoded.

**6. Rule-based alerts (Layer 1, conditional)**

🔴 High / 🟡 Warn. With benchmark context from Layer 2.

**7. Repo cards (left ~70%) + Leaderboard (right ~30%)**

Mini line charts, velocity pill, intelligence badge when available.

### Data flow

```
Dashboard element         → Source tool           → Layer → Storage
──────────────────────────────────────────────────────────────────────
AI brief (pre-generated)  → ceo_brief()           → L3   → briefs table
AI patterns card          → ceo_brief()           → L3   → briefs table
Intelligence score        → quality_analyze()     → L3   → quality_assessments table
Top 3 contributors       → quality_analyze()     → L3   → quality_assessments table
Status tiles              → org_dashboard()       → L1+2 → snapshots + benchmarks.py
Velocity chart            → org_dashboard()       → L1+2 → snapshots (sparklines)
Rule-based alerts         → org_dashboard()       → L1   → snapshots (computed)
Repo cards + mini charts  → org_dashboard()       → L1   → snapshots
Repo leaderboard          → org_dashboard()       → L1   → snapshots
```

---

## Database Schema

### Current tables (all ✅ Postgres)

| Table | Purpose | Layer |
|-------|---------|-------|
| `tracked_repos` | Which repos an org monitors | Setup |
| `snapshots` | Time-series activity metrics per repo | L1 |
| `ledger_state` | Execution summary per repo | L1 |
| `ledger_events` | Conversation history | L1 |

### Planned tables

| Table | Purpose | Layer | Step |
|-------|---------|-------|------|
| `briefs` | Pre-generated AI briefs per org | L3 | Step 4 |
| `quality_assessments` | Weekly code quality per repo + top contributors | L3 | Step 5 |

**`quality_assessments` table schema:**
- `id` — unique row identifier
- `org_id` — which organization
- `repo` — which repo (one row per repo per week)
- `week_start` — which week this covers
- `intelligence_score` — AI quality score (0-100)
- `analysis_json` — full LLM output: architecture decisions, tool choices, flags, recommendations, per-developer contribution assessments
- `created_at` — when generated

The `analysis_json` includes per-developer contribution assessments. `org_dashboard` (or a new endpoint) aggregates across repos to produce the org-wide "top 3 contributors" list.

### org_dashboard output — current vs target

| Field | Status | Layer | Step |
|-------|--------|-------|------|
| repos_tracked | ✅ | L1 | — |
| commits_24h_total | ✅ | L1 | — |
| commits_7d_total | ✅ | L1 | Step 1 ✅ |
| merged_prs_7d_total | ✅ | L1 | — |
| active_devs_total | ✅ | L1 | Step 1 ✅ |
| activity_score_total | ✅ | L1 | — |
| team_health_score | ✅ | L1 | Step 1 ✅ |
| ai_assisted_total | ✅ | L1 | Step 2 ✅ |
| ai_assisted_pct | ✅ | L1 | Step 2 ✅ |
| last_collection_ts | ✅ | L1 | — |
| trends | 🔲 | L2 | Step 3 |
| context object | 🔲 | L2 | Step 3 |

---

## Context Layer (Layer 2): Implementation

### Source 1: AI tool detection — ✅ Step 2 Done
Detects: Copilot, Claude Code, Cursor, CodeWhisperer, Aider, generic markers.

### Source 2: Industry benchmarks (`benchmarks.py`) — Step 3
DORA + CodePulse (803K+ PRs). Team-size-adjusted percentiles.

### Source 3: Benchmark lines on charts — Step 7

---

## Meaning Layer (Layer 3): Implementation

### ceo_brief — narrative intelligence (1-2x daily, pre-stored)

Reads: org_dashboard + metrics_series + latest quality_assessment + optional web search.
Generates: narrative + emergent patterns + dynamic benchmark picks + external intelligence.
Key behavior: If ai_assisted_pct rising but intelligence_score declining, warns about AI amplifying problems.
Modes: facts / balanced / speculative / investor.

### quality_analyze — deep code intelligence (weekly, pre-stored)

Reads: week's merged PRs via GitHub API → code diffs via `compare` tool.

Evaluates per repo:
- Architecture decisions, design quality, tool choices, engineering depth, flags

Evaluates per developer (within each repo):
- What did each contributor actually build this week?
- Quality and impact of their specific commits/PRs
- Who made the most impactful engineering contributions?

Produces:
- Intelligence score (0-100) per repo
- Top 3 contributors across org (with plain-English description of their best work)
- Detailed analysis stored in `quality_assessments`

---

## Customer Journey

1. Marketing page → "Start free"
2. GitHub OAuth → read-only access
3. Pick 3-5 repos
4. "Collecting first snapshot..." (30-60 seconds)
5. Dashboard with brief + velocity + benchmarks
6. One week later: intelligence score + AI patterns + top contributors
7. Developer sees their name in top 3 → motivated → tells friends
8. "Copy as investor update" → forward
9. Investor: "What tool is this?" → organic referral

---

## Build Plan (Micro-Steps)

### ✅ Completed

| Step | What | Date |
|------|------|------|
| Task 12 | Leaderboard + alerts | Done |
| Step A | PostgreSQL migration — all 14 tools, SQLite removed | 2026-03-31 |
| Step 1 | org_dashboard tiles: commits_7d, active_devs, team_health | 2026-04-05 |
| Step 2 | AI commit detection (Copilot/Claude/Cursor) in snapshots | 2026-04-05 |

### Step 3: benchmarks.py + context enrichment ← CURRENT

| Sub | What |
|-----|------|
| 3a | Create benchmarks.py with DORA + research data |
| 3b | Percentile computation functions (team-size-adjusted) |
| 3c | Add `context` object to org_dashboard output |
| 3d | Add `trends` to tiles (week-over-week deltas from snapshots) |
| 3e | Test + commit |

### Step 4: ceo_brief tool + briefs table

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
| 5b | Design quality analysis LLM prompt (include per-developer assessment) |
| 5c | Build quality_analyze (reads week's PRs + diffs) |
| 5d | LLM evaluates: architecture, design, tools, depth, flags |
| 5e | LLM evaluates: per-developer contribution quality |
| 5f | Intelligence score (0-100) per repo |
| 5g | Top 3 contributors across org |
| 5h | Store in quality_assessments |
| 5i | Wire into org_dashboard / API output |
| 5j | Update ceo_brief to reference quality + contributors |
| 5k | Test + commit |

### Step 6: FastAPI HTTP layer

| Sub | What |
|-----|------|
| 6a | FastAPI alongside MCP |
| 6b | GET /api/dashboard |
| 6c | GET /api/brief |
| 6d | POST /api/brief/regenerate |
| 6e | CORS + test + commit |

### Step 7: React Dashboard (Apple-level UX)

| Sub | What |
|-----|------|
| 7a | Vite + React + Tailwind |
| 7b | Brief card (hero, pre-loaded) |
| 7c | Tiles with benchmark lines |
| 7d | Velocity line chart (smooth curves, gradient fill, benchmark dashed line) |
| 7e | Intelligence score badge |
| 7f | Top 3 contributors card (from quality_assessments) |
| 7g | AI patterns card |
| 7h | Rule alerts bar |
| 7i | Repo cards with mini line charts + IQ badge |
| 7j | Leaderboard sidebar |
| 7k | Dark mode + responsive |
| 7l | "Copy as investor update" |
| 7m | Polish + commit |

### Step 8: V1.1 Metrics

Lead time breakdown: coding → pickup (92% of wait!) → review → deploy.
DORA 5th metric: rework rate. AI instability correlation.

| Sub | What |
|-----|------|
| 8a | PR cycle time (4 stages) |
| 8b | Time to first review (biggest bottleneck) |
| 8c | Deploy frequency proxy |
| 8d | Rework rate (DORA 5th metric) |
| 8e | AI instability correlation |
| 8f | New rule alerts: review bottleneck, large PR, rework spike |
| 8g | Add to benchmarks.py |
| 8h | Test + commit |

### Future

- **Step 9:** Linear integration (V1b)
- **Step 10:** Slack + CI/CD (V2)
- **Step 11:** DORA team archetype classification (V2)
- **Step 12:** Autonomous execution (V3)

---

## Competitive Landscape (April 2026)

| Tool | Pricing | Our edge |
|------|---------|----------|
| Jellyfish | $59/dev/mo | 5x cheaper, AI discovery, world context, intelligence score |
| LinearB | Enterprise | Brief-first, emergent patterns, quality-based dev recognition |
| Swarmia | Free → paid | Two-score system, deep code analysis, AI instability tracking |
| Allstacks | $400/dev/yr | 5 min setup, AI commit detection, pre-generated briefs |
| Faros AI | Enterprise | We're for startups; they need 1000+ engineers |
| **CEO Cockpit** | **Free → $12** | **Truth + intelligence + world context + quality recognition** |

---

## Tech Stack

- **Backend:** Python + FastAPI + FastMCP
- **Database:** PostgreSQL 16 (Docker) — 4 current + 2 planned tables
- **ORM:** SQLAlchemy 2.0
- **AI:** Model gateway — swappable LLM providers
- **Frontend:** React (Vite) — planned
- **Benchmarks:** benchmarks.py → LLM-updated → customer-aggregate

---

## What NOT to Do

- Don't put LLM in Layer 1 — deterministic foundation must stay deterministic
- Don't make the dashboard real-time — newspaper model, not live ticker
- Don't rank developers by commit counts or lines of code — gameable metrics create perverse incentives (Goodhart's Law)
- Don't show bottom performers — celebrate excellence, don't shame underperformance
- Don't hardcode all insights — let the AI discover patterns
- Don't ignore AI instability — track if AI adoption correlates with more reverts
- Don't confuse velocity (how much) with intelligence (how good)
- Don't let vision-code drift — documents must match reality at all times