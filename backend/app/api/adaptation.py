import logging
import sqlite3
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.adaptation import (
    AdaptationExperimentRequest,
    AdaptationExperimentSnapshot,
)
from app.storage.adaptation_queries import get_adaptation_experiment
from app.api.operator_auth import require_operator
from app.storage.job_queue import (
    ActiveExperimentError,
    create_adaptation_experiment,
    request_adaptation_cancel,
)

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