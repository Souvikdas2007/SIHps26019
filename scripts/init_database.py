"""Initialize the local PS26019 SQLite database."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Settings
from core.database.migrator import apply_migrations


if __name__ == "__main__":
    settings = Settings.from_environment()
    count = apply_migrations(settings.database_path)
    print(f"Applied {count} migration(s) to {settings.database_path}")
