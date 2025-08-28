from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.models.base import Base  # noqa: E402
import app.models.user  # noqa: F401
import app.models.project  # noqa: F401
import app.models.asset  # noqa: F401
import app.models.generation_job  # noqa: F401
import app.models.generated_asset  # noqa: F401
import app.models.repurposing_platform  # noqa: F401
import app.models.asset_format  # noqa: F401
import app.models.text_style_set  # noqa: F401
import app.models.app_settings  # noqa: F401

config = context.config

fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = os.getenv("DATABASE_URL")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.getenv("DATABASE_URL")
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
