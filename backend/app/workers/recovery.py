from hashlib import sha256
import json

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.rl.adaptation_metrics import (
    AdaptationEvaluation,
    AdaptationStatus,
)
from app.storage.adaptations import adaptation_checkpoint_path
from app.storage.job_queue import ClaimedAdaptationJob
import logging

from app.rl.adaptation_metrics import AdaptationProgress
from app.storage.job_queue import (
    get_active_adaptation_job,
    is_adaptation_cancel_requested,
    record_adaptation_progress,
    stop_adaptation_job,
)
class SavedAdaptationResult(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    schema_version: Literal[1]
    experiment_id: UUID
    agent: str
    status: AdaptationStatus
    time_to_threshold_steps: int | None = Field(ge=0)
    evaluations: tuple[AdaptationEvaluation, ...] = Field(min_length=1)

    @field_validator("evaluations", mode="before")
    @classmethod
    def restore_evaluations(cls, value: object) -> object:
        if not isinstance(value, list):
            return value

        evaluations: list[object] = []

        for evaluation in value:
            if isinstance(evaluation, dict):
                evaluation = evaluation.copy()
                evaluation.pop("success_rate", None)
                evaluation.pop("mean_original_reward", None)

            evaluations.append(evaluation)

        return evaluations

def read_completed_result(
    job: ClaimedAdaptationJob,
) -> SavedAdaptationResult | None:
    directory = adaptation_checkpoint_path(
        job.experiment_id,
        job.agent,
        0,
    ).parent

    try:
        serialized = (directory / "result.json").read_text(
            encoding="utf-8-sig",
        )
    except FileNotFoundError:
        return None

    result = SavedAdaptationResult.model_validate_json(serialized)

    if (
        result.experiment_id != job.experiment_id
        or result.agent != job.agent
    ):
        raise ValueError("El resultado no corresponde al trabajo activo.")

    return result

def _validate_final_checkpoint(
    job: ClaimedAdaptationJob,
    result: SavedAdaptationResult,
) -> None:
    last_evaluation = result.evaluations[-1]
    checkpoint = adaptation_checkpoint_path(
        job.experiment_id,
        job.agent,
        last_evaluation.extra_training_timesteps,
    )
    evaluation_index = len(result.evaluations)
    evaluation_path = (
        checkpoint.parent
        / "evaluations"
        / f"evaluation_{evaluation_index}.json"
    )
    reference = json.loads(
        evaluation_path.read_text(encoding="utf-8-sig")
    )

    if not isinstance(reference, dict):
        raise ValueError("El registro de evaluación debe ser un objeto.")

    if (
        reference.get("schema_version") != 1
        or reference.get("experiment_id") != job.experiment_id.hex
        or reference.get("agent") != job.agent
        or reference.get("evaluation_index") != evaluation_index
        or reference.get("checkpoint_filename") != checkpoint.name
    ):
        raise ValueError("La evaluación no corresponde al checkpoint final.")

    actual_hash = sha256(checkpoint.read_bytes()).hexdigest()

    if reference.get("checkpoint_sha256") != actual_hash:
        raise ValueError("El hash del checkpoint final no coincide.")

logger = logging.getLogger(__name__)


def _restore_completed_job(
    job: ClaimedAdaptationJob,
    result: SavedAdaptationResult,
) -> None:
    last_evaluation = result.evaluations[-1]

    record_adaptation_progress(
        job.job_id,
        AdaptationProgress(
            agent=job.agent,
            phase=result.status,
            extra_training_timesteps=last_evaluation.extra_training_timesteps,
            training_episodes=last_evaluation.training_episodes,
            elapsed_wall_seconds=last_evaluation.elapsed_wall_seconds,
            evaluation_count=len(result.evaluations),
        ),
    )
    logger.info("Resultado recuperado para el trabajo %s", job.job_id.hex)


def recover_interrupted_job() -> None:
    job = get_active_adaptation_job()

    if job is None:
        return

    try:
        result = read_completed_result(job)

        if result is not None:
            _validate_final_checkpoint(job, result)
            _restore_completed_job(job, result)
            return
    except (OSError, UnicodeError, ValueError) as error:
        logger.exception("No se pudo recuperar el trabajo %s", job.job_id.hex)
        stop_adaptation_job(
            job.job_id,
            status="failed",
            error=f"Recuperación inválida: {type(error).__name__}: {error}",
        )
        return

    cancelled = is_adaptation_cancel_requested(job.experiment_id)
    stop_adaptation_job(
        job.job_id,
        status="cancelled" if cancelled else "failed",
        error=(
            None
            if cancelled
            else "El worker se interrumpió antes de guardar el resultado final."
        ),
    )
    logger.warning("Trabajo interrumpido cerrado: %s", job.job_id.hex)