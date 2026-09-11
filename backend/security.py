"""Local password hashing, sessions, authorization and audit helpers."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets
import sqlite3


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    username: str
    role: str


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, salt_hex, digest_hex = encoded.split("$", 2)
        if algorithm != "scrypt":
            return False
        digest = hashlib.scrypt(
            password.encode("utf-8"), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def create_session(connection: sqlite3.Connection, user_id: int, hours: int = 8) -> str:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)
    connection.execute(
        "INSERT INTO auth_sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (token_hash, user_id, expires_at.isoformat()),
    )
    return raw_token


def get_user_for_token(
    connection: sqlite3.Connection, raw_token: str | None
) -> AuthenticatedUser | None:
    if not raw_token:
        return None
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    row = connection.execute(
        """
        SELECT u.id, u.username, r.name, s.expires_at
        FROM auth_sessions AS s
        JOIN users AS u ON u.id = s.user_id
        JOIN roles AS r ON r.id = u.role_id
        WHERE s.token_hash = ? AND u.is_active = 1
        """,
        (token_hash,),
    ).fetchone()
    if row is None:
        return None
    expires_at = datetime.fromisoformat(row[3])
    if expires_at <= datetime.now(timezone.utc):
        connection.execute("DELETE FROM auth_sessions WHERE token_hash = ?", (token_hash,))
        return None
    return AuthenticatedUser(id=row[0], username=row[1], role=row[2])


def write_audit(
    connection: sqlite3.Connection,
    *,
    event_type: str,
    user_id: int | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    details_json: str = "{}",
) -> None:
    connection.execute(
        """
        INSERT INTO audit_logs (user_id, event_type, entity_type, entity_id, details_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, event_type, entity_type, entity_id, details_json),
    )
