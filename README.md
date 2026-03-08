# githubsss

Small Python MCP server (SSE transport) for tracking GitHub repo activity.

## Setup (uv)

1) Install `uv`

- macOS (Homebrew):

```bash
brew install uv
```

- or official installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2) Create a virtualenv + install deps (this creates `uv.lock`)

```bash
uv venv
uv sync
```

3) Set your GitHub token

Create a `.env` file:

```bash
GITHUB_TOKEN=ghp_...
```

4) Run

```bash
uv run python server.py
```

