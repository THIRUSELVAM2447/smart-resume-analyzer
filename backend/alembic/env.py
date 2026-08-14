# backend/alembic/env.py

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.database.base import Base

# Import every model so its table is registered on Base.metadata.
# These imports are otherwise "unused" from a pure code-execution
# standpoint — they exist purely for their import-time side effect of
# registering each model class with Base's shared metadata registry.
# Without them, Alembic's autogenerate would see an incomplete schema
# and silently omit these tables from generated migrations.
from app.models.user import User  # noqa: F401
from app.models.resume import Resume, ResumeVersion  # noqa: F401
from app.models.job import Job  # noqa: F401
from app.models.job_analysis import JobAnalysis  # noqa: F401
from app.models.portfolio import Portfolio, PortfolioVersion  # noqa: F401
from app.models.sync_event import SyncEvent  # noqa: F401

# Alembic Config object, providing access to values within alembic.ini
config = context.config

# Inject the real database URL from application settings, rather than
# relying on a hard-coded value inside alembic.ini. This keeps the
# only source of truth for DATABASE_URL in app.core.config / .env.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging, as per alembic's
# standard template (controls Alembic's own log output).
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata is what autogenerate diffs the live database against.
# It must point at the SAME Base used by every model — never a second,
# separately created Base.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine, so no
    actual DBAPI connection is required. Calls to context.execute()
    emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    Creates an Engine from the resolved config and associates a
    connection with the migration context, then runs the migrations
    against the live database.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()