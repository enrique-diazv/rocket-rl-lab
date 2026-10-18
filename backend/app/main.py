from fastapi import FastAPI

from app.api.rocket_ai import router as rocket_ai_router


app = FastAPI(title="Rocket RL Lab")
app.include_router(rocket_ai_router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}