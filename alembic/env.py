import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.utils.db import Base

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()

config = context.config

pg_user = os.getenv("PG_USER", "postgres")
pg_password = os.getenv("PG_PASSWORD", "postgres")
pg_host = os.getenv("PG_HOST", "localhost")
pg_port = os.getenv("PG_PORT", "5432")
pg_db = os.getenv("PG_DB", "mydb")

ASYNC_DATABASE_URL = f"postgresql+asyncpg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
config.set_main_option("sqlalchemy.url", ASYNC_DATABASE_URL)

if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except Exception:
        import logging

        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).warning(
            "Не удалось прочитать конфиг логирования alembic.ini — fallback basicConfig")

target_metadata = Base.metadata


def do_run_migrations(conn: Connection):
    context.configure(connection=conn, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online():
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    run_migrations_online()
