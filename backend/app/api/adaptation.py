import logging
import sqlite3
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.schemas.adaptation import AdaptationExperimentSnapshot
from app.storage.adaptation_queries import get_adaptation_experiment


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