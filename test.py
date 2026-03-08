import asyncio
import os
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import SSETransport


def _as_names(tools: Any) -> list[str]:
    """
    list_tools() returns tool objects; this makes printing robust across versions.
    """
    names: list[str] = []
    for t in tools:
        # most versions expose .name
        n = getattr(t, "name", None)
        if isinstance(n, str):
            names.append(n)
        else:
            names.append(str(t))
    return names


def _print_result(label: str, result: Any) -> None:
    """
    FastMCP call_tool returns a CallToolResult with:
      - .is_error
      - .data  (best: hydrated structured result)
      - .structured_content (raw structured JSON)
      - .content (text blocks, etc.)
    We'll print the most useful parts.
    """
    is_error = getattr(result, "is_error", False)
    data = getattr(result, "data", None)
    structured = getattr(result, "structured_content", None)

    print(f"\n--- {label} ---")
    print("is_error:", is_error)

    if data is not None:
        print("data:", data)
        return

    if structured is not None:
        print("structured_content:", structured)
        return

    # Fallback: print content blocks (usually text)
    content = getattr(result, "content", None)
    print("content:", content)


async def main():
    # Your server is started with: mcp.run(transport="sse", host="127.0.0.1", port=8000)
    # FastMCP SSE transport expects the /sse endpoint by convention.
    # Change this if your server is mounted elsewhere.
    url = os.environ.get("MCP_SSE_URL", "http://127.0.0.1:8000/sse")
    org_id = os.environ.get("ORG_ID", "demo-org")

    # Optional: set repos to track via env, e.g.
    # export SAMPLE_REPOS="octocat/Hello-World:Hello,psf/requests:Requests"
    raw = os.environ.get("SAMPLE_REPOS", "").strip()
    sample_repos: list[tuple[str, str | None]] = []
    if raw:
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            if ":" in part:
                repo, display = part.split(":", 1)
                sample_repos.append((repo.strip(), display.strip() or None))
            else:
                sample_repos.append((part, None))

    transport = SSETransport(url=url)
    async with Client(transport) as client:
        # 0) sanity: list tools
        tools = await client.list_tools()
        tool_names = _as_names(tools)
        print("Connected to:", url)
        print("Tools:", tool_names)

        # 1) (optional) add repos
        if sample_repos:
            for repo, display_name in sample_repos:
                r = await client.call_tool(
                    "repos_add",
                    {"org_id": org_id, "repo": repo, "display_name": display_name},
                )
                _print_result(f"repos_add {repo}", r)

        # 2) list repos
        r = await client.call_tool("repos_list", {"org_id": org_id})
        _print_result("repos_list", r)

        # 3) collect snapshots (requires your GitHub token/env to be set on the server side)
        r = await client.call_tool("org_collect", {"org_id": org_id})
        _print_result("org_collect", r)

        # 4) dashboard
        r = await client.call_tool("org_dashboard", {"org_id": org_id, "spark_points": 20})
        _print_result("org_dashboard", r)

        dash = getattr(r, "data", None) or getattr(r, "structured_content", None) or {}
        if isinstance(dash, dict):
            print("\nDASH KEYS:", list(dash.keys()))
            print("LEADERBOARD size:", len(dash.get("leaderboard", [])))
            print("ALERTS size:", len(dash.get("alerts", [])))

            # Optional: show top 3 leaderboard rows
            lb = dash.get("leaderboard", [])
            if isinstance(lb, list) and lb:
                print("\nTop leaderboard rows:")
                for row in lb[:3]:
                    print(row)

            al = dash.get("alerts", [])
            if isinstance(al, list) and al:
                print("\nAlerts:")
                for a in al:
                    print(a)


if __name__ == "__main__":
    asyncio.run(main())