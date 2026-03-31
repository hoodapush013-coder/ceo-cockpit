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
This layer has TWO modes:

**Narrative mode** — LLM reads truth + context and generates a weekly brief. Every claim cites its source. Speculation is labeled. Three modes: facts / balanced / speculative. Plus investor update mode.

**Discovery mode** — LLM receives the FULL time-series history (12+ weeks of snapshots, day-of-week distributions, PR size distributions, cross-repo correlations) and discovers patterns nobody programmed:
- "Your commit velocity drops 35% every Thursday — consider moving reviews to Wednesday"
- "Every time auth-service goes quiet for 7+ days, the next PR averages 900+ lines"
- "PRs under 200 lines get reviewed 3x faster on your team"
- "frontend-app and backend-api always slow down together — possible hidden dependency"
- "Your Copilot adoption jumped from 22% to 38% in 6 weeks — teams on this curve reach 50% within 4 more weeks"

These are NOT hardcoded rules. The AI finds them by analyzing patterns in the data. The insights evolve every week as new data accumulates. This is the feature that makes customers say "how did it know that?"

**Dynamic benchmark selection** — The LLM also decides WHICH benchmarks are most relevant this week. If review speed is the bottleneck, it highlights review benchmarks. If everything is healthy, it highlights growth opportunities. The context panel adapts to what matters most RIGHT NOW, not a static set of comparisons.

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
| External signals | None | Framework releases, industry trends |
| Setup | Days to weeks | 5 minutes |
| Pricing | $59/dev/mo+ | Free → $12/dev/mo |
| Team size | 50+ engineers | 4-25 engineers |
| Surveillance | Often individual metrics | Never. Team-level only. |

---

## Dashboard Design

### Design philosophy: Apple-level useful beauty

Apple products are beautiful because they remove everything unnecessary and make what remains feel alive. Our dashboard follows the same principle:

- **No chart for the sake of charts.** Every visualization earns its place by answering a specific question.
- **Smooth line charts over bar charts.** Lines show trends and trajectories — bars show isolated snapshots. A founder cares about trajectory.
- **Generous whitespace.** Information density without visual noise. Every element breathes.
- **Subtle motion.** Hover states reveal detail. Transitions feel natural, never jarring.
- **Typography that breathes.** Tight letter-spacing on headlines (-0.3px). Generous line-height on brief text (1.8). Two weights only: regular and medium.
- **Dark mode by default.** CEO-grade aesthetic. Professional, not playful.

### Visual hierarchy (top to bottom)

**1. AI brief card (hero — top of screen, ~35% of above-fold)**

Bordered card with left accent bar. Contains the weekly narrative integrating all four layers. Includes two special tag types:

- `AI DISCOVERED` — emergent insights the AI found in the time-series data (not hardcoded rules)
- `WORLD` — external intelligence from framework releases, industry trends, AI tool updates

Three buttons: "Copy as investor update" / "Regenerate" / "Full brief"

Data flow: `ceo_brief()` → `org_dashboard()` data + `metrics_series()` history + web search → LLM → narrative + discovered patterns + priority benchmarks

**2. Status tiles (4 metric cards with benchmark context)**

| Tile | Example | Benchmark |
|------|---------|-----------|
| Commits (7d) | 47 ↑18% | "Top 25% for 6-person teams" |
| PRs merged (7d) | 8 ↑3 | "Median: 5 for your size" |
| AI-assisted code | 38% ↑5% | "Industry avg: 30%" |
| Team health | 82/100 | "2 alerts active" |

Each tile: large value, week-over-week delta, one-line benchmark in muted text.

**3. Velocity chart (smooth line chart — the "heartbeat")**

12-week line chart of commit activity with gradient fill under the curve. Switchable between commits, PRs merged, and activity score. This is the chart a founder screenshots and sends to their investors. It must be beautiful.

Design spec:
- `tension: 0.4` for smooth curves (not angular)
- Gradient fill from line color to transparent
- No point markers (clean line) — points appear on hover
- Minimal grid lines (y-axis only, very subtle)
- Pill-style toggle for switching metrics (not tabs, not dropdown)

**4. AI-discovered patterns card**

Dedicated card for emergent insights. Each insight has:
- Color dot: green (positive pattern), amber (risk), blue (neutral/trend)
- Plain English description of what the AI found
- Tag: `Pattern` / `Risk` / `Trend`

This card is NOT hardcoded. The LLM generates these insights fresh each week by analyzing the full time-series. Some weeks there might be 2 insights, some weeks 5. The card adapts.

**5. Alerts (conditional — only when alerts exist)**

Color-coded banners with benchmark-enriched context:
- "auth-service: No commits in 12 days (industry benchmark: stale after 7)"
- "data-pipeline: 1 active dev — single-owner risk (high-performing teams avg 3+)"

**6. Repo cards (left ~70%) + Leaderboard (right sidebar ~30%)**

Each repo card:
- Name + health pill (green/amber/red with score)
- Smooth mini line chart (12 data points, no axes, just the curve) — color indicates health
- One-line stats: commits, PRs, devs, last activity
- Click to expand: full metrics, per-metric line charts, recent PR list, AI insight if applicable

Leaderboard: repos ranked by score with visual bars. Provides context for individual scores.

### Complete data flow map

```
Dashboard element         → HTTP endpoint       → MCP tools                    → Sources
───────────────────────────────────────────────────────────────────────────────────────────
AI brief + discovered     → GET /api/brief       → ceo_brief()                  → org_dashboard + metrics_series + web_search + LLM
Investor update           → POST /api/brief      → ceo_brief(mode=investor)     → org_dashboard + LLM
Status tiles + benchmarks → GET /api/dashboard   → org_dashboard()              → tracked_repos + snapshots + benchmarks.py
Velocity chart            → GET /api/dashboard   → org_dashboard()              → snapshots (sparklines data)
AI patterns card          → GET /api/brief       → ceo_brief()                  → Full time-series + LLM discovery
Dynamic context panel     → GET /api/brief       → ceo_brief()                  → LLM picks priority benchmarks
Alerts                    → GET /api/dashboard   → org_dashboard()              → tracked_repos + snapshots + benchmarks.py
Repo cards + mini charts  → GET /api/dashboard   → org_dashboard()              → tracked_repos + snapshots
Leaderboard               → GET /api/dashboard   → org_dashboard()              → tracked_repos + snapshots
```

Key principle: `org_dashboard` provides the truth + context data. `ceo_brief` adds meaning + discovery. The React dashboard calls BOTH endpoints and assembles the view.

### Dashboard UX rules
- No configuration. Opinions over options.
- Glanceable in 5 seconds. Brief → tiles → alerts → done.
- Dark mode by default. Toggle available.
- Mobile-responsive. Brief + tiles stack single-column.
- Stale data warnings: yellow >1h, red >24h.
- Every chart is a smooth line, not a bar chart (trajectory over snapshot).
- No chart without a purpose. If removing a chart doesn't lose information, remove it.

---

## Context Layer: Implementation

### Source 1: AI tool detection (from commit metadata)
GitHub Copilot adds `Co-authored-by: copilot`. Cursor leaves similar patterns. Detect in `snapshot_collect` by scanning commit trailers. New metric: `ai_assisted_commits_7d`. Zero new API calls.

### Source 2: Industry benchmarks (`benchmarks.py`)
Hardcoded from DORA, CodePulse (803K+ PRs), and research. Structured for easy updates. `org_dashboard` compares team metrics against these and returns percentile rankings.

Later: benchmarks fetched from web source or computed from anonymized CEO Cockpit customer data.

### Source 3: External intelligence (web search in `ceo_brief`)
Brief generation optionally searches for framework releases, AI tool updates, industry trends relevant to team's tech stack. One nugget woven into brief, always tagged as external.

### Source 4: Emergent pattern discovery (LLM on time-series)
`ceo_brief` sends full 12-week time-series + day-of-week distributions + PR size data to LLM with prompt: "Discover patterns, correlations, anomalies. Label each as Pattern, Risk, or Trend." LLM returns structured insights. These power the "AI-discovered patterns" card on the dashboard.

### Dynamic benchmark selection
Same `ceo_brief` call. LLM receives all available benchmarks but prompt says: "Pick the 2-3 most important comparisons to highlight this week based on what the data shows." Returns `priority_benchmarks` array used by the context panel.

---

## Customer Journey

1. Land on marketing page → "Start free"
2. GitHub OAuth → read-only access
3. Pick 3-5 repos → checkboxes
4. "Collecting first snapshot..." → 30-60 seconds
5. Dashboard with brief + benchmarks + first AI insight
6. "How did it know our Thursday pattern?" → hooked
7. "Copy as investor update" → forward to investors
8. Investor: "What tool is this?" → organic referral
9. Growth flywheel

Steps 1-5: under 5 minutes.

---

## V1 — Startup Execution Console

### V1a — GitHub-first

| Feature | Description |
|---------|-------------|
| Repo tracking | Time-series snapshots of GitHub activity |
| Health scores | Transparent formula + team health aggregate |
| Alerts | Stale repos, low engagement — with benchmark context |
| AI detection | Copilot/Cursor commit scanning |
| Benchmarks | Industry percentile comparisons |
| AI brief | Weekly narrative with discovered patterns + external intelligence |
| Investor update | One-click reformatted brief for investors |
| Dashboard | Brief-first layout with line charts and context panel |

### V1b — Add Linear
Milestones as primary object. Cross-system risk detection.

### V1 Metrics

| Metric | Benchmark | Step |
|--------|-----------|------|
| Commits (24h, 7d) | Per-dev percentiles by team size | ✅ Done |
| Active developers | Healthy: 3+/repo | ✅ Done |
| Merged PRs (7d) | Per-dev percentiles | ✅ Done |
| Days since last commit | Stale: 7d warn, 14d high | ✅ Done |
| Activity score | — | ✅ Done |
| AI-assisted commits | Industry avg 30%, top 55%+ | Step A.5 |
| Team health score | From alert counts | Step B.5 |
| Benchmark percentiles | DORA + research | Step B.5 |
| Emergent patterns | LLM discovery | Step B |
| PR cycle time | Median 3h reviewed | Step D |
| Time to first review | Median 4h | Step D |

---

## V2 — Execution Workflows
Slack + CI/CD. Workflow actions. Dependency maps. Dynamic benchmarks from customer aggregate data. Predictive patterns.

## V3 — Intelligent Automation
Persistent context graph. Bounded autonomy. Slip simulation. Decision memory. "Teams like yours typically hit PMF 40% faster at this velocity."

---

## Code Impact Analysis

### New file: `benchmarks.py`
Industry data from DORA/research. Percentile computation functions. Team-size-adjusted comparisons.

### Modified: `snapshot_collect` (server.py)
Add AI commit detection: scan trailers for Copilot/Cursor patterns. Store `ai_assisted_commits` in `metrics_json`. Zero new API calls.

### Modified: `org_dashboard` (server.py)
Import `benchmarks.py`. Compute percentile rankings. Add `context` object and `ai_assisted_pct` to output. Add `team_health_score` and `trends`.

### New tool: `ceo_brief` (server.py)
Calls `org_dashboard()` for truth+context. Calls `metrics_series()` for full time-series. Optional web search for external intelligence. Feeds everything to LLM with discovery prompt. Returns: narrative + discovered_patterns + priority_benchmarks. Four modes: facts / balanced / speculative / investor.

### No changes needed: `models.py`, `db.py` (metrics_json already stores JSON; new fields go inside it)

### New: FastAPI layer (Step C)
HTTP endpoints (`/api/dashboard`, `/api/brief`) that call MCP tools and serve React frontend.

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

## What NOT to Do

- Don't hardcode all insights — let the AI discover patterns
- Don't show all benchmarks equally — let the AI pick what matters this week
- Don't use bar charts when line charts tell the story better
- Don't build 30 metrics — start with 8 + emergent discovery
- Don't show individual developer rankings — ever
- Don't make setup take more than 5 minutes
- Don't build a dashboard and call it done — the intelligence is the product

---

## Build Phases

### V1a — GitHub-first

| Step | What | Status |
|------|------|--------|
| Task 12 | Leaderboard + alerts | ✅ Done |
| Step A | PostgreSQL migration | 🔧 org_dashboard remaining |
| Step A.5 | AI commit detection in snapshot_collect | 🔲 |
| Step B | ceo_brief: narrative + discovery + investor mode | 🔲 |
| Step B.5 | benchmarks.py + org_dashboard context enrichment | 🔲 |
| Step C | React Dashboard (brief-first + line charts + patterns card) | 🔲 |
| Step D | V1.1 Metrics (PR cycle time, review speed, DORA) | 🔲 |