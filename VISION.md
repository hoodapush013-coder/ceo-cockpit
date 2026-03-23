# CEO Cockpit — Product Vision

> **"A Startup Execution Console, not a dashboard."**

---

## The Shape of the Product

1. **Connect roadmap to code movement.** Know which milestones relate to which PRs, commits, reviews, and releases.
2. **Detect execution risk.** Not vanity metrics — real things: stalled milestones, oversized PRs on critical work, dependency bottlenecks, review delays, "looks active but not converging."
3. **Summarize risk in business language.** Not "PR cycle time went up 14%." More like: "Onboarding launch is likely to slip because auth refactor is still under review and two dependent issues have not started."
4. **Recommend next actions.** This is where it stops being a dashboard and becomes an operating system.
5. **Automate low-risk coordination.** Less Slack archaeology, fewer standups, less manual status reporting.

---

## V1 — Startup Execution Console

**Customer:** Startup with 4–25 engineers, using GitHub and usually Linear, shipping fast, living in mild execution chaos.

**What it does:**

- Connects GitHub and Linear
- Shows milestones/projects as the main object (not repos)
- Tells the team: what's on track, what's drifting, what's blocked, what needs a decision

**High-signal risk detection:**

- Critical PR stuck in review
- Milestone with issue churn but weak code progress
- Single-owner dependency risk
- Large risky PR tied to launch work
- Unstarted dependent issues
- Review latency on critical path

**Weekly founder/CTO brief:**

- What shipped last week
- What slipped
- What is likely to slip next
- Top blockers
- Decisions needed

**One-click drill-down:** milestone → issues → PRs → commits → owners

**Release/launch-readiness summary** for important milestones.

**Value:** Clarity and earlier intervention.

---

## V2 — Execution Workflows

The product starts helping teams **act**, not just see.

- Add Slack and CI/CD signals
- Workflow actions: draft follow-up issues, suggest reviewers, flag scope cuts, post risk summaries to Slack, generate release notes, generate weekly investor/founder updates
- Dependency maps across issues, PRs, repos
- Launch-readiness workflows: what's merged, pending, risky, deferrable, needs sign-off
- Learn team patterns: which teams merge fast, where reviews stall, which launches slip

**Value:** Less management toil. Fewer avoidable misses.

---

## V3 — Autonomous Execution Layer

- Persistent context graph: projects, milestones, issues, PRs, commits, owners, reviews, releases, incidents, Slack decisions, past outcomes
- From "risk warning" to "execution copilot with bounded autonomy"
- Replan milestones, propose staffing changes, auto-open follow-up issues, assemble launch rooms, surface cross-project conflicts, simulate slip scenarios
- Long-running memory of why decisions were made

**Value:** Execution leverage. An engineering chief-of-staff system.

---

## The Clean Product Staircase

- **V1:** See the real state of execution
- **V2:** Drive the next action in the workflow
- **V3:** Run bounded parts of execution automatically

---

## Tech Stack

- **Frontend:** React (Vite), evolve to Next.js if needed
- **Backend:** Python + FastAPI (also MCP for AI tool layer)
- **Database:** Postgres (the brain — relationships are the core asset)
- **Cache/Queue:** Redis
- **Ingestion:** GitHub webhooks + APIs, Linear APIs/webhooks
- **AI:** Model gateway approach — swappable providers, cheap model for classification, stronger model for reasoning
- **Search:** Postgres full-text first, vector layer only when needed
- **Auth:** OAuth with GitHub, workspace-level tenancy
- **Deployment:** Managed cloud (managed Postgres, managed Redis, containerized API/workers)

---

## What to Automate First

Not coding. The ugly coordination tasks:

- Weekly engineering status synthesis
- Milestone risk summaries
- Release readiness summaries
- Follow-up issue drafting
- Review bottleneck detection
- Dependency visibility
- Slack nudges for important blockers
- Founder/CTO weekly brief generation

---

## What NOT to Do

- Don't make V1 a generic "engineering analytics suite"
- Don't stuff it with 30 metrics
- Don't make it feel like employee surveillance
- Don't try to support every tool immediately
- Don't start with enterprise permissions and consultancy sludge
- Don't build "AI chat with GitHub" and pretend it's a company

---

## Build Phases (Current Plan)

### V1a — GitHub-first (current milestone)

| Step | What | Status |
|------|------|--------|
| Task 12 | Leaderboard + alerts | ✅ Done |
| Step A | PostgreSQL migration | 🔲 Next |
| Step B | LLM Analyst (founder brief) | 🔲 |
| Step C | React Dashboard (execution-focused) | 🔲 |

### V1b — Add Linear

- Linear API integration
- Milestones as main object
- Issue → PR linking
- Risk detection across both systems

### V2 — Execution Workflows

- Slack + CI/CD integration
- Workflow actions
- Dependency maps
- Team pattern learning

### V3 — Autonomous Execution

- Context graph
- Bounded autonomy
- Scenario simulation
- Long-running decision memory
