#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

python3 -m venv .venv
.venv/bin/python -m pip install -e './apps/api[dev]'
npm --prefix apps/web ci

if ! command -v docker >/dev/null 2>&1; then
  echo 'Docker is required for the local PostgreSQL service.' >&2
  exit 1
fi
docker compose -f infra/compose.yaml up -d --wait db
.venv/bin/alembic -c apps/api/alembic.ini upgrade head

echo 'Web: http://localhost:5173 | API: http://localhost:8000/api/v1/health'
.venv/bin/uvicorn gaitmate_api.main:app --reload --host 127.0.0.1 --port 8000 &
api_pid=$!
trap 'kill "$api_pid" 2>/dev/null || true' EXIT
npm --prefix apps/web run dev

