# PR Engine

A single-athlete training API: FastAPI + SQLite, with an MCP server for the
planning client.

## Requirements

- Python 3.12 (pinned in `.python-version`)
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
cp .env.example .env   # then set PRENGINE_TOKEN
```

`PRENGINE_TOKEN` is required. Without it the app refuses to start rather than
serving `/api` unauthenticated.

## Run

```bash
uv run uvicorn app.main:app --reload
```

- `GET /health` — open, returns `{"status":"ok"}`
- `GET /api/*` — requires `Authorization: Bearer $PRENGINE_TOKEN`

## Tests

```bash
uv run pytest
```

## Migrations

Alembic is initialized with no migrations yet (tables land in #1).

```bash
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "..."
```
