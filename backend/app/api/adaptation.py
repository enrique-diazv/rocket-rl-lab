import logging
import sqlite3
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from app.schemas.adaptation import (
    AdaptationAgentSummary,
    AdaptationExperimentRequest,
    AdaptationExperimentSnapshot,
)
from app.storage.adaptation_queries import (
    get_adaptation_experiment,
    list_adaptation_agents,
)
from app.api.operator_auth import require_operator
from app.storage.job_queue import (
    ActiveExperimentError,
    create_adaptation_experiment,
    request_adaptation_cancel,
)
from typing import Annotated

from fastapi.responses import StreamingResponse

from app.api.adaptation_stream import stream_adaptation_events

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/adaptation",
    tags=["Adaptación"],
)


@router.get(
    "/experiments/{experiment_id}",
    response_model=AdaptationExperimentSnapshot,
)
def get_experiment(
    experiment_id: UUID,
) -> AdaptationExperimentSnapshot:
    try:
        return get_adaptation_experiment(experiment_id)
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Experimento no encontrado.",
        ) from error
    except (ValueError, sqlite3.Error) as error:
        logger.exception(
            "No se pudo consultar el experimento %s",
            experiment_id.hex,
        )
        raise HTTPException(
            status_code=500,
            detail="No se pudo leer el estado del experimento.",
        ) from error

@router.post(
    "/experiments",
    status_code=202,
    response_model=AdaptationExperimentSnapshot,
    dependencies=[Depends(require_operator)],
)
def create_experiment(
    config: AdaptationExperimentRequest,
) -> AdaptationExperimentSnapshot:
    try:
        experiment_id = create_adaptation_experiment(config)
        return get_adaptation_experiment(experiment_id)
    except ActiveExperimentError as error:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un experimento pendiente o en ejecución.",
        ) from error
    except (ValueError, sqlite3.Error) as error:
        logger.exception("No se pudo crear el experimento.")
        raise HTTPException(
            status_code=500,
            detail="No se pudo crear el experimento.",
        ) from error

@router.post(
    "/experiments/{experiment_id}/cancel",
    status_code=202,
    response_model=AdaptationExperimentSnapshot,
    dependencies=[Depends(require_operator)],
)
def cancel_experiment(
    experiment_id: UUID,
) -> AdaptationExperimentSnapshot:
    try:
        request_adaptation_cancel(experiment_id)
        return get_adaptation_experiment(experiment_id)
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Experimento no encontrado.",
        ) from error
    except (ValueError, sqlite3.Error) as error:
        logger.exception(
            "No se pudo cancelar el experimento %s",
            experiment_id.hex,
        )
        raise HTTPException(
            status_code=500,
            detail="No se pudo solicitar la cancelación.",
        ) from error

_MAX_EVENT_ID = 2**63 - 1


@router.get(
    "/experiments/{experiment_id}/events",
    response_class=StreamingResponse,
    responses={200: {"content": {"text/event-stream": {}}}},
)
def get_experiment_events(
    request: Request,
    experiment_id: UUID,
    after: Annotated[int, Query(ge=0, le=_MAX_EVENT_ID)] = 0,
    last_event_id: Annotated[
        int | None,
        Header(alias="Last-Event-ID", ge=0, le=_MAX_EVENT_ID),
    ] = None,
) -> StreamingResponse:
    try:
        snapshot = get_adaptation_experiment(experiment_id)
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Experimento no encontrado.",
        ) from error
    except (OSError, ValueError, sqlite3.Error) as error:
        logger.exception(
            "No se pudo abrir la transmisión del experimento %s",
            experiment_id.hex,
        )
        raise HTTPException(
            status_code=500,
            detail="No se pudo abrir la transmisión de progreso.",
        ) from error

    cursor = max(after, last_event_id or 0)

    if cursor > snapshot.last_event_id:
        raise HTTPException(
            status_code=422,
            detail="El cursor supera el último evento del experimento.",
        )

    return StreamingResponse(
        stream_adaptation_events(request, experiment_id, cursor),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )

@router.get(
    "/agents",
    response_model=list[AdaptationAgentSummary],
)
def get_agents() -> list[AdaptationAgentSummary]:
    return list_adaptation_agents()