from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.adaptation import router as adaptation_router
from app.api.rocket_ai import router as rocket_ai_router
from app.storage.schema import initialize_database


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(
    title="Rocket RL Lab",
    lifespan=lifespan,
)
app.include_router(rocket_ai_router)
app.include_router(adaptation_router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}