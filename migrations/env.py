from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app import settings as app_settings
from app.database import base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
settings = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(settings.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support


target_metadata = base.CustomBase.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

sqlalchemy_db_uri = app_settings.Settings().api.db_url


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = sqlalchemy_db_uri
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(sqlalchemy_db_uri, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
