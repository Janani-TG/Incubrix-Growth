"""Repository layer for SQLite persistence, retrieval, and deduplication."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import logging
import re
import sqlite3
from typing import Any

from app.models import (
    AssetStatus,
    ContentAsset,
    ContentFormat,
    EvidenceReference,
    GenerationMethod,
    GenerationRun,
    Platform,
    RunStatus,
    SourceDocument,
)

logger = logging.getLogger("incubrix.repository")


# ============================================================================
# Exceptions
# ============================================================================

class RepositoryError(Exception):
    """Base exception for repository operations."""
    pass


class DuplicateRecordError(RepositoryError):
    """Raised when attempting to insert a duplicate record violating uniqueness."""
    pass


class RecordNotFoundError(RepositoryError):
    """Raised when an expected record is not found."""
    pass


class DatabaseConstraintError(RepositoryError):
    """Raised when a foreign key or integrity constraint is violated."""
    pass


# ============================================================================
# Helper Functions & Fingerprinting
# ============================================================================

def compute_asset_fingerprint(
    platform: Platform | str,
    content_format: ContentFormat | str,
    hook: str,
    main_content: str,
) -> str:
    """Compute a deterministic normalized SHA-256 fingerprint for asset deduplication."""
    plat_str = platform.value if isinstance(platform, Platform) else str(platform).strip()
    fmt_str = content_format.value if isinstance(content_format, ContentFormat) else str(content_format).strip()

    # Normalize whitespace and lowercase
    norm_hook = re.sub(r"\s+", " ", hook.strip().lower())
    norm_content = re.sub(r"\s+", " ", main_content.strip().lower())

    payload = f"{plat_str.lower()}|{fmt_str.lower()}|{norm_hook}|{norm_content}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _row_to_source_document(row: sqlite3.Row) -> SourceDocument:
    """Map a SQLite row to a validated SourceDocument model."""
    data = dict(row)
    if "source_id" in data and "id" not in data:
        data["id"] = data.pop("source_id")
    return SourceDocument.model_validate(data)


def _row_to_content_asset(row: sqlite3.Row) -> ContentAsset:
    """Map a SQLite row to a validated ContentAsset model."""
    data = dict(row)
    if "asset_id" in data and "id" not in data:
        data["id"] = data.pop("asset_id")

    if isinstance(data.get("hashtags"), str):
        data["hashtags"] = json.loads(data["hashtags"])
    if isinstance(data.get("evidence_references"), str):
        data["evidence_references"] = json.loads(data["evidence_references"])

    data["review_required"] = bool(data.get("review_required", 0))
    data.pop("content_fingerprint", None)
    return ContentAsset.model_validate(data)


def _row_to_generation_run(row: sqlite3.Row) -> GenerationRun:
    """Map a SQLite row to a validated GenerationRun model."""
    data = dict(row)
    if "run_id" in data and "id" not in data:
        data["id"] = data.pop("run_id")
    if "input_source_id" in data and "source_id" not in data:
        data["source_id"] = data.pop("input_source_id")
    return GenerationRun.model_validate(data)


# ============================================================================
# Source Document Repository Functions
# ============================================================================

def insert_source_document(conn: sqlite3.Connection, source: SourceDocument) -> SourceDocument:
    """Insert a source document. Rejects duplicates with DuplicateRecordError."""
    sql = """
    INSERT INTO source_documents (
        source_id, title, source_type, source_url, content_hash, content, imported_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    params = (
        source.id,
        source.title,
        source.source_type,
        source.source_url,
        source.content_hash,
        source.content,
        source.imported_at.isoformat(),
    )
    try:
        conn.execute(sql, params)
        logger.info("Source document '%s' inserted successfully.", source.id)
        return source
    except sqlite3.IntegrityError as exc:
        err_msg = str(exc)
        if "content_hash" in err_msg or "source_id" in err_msg or "UNIQUE" in err_msg:
            raise DuplicateRecordError(
                f"Source document with content hash '{source.content_hash}' or ID '{source.id}' already exists."
            ) from exc
        raise DatabaseConstraintError(f"Integrity error inserting source document: {err_msg}") from exc


def get_source_document_by_id(conn: sqlite3.Connection, source_id: str) -> SourceDocument | None:
    """Retrieve a source document by its primary key ID."""
    sql = "SELECT * FROM source_documents WHERE source_id = ?;"
    cursor = conn.execute(sql, (source_id.strip(),))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_source_document(row)


def get_source_document_by_hash(conn: sqlite3.Connection, content_hash: str) -> SourceDocument | None:
    """Retrieve a source document by its SHA-256 content hash."""
    sql = "SELECT * FROM source_documents WHERE content_hash = ?;"
    cursor = conn.execute(sql, (content_hash.strip().lower(),))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_source_document(row)


def is_duplicate_source(conn: sqlite3.Connection, content_hash: str) -> bool:
    """Check if a source document with the given content hash already exists."""
    sql = "SELECT 1 FROM source_documents WHERE content_hash = ? LIMIT 1;"
    cursor = conn.execute(sql, (content_hash.strip().lower(),))
    return cursor.fetchone() is not None


# ============================================================================
# Content Asset Repository Functions
# ============================================================================

def is_duplicate_asset(
    conn: sqlite3.Connection,
    asset_or_fingerprint: ContentAsset | str,
    platform: Platform | str | None = None,
) -> bool:
    """Check if an asset with matching normalized content fingerprint exists."""
    if isinstance(asset_or_fingerprint, ContentAsset):
        fp = compute_asset_fingerprint(
            asset_or_fingerprint.platform,
            asset_or_fingerprint.content_format,
            asset_or_fingerprint.hook,
            asset_or_fingerprint.main_content,
        )
        plat = asset_or_fingerprint.platform.value
    else:
        fp = str(asset_or_fingerprint)
        plat = platform.value if isinstance(platform, Platform) else (str(platform) if platform else None)

    if plat:
        sql = "SELECT 1 FROM content_assets WHERE content_fingerprint = ? AND platform = ? LIMIT 1;"
        cursor = conn.execute(sql, (fp, plat))
    else:
        sql = "SELECT 1 FROM content_assets WHERE content_fingerprint = ? LIMIT 1;"
        cursor = conn.execute(sql, (fp,))

    return cursor.fetchone() is not None


def insert_content_asset(
    conn: sqlite3.Connection,
    asset: ContentAsset,
    allow_duplicate: bool = False,
) -> ContentAsset:
    """Insert a content asset with foreign key checking and duplicate detection."""
    fingerprint = compute_asset_fingerprint(
        asset.platform,
        asset.content_format,
        asset.hook,
        asset.main_content,
    )

    if not allow_duplicate and is_duplicate_asset(conn, fingerprint, asset.platform):
        raise DuplicateRecordError(
            f"Duplicate asset detected for platform '{asset.platform.value}' with matching content fingerprint."
        )

    sql = """
    INSERT INTO content_assets (
        asset_id, platform, content_format, content_pillar, audience_segment,
        hook, main_content, caption, hashtags, call_to_action, tracking_url,
        source_id, evidence_references, review_required, review_notes,
        generation_method, created_at, status, duration_seconds, content_fingerprint
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    params = (
        asset.id,
        asset.platform.value,
        asset.content_format.value,
        asset.content_pillar,
        asset.audience_segment,
        asset.hook,
        asset.main_content,
        asset.caption,
        json.dumps(asset.hashtags),
        asset.call_to_action,
        asset.tracking_url,
        asset.source_id,
        json.dumps([ref.model_dump() for ref in asset.evidence_references]),
        1 if asset.review_required else 0,
        asset.review_notes,
        asset.generation_method.value,
        asset.created_at.isoformat(),
        asset.status.value,
        asset.duration_seconds,
        fingerprint,
    )

    try:
        conn.execute(sql, params)
        logger.info("Content asset '%s' inserted successfully.", asset.id)
        return asset
    except sqlite3.IntegrityError as exc:
        err_msg = str(exc)
        if "FOREIGN KEY" in err_msg:
            raise DatabaseConstraintError(
                f"Foreign key violation: source_id '{asset.source_id}' does not exist in source_documents."
            ) from exc
        if "asset_id" in err_msg or "UNIQUE" in err_msg:
            raise DuplicateRecordError(f"Asset with ID '{asset.id}' already exists.") from exc
        raise DatabaseConstraintError(f"Integrity error inserting asset: {err_msg}") from exc


def get_content_asset_by_id(conn: sqlite3.Connection, asset_id: str) -> ContentAsset | None:
    """Retrieve a content asset by its primary key ID."""
    sql = "SELECT * FROM content_assets WHERE asset_id = ?;"
    cursor = conn.execute(sql, (asset_id.strip(),))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_content_asset(row)


def list_content_assets(
    conn: sqlite3.Connection,
    platform: Platform | str | None = None,
    status: AssetStatus | str | None = None,
    source_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[ContentAsset]:
    """List content assets with optional platform, status, and source_id filters."""
    conditions: list[str] = []
    params: list[Any] = []

    if platform is not None:
        plat_val = platform.value if isinstance(platform, Platform) else Platform(platform).value
        conditions.append("platform = ?")
        params.append(plat_val)

    if status is not None:
        stat_val = status.value if isinstance(status, AssetStatus) else AssetStatus(status).value
        conditions.append("status = ?")
        params.append(stat_val)

    if source_id is not None:
        conditions.append("source_id = ?")
        params.append(source_id.strip())

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"""
    SELECT * FROM content_assets
    {where_clause}
    ORDER BY created_at DESC
    LIMIT ? OFFSET ?;
    """
    params.extend([max(1, limit), max(0, offset)])

    cursor = conn.execute(sql, params)
    return [_row_to_content_asset(row) for row in cursor.fetchall()]


# ============================================================================
# Generation Run Repository Functions
# ============================================================================

def insert_generation_run(conn: sqlite3.Connection, run: GenerationRun) -> GenerationRun:
    """Insert an execution telemetry record for a generation run."""
    sql = """
    INSERT INTO generation_runs (
        run_id, input_source_id, started_at, completed_at, runtime_ms,
        generation_method, assets_created, review_required_count, status, error_details
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    params = (
        run.id,
        run.source_id,
        run.started_at.isoformat(),
        run.completed_at.isoformat() if run.completed_at else None,
        run.runtime_ms,
        run.generation_method.value,
        run.assets_created,
        run.review_required_count,
        run.status.value,
        run.error_details,
    )

    try:
        conn.execute(sql, params)
        logger.info("Generation run '%s' inserted successfully.", run.id)
        return run
    except sqlite3.IntegrityError as exc:
        err_msg = str(exc)
        if "FOREIGN KEY" in err_msg:
            raise DatabaseConstraintError(
                f"Foreign key violation: input_source_id '{run.source_id}' does not exist in source_documents."
            ) from exc
        if "run_id" in err_msg or "UNIQUE" in err_msg:
            raise DuplicateRecordError(f"Generation run with ID '{run.id}' already exists.") from exc
        raise DatabaseConstraintError(f"Integrity error inserting generation run: {err_msg}") from exc


def get_generation_run_by_id(conn: sqlite3.Connection, run_id: str) -> GenerationRun | None:
    """Retrieve a generation run record by its primary key ID."""
    sql = "SELECT * FROM generation_runs WHERE run_id = ?;"
    cursor = conn.execute(sql, (run_id.strip(),))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_generation_run(row)


def update_generation_run(
    conn: sqlite3.Connection,
    run_id: str,
    status: RunStatus | str,
    completed_at: datetime | None = None,
    runtime_ms: float | None = None,
    assets_created: int | None = None,
    review_required_count: int | None = None,
    error_details: str | None = None,
) -> GenerationRun:
    """Update execution status, runtime metrics, and completion details for a generation run."""
    existing = get_generation_run_by_id(conn, run_id)
    if existing is None:
        raise RecordNotFoundError(f"Generation run '{run_id}' not found.")

    status_val = status.value if isinstance(status, RunStatus) else RunStatus(status).value
    comp_iso = completed_at.isoformat() if completed_at else (
        existing.completed_at.isoformat() if existing.completed_at else None
    )

    sql = """
    UPDATE generation_runs
    SET status = ?,
        completed_at = COALESCE(?, completed_at),
        runtime_ms = COALESCE(?, runtime_ms),
        assets_created = COALESCE(?, assets_created),
        review_required_count = COALESCE(?, review_required_count),
        error_details = ?
    WHERE run_id = ?;
    """
    params = (
        status_val,
        comp_iso,
        runtime_ms if runtime_ms is not None else existing.runtime_ms,
        assets_created if assets_created is not None else existing.assets_created,
        review_required_count if review_required_count is not None else existing.review_required_count,
        error_details if error_details is not None else existing.error_details,
        run_id.strip(),
    )

    conn.execute(sql, params)
    updated = get_generation_run_by_id(conn, run_id)
    if updated is None:
        raise RecordNotFoundError(f"Generation run '{run_id}' disappeared during update.")
    return updated
