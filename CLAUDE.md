# system-design-interview-python

Interview reference boilerplate: Django REST backend + React/TypeScript/Tailwind frontend. Local only. Keep it small and readable: it is a reference to copy patterns from, not a product.

## Layout
- `backend/` — Django. Python in `backend/.venv`.
  - `config/` settings, root urls, wsgi/asgi
  - `user/` the only module: `models.py`, `dto/`, `services.py`, `views.py`, `urls.py`, `migrations/`
  - `utils/` env, exceptions, exception handler, DTO validator, pagination, enum field, `redis_client.py`
  - `middlewares/` JWT auth, CSRF exempt, request logging
  - `decorators/` `is_public`, `roles`
  - `dto/` DTOs shared across modules
  - `tests/` mirrors the source layout (`tests/user/test_user_service.py`)
- `frontend/` — Vite + React + TypeScript + Tailwind v4, one empty page. Package manager: npm.
- Startup scripts live outside the repo, in the parent workspace folder: `scripts/` and `start.sh`. Logs go to `logs/` there.

## Ports
Postgres 21010, Redis 21011, backend 21012, frontend 21013. Check `ss -tlnH` before picking a new port and keep them in this 2101x block.

## Run
- Everything: from the workspace folder (parent of this repo), `bash scripts/start-all.sh`. Install packages and create the `.env` files first (see README); the scripts do not do first-time setup.
- Docker (`backend/docker-compose.yml`) runs only Postgres and Redis. Backend and frontend run on the host.
- Migrations are never run automatically. After a fresh DB or a pull with new migrations, run `cd backend && .venv/bin/python manage.py migrate`.
- Unit tests (service layer only): `cd backend && .venv/bin/pytest`
- Frontend: `npm run dev`, `npm run build`, `npm run lint` in `frontend/`.
- Config lives in `backend/.env` and `frontend/.env` (gitignored). Add every new variable to the matching `.env.example` and read it with `get_env` (fails fast when missing).

## Backend conventions
- 2-space indent, single quotes, type hints on new function signatures.
- Layering: DTO (DRF serializer) validates input -> service holds all logic and DB access -> view stays thin (validate, call service, return `Response`). No ORM calls in views.
- Validate with `DTOValidator.validate(Dto, data)`; it raises `BadRequestException` with field errors.
- Raise exceptions from `utils/exceptions.py` (`NotFoundException`, `ConflictException`, `UnauthorizedException`, `ForbiddenException`, `BadRequestException`). Never return error responses by hand. The handler formats everything as `{message, error?}`.
- Routes: `/api/<plural>` with no trailing slash (`APPEND_SLASH = False`). Register each app in `INSTALLED_APPS` and mount it in `config/urls.py`.
- Auth: every route needs `Authorization: Bearer <jwt>` unless the view has `@is_public` (placed above `@api_view`). The middleware exposes the payload as `request.jwt_user`. `@roles([UserRole.ADMIN])` goes below `@api_view` so DRF turns the exception into a response.
- Never return password hashes. Return explicit field lists (`PUBLIC_FIELDS` in `user/services.py`).
- Passwords: bcrypt only. Tokens: HS256 JWT signed with `JWT_SECRET_KEY`.

## Database conventions
- Table names plural snake_case via `Meta.db_table`. Primary key is a UUID. Include `created_at`, `updated_at` and `deleted_at`.
- Soft delete: set `deleted_at`; every query filters `deleted_at=None`.
- Postgres enums use `EnumField` plus a `RunSQL` `CREATE TYPE` in the migration (`makemigrations` cannot generate it). Write that migration by hand.
- Migration-based schema: change a model, run `makemigrations`, review the generated file, commit it, then `migrate`. Nothing auto-syncs the schema.

## Adding a module (checklist)
1. `backend/<name>/` with `models.py`, `dto/`, `services.py`, `views.py`, `urls.py`, `migrations/__init__.py`.
2. Add to `INSTALLED_APPS` and `config/urls.py`.
3. Write the service first, then its unit tests in `tests/<name>/`.
4. Run `makemigrations`, review the file, then `migrate`.

## Testing conventions
- Unit tests only, service layer only. No DB or Redis: mock `User.objects` (or the model) with `mocker.patch('<module>.services.<Model>')`.
- `pytest` + `pytest-django` + `pytest-mock`. `tests/conftest.py` sets dummy env vars before settings load; keep test secrets at least 32 bytes.
- One test class per service method, named `Test<Method>`; test names say the behavior (`test_raises_conflict_when_email_exists`).
- Run the tests and `python manage.py check` before finishing backend work.

## Frontend conventions
- TypeScript strict-style (`noUnusedLocals`, `erasableSyntaxOnly`): no enums, no unused code. Function components only, one component per file, PascalCase file names.
- Styling with Tailwind utility classes. No separate CSS files beyond `src/index.css`.
- API base URL comes from `VITE_API_URL`; never hardcode ports in code.
- Run `npm run build` and `npm run lint` before finishing frontend work.

## Redis
`utils/redis_client.py` (`redis_get`, `redis_set`, `redis_delete`) is ready but intentionally unused. Import it only when a feature needs it, and add a test with the client mocked.

## Git
- Keep `.gitignore` comprehensive (logs, env files except `.env.example`, dependencies, caches, build/dist/output, test and coverage artifacts, editor and OS files). Extend it whenever new tooling adds files.
- Never commit `.env`, `.venv`, `node_modules`, `dist` or `logs`.
- Do not put names, emails, usernames, absolute home-directory paths or other personal information in any file (code, docs, scripts, config). Use relative paths and placeholders.
