"""Unit and integration tests for Stage 4 content generation engine, templates, and REST API."""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.database import get_connection, init_db
from app.main import app
from app.models import (
    AssetStatus,
    ContentAsset,
    ContentFormat,
    GenerationMethod,
    Platform,
    RunStatus,
    SourceDocument,
)
from app.repositories import insert_source_document
from app.services.content_engine import (
    build_tracking_url,
    extract_sections_and_facts,
    generate_assets_from_source,
    run_generation_service,
)

SAMPLE_DOCUMENT_TEXT = """# Building Scalable Growth Engineering Telemetry for B2B SaaS

## 1. The Core Retention Telemetry Loop
Retention is the single most critical foundation for B2B SaaS unit economics. When cohort retention flattens below 60%, scaling paid performance marketing burns capital without creating compounding enterprise value.

- Teams must verify cohort retention loops prior to capital allocation.
- Target a net revenue retention rate of 115% or higher for expansion viability.
- Instrument activation events within the first 48 hours of onboarding.

## 2. Organic Engineering-Led Distribution Frameworks
Paid channels exhibit rapidly diminishing returns as competition increases. In contrast, organic engineering-led distribution compounds over 12 to 18 months through technical documentation and reproducible workflows.

Technical documentation and transparent architecture teardowns generate 3.4x higher pipeline intent compared to generic marketing blog content. Developer audiences evaluate infrastructure by inspecting code patterns, deployment scripts, and telemetry schemas before requesting enterprise demos.

## 3. Telemetry Architecture and Cohort Feedback
Growth engineering infrastructure must decouple event collection from analysis. Event queues must guarantee at-least-once delivery with latency under 200 milliseconds to avoid degrading user experience during sign-up workflows.
"""


@pytest.fixture
def sample_source() -> SourceDocument:
    """Fixture providing a validated SourceDocument."""
    return SourceDocument(
        id="src_growth_whitepaper",
        title="Building Scalable Growth Engineering Telemetry for B2B SaaS",
        content=SAMPLE_DOCUMENT_TEXT,
        source_type="whitepaper",
        source_url="https://incubrix.com/whitepapers/growth-telemetry",
    )


@pytest.fixture
def client_with_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Fixture providing a TestClient connected to an isolated temporary SQLite database."""
    db_file = tmp_path / "test_api_growth.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_file))
    init_db(db_file)
    with TestClient(app) as test_client:
        yield test_client


# ============================================================================
# 1. Fact Extraction Tests
# ============================================================================

def test_fact_extraction_from_valid_source():
    """Verify deterministic fact extraction preserves exact source quotes and section references."""
    facts = extract_sections_and_facts(SAMPLE_DOCUMENT_TEXT)
    assert len(facts) >= 3

    for fact in facts:
        # Grounding check: source_quote must be an exact verbatim substring
        assert fact.source_quote in SAMPLE_DOCUMENT_TEXT
        assert len(fact.claim) > 0
        assert len(fact.section_or_page) > 0
        assert fact.is_verified is True


def test_fact_extraction_rejects_empty_or_short_input():
    """Verify clear error rejection when source text is too short or lacks sufficient words."""
    short_inputs = [
        "",
        "Too short.",
        "A " * 20,  # 40 chars
        "Short snippet with only eight words in total.",  # 45 chars, 8 words
    ]

    for short_text in short_inputs:
        with pytest.raises(ValueError) as exc_info:
            extract_sections_and_facts(short_text)
        assert "too short" in str(exc_info.value).lower() or "too few words" in str(exc_info.value).lower()


# ============================================================================
# 2. Tracking URL and UTM Parameter Tests
# ============================================================================

def test_build_tracking_url_valid_and_absent():
    """Verify UTM parameter construction and handling when landing page URL is omitted."""
    # Omitted base URL must safely return None
    assert build_tracking_url(None, Platform.LINKEDIN, ContentFormat.TEXT_POST) is None
    assert build_tracking_url("   ", Platform.X, ContentFormat.GRAPHIC) is None

    # Valid base URL generates proper UTM parameters
    base = "https://incubrix.com/resources"
    url = build_tracking_url(
        base_url=base,
        platform=Platform.LINKEDIN,
        content_format=ContentFormat.SHORT_VIDEO,
        campaign="q4_growth",
        asset_id="ast_test999",
    )
    assert url is not None
    assert url.startswith("https://incubrix.com/resources?")
    assert "utm_source=linkedin" in url
    assert "utm_medium=video" in url
    assert "utm_campaign=q4_growth" in url
    assert "utm_content=short_video_ast_test" in url

    # Invalid URL scheme must raise ValueError
    with pytest.raises(ValueError):
        build_tracking_url("invalid-url-without-scheme", Platform.X, ContentFormat.TEXT_POST)


# ============================================================================
# 3. Content Asset Generation & Multi-Platform Diversity Tests
# ============================================================================

def test_generate_at_least_10_assets_across_platforms(sample_source: SourceDocument):
    """Verify generating at least 10 distinct assets across at least 3 social platforms."""
    assets = generate_assets_from_source(
        source=sample_source,
        base_tracking_url="https://incubrix.com/demo",
    )

    # Must generate at least 10 assets
    assert len(assets) >= 10

    # Must cover at least 3 platforms
    platforms_covered = {a.platform for a in assets}
    assert len(platforms_covered) >= 3
    assert Platform.LINKEDIN in platforms_covered
    assert Platform.X in platforms_covered
    assert Platform.INSTAGRAM in platforms_covered
    assert Platform.YOUTUBE_SHORTS in platforms_covered
    assert Platform.REDDIT in platforms_covered

    # Must include required content formats
    formats_covered = {a.content_format for a in assets}
    assert ContentFormat.SHORT_VIDEO in formats_covered
    assert ContentFormat.CAROUSEL in formats_covered
    assert ContentFormat.GRAPHIC in formats_covered
    assert ContentFormat.TEXT_POST in formats_covered
    assert ContentFormat.DISCUSSION_POST in formats_covered

    # Video durations must be <= 60 seconds
    for a in assets:
        if a.content_format == ContentFormat.SHORT_VIDEO:
            assert a.duration_seconds is not None
            assert 0 < a.duration_seconds <= 60.0

    # Generation method must be template
    for a in assets:
        assert a.generation_method == GenerationMethod.TEMPLATE

    # Status must be draft or needs_review only (never approved or published)
    for a in assets:
        assert a.status in (AssetStatus.DRAFT, AssetStatus.NEEDS_REVIEW)


def test_evidence_safety_guardrails_and_review_flags(sample_source: SourceDocument):
    """Verify that factual claims cite source quotes and unverified claims require review."""
    assets = generate_assets_from_source(sample_source)

    verified_assets = [a for a in assets if not a.review_required]
    review_required_assets = [a for a in assets if a.review_required]

    # Majority of assets are grounded in verified source excerpts
    assert len(verified_assets) >= 9
    for a in verified_assets:
        assert len(a.evidence_references) >= 1
        for ref in a.evidence_references:
            assert ref.is_verified is True
            # Verbatim grounding check
            assert ref.source_quote in sample_source.content

    # Assets containing unverified claims must require review
    assert len(review_required_assets) >= 1
    for a in review_required_assets:
        assert a.status == AssetStatus.NEEDS_REVIEW
        assert a.review_notes is not None
        assert "review" in a.review_notes.lower()


# ============================================================================
# 4. Service Persistence and Duplicate Prevention Tests
# ============================================================================

def test_service_run_persistence_and_duplicate_deduplication(tmp_path: Path, sample_source: SourceDocument):
    """Verify generation service persists assets, runs telemetry, and skips duplicates on re-run."""
    db_file = tmp_path / "test_service_dedup.db"
    init_db(db_file)
    conn = get_connection(db_file)

    try:
        # Pre-insert source document
        insert_source_document(conn, sample_source)

        # First generation run
        result1 = run_generation_service(
            source=sample_source,
            base_tracking_url="https://incubrix.com/signup",
            conn=conn,
            persist=True,
        )

        assert result1.run.status == RunStatus.SUCCESS
        assert result1.created_count >= 10
        assert result1.skipped_duplicate_count == 0
        assert result1.review_required_count >= 1

        # Second generation run with the exact same source
        result2 = run_generation_service(
            source=sample_source,
            base_tracking_url="https://incubrix.com/signup",
            conn=conn,
            persist=True,
        )

        assert result2.run.status == RunStatus.SUCCESS
        assert result2.created_count == 0  # No duplicates created
        assert result2.skipped_duplicate_count == len(result1.assets)
    finally:
        conn.close()


# ============================================================================
# 5. REST API Integration Tests
# ============================================================================

def test_api_create_source_and_duplicate_conflict(client_with_db: TestClient):
    """Verify POST /api/v1/sources accepts valid source and returns 409 for duplicate content."""
    payload = {
        "title": "Scaling SaaS Growth",
        "content": SAMPLE_DOCUMENT_TEXT,
        "source_type": "whitepaper",
        "source_url": "https://incubrix.com/whitepaper",
    }

    # 1. Successful creation
    resp = client_with_db.post("/api/v1/sources", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == payload["title"]
    assert "content_hash" in data
    source_id = data["id"]

    # 2. Duplicate submission returns 409 Conflict
    dup_resp = client_with_db.post("/api/v1/sources", json=payload)
    assert dup_resp.status_code == 409
    assert "already exists" in dup_resp.json()["detail"]

    # 3. Unusably short input returns 400 Bad Request
    bad_resp = client_with_db.post("/api/v1/sources", json={"title": "Short", "content": "Too short"})
    assert bad_resp.status_code == 422 or bad_resp.status_code == 400


def test_api_generation_and_asset_retrieval(client_with_db: TestClient):
    """Verify POST /api/v1/generations and GET asset listing/retrieval endpoints."""
    # 1. Ingest source
    src_resp = client_with_db.post(
        "/api/v1/sources",
        json={"title": "Test Telemetry", "content": SAMPLE_DOCUMENT_TEXT},
    )
    assert src_resp.status_code == 201
    source_id = src_resp.json()["id"]

    # 2. Trigger generation
    gen_resp = client_with_db.post(
        "/api/v1/generations",
        json={"source_id": source_id, "base_tracking_url": "https://incubrix.com/start"},
    )
    assert gen_resp.status_code == 201
    gen_data = gen_resp.json()
    assert gen_data["status"] == "success"
    assert gen_data["assets_created"] >= 10
    run_id = gen_data["run_id"]
    assets = gen_data["assets"]
    first_asset_id = assets[0]["id"]

    # 3. Retrieve run by ID
    run_resp = client_with_db.get(f"/api/v1/runs/{run_id}")
    assert run_resp.status_code == 200
    assert run_resp.json()["id"] == run_id

    # 4. Retrieve single asset by ID
    asset_resp = client_with_db.get(f"/api/v1/assets/{first_asset_id}")
    assert asset_resp.status_code == 200
    assert asset_resp.json()["id"] == first_asset_id

    # 5. List assets filtered by platform
    li_resp = client_with_db.get("/api/v1/assets?platform=LinkedIn")
    assert li_resp.status_code == 200
    li_assets = li_resp.json()
    assert len(li_assets) >= 1
    assert all(a["platform"] == "LinkedIn" for a in li_assets)

    # 6. Non-existent IDs return 404
    assert client_with_db.get("/api/v1/assets/missing_asset_123").status_code == 404
    assert client_with_db.get("/api/v1/runs/missing_run_123").status_code == 404
    assert client_with_db.post("/api/v1/generations", json={"source_id": "non_existent_source"}).status_code == 404
