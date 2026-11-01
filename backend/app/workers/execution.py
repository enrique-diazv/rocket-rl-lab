from threading import Event

import logging

from app.rl.adaptation_runner import AdaptationSession
from app.storage.job_queue import stop_adaptation_job
from app.rl.adaptation_metrics import AdaptationProgress
from app.storage.job_queue import (
    ClaimedAdaptationJob,
    is_adaptation_cancel_requested,
    record_adaptation_progress,
)


class AdaptationCancelled(Exception):
    pass


class JobProgressReporter:
    def __init__(
        self,
        job: ClaimedAdaptationJob,
        stop_requested: Event,
    ) -> None:
        self._job = job
        self._stop_requested = stop_requested

    def __call__(self, progress: AdaptationProgress) -> None:
        record_adaptation_progress(self._job.job_id, progress)

        if progress.phase not in ("evaluating", "training"):
            return

        if self._stop_requested.is_set():
            raise AdaptationCancelled("Se solicitó detener el worker.")

        if is_adaptation_cancel_requested(self._job.experiment_id):
            raise AdaptationCancelled("Se solicitó cancelar el experimento.")

logger = logging.getLogger(__name__)


def run_adaptation_job(
    job: ClaimedAdaptationJob,
    stop_requested: Event,
) -> None:
    reporter = JobProgressReporter(job, stop_requested)

    try:
        session = AdaptationSession(
            job.agent,
            job.config,
            job.experiment_id,
            on_progress=reporter,
        )
        result = session.run()
    except AdaptationCancelled as error:
        stop_adaptation_job(job.job_id, status="cancelled")
        logger.info("Trabajo %s cancelado: %s", job.job_id.hex, error)
    except Exception as error:
        logger.exception("Falló el trabajo %s", job.job_id.hex)
        stop_adaptation_job(
            job.job_id,
            status="failed",
            error=f"{type(error).__name__}: {error}",
        )
    else:
        logger.info(
            "Trabajo %s terminado: %s",
            job.job_id.hex,
            result.status,
        )