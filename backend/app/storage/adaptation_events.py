import json
import sqlite3
from uuid import UUID

from app.schemas.adaptation import AdaptationEventSnapshot
from app.storage.database import database_connection


def _event_snapshot(row: sqlite3.Row) -> AdaptationEventSnapshot:
    payload = json.loads(row["payload_json"])

    if not isinstance(payload, dict):
        raise ValueError("El contenido del evento debe ser un objeto.")

    return AdaptationEventSnapshot(
        id=row["id"],
        experiment_id=UUID(row["experiment_id"]),
        job_id=(
            None
            if row["job_id"] is None
            else UUID(row["job_id"])
        ),
        event_type=row["event_type"],
        created_at=row["created_at"],
        agent=payload.get("agent"),
        status=payload.get("status"),
        finished_at=payload.get("finished_at"),
        progress=payload.get("progress"),
        cancel_requested=payload.get("cancel_requested"),
        error=(
            "No se pudo completar este trabajo."
            if payload.get("status") == "failed"
            else None
        ),
    )

def list_adaptation_events(
    experiment_id: UUID,
    after_event_id: int,
) -> list[AdaptationEventSnapshot]:
    with database_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id, experiment_id, job_id,
                event_type, created_at, payload_json
            FROM adaptation_events
            WHERE experiment_id = ?
                AND id > ?
            ORDER BY id ASC
            LIMIT 100
            """,
            (experiment_id.hex, after_event_id),
        ).fetchall()

    return [_event_snapshot(row) for row in rows]