# Repository Guidelines

## Project Structure & Module Organization
- Backend: `backend/app/` (FastAPI). Entry points by stage: `main.py` (simple), `main_stage4.py` (full). Domain modules live alongside (`sel_service.py`, `analytics_service.py`, etc.).
- Tests: `backend/tests/` with `unit/` and `integration/`. Ad‑hoc quick tests at `backend/test_*.py`.
- Frontend: `frontend/` static HTML + i18n JSON in `frontend/locales/`.
- Ops: `Makefile`, `docker-compose*.yml`, `scripts/` (CLI, secrets, DB init), `monitoring/`, `traefik/`, `docs/`.

## Build, Test, and Development Commands
- `make start` — start stack via Docker Compose (Traefik, backend, frontend, DB, etc.).
- `make dev` — spin up infra; run backend locally with your IDE/uvicorn.
- `make test` | `make test-unit` | `make test-integration` — run pytest (installs test deps in container).
- Local (no Docker): `scripts/run-tests-local.sh [unit|simple|coverage]` inside a venv.
- Logs and health: `make logs`, `make logs-backend`, `make health`.

Tip: Makefile targets use `docker-compose.stage4.yml`. For production with HTTPS, prefer `docker-compose.traefik.yml` (see `CLAUDE.md`). Otherwise, you can run `docker compose -f <file> up -d` with the file that matches your context.

## Coding Style & Naming Conventions
- Python: 4‑space indent; snake_case for files, functions, variables; PascalCase for classes.
- Formatters/linters: Black, isort, flake8. Run `make format` then `make lint` before PRs.
- Tests: name `test_*.py`; keep unit tests fast and isolated.

## Testing Guidelines
- Framework: `pytest` with markers (`unit`, `integration`, `auth`, `sel`, etc.).
- Coverage: enforced ≥ 80% (see `backend/pytest.ini`). Generate HTML via `make test-coverage` or `scripts/run-tests-local.sh coverage`.
- DB: integration tests use ephemeral SQLite/Postgres per configuration; avoid relying on preexisting data.

## Commit & Pull Request Guidelines
- Commits: follow Conventional Commits (e.g., `feat: ...`, `fix: ...`, `refactor: ...`). Keep messages imperative and scoped.
- PRs: include a clear description, linked issues, screenshots for UI changes, and test notes. Ensure CI passes and no `make lint` errors.

## Security & Configuration
- Configuration: copy `.env.example` to `.env` for local use. Do not commit secrets; real secrets live in `secrets/` and are generated via `scripts/generate-secrets.sh`.
- JWT/DB/Redis/MinIO are configured via env or Docker secrets; see `docs/` for details.

## Architecture Overview (Stages)
- Stage 0: Minimal auth/profiles (SQLite). Entry: `backend/app/main.py`.
- Stage 1–2: +SEL, +Messaging/Events (PostgreSQL, Redis, WebSockets).
- Stage 3–4: +Shop/Education, +Multilingual/Analytics (MinIO, monitoring). Entry: `backend/app/main_stage4.py` at `/api`.

## Agent‑Specific Instructions
- Simplicity first; preserve backward compatibility between stages.
- Prefer `docker-compose.traefik.yml` for real deployments; use `.env.example` as the baseline. Never commit secrets.
- Follow Belgian context (classes M1–M3, P1–P6) and GDPR basics.
- Before PRs: run `make format`, `make lint`, and appropriate `make test-*` targets; attach notes/screenshots when UI changes.
