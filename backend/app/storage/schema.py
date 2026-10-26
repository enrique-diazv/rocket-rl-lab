from collections.abc import Iterator
from pathlib import Path
import sqlite3

from app.storage.database import DATABASE_PATH, database_connection


SCHEMA_VERSION = 1
INITIAL_MIGRATION = (
    Path(__file__).with_name("migrations") / "001_initial.sql"
)


def _migration_statements(path: Path) -> Iterator[str]:
    pending = ""

    for line in path.read_text(encoding="utf-8-sig").splitlines(
        keepends=True
    ):
        pending += line

        if sqlite3.complete_statement(pending):
            yield pending
            pending = ""

    if pending.strip():
        yield pending


def initialize_database() -> None:
    with database_connection() as connection:
        connection.execute("PRAGMA journal_mode = WAL").fetchone()
        connection.execute("BEGIN IMMEDIATE")
        current_version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

        if current_version == SCHEMA_VERSION:
            return

        if current_version != 0:
            raise RuntimeError(
                f"Versión de base de datos no compatible: {current_version}."
            )

        for statement in _migration_statements(INITIAL_MIGRATION):
            connection.execute(statement)

        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


def main() -> None:
    initialize_database()

    with database_connection() as connection:
        schema_version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]
        journal_mode = connection.execute(
            "PRAGMA journal_mode"
        ).fetchone()[0]

    print(f"Base de datos: {DATABASE_PATH}")
    print(f"Version del esquema: {schema_version}")
    print(f"Modo de diario: {journal_mode}")


if __name__ == "__main__":
    main()