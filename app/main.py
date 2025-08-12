import logging

from fastapi import FastAPI

from app.routes import activities, buildings, organizations
from app.utils.exception_handler import global_exception_handler
from app.utils.migrations import lifespan

logging.basicConfig(level=logging.INFO)


app = FastAPI(
    title="Organizations referene book API",
    version="1.0.0",
    description="REST API для справочника организаций, зданий и видов деятельности",
    lifespan=lifespan
)

app.add_exception_handler(Exception, global_exception_handler)

app.include_router(organizations.router, prefix="/api/v1")
app.include_router(buildings.router, prefix="/api/v1")
app.include_router(activities.router, prefix="/api/v1")


@app.get("/health_check")
async def ping():
    return {"ping": "pong"}
