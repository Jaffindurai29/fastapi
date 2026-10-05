from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Run from example/13/a, so these are the app's own modules
# (alembic.ini has prepend_sys_path = .). Importing models registers the
# migrated_items table on Base.metadata.
import models  # noqa: F401
from database import DATABASE_URL, Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Same URL as the app (env vars / .env / default), never hardcoded in
# alembic.ini. "%" is doubled because the ini parser treats it specially
# (a URL-encoded password like p%40ss would otherwise break).
config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("%", "%%"))

# What autogenerate compares the real database against.
target_metadata = Base.metadata

# Our own bookkeeping table instead of the default "alembic_version", so
# this lesson never collides with another project's Alembic in the same
# fastapi_learn database.
VERSION_TABLE = "alembic_version_13a"


def include_name(name, type_, parent_names):
    """Only look at tables this app's models define.

    fastapi_learn is shared by every topic (items, crud_react_items, ...).
    Without this filter, autogenerate sees those tables in the database,
    doesn't find them in our models, and writes op.drop_table() for each
    of them. This makes autogenerate ignore every table that isn't ours.
    """
    if type_ == "table":
        return name in target_metadata.tables
    return True


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table=VERSION_TABLE,
        include_name=include_name,
        render_as_batch=url.startswith("sqlite"),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

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
            version_table=VERSION_TABLE,
            include_name=include_name,
            # SQLite can't ALTER most things in place. Batch mode makes
            # Alembic copy the table, change it, and swap it in instead.
            # MySQL doesn't need it, so it's only switched on for SQLite.
            render_as_batch=connection.dialect.name == "sqlite",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
