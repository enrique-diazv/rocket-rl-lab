from dataclasses import dataclass
from datetime import datetime, timezone
import json
import sqlite3
from uuid import UUID


@dataclass(frozen=True)
class QueueEvent:
    experiment_id: UUID
    job_id: UUID | None
    event_type: str
    payload: dict[str, object]


def append_queue_event(
    connection: sqlite3.Connection,
    event: QueueEvent,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO adaptation_events (
            experiment_id,
            job_id,
            event_type,
            created_at,
            payload_json
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            event.experiment_id.hex,
            event.job_id.hex if event.job_id is not None else None,
            event.event_type,
            datetime.now(timezone.utc).isoformat(),
            json.dumps(
                event.payload,
                ensure_ascii=False,
                allow_nan=False,
            ),
        ),
    )
    return int(cursor.lastrowid)