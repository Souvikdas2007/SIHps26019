"""Local evidence indexing and SQLite FTS5 retrieval."""

from dataclasses import dataclass
import re
import sqlite3
from typing import Iterable


@dataclass(frozen=True)
class EvidenceResult:
    source_id: str
    title: str
    source: str
    chunk_id: int
    snippet: str


def index_document(
    connection: sqlite3.Connection,
    *,
    source_id: str,
    title: str,
    source: str,
    file_path: str,
    chunks: Iterable[str],
    source_url: str | None = None,
    publisher: str | None = None,
    document_type: str | None = None,
) -> int:
    """Persist document metadata, chunks and their FTS5 rows."""
    document_cursor = connection.execute(
        """
        INSERT INTO documents (
            source_id, title, source, source_url, publisher,
            document_type, file_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (source_id, title, source, source_url, publisher, document_type, file_path),
    )
    document_id = int(document_cursor.lastrowid)
    chunk_count = 0
    for chunk_index, content in enumerate(chunks):
        if not content.strip():
            continue
        chunk_cursor = connection.execute(
            """
            INSERT INTO document_chunks (document_id, chunk_index, content)
            VALUES (?, ?, ?)
            """,
            (document_id, chunk_index, content.strip()),
        )
        chunk_id = int(chunk_cursor.lastrowid)
        connection.execute(
            """
            INSERT INTO document_chunks_fts (content, source_id, document_chunk_id)
            VALUES (?, ?, ?)
            """,
            (content.strip(), source_id, chunk_id),
        )
        chunk_count += 1
    return chunk_count


def search_evidence(
    connection: sqlite3.Connection,
    query: str,
    *,
    limit: int = 10,
) -> list[EvidenceResult]:
    """Search local FTS5 evidence and return source-attributed snippets."""
    tokens = re.findall(r"[A-Za-z0-9_]+", query.lower())
    if not tokens:
        return []
    fts_query = " AND ".join(f'"{token}"' for token in tokens)
    rows = connection.execute(
        """
        SELECT
            f.source_id,
            d.title,
            d.source,
            f.document_chunk_id,
            snippet(document_chunks_fts, 0, '[', ']', '...', 18)
        FROM document_chunks_fts AS f
        JOIN documents AS d ON d.source_id = f.source_id
        WHERE document_chunks_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        """,
        (fts_query, max(1, min(limit, 50))),
    )
    return [EvidenceResult(*row) for row in rows]
