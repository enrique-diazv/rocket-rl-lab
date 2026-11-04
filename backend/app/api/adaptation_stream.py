import asyncio
from collections.abc import AsyncIterator
import json
import logging
import sqlite3
from time import monotonic
from uuid import UUID

from fastapi import Request
from starlette.concurrency import run_in_threadpool

from app.schemas.adaptation import AdaptationEventSnapshot
from app.storage.adaptation_events import list_adaptation_events
from app.storage.adaptation_queries import get_adaptation_experiment


logger = logging.getLogger(__name__)


def _format_event(event: AdaptationEventSnapshot) -> str:
    return (
        f"id: {event.id}\n"
        "event: adaptation\n"
        f"data: {event.model_dump_json()}\n\n"
    )

async def stream_adaptation_events(
    request: Request,
    experiment_id: UUID,
    after_event_id: int,
) -> AsyncIterator[str]:
    cursor = after_event_id
    last_sent_at = monotonic()

    yield "retry: 2000\n\n"

    try:
        while True:
            if await request.is_disconnected():
                return

            events = await run_in_threadpool(
                list_adaptation_events,
                experiment_id,
                cursor,
            )

            for event in events:
                yield _format_event(event)
                cursor = event.id
                last_sent_at = monotonic()

            snapshot = await run_in_threadpool(
                get_adaptation_experiment,
                experiment_id,
            )
            finished = all(
                job.finished_at is not None
                for job in snapshot.jobs
            )

            if finished and cursor >= snapshot.last_event_id:
                payload = json.dumps(
                    {"last_event_id": snapshot.last_event_id}
                )
                yield f"event: end\ndata: {payload}\n\n"
                return

            if cursor < snapshot.last_event_id:
                continue

            if monotonic() - last_sent_at >= 15:
                yield ": keep-alive\n\n"
                last_sent_at = monotonic()

            await asyncio.sleep(1)
    except (OSError, ValueError, sqlite3.Error):
        logger.exception(
            "No se pudo transmitir el experimento %s",
            experiment_id.hex,
        )
        yield (
            "event: stream_error\n"
            'data: {"detail":"No se pudo leer el progreso."}\n\n'
        )