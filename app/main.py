"""FastAPI application for IncuBrix Social Media Marketing and Content Engine."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from contextlib import asynccontextmanager
from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from app.database import check_db_readiness, get_db_connection, init_db
from app.models import ContentAsset, GenerationRun, Platform, SourceDocument
from app.repositories import (
    get_content_asset_by_id,
    get_generation_run_by_id,
    get_source_document_by_hash,
    get_source_document_by_id,
    insert_source_document,
    is_duplicate_source,
    list_content_assets,
)
from app.services.content_engine import run_generation_service
from app.services.export_service import (
    InvalidFilterError,
    export_assets_to_calendar_csv,
    export_assets_to_csv,
    export_assets_to_json,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context initializing SQLite tables on startup."""
    init_db()
    yield


app = FastAPI(
    title="IncuBrix Content Engine",
    description="Social Media Marketing and Content Engine for IncuBrix Growth Engineering.",
    version="0.1.0",
    lifespan=lifespan,
)


# ============================================================================
# API Request & Response Schemas
# ============================================================================

class SourceCreateRequest(BaseModel):
    """Request payload for registering a new source document."""
    title: str = Field(..., min_length=1, max_length=300, description="Title of the source material.")
    content: str = Field(..., min_length=100, description="Original text body (minimum 100 characters).")
    source_type: str = Field(default="document", max_length=100, description="Type of source document.")
    source_url: str | None = Field(default=None, description="Optional public URL of source material.")


class GenerationRequest(BaseModel):
    """Request payload for triggering content asset generation."""
    source_id: str = Field(..., min_length=1, description="Identifier of the ingested source document.")
    base_tracking_url: str | None = Field(
        default=None,
        description="Optional base URL for UTM parameter generation (e.g. https://incubrix.com).",
    )
    campaign: str = Field(
        default="growth_engine",
        description="Campaign tag for UTM tracking parameters.",
    )


class GenerationResponse(BaseModel):
    """Response payload for a generation run execution."""
    run_id: str
    source_id: str
    status: str
    runtime_ms: float
    assets_created: int
    assets_skipped: int
    review_required_count: int
    assets: list[ContentAsset]


# ============================================================================
# Core Health & Service Endpoints
# ============================================================================

@app.get("/", tags=["General"])
def root() -> Dict[str, str]:
    """Root endpoint providing service status links."""
    return {
        "message": "IncuBrix Social Media Marketing and Content Engine API is running.",
        "docs_url": "/docs",
        "health_url": "/health",
    }


@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, str]:
    """Basic health check endpoint returning system status and database readiness."""
    db_ok = check_db_readiness()
    return {
        "status": "healthy",
        "service": "incubrix-content-engine",
        "version": "0.1.0",
        "database": "connected" if db_ok else "uninitialized",
    }


# ============================================================================
# Content Engine REST API (v1)
# ============================================================================

@app.post(
    "/api/v1/sources",
    response_model=SourceDocument,
    status_code=status.HTTP_201_CREATED,
    tags=["Sources"],
)
def create_source(payload: SourceCreateRequest) -> SourceDocument:
    """Ingest a new source document with duplicate detection and hash verification."""
    words = payload.content.strip().split()
    if len(words) < 15:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source content contains too few words (minimum 15 words required).",
        )

    try:
        source_doc = SourceDocument(
            title=payload.title,
            content=payload.content,
            source_type=payload.source_type,
            source_url=payload.source_url,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source document: {str(exc)}",
        ) from exc

    with get_db_connection() as conn:
        if is_duplicate_source(conn, source_doc.content_hash):
            existing = get_source_document_by_hash(conn, source_doc.content_hash)
            existing_id = existing.id if existing else "unknown"
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Source document with matching content already exists (ID: {existing_id}).",
            )

        insert_source_document(conn, source_doc)

    return source_doc


@app.post(
    "/api/v1/generations",
    response_model=GenerationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Generations"],
)
def generate_assets(payload: GenerationRequest) -> GenerationResponse:
    """Generate platform-tailored content assets from an ingested source document."""
    with get_db_connection() as conn:
        source = get_source_document_by_id(conn, payload.source_id)
        if source is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source document '{payload.source_id}' not found.",
            )

        try:
            result = run_generation_service(
                source=source,
                base_tracking_url=payload.base_tracking_url,
                campaign=payload.campaign,
                conn=conn,
                persist=True,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Generation failed: {str(exc)}",
            ) from exc

    return GenerationResponse(
        run_id=result.run.id,
        source_id=result.run.source_id,
        status=result.run.status.value,
        runtime_ms=result.run.runtime_ms or 0.0,
        assets_created=result.created_count,
        assets_skipped=result.skipped_duplicate_count,
        review_required_count=result.review_required_count,
        assets=result.assets,
    )


@app.get(
    "/api/v1/assets",
    response_model=list[ContentAsset],
    tags=["Assets"],
)
def list_assets(
    platform: str | None = Query(default=None, description="Filter by social media platform."),
    status: str | None = Query(default=None, description="Filter by asset lifecycle status."),
    source_id: str | None = Query(default=None, description="Filter by origin source ID."),
    limit: int = Query(default=50, ge=1, le=200, description="Page limit."),
    offset: int = Query(default=0, ge=0, description="Page offset."),
) -> list[ContentAsset]:
    """Retrieve content assets with optional platform, status, and source filters."""
    with get_db_connection() as conn:
        return list_content_assets(
            conn=conn,
            platform=platform,
            status=status,
            source_id=source_id,
            limit=limit,
            offset=offset,
        )


@app.get(
    "/api/v1/assets/{asset_id}",
    response_model=ContentAsset,
    tags=["Assets"],
)
def get_asset(asset_id: str) -> ContentAsset:
    """Retrieve an individual content asset by ID."""
    with get_db_connection() as conn:
        asset = get_content_asset_by_id(conn, asset_id)
        if asset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content asset '{asset_id}' not found.",
            )
        return asset


@app.get(
    "/api/v1/runs/{run_id}",
    response_model=GenerationRun,
    tags=["Generations"],
)
def get_run(run_id: str) -> GenerationRun:
    """Retrieve execution metrics and telemetry for a generation run."""
    with get_db_connection() as conn:
        run_rec = get_generation_run_by_id(conn, run_id)
        if run_rec is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Generation run '{run_id}' not found.",
            )
        return run_rec


# ============================================================================
# Asset Export Endpoints (CSV & JSON)
# ============================================================================

@app.get(
    "/api/v1/exports/csv",
    tags=["Exports"],
)
def export_csv(
    platform: str | None = Query(default=None, description="Filter by social media platform."),
    status_filter: str | None = Query(default=None, alias="status", description="Filter by asset lifecycle status."),
    source_id: str | None = Query(default=None, description="Filter by origin source ID."),
) -> Response:
    """Download stored content assets as a generic scheduler-ready CSV with UTF-8 BOM."""
    with get_db_connection() as conn:
        try:
            csv_bytes = export_assets_to_csv(
                conn=conn,
                platform=platform,
                status=status_filter,
                source_id=source_id,
                sanitize_formulas=True,
            )
        except InvalidFilterError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"CSV export failed: {str(exc)}",
            ) from exc

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"incubrix_assets_{timestamp}.csv"

    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


@app.get(
    "/api/v1/exports/json",
    tags=["Exports"],
)
def export_json(
    platform: str | None = Query(default=None, description="Filter by social media platform."),
    status_filter: str | None = Query(default=None, alias="status", description="Filter by asset lifecycle status."),
    source_id: str | None = Query(default=None, description="Filter by origin source ID."),
) -> Response:
    """Download stored content assets as a structured JSON payload with metadata."""
    with get_db_connection() as conn:
        try:
            data = export_assets_to_json(
                conn=conn,
                platform=platform,
                status=status_filter,
                source_id=source_id,
            )
        except InvalidFilterError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"JSON export failed: {str(exc)}",
            ) from exc

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"incubrix_assets_{timestamp}.json"
    content_bytes = json.dumps(data, indent=2).encode("utf-8")

    return Response(
        content=content_bytes,
        media_type="application/json; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


@app.get(
    "/api/v1/exports/calendar",
    tags=["Exports"],
)
def export_calendar(
    platform: str | None = Query(default=None, description="Filter by social media platform."),
    status_filter: str | None = Query(default=None, alias="status", description="Filter by asset lifecycle status."),
    source_id: str | None = Query(default=None, description="Filter by origin source ID."),
) -> Response:
    """Download stored content assets formatted for the official assessment workbook (02_ASSETS tab, 23 columns)."""
    with get_db_connection() as conn:
        try:
            csv_bytes = export_assets_to_calendar_csv(
                conn=conn,
                platform=platform,
                status=status_filter,
                source_id=source_id,
                sanitize_formulas=True,
            )
        except InvalidFilterError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Calendar export failed: {str(exc)}",
            ) from exc

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"incubrix_calendar_{timestamp}.csv"

    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


