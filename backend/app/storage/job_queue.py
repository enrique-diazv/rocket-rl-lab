import json

from app.rl.adaptation_metrics import AdaptationProgress
from datetime import datetime, timezone
from uuid import UUID, uuid4
from dataclasses import dataclass

from app.rl.adaptation_config import AdaptationConfig
from app.rl.agent_profiles import AGENT_PROFILES
from app.storage.database import database_connection
from app.storage.queue_events import QueueEvent, append_queue_event

import sqlite3
from typing import Literal


class ActiveExperimentError(RuntimeError):
    pass


@dataclass(frozen=True)
class ClaimedAdaptationJob:
    job_id: UUID
    experiment_id: UUID
    agent: str
    config: AdaptationConfig


def create_adaptation_experiment(config: AdaptationConfig) -> UUID:
    experiment_id = uuid4()
    created_at = datetime.now(timezone.utc).isoformat()

    with database_connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        unfinished = connection.execute("""
            SELECT 1
            FROM adaptation_jobs
            WHERE status IN ('queued', 'running', 'evaluating', 'training')
            LIMIT 1
            """).fetchone()

        if unfinished is not None:
            raise ActiveExperimentError(
                "Ya existe un experimento en cola o en ejecución."
            )

        connection.execute(
            """
            INSERT INTO adaptation_experiments (
                id, created_at, config_json
            )
            VALUES (?, ?, ?)
            """,
            (
                experiment_id.hex,
                created_at,
                config.model_dump_json(),
            ),
        )
        connection.executemany(
            """
            INSERT INTO adaptation_jobs (
                id, experiment_id, agent, status, position, created_at
            )
            VALUES (?, ?, ?, 'queued', ?, ?)
            """,
            [
                (
                    uuid4().hex,
                    experiment_id.hex,
                    agent,
                    position,
                    created_at,
                )
                for position, agent in enumerate(AGENT_PROFILES)
            ],
        )
        append_queue_event(
            connection,
            QueueEvent(
                experiment_id=experiment_id,
                job_id=None,
                event_type="experiment_created",
                payload={
                    "experiment_id": experiment_id.hex,
                    "agents": list(AGENT_PROFILES),
                    "status": "queued",
                },
            ),
        )

    return experiment_id


def claim_next_adaptation_job() -> ClaimedAdaptationJob | None:
    with database_connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        active_job = connection.execute("""
            SELECT 1
            FROM adaptation_jobs
            WHERE status IN ('running', 'evaluating', 'training')
            LIMIT 1
            """).fetchone()

        if active_job is not None:
            return None

        queued_job = connection.execute("""
            SELECT j.id, j.experiment_id, j.agent, e.config_json
            FROM adaptation_jobs AS j
            JOIN adaptation_experiments AS e
                ON e.id = j.experiment_id
            WHERE j.status = 'queued'
                AND e.cancel_requested = 0
            ORDER BY j.created_at, j.position
            LIMIT 1
            """).fetchone()

        if queued_job is None:
            return None

        claimed = ClaimedAdaptationJob(
            job_id=UUID(queued_job["id"]),
            experiment_id=UUID(queued_job["experiment_id"]),
            agent=queued_job["agent"],
            config=AdaptationConfig.model_validate_json(queued_job["config_json"]),
        )
        connection.execute(
            """
            UPDATE adaptation_jobs
            SET status = 'running', started_at = ?
            WHERE id = ?
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                claimed.job_id.hex,
            ),
        )
        append_queue_event(
            connection,
            QueueEvent(
                experiment_id=claimed.experiment_id,
                job_id=claimed.job_id,
                event_type="job_started",
                payload={
                    "job_id": claimed.job_id.hex,
                    "agent": claimed.agent,
                    "status": "running",
                },
            ),
        )

    return claimed


def _progress_snapshot(
    progress: AdaptationProgress,
    previous_json: str | None,
) -> dict[str, object]:
    previous_snapshot = json.loads(previous_json) if previous_json is not None else {}
    last_evaluation = previous_snapshot.get("last_evaluation")

    if progress.evaluation is not None:
        evaluation = progress.evaluation
        last_evaluation = {
            "evaluation_index": progress.evaluation_count,
            "extra_training_timesteps": evaluation.extra_training_timesteps,
            "training_episodes": evaluation.training_episodes,
            "elapsed_wall_seconds": evaluation.elapsed_wall_seconds,
            "episode_count": len(evaluation.episodes),
            "success_rate": evaluation.success_rate,
            "mean_original_reward": evaluation.mean_original_reward,
        }

    return {
        "agent": progress.agent,
        "phase": progress.phase,
        "extra_training_timesteps": progress.extra_training_timesteps,
        "training_episodes": progress.training_episodes,
        "elapsed_wall_seconds": progress.elapsed_wall_seconds,
        "evaluation_count": progress.evaluation_count,
        "last_evaluation": last_evaluation,
    }


def record_adaptation_progress(
    job_id: UUID,
    progress: AdaptationProgress,
) -> None:
    with database_connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        job = connection.execute(
            """
            SELECT experiment_id, agent, status, progress_json
            FROM adaptation_jobs
            WHERE id = ?
            """,
            (job_id.hex,),
        ).fetchone()

        if job is None:
            raise FileNotFoundError("El trabajo solicitado no existe.")

        if job["agent"] != progress.agent:
            raise ValueError("El progreso no corresponde al agente reservado.")

        if job["status"] not in ("running", "evaluating", "training"):
            raise ValueError("El trabajo no está activo.")

        snapshot = _progress_snapshot(progress, job["progress_json"])
        finished_at = (
            datetime.now(timezone.utc).isoformat()
            if progress.phase not in ("evaluating", "training")
            else None
        )

        connection.execute(
            """
            UPDATE adaptation_jobs
            SET status = ?, progress_json = ?, finished_at = ?
            WHERE id = ?
            """,
            (
                progress.phase,
                json.dumps(snapshot, ensure_ascii=False, allow_nan=False),
                finished_at,
                job_id.hex,
            ),
        )
        append_queue_event(
            connection,
            QueueEvent(
                experiment_id=UUID(job["experiment_id"]),
                job_id=job_id,
                event_type=(
                    "evaluation_completed"
                    if progress.evaluation is not None
                    else "job_progress"
                ),
                payload={
                    "job_id": job_id.hex,
                    "agent": progress.agent,
                    "status": progress.phase,
                    "finished_at": finished_at,
                    "progress": snapshot,
                },
            ),
        )


def _stop_job(
    connection: sqlite3.Connection,
    job: sqlite3.Row,
    status: Literal["failed", "cancelled"],
    error: str | None,
) -> None:
    finished_at = datetime.now(timezone.utc).isoformat()
    connection.execute(
        """
        UPDATE adaptation_jobs
        SET status = ?, error = ?, finished_at = ?
        WHERE id = ?
        """,
        (status, error, finished_at, job["id"]),
    )
    append_queue_event(
        connection,
        QueueEvent(
            experiment_id=UUID(job["experiment_id"]),
            job_id=UUID(job["id"]),
            event_type="job_stopped",
            payload={
                "job_id": job["id"],
                "agent": job["agent"],
                "status": status,
                "finished_at": finished_at,
                "error": error,
            },
        ),
    )


def stop_adaptation_job(
    job_id: UUID,
    *,
    status: Literal["failed", "cancelled"],
    error: str | None = None,
) -> None:
    with database_connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        job = connection.execute(
            """
            SELECT id, experiment_id, agent, status
            FROM adaptation_jobs
            WHERE id = ?
            """,
            (job_id.hex,),
        ).fetchone()

        if job is None:
            raise FileNotFoundError("El trabajo solicitado no existe.")

        if job["status"] not in ("queued", "running", "evaluating", "training"):
            return

        _stop_job(connection, job, status, error)


def is_adaptation_cancel_requested(experiment_id: UUID) -> bool:
    with database_connection() as connection:
        experiment = connection.execute(
            """
            SELECT cancel_requested
            FROM adaptation_experiments
            WHERE id = ?
            """,
            (experiment_id.hex,),
        ).fetchone()

    if experiment is None:
        raise FileNotFoundError("El experimento solicitado no existe.")

    return bool(experiment["cancel_requested"])


def request_adaptation_cancel(experiment_id: UUID) -> None:
    with database_connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        experiment = connection.execute(
            """
            SELECT cancel_requested
            FROM adaptation_experiments
            WHERE id = ?
            """,
            (experiment_id.hex,),
        ).fetchone()

        if experiment is None:
            raise FileNotFoundError("El experimento solicitado no existe.")

        if experiment["cancel_requested"]:
            return

        unfinished = connection.execute(
            """
            SELECT id, experiment_id, agent, status
            FROM adaptation_jobs
            WHERE experiment_id = ?
                AND status IN (
                    'queued', 'running', 'evaluating', 'training'
                )
            ORDER BY position
            """,
            (experiment_id.hex,),
        ).fetchall()

        if not unfinished:
            return

        connection.execute(
            """
            UPDATE adaptation_experiments
            SET cancel_requested = 1
            WHERE id = ?
            """,
            (experiment_id.hex,),
        )

        for job in unfinished:
            if job["status"] == "queued":
                _stop_job(connection, job, "cancelled", None)

        append_queue_event(
            connection,
            QueueEvent(
                experiment_id=experiment_id,
                job_id=None,
                event_type="cancel_requested",
                payload={
                    "experiment_id": experiment_id.hex,
                    "cancel_requested": True,
                },
            ),
        )
