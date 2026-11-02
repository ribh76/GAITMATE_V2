# Local development and secrets

Run `./scripts/bootstrap.sh` from the repository root. It creates `.env`, installs
Python and frontend dependencies, starts PostgreSQL in Docker, then starts the API
and Vite. Prerequisites: Python 3.11+, Node 20.19+ or 22.12+, npm, and Docker Compose.
Use Ctrl-C to stop both app servers; `docker compose -f infra/compose.yaml down`
stops the database. Its named volume persists between runs.

The values in `.env.example` are development-only defaults. `.env` is ignored by Git.
Never place real patient data, production credentials, or tokens in this repo or in
`VITE_` variables: Vite embeds those variables in browser assets. Set production
secrets through the deployment platform's secret manager. Rotate any secret that
is accidentally committed.

The API reads `DATABASE_URL`, but does not yet create tables or query the database;
schema and migrations belong to the next phase. All API timestamps use UTC. Routes
begin with `/api/v1`; successful responses use a `data` envelope. FastAPI's standard
validation error format remains in use until domain error contracts are introduced.
Python's standard logging should be used for new API modules without recording
credentials or health-like message bodies.

Checks:

```sh
.venv/bin/ruff check apps/api
.venv/bin/ruff format --check apps/api
.venv/bin/mypy apps/api/src
.venv/bin/pytest apps/api/tests
npm --prefix apps/web run lint
npm --prefix apps/web run format
npm --prefix apps/web run typecheck
npm --prefix apps/web test
npm --prefix apps/web run build
```

