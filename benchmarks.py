"""
benchmarks.py — Industry benchmark data and percentile comparison engine.

Layer 2 (Context): deterministic at runtime, no LLM.

Data sources:
  - DORA 2025 (5,000 professionals)
  - CodePulse 803K+ merged PR study
  - LinearB 2026 Benchmarks (8.1M PRs, 4,800 teams, 42 countries)

Last updated: 2026-04-05
"""

BENCHMARKS = {
    "commits_7d": {
        "per_dev": True,
        "distribution": {"p25": 3, "p50": 6, "p75": 10, "p90": 16},
        "unit": "commits/dev/week",
    },
    "merged_prs_7d": {
        "per_dev": True,
        "distribution": {"p25": 0.5, "p50": 1.0, "p75": 2.0, "p90": 3.5},
        "unit": "PRs/dev/week",
    },
    "ai_assisted_pct": {
        "per_dev": False,
        "distribution": {"p25": 8, "p50": 22, "p75": 38, "p90": 55},
        "unit": "%",
    },
}


def get_percentile(metric_name: str, total_value: float, num_devs: int = 1) -> dict:
    """Compare a metric value against industry benchmarks."""
    if metric_name not in BENCHMARKS:
        return None

    bench = BENCHMARKS[metric_name]
    dist = bench["distribution"]
    unit = bench["unit"]

    if bench["per_dev"]:
        per_dev = round(total_value / max(num_devs, 1), 1)
    else:
        per_dev = round(total_value, 1)

    if per_dev >= dist["p90"]:
        percentile = 90
        label = "Top 10%"
    elif per_dev >= dist["p75"]:
        percentile = 75
        label = "Top 25%"
    elif per_dev >= dist["p50"]:
        percentile = 50
        label = "Above median"
    elif per_dev >= dist["p25"]:
        percentile = 25
        label = "Below median"
    else:
        percentile = 10
        label = "Bottom 25%"

    median = dist["p50"]
    detail = f"{per_dev} {unit} (median: {median})"

    return {
        "metric": metric_name,
        "raw_value": total_value,
        "per_dev_value": per_dev,
        "percentile": percentile,
        "label": label,
        "detail": detail,
        "median": median,
    }


def get_all_benchmarks(
    commits_7d: int,
    merged_prs_7d: int,
    ai_assisted_pct: float,
    num_devs: int,
) -> dict:
    """Compute benchmarks for all tracked metrics at once."""
    return {
        "commits_7d": get_percentile("commits_7d", commits_7d, num_devs),
        "merged_prs_7d": get_percentile("merged_prs_7d", merged_prs_7d, num_devs),
        "ai_assisted_pct": get_percentile("ai_assisted_pct", ai_assisted_pct, 1),
    }