"""MCP server exposing GitHub activity metrics and ledger tools.

This module is intentionally self-contained and SQLite-backed so that it can be
run as a simple local service but still behave like a miniature data plane
for a GitHub dashboard.

High level pieces:
- GitHub helpers: normalize repo identifiers and talk to the GitHub API.
- Database layer: SQLite schema for ledger state, events, tracked repos, and snapshots.
- MCP tools: small, composable endpoints that higher-level systems (LLMs, APIs, UIs)
  can call to build dashboards or workflows.
"""

import os
from typing import Any
from dotenv import load_dotenv
import httpx
from fastmcp import FastMCP
import base64
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
# --- Postgres / SQLAlchemy imports ---
from db import SessionLocal, init_db
from models import TrackedRepo, Snapshot, LedgerState, LedgerEvent


# Single MCP application instance – all tools in this file register on it.
mcp = FastMCP("GitHub Tracker (read-only)")

# Load environment variables from a local .env file (if present) and capture
# the GitHub token used for all outbound API calls.
load_dotenv()
# The GitHub token is optional but strongly recommended. Without it, most API
# calls will hit anonymous rate limits or 401s quickly.
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("WARNING: GITHUB_TOKEN not set. Put it in .env (GITHUB_TOKEN=...)")


# ---------------------------------------------------------------------------
# GitHub helper functions
# ---------------------------------------------------------------------------

def parse_repo(repo: str) -> tuple[str, str]:
    """Validate a GitHub repo string and return (owner, name).

    The expected format is 'owner/repo', for example: 'octocat/Hello-World'.
    """
    # Basic shape validation first so later code can assume a slash is present.
    if "/" not in repo:
        raise ValueError('repo must be in "owner/repo" format')

    owner, name = repo.split("/", 1)

    # Extra validation: reject "owner/" or "/repo"
    if not owner or not name:
        raise ValueError('repo must be in "owner/repo" format with both parts non-empty')

    return owner, name


async def get_default_branch(
    client: httpx.AsyncClient,
    owner: str,
    name: str,
    headers: dict,
) -> str:
    """Resolve the default branch for a repository via the GitHub REST API."""
    repo_url = f"https://api.github.com/repos/{owner}/{name}"
    resp = await client.get(repo_url, headers=headers)

    if resp.status_code != 200:
        raise ValueError(f"Cannot fetch repo metadata: status={resp.status_code} body={resp.text[:200]}")

    data = resp.json()
    return data.get("default_branch") or "main"


def repo_score(metrics: dict) -> float:
    """Compute a simple activity score from snapshot metrics.

    score = 10*merged_prs_7d + commits_24h + 0.2*commits_7d
    The exact weights are tuned for dashboards, not strict analytics.
    """
    mpr = metrics.get("merged_prs_7d", 0)
    c24 = metrics.get("commits_24h", 0)
    c7 = metrics.get("commits_7d", 0)
    return 10 * (mpr if isinstance(mpr, (int, float)) else 0) + \
           (c24 if isinstance(c24, (int, float)) else 0) + \
           0.2 * (c7 if isinstance(c7, (int, float)) else 0)


def repo_alerts(repo: str, display_name: str | None, metrics: dict) -> list[dict]:
    """Generate high-level health alerts for a single repo from metrics."""
    alerts: list[dict] = []

    days = metrics.get("days_since_last_commit", None)
    if isinstance(days, (int, float)):
        if days >= 14:
            alerts.append({
                "level": "high",
                "repo": repo,
                "display_name": display_name,
                "title": "Stale repo",
                "detail": f"No commits in {int(days)} days"
            })
        elif days >= 7:
            alerts.append({
                "level": "warn",
                "repo": repo,
                "display_name": display_name,
                "title": "Stale repo",
                "detail": f"No commits in {int(days)} days"
            })

    active = metrics.get("active_devs_7d", None)
    c7 = metrics.get("commits_7d", None)
    if isinstance(active, (int, float)) and isinstance(c7, (int, float)):
        if active <= 1 and c7 <= 2:
            alerts.append({
                "level": "warn",
                "repo": repo,
                "display_name": display_name,
                "title": "Low engagement",
                "detail": f"Only {int(active)} active dev(s) and {int(c7)} commits in 7d"
            })

    return alerts


# ---------------------------------------------------------------------------
# Database location & schema
# ---------------------------------------------------------------------------



init_db()


async def get_head_sha(
    client: httpx.AsyncClient,
    owner: str,
    name: str,
    headers: dict,
    ref: str,
) -> str:
    """Return the HEAD commit SHA for a branch / ref."""
    url = f"https://api.github.com/repos/{owner}/{name}/commits"
    resp = await client.get(url, headers=headers, params={"sha": ref, "per_page": 1})
    if resp.status_code != 200:
        raise ValueError(f"Cannot fetch head commit: status={resp.status_code} body={resp.text[:200]}")
    data = resp.json()
    return data[0]["sha"]


# ---------------------------------------------------------------------------
# MCP tools – GitHub and ledger operations
# ---------------------------------------------------------------------------

@mcp.tool()
async def ping() -> dict:
    """Cheap health-check to verify the MCP server is reachable."""
    return {"ok": True}

@mcp.tool()
async def list_commits(repo: str, branch: str = "main", limit: int = 10) -> dict:
    """
    Return the latest commits for a GitHub repo on a branch.
    repo format: "owner/name"
    """
    owner, name = parse_repo(repo)

    # Keep responses and API load sane
    if limit < 1:
        limit = 1
    if limit > 50:
        limit = 50

    url = f"https://api.github.com/repos/{owner}/{name}/commits"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    params = {"sha": branch, "per_page": limit}

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return {
            "ok": False,
            "status": response.status_code,
            "error": response.text[:500],
            "hint": "Check token permissions, repo name, or branch name.",
        }

    commits = response.json()

    simplified = []
    for item in commits:
        commit = item.get("commit", {})
        author_block = commit.get("author") or {}
        simplified.append(
            {
                "sha": item.get("sha"),
                "author": author_block.get("name"),
                "date": author_block.get("date"),
                "message": commit.get("message"),
                "html_url": item.get("html_url"),
            }
        )

    return {"ok": True, "repo": repo, "branch": branch, "commits": simplified}

@mcp.tool()
async def get_file(repo: str, path: str, ref: str | None = None, max_chars: int = 200_000) -> dict:
    """
    Read a single file (or list a directory) from a GitHub repo at a ref.
    repo: "owner/name"
    path: "folder/file.py"
    ref: branch name or commit SHA (optional; defaults to repo default branch)
    """
    owner, name = parse_repo(repo)

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        if ref is None:
            try:
                ref = await get_default_branch(client, owner, name, headers)
            except ValueError as e:
                return {"ok": False, "error": str(e), "hint": "Cannot fetch repo metadata for default branch."}

        url = f"https://api.github.com/repos/{owner}/{name}/contents/{path}"
        params = {"ref": ref}

        resp = await client.get(url, headers=headers, params=params)

    if resp.status_code != 200:
        return {
            "ok": False,
            "status": resp.status_code,
            "error": resp.text[:500],
            "hint": "Check repo/path/ref. For private repos, token permissions can also appear as 404.",
        }

    data = resp.json()

    # Directory case: GitHub returns a list of entries
    if isinstance(data, list):
        listing = [{"name": x.get("name"), "path": x.get("path"), "type": x.get("type")} for x in data]
        return {"ok": True, "repo": repo, "path": path, "ref": ref, "type": "dir", "listing": listing}

    # File case: GitHub returns an object with Base64 content
    if data.get("type") != "file":
        return {"ok": False, "repo": repo, "path": path, "ref": ref, "error": f"Unsupported type: {data.get('type')}"}

    encoding = data.get("encoding")
    content_b64 = data.get("content") or ""

    if encoding != "base64":
        return {"ok": False, "repo": repo, "path": path, "ref": ref, "error": f"Unexpected encoding: {encoding}"}

    # GitHub may include newlines in base64; remove them before decoding
    raw_bytes = base64.b64decode(content_b64.replace("\n", ""))
    text = raw_bytes.decode("utf-8", errors="replace")

    truncated = False
    if len(text) > max_chars:
        text = text[:max_chars]
        truncated = True

    return {
        "ok": True,
        "repo": repo,
        "path": path,
        "ref": ref,
        "type": "file",
        "sha": data.get("sha"),
        "size": data.get("size"),
        "truncated": truncated,
        "content": text,
        "html_url": data.get("html_url"),
        "download_url": data.get("download_url"),
    }
@mcp.tool()
async def compare(
    repo: str,
    base: str,
    head: str,
    max_patch_chars: int = 40_000,
    max_files: int = 200,
) -> dict:
    """
    Compare two refs (commit SHA / branch / tag) and summarize changes.
    base: older ref
    head: newer ref
    """
    owner, name = parse_repo(repo)

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    url = f"https://api.github.com/repos/{owner}/{name}/compare/{base}...{head}"

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(url, headers=headers)

    if resp.status_code != 200:
        return {
            "ok": False,
            "status": resp.status_code,
            "error": resp.text[:500],
            "hint": "Check repo/base/head. If repo is private, token permissions can appear as 404.",
        }

    data = resp.json()

    files = data.get("files") or []
    commits = data.get("commits") or []

    simplified_files = []
    for f in files[:max_files]:
        patch = f.get("patch")
        if patch and len(patch) > max_patch_chars:
            patch = patch[:max_patch_chars] + "\n...[patch truncated]"

        simplified_files.append(
            {
                "filename": f.get("filename"),
                "status": f.get("status"),  # added/modified/removed/renamed
                "additions": f.get("additions"),
                "deletions": f.get("deletions"),
                "changes": f.get("changes"),
                "patch": patch,  # may be None (binary/large file)
                "blob_url": f.get("blob_url"),
                "raw_url": f.get("raw_url"),
            }
        )

    simplified_commits = []
    for c in commits:
        commit = c.get("commit", {})
        author_block = (commit.get("author") or {})
        simplified_commits.append(
            {
                "sha": c.get("sha"),
                "author": author_block.get("name"),
                "date": author_block.get("date"),
                "message": commit.get("message"),
                "html_url": c.get("html_url"),
            }
        )
    merge_base = (data.get("merge_base_commit") or {}).get("sha")

    return {
        "ok": True,
        "repo": repo,
        "base": (data.get("base_commit") or {}).get("sha") or base,
        "head": head,                    # <- keep the actual head ref you compared
        "merge_base": merge_base,         # <- store merge base separately
        "status": data.get("status"),
        "ahead_by": data.get("ahead_by"),
        "behind_by": data.get("behind_by"),
        "total_commits": data.get("total_commits"),
        "files": simplified_files,
        "commits": simplified_commits,
        "html_url": data.get("html_url"),
    }

@mcp.tool()
async def ledger_get(repo: str) -> dict:
    """Fetch the current ledger state for a repository, if it exists."""
    parse_repo(repo)

    with SessionLocal() as session:
        row = session.query(LedgerState).filter_by(repo=repo).first()

    if not row:
        return {
            "ok": True,
            "repo": repo,
            "exists": False,
            "summary": "",
            "constraints": "",
            "next_steps": "",
            "last_verified_sha": None,
        }

    return {
        "ok": True,
        "repo": repo,
        "exists": True,
        "summary": row.summary,
        "constraints": row.constraints,
        "next_steps": row.next_steps,
        "last_verified_sha": row.last_verified_sha,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }

@mcp.tool()
async def ledger_set(
    repo: str,
    summary: str,
    constraints: str,
    next_steps: str,
    last_verified_sha: str | None = None,
) -> dict:
    """Upsert the ledger state for a repository."""
    parse_repo(repo)

    with SessionLocal() as session:
        existing = session.query(LedgerState).filter_by(repo=repo).first()

        if existing:
            existing.summary = summary
            existing.constraints = constraints
            existing.next_steps = next_steps
            existing.last_verified_sha = last_verified_sha
            # updated_at auto-updates via onupdate=func.now() in the model
        else:
            new_state = LedgerState(
                repo=repo,
                summary=summary,
                constraints=constraints,
                next_steps=next_steps,
                last_verified_sha=last_verified_sha,
            )
            session.add(new_state)

        session.commit()

    return {"ok": True, "repo": repo, "last_verified_sha": last_verified_sha}


@mcp.tool()
async def ledger_record_turn(repo: str, user_text: str, assistant_text: str) -> dict:
    """Append a conversation turn and record the GitHub state transition."""
    owner, name = parse_repo(repo)

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # 1) Load last_verified_sha from ledger_state
    with SessionLocal() as session:
        state = session.query(LedgerState).filter_by(repo=repo).first()
        last_verified_sha = state.last_verified_sha if state else None

    # 2) Find default branch + head sha
    async with httpx.AsyncClient(timeout=20) as client:
        default_ref = await get_default_branch(client, owner, name, headers)
        head_sha = await get_head_sha(client, owner, name, headers, default_ref)

        diff_summary = None
        base_sha = last_verified_sha

        # 3) If we have a baseline, compute diff receipts
        if last_verified_sha and last_verified_sha != head_sha:
            cmp_url = f"https://api.github.com/repos/{owner}/{name}/compare/{last_verified_sha}...{head_sha}"
            cmp_resp = await client.get(cmp_url, headers=headers)
            if cmp_resp.status_code == 200:
                cmp_data = cmp_resp.json()
                files = cmp_data.get("files") or []
                diff_summary = [
                    {
                        "filename": f.get("filename"),
                        "status": f.get("status"),
                        "additions": f.get("additions"),
                        "deletions": f.get("deletions"),
                        "changes": f.get("changes"),
                    }
                    for f in files
                ]
            else:
                diff_summary = {"error": cmp_resp.text[:300], "status": cmp_resp.status_code}

    # 4) Write event + update state in one transaction
    with SessionLocal() as session:
        # Ensure state row exists and update sha
        state = session.query(LedgerState).filter_by(repo=repo).first()
        if state:
            state.last_verified_sha = head_sha
        else:
            session.add(LedgerState(
                repo=repo,
                summary="",
                constraints="",
                next_steps="",
                last_verified_sha=head_sha,
            ))

        # Append the event
        session.add(LedgerEvent(
            repo=repo,
            user_text=user_text,
            assistant_text=assistant_text,
            head_sha=head_sha,
            base_sha=base_sha,
            diff_json=json.dumps(diff_summary) if diff_summary is not None else None,
            verification_note="GitHub head sha recorded; diff recorded when baseline existed.",
        ))

        session.commit()

    return {
        "ok": True,
        "repo": repo,
        "base_sha": base_sha,
        "head_sha": head_sha,
        "diff_recorded": diff_summary is not None,
    }



@mcp.tool()
async def repos_add(org_id: str, repo: str, display_name: str | None = None) -> dict:
    """Add or re-enable a repository in the tracked_repos table for an org."""
    parse_repo(repo)

    with SessionLocal() as session:
        # Check if this repo already exists for this org
        existing = session.query(TrackedRepo).filter_by(
            org_id=org_id,
            repo=repo,
        ).first()

        if existing:
            # Re-enable and update display name if provided
            existing.is_tracked = True
            if display_name is not None:
                existing.display_name = display_name
        else:
            # Create a brand new tracked repo
            new_repo = TrackedRepo(
                org_id=org_id,
                repo=repo,
                display_name=display_name,
                is_tracked=True,
            )
            session.add(new_repo)

        session.commit()

    return {"ok": True, "org_id": org_id, "repo": repo, "display_name": display_name}


@mcp.tool()
async def repos_list(org_id: str) -> dict:
    """List all actively tracked repositories for an org."""
    with SessionLocal() as session:
        rows = session.query(TrackedRepo).filter_by(
            org_id=org_id,
            is_tracked=True,
        ).order_by(TrackedRepo.added_at.desc()).all()

    items = [
        {
            "repo": r.repo,
            "display_name": r.display_name,
            "added_at": r.added_at.isoformat() if r.added_at else None,
        }
        for r in rows
    ]
    return {"ok": True, "org_id": org_id, "repos": items}


@mcp.tool()
async def repos_remove(org_id: str, repo: str) -> dict:
    """Soft-delete a repo from an org's tracked list (is_tracked=False)."""
    parse_repo(repo)

    with SessionLocal() as session:
        existing = session.query(TrackedRepo).filter_by(
            org_id=org_id,
            repo=repo,
        ).first()

        if existing:
            existing.is_tracked = False
            session.commit()

    return {"ok": True, "org_id": org_id, "repo": repo}


@mcp.tool()
async def snapshot_collect(repo: str) -> dict:
    """Collect and persist a fresh activity snapshot for a single repository."""
    owner, name = parse_repo(repo)

    commits_url = f"https://api.github.com/repos/{owner}/{name}/commits"
    prs_url = f"https://api.github.com/repos/{owner}/{name}/pulls"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    now = datetime.now(timezone.utc)
    since_24h = (now - timedelta(hours=24)).isoformat()
    since_7d = (now - timedelta(days=7)).isoformat()

    # --- fetch data (network) ---
    async with httpx.AsyncClient(timeout=20) as client:
        resp24 = await client.get(commits_url, headers=headers, params={"since": since_24h, "per_page": 100})
        commits24 = resp24.json()

        resp7 = await client.get(commits_url, headers=headers, params={"since": since_7d, "per_page": 100})
        commits7 = resp7.json()

        # If both windows are empty, fetch the latest commit overall (per_page=1)
        latest_commits = None
        if not commits24 and not commits7:
            resp_latest = await client.get(commits_url, headers=headers, params={"per_page": 1})
            latest_commits = resp_latest.json()

        prs_resp = await client.get(
            prs_url,
            headers=headers,
            params={"state": "closed", "sort": "updated", "direction": "desc", "per_page": 100},
        )
        prs = prs_resp.json()

    # --- commits metrics ---
    commits_24h = len(commits24) if isinstance(commits24, list) else 0
    commits_7d = len(commits7) if isinstance(commits7, list) else 0

    # --- active devs (unique authors in last 7d commits) ---
    authors = set[Any]()
    if isinstance(commits7, list):
        for item in commits7:
            gh_author = item.get("author") or {}
            login = gh_author.get("login")
            if login:
                authors.add(login)
            else:
                commit_author = ((item.get("commit") or {}).get("author") or {})
                email = commit_author.get("email")
                name_ = commit_author.get("name")
                authors.add(email or name_ or "unknown")
    active_devs_7d = len(authors)

    # --- helper: parse GitHub ISO timestamps safely ---
    def parse_github_iso(s: str) -> datetime:
        s = s.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)

    # --- last commit timestamp (24h -> 7d -> latest overall) ---
    last_commit_iso = None

    if isinstance(commits24, list) and commits24:
        c = commits24[0].get("commit") or {}
        last_commit_iso = ((c.get("committer") or {}).get("date")) or ((c.get("author") or {}).get("date"))

    elif isinstance(commits7, list) and commits7:
        c = commits7[0].get("commit") or {}
        last_commit_iso = ((c.get("committer") or {}).get("date")) or ((c.get("author") or {}).get("date"))

    elif isinstance(latest_commits, list) and latest_commits:
        c = latest_commits[0].get("commit") or {}
        last_commit_iso = ((c.get("committer") or {}).get("date")) or ((c.get("author") or {}).get("date"))

    days_since_last_commit = None
    if last_commit_iso:
        last_dt = parse_github_iso(last_commit_iso)
        days_since_last_commit = (datetime.now(timezone.utc) - last_dt).days

    # --- merged PRs in last 7 days ---
    merged_prs_7d = 0
    since_dt = parse_github_iso(since_7d)

    if isinstance(prs, list):
        for pr in prs:
            merged_at = pr.get("merged_at")
            if not merged_at:
                continue

            merged_dt = parse_github_iso(merged_at)
            if merged_dt >= since_dt:
                merged_prs_7d += 1

    # --- write snapshot ---
# --- write snapshot ---
    with SessionLocal() as session:
        # Count existing snapshots for heartbeat number
        count = session.query(Snapshot).filter_by(repo=repo).count()

        metrics = {
            "heartbeat": count + 1,
            "commits_24h": commits_24h,
            "commits_7d": commits_7d,
            "active_devs_7d": active_devs_7d,
            "days_since_last_commit": days_since_last_commit,
            "merged_prs_7d": merged_prs_7d,
        }

        new_snap = Snapshot(
            repo=repo,
            metrics_json=json.dumps(metrics),
        )
        session.add(new_snap)
        session.commit()

        # After commit, Postgres has filled in id and ts automatically
        session.refresh(new_snap)
        ts = new_snap.ts.isoformat() if new_snap.ts else None

    return {"ok": True, "repo": repo, "ts": ts, "metrics": metrics}


@mcp.tool()
async def metrics_series(repo: str, key: str, limit: int = 100) -> dict:
    """Return a time-ordered series for a single metric key for a repo."""
    parse_repo(repo)

    with SessionLocal() as session:
        rows = session.query(Snapshot).filter_by(
            repo=repo,
        ).order_by(Snapshot.id.desc()).limit(limit).all()

    # rows are newest-first; reverse to oldest-first for graphing
    rows.reverse()

    series = []
    for snap in rows:
        metrics = json.loads(snap.metrics_json)
        if key in metrics:
            series.append({
                "ts": snap.ts.isoformat() if snap.ts else None,
                "value": metrics[key],
            })

    return {"ok": True, "repo": repo, "key": key, "series": series}
    

@mcp.tool()
async def org_collect(org_id: str) -> dict:
    """Run snapshot collection for all tracked repos in an org."""
    with SessionLocal() as session:
        rows = session.query(TrackedRepo).filter_by(
            org_id=org_id,
            is_tracked=True,
        ).all()
        repos = [r.repo for r in rows]

    # Collect snapshot for each repo (calls GitHub API)
    results = []
    for repo in repos:
        out = await snapshot_collect.fn(repo=repo)
        results.append({"repo": repo, "ts": out["ts"], "metrics": out["metrics"]})

    return {"ok": True, "org_id": org_id, "repos_count": len(repos), "collected": results}


@mcp.tool()
async def org_dashboard(org_id: str, spark_points: int = 20) -> dict:
    """Assemble a dashboard-ready view for an org: tiles + per-repo data."""

    with SessionLocal() as session:
        # ── 1) Get tracked repos (control plane) ──────────────────────
        tracked = session.query(TrackedRepo).filter_by(
            org_id=org_id,
            is_tracked=True,
        ).order_by(TrackedRepo.added_at.asc()).all()

        repos = []
        commits_24h_total = 0
        commits_7d_total = 0
        merged_prs_7d_total = 0
        last_collection_ts = None
        active_devs_total = 0
        leaderboard = []
        alerts = []

        # ── 2) For each repo, load snapshots + compute ────────────────
        for tr in tracked:
            repo = tr.repo
            display_name = tr.display_name

            # Sparkline data: last N snapshots, newest-first from DB
            spark_rows = session.query(Snapshot).filter_by(
                repo=repo,
            ).order_by(Snapshot.id.desc()).limit(spark_points).all()

            spark_rows.reverse()  # oldest-first for graphing

            keys = [
                "heartbeat", "commits_24h", "commits_7d",
                "active_devs_7d", "days_since_last_commit", "merged_prs_7d",
            ]
            sparklines = {k: [] for k in keys}

            for snap in spark_rows:
                m = json.loads(snap.metrics_json)
                s_ts = snap.ts.isoformat() if snap.ts else None
                for k in keys:
                    if k in m:
                        sparklines[k].append({"ts": s_ts, "value": m[k]})

            # Latest snapshot (first element of our already-fetched list,
            # but from the UN-reversed order, so the LAST element now)
            latest = spark_rows[-1] if spark_rows else None

            if latest is None:
                repos.append({
                    "repo": repo,
                    "display_name": display_name,
                    "ts": None,
                    "metrics": {},
                    "sparklines": sparklines,
                })
                leaderboard.append({
                    "repo": repo,
                    "display_name": display_name,
                    "score": 0.0,
                })
                continue

            ts = latest.ts.isoformat() if latest.ts else None
            metrics = json.loads(latest.metrics_json)
            score = repo_score(metrics)

            leaderboard.append({
                "repo": repo,
                "display_name": display_name,
                "score": float(score),
            })
            alerts.extend(repo_alerts(repo, display_name, metrics))

            # Aggregate org-wide totals
            c24 = metrics.get("commits_24h", 0)
            if isinstance(c24, int):
                commits_24h_total += c24

            c7 = metrics.get("commits_7d", 0)
            if isinstance(c7, int):
                commits_7d_total += c7

            mpr = metrics.get("merged_prs_7d", 0)
            if isinstance(mpr, int):
                merged_prs_7d_total += mpr
            
            adev = metrics.get("active_devs_7d", 0)
            if isinstance(adev, int):
                active_devs_total += adev

            if ts and (last_collection_ts is None or ts > last_collection_ts):
                last_collection_ts = ts

            repos.append({
                "repo": repo,
                "display_name": display_name,
                "ts": ts,
                "metrics": metrics,
                "score": float(score),
                "sparklines": sparklines,
            })

        # ── 3) Build final response ───────────────────────────────────
        activity_score_total = (
            10 * merged_prs_7d_total
            + commits_24h_total
            + 0.2 * commits_7d_total
        )
        leaderboard.sort(key=lambda x: x.get("score", 0), reverse=True)

        high_count = sum(1 for a in alerts if a.get("level") == "high")
        warn_count = sum(1 for a in alerts if a.get("level") == "warn")
        team_health_score = max(0, 100 - (high_count * 25) - (warn_count * 10))

        tiles = {
            "repos_tracked": len(tracked),
            "last_collection_ts": last_collection_ts,
            "commits_24h_total": commits_24h_total,
            "commits_7d_total": commits_7d_total,
            "merged_prs_7d_total": merged_prs_7d_total,
            "active_devs_total": active_devs_total,
            "activity_score_total": activity_score_total,
            "team_health_score": team_health_score,
        }

        return {
            "ok": True,
            "org_id": org_id,
            "tiles": tiles,
            "repos": repos,
            "leaderboard": leaderboard,
            "alerts": alerts,
        }

if __name__ == "__main__":
    # SSE is the classic HTTP transport for MCP servers
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
