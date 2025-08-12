import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.initial_data import ensure_test_data
from app.utils.db import async_session_maker


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("LIFESPAN startup: ensuring test data")
    try:
        # Если ensure_test_data принимает AsyncSession — передаём сессию
        async with async_session_maker() as session:
            await ensure_test_data(session)
        logging.info("LIFESPAN startup: test data ensured")
    except Exception:
        logging.exception("Error during startup (seeding test data)")

    # Пропускаем управление в приложение
    yield

    logging.info("LIFESPAN shutdown: cleaning up if necessary")
    logging.info("LIFESPAN shutdown: done")
