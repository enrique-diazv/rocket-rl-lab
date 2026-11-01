import sqlite3
from uuid import UUID

from app.rl.adaptation_config import AdaptationConfig
from app.schemas.adaptation import (
    AdaptationExperimentSnapshot,
    AdaptationJobSnapshot,
    AdaptationProgressSnapshot,
)
from app.storage.database import database_connection


def _job_snapshot(row: sqlite3.Row) -> AdaptationJobSnapshot:
    progress = (
        None
        if row["progress_json"] is None
        else AdaptationProgressSnapshot.model_validate_json(
            row["progress_json"]
        )
    )

    return AdaptationJobSnapshot(
        id=UUID(row["id"]),
        agent=row["agent"],
        status=row["status"],
        created_at=row["created_at"],
        started_at=row["started_at"],
        finished_at=row["finished_at"],
        progress=progress,
        error=(
            "No se pudo completar este trabajo."
            if row["status"] == "failed"
            else None
        ),
    )

def get_adaptation_experiment(
    experiment_id: UUID,
) -> AdaptationExperimentSnapshot:
    with database_connection() as connection:
        connection.execute("BEGIN")

        experiment = connection.execute(
            """
            SELECT id, created_at, config_json, cancel_requested
            FROM adaptation_experiments
            WHERE id = ?
            """,
            (experiment_id.hex,),
        ).fetchone()

        if experiment is None:
            raise FileNotFoundError("Experimento de adaptación no encontrado.")

        jobs = connection.execute(
            """
            SELECT
                id, agent, status, created_at,
                started_at, finished_at, progress_json
            FROM adaptation_jobs
            WHERE experiment_id = ?
            ORDER BY position
            """,
            (experiment_id.hex,),
        ).fetchall()

        last_event_id = connection.execute(
            """
            SELECT COALESCE(MAX(id), 0)
            FROM adaptation_events
            WHERE experiment_id = ?
            """,
            (experiment_id.hex,),
        ).fetchone()[0]

    return AdaptationExperimentSnapshot(
        id=experiment_id,
        created_at=experiment["created_at"],
        config=AdaptationConfig.model_validate_json(
            experiment["config_json"]
        ),
        cancel_requested=bool(experiment["cancel_requested"]),
        jobs=[_job_snapshot(job) for job in jobs],
        last_event_id=last_event_id,
    )