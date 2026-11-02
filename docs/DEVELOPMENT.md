# Local development and secrets

Run `./scripts/bootstrap.sh` from the repository root. It creates `.env`, installs
Python and frontend dependencies, starts PostgreSQL in Docker, then starts the API
and Vite on the host. Prerequisites: Python 3.11+, Node 20.19+ or 22.12+, npm,
and Docker Compose. Use Ctrl-C to stop both app servers;
`docker compose -f infra/compose.yaml down` stops the database. Its named volume
persists between runs. Frontend edits use Vite on the host; no container rebuild
is needed.

To run only PostgreSQL in Docker, use
`docker compose -f infra/compose.yaml up -d --wait db`. To run PostgreSQL and a
production-style API container instead of local Uvicorn, use
`docker compose -f infra/compose.yaml --profile api up -d --build --wait` and run
`npm --prefix apps/web run dev` separately. Stop the stack with
`docker compose -f infra/compose.yaml --profile api down`. Do not run the API
container and local Uvicorn at the same time; both use port 8000.

The values in `.env.example` are development-only defaults. `.env` is ignored by Git.
Never place real patient data, production credentials, or tokens in this repo or in
`VITE_` variables: Vite embeds those variables in browser assets. Set production
secrets through the deployment platform's secret manager. Rotate any secret that
is accidentally committed.

The API reads `DATABASE_URL` and the bootstrap script applies the initial
Alembic migration. The health endpoint does not query tables; application data
services are future work. See [data model](DATA_MODEL.md) for ownership and
migration commands, and [API conventions](API_CONVENTIONS.md) for versioning,
response and error envelopes, UTC timestamps, and logging rules.

Checks:

```sh
.venv/bin/ruff check apps/api
.venv/bin/ruff format --check apps/api
.venv/bin/mypy apps/api/src
.venv/bin/pytest apps/api/tests
.venv/bin/alembic -c apps/api/alembic.ini check
npm --prefix apps/web run lint
npm --prefix apps/web run format
npm --prefix apps/web run typecheck
npm --prefix apps/web test
npm --prefix apps/web run build
```

