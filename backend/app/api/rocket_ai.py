from fastapi import APIRouter

from app.storage.checkpoints import CheckpointSummary, list_checkpoints


router = APIRouter(
    prefix="/api/rocket-ai",
    tags=["Rocket AI"],
)


@router.get("/models")
def get_models() -> list[CheckpointSummary]:
    return list_checkpoints()