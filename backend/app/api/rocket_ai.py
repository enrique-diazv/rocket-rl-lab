from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.storage.checkpoints import CheckpointSummary, list_checkpoints
from app.storage.episodes import get_episode_path


router = APIRouter(
    prefix="/api/rocket-ai",
    tags=["Rocket AI"],
)


@router.get("/models")
def get_models() -> list[CheckpointSummary]:
    return list_checkpoints()


@router.get("/episodes/{episode_id}", response_class=FileResponse)
def get_episode(episode_id: UUID) -> FileResponse:
    try:
        path = get_episode_path(episode_id)
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Episodio no encontrado.",
        ) from error

    return FileResponse(path, media_type="application/json")