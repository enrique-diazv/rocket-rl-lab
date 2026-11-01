import logging
import signal
from threading import Event
from types import FrameType

from app.storage.job_queue import claim_next_adaptation_job
from app.storage.schema import initialize_database
from app.workers.execution import run_adaptation_job
from app.workers.recovery import recover_interrupted_job
from app.workers.worker_lock import worker_lock


logger = logging.getLogger(__name__)


def _run_queue(stop_requested: Event) -> None:
    while not stop_requested.is_set():
        job = claim_next_adaptation_job()

        if job is None:
            stop_requested.wait(timeout=1.0)
            continue

        logger.info(
            "Iniciando trabajo %s (%s)",
            job.job_id.hex,
            job.agent,
        )
        run_adaptation_job(job, stop_requested)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    stop_requested = Event()

    def request_shutdown(
        _signal_number: int,
        _frame: FrameType | None,
    ) -> None:
        stop_requested.set()
        logger.info(
            "Detención solicitada. Esperando al siguiente punto seguro."
        )

    signal.signal(signal.SIGINT, request_shutdown)

    with worker_lock():
        initialize_database()
        recover_interrupted_job()
        logger.info("Worker listo. Esperando trabajos.")
        _run_queue(stop_requested)

    logger.info("Worker detenido.")


if __name__ == "__main__":
    main()