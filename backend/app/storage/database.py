from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
import sqlite3


DATABASE_PATH = (
    Path(__file__).resolve().parents[2]
    / "experiments"
    / "rocket_rl.sqlite3"
)


@contextmanager
def database_connection() -> Iterator[sqlite3.Connection]:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=5.0,
        autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL,
    )

    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")

        with connection:
            yield connection
    finally:
        connection.close()