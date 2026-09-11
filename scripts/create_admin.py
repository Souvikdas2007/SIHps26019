"""Create or update a local administrator without putting credentials in source."""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Settings
from backend.security import hash_password
from core.database.connection import connect
from core.database.migrator import apply_migrations


def main() -> None:
    username = os.getenv("PS26019_ADMIN_USERNAME")
    password = os.getenv("PS26019_ADMIN_PASSWORD")
    if not username or not password:
        raise SystemExit(
            "Set PS26019_ADMIN_USERNAME and PS26019_ADMIN_PASSWORD in the shell"
        )
    settings = Settings.from_environment()
    apply_migrations(settings.database_path)
    with connect(settings.database_path) as connection:
        role = connection.execute(
            "SELECT id FROM roles WHERE name = 'ADMIN'"
        ).fetchone()
        connection.execute(
            """
            INSERT INTO users (username, password_hash, role_id)
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                password_hash = excluded.password_hash,
                role_id = excluded.role_id,
                is_active = 1
            """,
            (username, hash_password(password), role[0]),
        )
    print(f"Administrator configured: {username}")


if __name__ == "__main__":
    main()
