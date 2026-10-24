"""Export service for serializing ContentAsset records to generic scheduler-ready CSV and structured JSON."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import io
import json
import logging
from pathlib import Path
import re
import sqlite3
from typing import Any
import uuid

from app.models import AssetStatus, ContentAsset, GenerationMethod, Platform
from app.repositories import compute_asset_fingerprint, list_content_assets

logger = logging.getLogger("incubrix.export_service")

# Generic scheduler-ready CSV columns (19 columns)
CSV_FIELDNAMES = [
    "asset_id",
    "platform",
    "content_format",
    "content_pillar",
    "audience_segment",
    "hook",
    "main_content",
    "caption",
    "hashtags",
    "call_to_action",
    "tracking_url",
    "source_id",
    "evidence_references",
    "review_required",
    "review_notes",
    "generation_method",
    "created_at",
    "status",
    "duration_seconds",
]

# Official Assessment Workbook 02_ASSETS tab columns (exact 23 columns)
WORKBOOK_FIELDNAMES = [
    "asset_id",
    "platform",
    "format",
    "content_pillar",
    "hook",
    "caption",
    "cta",
    "utm_link",
    "final_file_url",
    "source_file_url",
    "source_input",
    "tools_used",
    "rights_checked",
    "ai_label_needed",
    "scheduled_date",
    "test_published_url",
    "impressions_or_views",
    "engagement_rate",
    "clicks",
    "status",
    "notes",
    "duplicate_check",
    "completeness_check",
]

# Characters that trigger spreadsheet formula execution in Excel/Sheets/Calc
FORMULA_TRIGGERS = ("=", "+", "-", "@", "\t", "\r")


class ExportError(Exception):
    """Base exception for export service errors."""
    pass


class InvalidFilterError(ExportError):
    """Raised when an invalid query filter (e.g. unknown platform or status) is specified."""
    pass


def sanitize_formula_injection(value: str) -> str:
    """Escape spreadsheet formula-leading characters (=, +, -, @) to prevent CSV formula injection.
    
    Chosen policy:
    Values starting with formula-leading characters are prefixed with a single quote (').
    Spreadsheet software parses single-quote prefixed cells as verbatim string literals
    without executing dynamic formulas or DDE command links.
    """
    if value and value.startswith(FORMULA_TRIGGERS):
        return f"'{value}"
    return value


def validate_export_filters(
    platform: str | None = None,
    status: str | None = None,
) -> tuple[Platform | None, AssetStatus | None]:
    """Validate and normalize platform and status filter parameters."""
    validated_platform: Platform | None = None
    if platform is not None and platform.strip():
        try:
            validated_platform = Platform(platform.strip())
        except ValueError as exc:
            raise InvalidFilterError(
                f"Unsupported platform filter: '{platform}'. "
                f"Allowed: {[p.value for p in Platform]}"
            ) from exc

    validated_status: AssetStatus | None = None
    if status is not None and status.strip():
        try:
            validated_status = AssetStatus(status.strip())
        except ValueError as exc:
            raise InvalidFilterError(
                f"Unsupported status filter: '{status}'. "
                f"Allowed: {[s.value for s in AssetStatus]}"
            ) from exc

    return validated_platform, validated_status


def export_assets_to_csv(
    conn: sqlite3.Connection,
    platform: str | None = None,
    status: str | None = None,
    source_id: str | None = None,
    sanitize_formulas: bool = True,
) -> bytes:
    """Serialize matching ContentAsset records to scheduler-ready CSV with UTF-8 BOM encoding."""
    val_plat, val_stat = validate_export_filters(platform, status)

    assets = list_content_assets(
        conn=conn,
        platform=val_plat,
        status=val_stat,
        source_id=source_id.strip() if source_id else None,
        limit=10000,
        offset=0,
    )

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=CSV_FIELDNAMES,
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\r\n",
    )
    writer.writeheader()

    for asset in assets:
        row: dict[str, Any] = {
            "asset_id": asset.id,
            "platform": asset.platform.value,
            "content_format": asset.content_format.value,
            "content_pillar": asset.content_pillar,
            "audience_segment": asset.audience_segment,
            "hook": asset.hook,
            "main_content": asset.main_content,
            "caption": asset.caption,
            "hashtags": json.dumps(asset.hashtags),
            "call_to_action": asset.call_to_action,
            "tracking_url": asset.tracking_url or "",
            "source_id": asset.source_id,
            "evidence_references": json.dumps([ref.model_dump() for ref in asset.evidence_references]),
            "review_required": "true" if asset.review_required else "false",
            "review_notes": asset.review_notes or "",
            "generation_method": asset.generation_method.value,
            "created_at": asset.created_at.isoformat(),
            "status": asset.status.value,
            "duration_seconds": str(asset.duration_seconds) if asset.duration_seconds is not None else "",
        }

        if sanitize_formulas:
            for key, val in row.items():
                if isinstance(val, str):
                    row[key] = sanitize_formula_injection(val)

        writer.writerow(row)

    csv_text = output.getvalue()
    # Encode with UTF-8 BOM (utf-8-sig) for native Excel/Windows spreadsheet compatibility
    return csv_text.encode("utf-8-sig")


def export_assets_to_calendar_csv(
    conn: sqlite3.Connection,
    platform: str | None = None,
    status: str | None = None,
    source_id: str | None = None,
    sanitize_formulas: bool = True,
) -> bytes:
    """Serialize matching ContentAsset records to official assessment workbook (02_ASSETS tab, 23 columns).
    
    Guarantees:
    - Exact 23 columns in required order matching the official assessment workbook.
    - Deterministic ordering by created_at and asset_id.
    - Unavailable final-file URLs, editable-source URLs, scheduled dates, publication URLs,
      and audience metrics are left strictly blank (never fabricated).
    - Status is faithfully reflected; generated drafts are NEVER marked 'Ready'.
    - AI disclosure (ai_label_needed) is explicit based on generation_method.
    - Rights clearance (rights_checked) is marked 'Pending' (never claimed without actual check).
    - Formula injection leading characters (=, +, -, @) are sanitized with single-quote prefix.
    """
    val_plat, val_stat = validate_export_filters(platform, status)

    assets = list_content_assets(
        conn=conn,
        platform=val_plat,
        status=val_stat,
        source_id=source_id.strip() if source_id else None,
        limit=10000,
        offset=0,
    )

    # Deterministic ordering by created_at and asset_id for repeatable exports
    assets = sorted(assets, key=lambda a: (a.created_at.isoformat(), a.id))

    # Fetch source metadata to map legitimate source_url where available
    source_urls: dict[str, str] = {}
    try:
        cursor = conn.execute("SELECT source_id, source_url FROM source_documents;")
        for s_row in cursor.fetchall():
            source_urls[s_row["source_id"]] = s_row["source_url"] or ""
    except Exception as exc:
        logger.warning("Could not query source_documents for source_urls: %s", exc)

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=WORKBOOK_FIELDNAMES,
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\r\n",
    )
    writer.writeheader()

    seen_fingerprints: set[str] = set()

    for asset in assets:
        # Completeness check: verified presence of required core fields
        is_complete = bool(asset.hook and asset.caption and asset.call_to_action and asset.main_content)
        completeness_val = "Complete Draft" if is_complete else "Incomplete"

        # Duplicate check: check against previously seen fingerprints in this export batch
        fp = compute_asset_fingerprint(
            asset.platform,
            asset.content_format,
            asset.hook,
            asset.main_content,
        )
        if fp in seen_fingerprints:
            duplicate_val = "Duplicate Detected"
        else:
            seen_fingerprints.add(fp)
            duplicate_val = "Passed (Unique Fingerprint)"

        # Readiness guardrail:
        # Do not mark generated drafts as Ready. Only use Ready after the final asset exists,
        # required fields are complete, rights have been checked, and the asset has passed the quality review.
        final_file_exists = False  # Unavailable/blank for newly generated drafts
        rights_cleared = False     # Rights check is 'Pending' until verified by human editor
        quality_reviewed = (not asset.review_required) and (asset.status == AssetStatus.APPROVED)

        if final_file_exists and is_complete and rights_cleared and quality_reviewed:
            status_display = "Ready"
        elif asset.status == AssetStatus.DRAFT:
            status_display = "Draft"
        elif asset.status == AssetStatus.NEEDS_REVIEW:
            status_display = "Needs Review"
        elif asset.status == AssetStatus.APPROVED:
            status_display = "Approved"
        elif asset.status == AssetStatus.SCHEDULED:
            status_display = "Scheduled"
        elif asset.status == AssetStatus.PUBLISHED:
            status_display = "Published"
        elif asset.status == AssetStatus.REJECTED:
            status_display = "Rejected"
        else:
            status_display = asset.status.value

        # AI label disclosure
        ai_label = "Yes" if asset.generation_method == GenerationMethod.AI else "No"

        # Tools used
        tools_val = f"IncuBrix Content Engine ({asset.generation_method.value})"

        # Legitimate source document URL if supplied in metadata, otherwise empty
        legitimate_source_url = source_urls.get(asset.source_id, "")

        row: dict[str, Any] = {
            "asset_id": asset.id,
            "platform": asset.platform.value,
            "format": asset.content_format.value,
            "content_pillar": asset.content_pillar,
            "hook": asset.hook,
            "caption": asset.caption,
            "cta": asset.call_to_action,
            "utm_link": asset.tracking_url or "",
            "final_file_url": "",           # Unavailable: left blank per requirements
            "source_file_url": legitimate_source_url, # Original source URL if supplied, else blank
            "source_input": asset.source_id,
            "tools_used": tools_val,
            "rights_checked": "Pending",     # Never claim rights clearance without an actual human check
            "ai_label_needed": ai_label,
            "scheduled_date": "",           # Unavailable: left blank per requirements
            "test_published_url": "",       # Unavailable: left blank per requirements
            "impressions_or_views": "",     # Unavailable: left blank per requirements
            "engagement_rate": "",          # Unavailable: left blank per requirements
            "clicks": "",                   # Unavailable: left blank per requirements
            "status": status_display,
            "notes": asset.review_notes or "",
            "duplicate_check": duplicate_val,
            "completeness_check": completeness_val,
        }

        if sanitize_formulas:
            for key, val in row.items():
                if isinstance(val, str):
                    row[key] = sanitize_formula_injection(val)

        writer.writerow(row)

    csv_text = output.getvalue()
    return csv_text.encode("utf-8-sig")



def export_assets_to_json(
    conn: sqlite3.Connection,
    platform: str | None = None,
    status: str | None = None,
    source_id: str | None = None,
) -> dict[str, Any]:
    """Serialize matching ContentAsset records to a structured JSON export dictionary."""
    val_plat, val_stat = validate_export_filters(platform, status)

    assets = list_content_assets(
        conn=conn,
        platform=val_plat,
        status=val_stat,
        source_id=source_id.strip() if source_id else None,
        limit=10000,
        offset=0,
    )

    now_utc = datetime.now(timezone.utc)

    return {
        "export_metadata": {
            "exported_at": now_utc.isoformat(),
            "generator": "incubrix-content-engine",
            "engine_version": "0.1.0",
        },
        "schema_version": "1.0.0",
        "applied_filters": {
            "platform": val_plat.value if val_plat else None,
            "status": val_stat.value if val_stat else None,
            "source_id": source_id.strip() if source_id else None,
        },
        "asset_count": len(assets),
        "assets": [asset.model_dump(mode="json") for asset in assets],
    }


def save_export_file(
    content: str | bytes | dict[str, Any],
    extension: str,
    outputs_dir: str | Path = "outputs",
    prefix: str = "incubrix_assets",
) -> Path:
    """Safely persist export data to a timestamped file within the configured outputs directory."""
    resolved_dir = Path(outputs_dir).resolve()
    resolved_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:6]
    clean_ext = extension.lstrip(".").lower()
    filename = f"{prefix}_{timestamp}_{uid}.{clean_ext}"

    target_path = (resolved_dir / filename).resolve()

    # Guard against directory traversal
    try:
        target_path.relative_to(resolved_dir)
    except ValueError as exc:
        raise ExportError("Path traversal vulnerability detected; unsafe export destination.") from exc

    if isinstance(content, dict):
        payload = json.dumps(content, indent=2).encode("utf-8")
        target_path.write_bytes(payload)
    elif isinstance(content, bytes):
        target_path.write_bytes(content)
    else:
        target_path.write_text(content, encoding="utf-8")

    logger.info("Export file safely persisted to %s", target_path)
    return target_path
