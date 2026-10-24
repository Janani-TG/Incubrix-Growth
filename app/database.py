"""Database connection management and schema initialization for SQLite."""

from __future__ import annotations

from contextlib import contextmanager
import logging
import os
from pathlib import Path
import sqlite3
from typing import Generator

logger = logging.getLogger("incubrix.database")

DEFAULT_DB_PATH = Path("data/incubrix_growth.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS source_documents (
    source_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_url TEXT,
    content_hash TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    imported_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_source_content_hash ON source_documents(content_hash);
CREATE INDEX IF NOT EXISTS idx_source_imported_at ON source_documents(imported_at);

CREATE TABLE IF NOT EXISTS content_assets (
    asset_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    content_format TEXT NOT NULL,
    content_pillar TEXT NOT NULL,
    audience_segment TEXT NOT NULL,
    hook TEXT NOT NULL,
    main_content TEXT NOT NULL,
    caption TEXT NOT NULL,
    hashtags TEXT NOT NULL,
    call_to_action TEXT NOT NULL,
    tracking_url TEXT,
    source_id TEXT NOT NULL,
    evidence_references TEXT NOT NULL,
    review_required INTEGER NOT NULL DEFAULT 0,
    review_notes TEXT,
    generation_method TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL,
    duration_seconds REAL,
    content_fingerprint TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES source_documents(source_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_assets_platform ON content_assets(platform);
CREATE INDEX IF NOT EXISTS idx_assets_status ON content_assets(status);
CREATE INDEX IF NOT EXISTS idx_assets_source_id ON content_assets(source_id);
CREATE INDEX IF NOT EXISTS idx_assets_fingerprint ON content_assets(content_fingerprint);
CREATE INDEX IF NOT EXISTS idx_assets_created_at ON content_assets(created_at);

CREATE TABLE IF NOT EXISTS generation_runs (
    run_id TEXT PRIMARY KEY,
    input_source_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    runtime_ms REAL,
    generation_method TEXT NOT NULL,
    assets_created INTEGER NOT NULL DEFAULT 0,
    review_required_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    error_details TEXT,
    FOREIGN KEY (input_source_id) REFERENCES source_documents(source_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_runs_source_id ON generation_runs(input_source_id);
CREATE INDEX IF NOT EXISTS idx_runs_status ON generation_runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_started_at ON generation_runs(started_at);
"""


def resolve_db_path(db_path: str | Path | None = None) -> Path:
    """Resolve database path from argument or environment variable and ensure parent directory exists."""
    if db_path is not None:
        path = Path(db_path)
    else:
        env_val = os.getenv("DATABASE_PATH")
        path = Path(env_val) if env_val else DEFAULT_DB_PATH

    resolved = path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Create and return a configured SQLite connection with foreign keys enabled."""
    target_path = resolve_db_path(db_path)
    conn = sqlite3.connect(
        database=str(target_path),
        timeout=10.0,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def get_db_connection(db_path: str | Path | None = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for acquiring a database connection that automatically commits or rolls back."""
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.error("Transaction rolled back due to error: %s", exc.__class__.__name__)
        raise
    finally:
        conn.close()


@contextmanager
def transaction(conn: sqlite3.Connection) -> Generator[sqlite3.Connection, None, None]:
    """Context manager executing an isolated transaction block on an existing connection."""
    try:
        conn.execute("BEGIN;")
        yield conn
        conn.execute("COMMIT;")
    except Exception as exc:
        conn.execute("ROLLBACK;")
        logger.error("Explicit transaction rolled back due to error: %s", exc.__class__.__name__)
        raise


def init_db(db_path: str | Path | None = None) -> None:
    """Initialize database tables and indexes. Safe to run repeatedly (idempotent)."""
    with get_db_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
    logger.info("Database schema initialized successfully.")


def check_db_readiness(db_path: str | Path | None = None) -> bool:
    """Verify database connectivity and foreign key status."""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.execute("SELECT 1;")
            result = cursor.fetchone()
            return result is not None and result[0] == 1
    except Exception as exc:
        logger.warning("Database readiness check failed: %s", exc.__class__.__name__)
        return False
