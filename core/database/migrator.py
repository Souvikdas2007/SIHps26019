"""Small, dependency-free SQLite migration runner."""

from pathlib import Path
import sqlite3

from core.database.connection import connect


MIGRATIONS_PATH = Path(__file__).with_name("migrations")


def apply_migrations(database_path: Path, migrations_path: Path = MIGRATIONS_PATH) -> int:
    """Apply each pending numbered SQL migration exactly once."""
    with connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        applied = {
            row[0]
            for row in connection.execute("SELECT version FROM schema_migrations")
        }
        migration_files = sorted(migrations_path.glob("[0-9][0-9][0-9]_*.sql"))
        applied_count = 0
        for migration_file in migration_files:
            version = migration_file.stem
            if version in applied:
                continue
            connection.executescript(migration_file.read_text(encoding="utf-8"))
            connection.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)", (version,)
            )
            applied_count += 1
        return applied_count
