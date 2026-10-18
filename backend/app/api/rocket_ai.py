from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.storage.checkpoints import CheckpointSummary, list_checkpoints
from app.storage.episodes import (
    EpisodeSummary,
    get_episode_path,
    list_episodes,
)
from app.storage.evaluations import (
    EvaluationSummary,
    get_evaluation_path,
    list_evaluations,
)

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


@router.get("/episodes")
def get_episodes(
    model_id: str = Query(min_length=1),
) -> list[EpisodeSummary]:
    return list_episodes(model_id=model_id)

@router.get("/evaluations/{evaluation_id}", response_class=FileResponse)
def get_evaluation(evaluation_id: UUID) -> FileResponse:
    try:
        path = get_evaluation_path(evaluation_id)
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Evaluación no encontrada.",
        ) from error

    return FileResponse(path, media_type="application/json")

@router.get("/evaluations")
def get_evaluations(
    model_id: str = Query(min_length=1),
) -> list[EvaluationSummary]:
    return list_evaluations(model_id=model_id)