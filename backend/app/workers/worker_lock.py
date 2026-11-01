from collections.abc import Iterator
from contextlib import contextmanager
import msvcrt

from app.storage.database import DATABASE_PATH


WORKER_LOCK_PATH = DATABASE_PATH.with_suffix(".worker.lock")


@contextmanager
def worker_lock() -> Iterator[None]:
    WORKER_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)

    with WORKER_LOCK_PATH.open("a+b") as lock_file:
        lock_file.seek(0)
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)

        try:
            yield
        finally:
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)