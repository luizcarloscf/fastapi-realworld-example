# Alembic Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) with SQLModel metadata to manage schema changes. Alembic is wired in this project as:

- Alembic entrypoint: `alembic.ini`
- Migration scripts: `alembic/versions/`
- Runtime config: `alembic/env.py`
- Metadata source: `SQLModel.metadata` (from `conduit/models.py`)

`alembic/env.py` loads settings from the app (`conduit.core.settings.get_settings_cached`) and builds the database URL from environment variables.

## Prerequisites

- PostgreSQL must be reachable.
- Environment variables must be set (`DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`).
- Use the same environment file strategy as the app:
  - `.env.local` if it exists
  - otherwise `.env`

## Running migrations

From the project root:

```bash
poetry run alembic upgrade head
```

## Creating a new migration

1. Update models in `conduit/models.py`.
2. Generate a migration:

```bash
poetry run alembic revision --autogenerate -m "describe_change"
```

3. Review the generated script in `alembic/versions/`.
4. Apply it:

```bash
poetry run alembic upgrade head
```
