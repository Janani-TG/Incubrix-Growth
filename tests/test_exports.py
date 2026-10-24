"""Unit and integration tests for Stage 5 CSV and JSON export services and API endpoints."""

import csv
import io
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.database import get_connection, init_db
from app.main import app
from app.models import (
    AssetStatus,
    ContentAsset,
    ContentFormat,
    EvidenceReference,
    GenerationMethod,
    Platform,
    SourceDocument,
)
from app.repositories import insert_content_asset, insert_source_document
from app.services.export_service import (
    CSV_FIELDNAMES,
    WORKBOOK_FIELDNAMES,
    ExportError,
    InvalidFilterError,
    export_assets_to_calendar_csv,
    export_assets_to_csv,
    export_assets_to_json,
    save_export_file,
)


@pytest.fixture
def export_db_path(tmp_path: Path) -> Path:
    """Fixture providing the path to an isolated temporary SQLite database."""
    return tmp_path / "test_export.db"


@pytest.fixture
def export_db(export_db_path: Path):
    """Fixture providing an isolated SQLite database with populated test assets."""
    init_db(export_db_path)
    conn = get_connection(export_db_path)

    source = SourceDocument(
        id="src_export_test",
        title="Telemetry Frameworks for Growth Engineering",
        content="Long form source document body for export testing purposes. " * 5,
        source_type="whitepaper",
    )
    insert_source_document(conn, source)

    # 1. Standard LinkedIn Text Post
    asset1 = ContentAsset(
        id="ast_exp_01",
        platform=Platform.LINKEDIN,
        content_format=ContentFormat.TEXT_POST,
        content_pillar="Architecture",
        audience_segment="Founders",
        hook="Cohort retention is paramount for SaaS efficiency.",
        main_content="Line 1: Data point.\nLine 2: Action item,\nwith commas and 'quotes'.",
        caption="Summary caption with Unicode emojis 🚀📊",
        hashtags=["#Growth", "#Engineering"],
        call_to_action="Read full report at the link.",
        tracking_url="https://incubrix.com/doc?utm_source=linkedin",
        source_id="src_export_test",
        evidence_references=[
            EvidenceReference(
                claim="Cohort retention drives enterprise value.",
                source_quote="Long form source document body for export testing purposes.",
                section_or_page="Section 1",
                is_verified=True,
            )
        ],
        review_required=False,
        generation_method=GenerationMethod.TEMPLATE,
        status=AssetStatus.DRAFT,
    )

    # 2. X Graphic Post with formula injection candidate
    asset2 = ContentAsset(
        id="ast_exp_02",
        platform=Platform.X,
        content_format=ContentFormat.GRAPHIC,
        content_pillar="Tactics",
        audience_segment="Developers",
        hook="=SUM(1+1)*cmd|' /C calc'!A0",  # Hostile formula injection test string
        main_content="+100% growth lift observed across primary cohort segments.",
        caption="Visual graphic concept for X.",
        hashtags=["#TechTwitter"],
        call_to_action="Follow for updates.",
        tracking_url=None,
        source_id="src_export_test",
        evidence_references=[],
        review_required=False,
        generation_method=GenerationMethod.TEMPLATE,
        status=AssetStatus.DRAFT,
    )

    # 3. Instagram Video requiring review
    asset3 = ContentAsset(
        id="ast_exp_03",
        platform=Platform.INSTAGRAM,
        content_format=ContentFormat.SHORT_VIDEO,
        duration_seconds=30.0,
        content_pillar="Shorts",
        audience_segment="Creators",
        hook="@everyone: check out this activation strategy.",
        main_content="30-second script for Instagram Reel.",
        caption="Tactical advice for growth.",
        hashtags=["#GrowthTips"],
        call_to_action="Save for later.",
        tracking_url=None,
        source_id="src_export_test",
        evidence_references=[
            EvidenceReference(
                claim="Unverified claim about 50% cost reductions.",
                source_quote="Speculative claim requiring manual validation.",
                section_or_page="Industry Commentary",
                is_verified=False,
                verification_notes="Unverified industry claim flagged for human review.",
            )
        ],
        review_required=True,
        review_notes="Flagged for manual review: contains unverified benchmark.",
        generation_method=GenerationMethod.TEMPLATE,
        status=AssetStatus.NEEDS_REVIEW,
    )

    insert_content_asset(conn, asset1)
    insert_content_asset(conn, asset2)
    insert_content_asset(conn, asset3)
    conn.commit()

    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def client_with_export_db(
    export_db_path: Path, monkeypatch: pytest.MonkeyPatch, export_db
) -> TestClient:
    """Fixture providing TestClient pointed at the test database."""
    monkeypatch.setenv("DATABASE_PATH", str(export_db_path))
    with TestClient(app) as test_client:
        yield test_client


# ============================================================================
# 1. CSV Header, Field Order, Quoting & Unicode Tests
# ============================================================================

def test_csv_export_headers_and_stable_columns(export_db):
    """Verify CSV header names match documented specification in exact deterministic order."""
    csv_bytes = export_assets_to_csv(export_db)
    # Check for UTF-8 BOM prefix
    assert csv_bytes.startswith(b"\xef\xbb\xbf")

    csv_text = csv_bytes.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(csv_text))
    header = next(reader)
    assert header == CSV_FIELDNAMES


def test_csv_export_quoting_multiline_and_unicode(export_db):
    """Verify proper escaping of commas, quotes, line breaks, and Unicode emojis."""
    csv_bytes = export_assets_to_csv(export_db)
    csv_text = csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)

    # Check row 1 (contains multiline content, commas, quotes, emojis)
    row1 = next(r for r in rows if r["asset_id"] == "ast_exp_01")
    assert "Line 1: Data point." in row1["main_content"]
    assert "Line 2: Action item,\nwith commas and 'quotes'." in row1["main_content"]
    assert "🚀📊" in row1["caption"]
    assert row1["platform"] == "LinkedIn"
    assert row1["status"] == "draft"

    # Hashtags parsed from JSON cell
    tags = json.loads(row1["hashtags"])
    assert tags == ["#Growth", "#Engineering"]

    # Evidence references parsed from JSON cell
    ev_refs = json.loads(row1["evidence_references"])
    assert len(ev_refs) == 1
    assert ev_refs[0]["claim"] == "Cohort retention drives enterprise value."


# ============================================================================
# 2. Formula Injection Protection Tests
# ============================================================================

def test_csv_formula_injection_sanitization(export_db):
    """Verify formula-leading characters (=, +, -, @) are sanitized with single-quote prefix."""
    csv_bytes = export_assets_to_csv(export_db, sanitize_formulas=True)
    csv_text = csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)

    row2 = next(r for r in rows if r["asset_id"] == "ast_exp_02")
    # Starts with '=': should be sanitized with leading quote
    assert row2["hook"].startswith("'=")
    # Starts with '+': should be sanitized with leading quote
    assert row2["main_content"].startswith("'+")

    row3 = next(r for r in rows if r["asset_id"] == "ast_exp_03")
    # Starts with '@': should be sanitized with leading quote
    assert row3["hook"].startswith("'@")


# ============================================================================
# 3. JSON Export Schema and Serialization Tests
# ============================================================================

def test_json_export_structure_and_metadata(export_db):
    """Verify JSON export contains required metadata, schema_version, filter info, and asset models."""
    data = export_assets_to_json(export_db)

    assert "export_metadata" in data
    assert "exported_at" in data["export_metadata"]
    assert data["export_metadata"]["generator"] == "incubrix-content-engine"
    assert data["schema_version"] == "1.0.0"
    assert "applied_filters" in data
    assert data["asset_count"] == 3
    assert len(data["assets"]) == 3

    # Check asset serialization details
    first_asset = data["assets"][0]
    assert "asset_id" in first_asset or "id" in first_asset
    assert "platform" in first_asset
    assert "evidence_references" in first_asset
    assert isinstance(first_asset["evidence_references"], list)


# ============================================================================
# 4. Filtering Tests (Platform, Status, Source ID)
# ============================================================================

def test_export_filtering_by_platform_and_status(export_db):
    """Verify filtering exports by platform, lifecycle status, and source_id."""
    # 1. Filter by platform
    li_csv = export_assets_to_csv(export_db, platform="LinkedIn").decode("utf-8-sig")
    li_rows = list(csv.DictReader(io.StringIO(li_csv)))
    assert len(li_rows) == 1
    assert li_rows[0]["platform"] == "LinkedIn"

    li_json = export_assets_to_json(export_db, platform="LinkedIn")
    assert li_json["asset_count"] == 1
    assert li_json["applied_filters"]["platform"] == "LinkedIn"

    # 2. Filter by status
    review_json = export_assets_to_json(export_db, status="needs_review")
    assert review_json["asset_count"] == 1
    assert review_json["assets"][0]["status"] == "needs_review"
    assert review_json["assets"][0]["review_required"] is True

    # 3. Filter by non-matching source_id (empty export)
    empty_csv = export_assets_to_csv(export_db, source_id="non_existent_source").decode("utf-8-sig")
    empty_rows = list(csv.DictReader(io.StringIO(empty_csv)))
    assert len(empty_rows) == 0

    empty_json = export_assets_to_json(export_db, source_id="non_existent_source")
    assert empty_json["asset_count"] == 0
    assert empty_json["assets"] == []


def test_export_rejects_invalid_filters(export_db):
    """Verify invalid platform or status filters raise InvalidFilterError."""
    with pytest.raises(InvalidFilterError) as exc_info:
        export_assets_to_csv(export_db, platform="InvalidPlatform")
    assert "Unsupported platform filter" in str(exc_info.value)

    with pytest.raises(InvalidFilterError) as exc_info:
        export_assets_to_json(export_db, status="invalid_status")
    assert "Unsupported status filter" in str(exc_info.value)


# ============================================================================
# 5. Output File Creation & Anti-Path Traversal Tests
# ============================================================================

def test_save_export_file_and_path_security(tmp_path: Path):
    """Verify save_export_file writes files to outputs directory and rejects path traversal."""
    out_dir = tmp_path / "custom_outputs"
    content = b"header1,header2\r\nval1,val2"

    saved_path = save_export_file(
        content=content,
        extension="csv",
        outputs_dir=out_dir,
        prefix="test_export",
    )

    assert saved_path.exists()
    assert saved_path.parent == out_dir.resolve()
    assert saved_path.name.startswith("test_export_")
    assert saved_path.name.endswith(".csv")
    assert saved_path.read_bytes() == content

    # Verify anti-traversal security
    with pytest.raises(ExportError):
        save_export_file(
            content=content,
            extension="csv",
            outputs_dir=out_dir,
            prefix="../../dangerous_traversal",
        )


# ============================================================================
# 6. Asset Immutability Tests
# ============================================================================

def test_export_preserves_asset_status_immutability(export_db):
    """Verify that exporting records never modifies asset status in the database."""
    # Check status prior to export
    cursor = export_db.execute("SELECT asset_id, status FROM content_assets ORDER BY asset_id;")
    pre_export_states = {r["asset_id"]: r["status"] for r in cursor.fetchall()}

    # Perform CSV and JSON exports
    export_assets_to_csv(export_db)
    export_assets_to_json(export_db)

    # Check status post export: must be strictly unchanged
    cursor = export_db.execute("SELECT asset_id, status FROM content_assets ORDER BY asset_id;")
    post_export_states = {r["asset_id"]: r["status"] for r in cursor.fetchall()}

    assert pre_export_states == post_export_states
    assert post_export_states["ast_exp_01"] == "draft"
    assert post_export_states["ast_exp_03"] == "needs_review"


# ============================================================================
# 7. REST API Integration Tests
# ============================================================================

def test_api_export_csv_endpoint(client_with_export_db: TestClient):
    """Verify GET /api/v1/exports/csv returns 200, correct media_type, and attachment header."""
    resp = client_with_export_db.get("/api/v1/exports/csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    assert "attachment; filename=\"incubrix_assets_" in resp.headers["content-disposition"]
    assert resp.content.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM

    # Verify content parses as CSV
    reader = csv.DictReader(io.StringIO(resp.content.decode("utf-8-sig")))
    rows = list(reader)
    assert len(rows) == 3


def test_api_export_json_endpoint(client_with_export_db: TestClient):
    """Verify GET /api/v1/exports/json returns 200, JSON schema, and attachment header."""
    resp = client_with_export_db.get("/api/v1/exports/json")
    assert resp.status_code == 200
    assert "application/json" in resp.headers["content-type"]
    assert "attachment; filename=\"incubrix_assets_" in resp.headers["content-disposition"]

    data = resp.json()
    assert data["schema_version"] == "1.0.0"
    assert data["asset_count"] == 3


def test_api_export_endpoints_invalid_filters(client_with_export_db: TestClient):
    """Verify API export endpoints return 400 Bad Request for unsupported query filters."""
    # Invalid platform
    csv_err = client_with_export_db.get("/api/v1/exports/csv?platform=UnsupportedNetwork")
    assert csv_err.status_code == 400
    assert "Unsupported platform filter" in csv_err.json()["detail"]

    json_err = client_with_export_db.get("/api/v1/exports/json?status=unsupported_status")
    assert json_err.status_code == 400
    assert "Unsupported status filter" in json_err.json()["detail"]


# ============================================================================
# 8. Assessment Workbook Calendar Export (02_ASSETS tab, 23 Columns) Tests
# ============================================================================

def test_calendar_export_headers_and_exact_23_columns(export_db):
    """Verify calendar export generates exact 23 columns in required assessment workbook order."""
    csv_bytes = export_assets_to_calendar_csv(export_db)
    # Check for UTF-8 BOM
    assert csv_bytes.startswith(b"\xef\xbb\xbf")

    csv_text = csv_bytes.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(csv_text))
    header = next(reader)

    expected_23_columns = [
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

    assert len(header) == 23
    assert header == expected_23_columns
    assert header == WORKBOOK_FIELDNAMES


def test_calendar_export_field_mapping_and_blank_unavailable_fields(export_db):
    """Verify field mapping, blank unavailable fields, and editorial guardrails."""
    csv_bytes = export_assets_to_calendar_csv(export_db)
    csv_text = csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)

    assert len(rows) == 3

    for row in rows:
        # 1. Unavailable fields MUST be left strictly blank (never fabricated)
        assert row["final_file_url"] == ""
        assert row["scheduled_date"] == ""
        assert row["test_published_url"] == ""
        assert row["impressions_or_views"] == ""
        assert row["engagement_rate"] == ""
        assert row["clicks"] == ""

        # 2. Rights clearance must be 'Pending' (never claimed without actual check)
        assert row["rights_checked"] == "Pending"

        # 3. Generated drafts MUST NEVER be marked 'Ready'
        assert row["status"] != "Ready"
        assert row["status"] in ("Draft", "Needs Review", "Approved", "Scheduled", "Published", "Rejected")

        # 4. Verification flags
        assert row["duplicate_check"] == "Passed (Unique Fingerprint)"
        assert row["completeness_check"] == "Complete Draft"
        assert "IncuBrix Content Engine" in row["tools_used"]

    # Specific row checks
    li_row = next(r for r in rows if r["asset_id"] == "ast_exp_01")
    assert li_row["platform"] == "LinkedIn"
    assert li_row["format"] == "text_post"
    assert li_row["content_pillar"] == "Architecture"
    assert li_row["cta"] == "Read full report at the link."
    assert li_row["utm_link"] == "https://incubrix.com/doc?utm_source=linkedin"
    assert li_row["source_input"] == "src_export_test"
    assert li_row["ai_label_needed"] == "No"  # Template generation
    assert li_row["status"] == "Draft"

    ig_row = next(r for r in rows if r["asset_id"] == "ast_exp_03")
    assert ig_row["platform"] == "Instagram"
    assert ig_row["format"] == "short_video"
    assert ig_row["status"] == "Needs Review"
    assert "contains unverified benchmark" in ig_row["notes"]


def test_calendar_export_ai_label_disclosure(export_db):
    """Verify explicit AI disclosure in calendar export when generation_method is AI."""
    ai_asset = ContentAsset(
        id="ast_exp_ai_01",
        platform=Platform.TIKTOK,
        content_format=ContentFormat.SHORT_VIDEO,
        duration_seconds=25.0,
        content_pillar="Growth",
        audience_segment="Developers",
        hook="AI-generated hook for automated pipeline walkthrough.",
        main_content="Visual demo of automated deployment pipeline.",
        caption="AI-crafted script caption.",
        hashtags=["#DevOps", "#AI"],
        call_to_action="Check out the repo.",
        tracking_url="https://incubrix.com/devops?utm_source=tiktok",
        source_id="src_export_test",
        evidence_references=[],
        review_required=True,
        review_notes="AI generated script flagged for review.",
        generation_method=GenerationMethod.AI,
        status=AssetStatus.DRAFT,
    )
    insert_content_asset(export_db, ai_asset)
    export_db.commit()

    csv_bytes = export_assets_to_calendar_csv(export_db)
    csv_text = csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)

    ai_row = next(r for r in rows if r["asset_id"] == "ast_exp_ai_01")
    assert ai_row["ai_label_needed"] == "Yes"
    assert "ai" in ai_row["tools_used"].lower()
    assert ai_row["status"] == "Draft"


def test_calendar_export_quoting_unicode_and_escaping(export_db):
    """Verify Unicode emojis, commas, quotes, and formula injection sanitization in calendar export."""
    csv_bytes = export_assets_to_calendar_csv(export_db, sanitize_formulas=True)
    csv_text = csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)

    # Unicode emojis in caption preserved
    row1 = next(r for r in rows if r["asset_id"] == "ast_exp_01")
    assert "🚀📊" in row1["caption"]
    assert "Read full report at the link." == row1["cta"]

    # Formula injection sanitized with single-quote prefix
    row2 = next(r for r in rows if r["asset_id"] == "ast_exp_02")
    assert row2["hook"].startswith("'=")


def test_calendar_export_deterministic_repeat_behavior(export_db):
    """Verify repeat calendar exports produce byte-for-byte identical output."""
    run1 = export_assets_to_calendar_csv(export_db)
    run2 = export_assets_to_calendar_csv(export_db)
    assert run1 == run2


def test_calendar_export_duplicate_detection(export_db):
    """Verify duplicate assets in export batch are flagged appropriately."""
    # Insert an asset with identical content fingerprint using allow_duplicate=True
    duplicate_asset = ContentAsset(
        id="ast_exp_dup_01",
        platform=Platform.LINKEDIN,
        content_format=ContentFormat.TEXT_POST,
        content_pillar="Architecture",
        audience_segment="Founders",
        hook="Cohort retention is paramount for SaaS efficiency.",
        main_content="Line 1: Data point.\nLine 2: Action item,\nwith commas and 'quotes'.",
        caption="Summary caption with Unicode emojis 🚀📊",
        hashtags=["#Growth"],
        call_to_action="Read full report at the link.",
        tracking_url=None,
        source_id="src_export_test",
        evidence_references=[],
        review_required=False,
        generation_method=GenerationMethod.TEMPLATE,
        status=AssetStatus.DRAFT,
    )
    insert_content_asset(export_db, duplicate_asset, allow_duplicate=True)
    export_db.commit()

    csv_bytes = export_assets_to_calendar_csv(export_db)
    csv_text = csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)

    # First one passed, duplicate one flagged
    matching = [r for r in rows if r["hook"] == "Cohort retention is paramount for SaaS efficiency."]
    assert len(matching) == 2
    statuses = [r["duplicate_check"] for r in matching]
    assert "Passed (Unique Fingerprint)" in statuses
    assert "Duplicate Detected" in statuses


def test_calendar_export_never_marks_approved_asset_ready_without_final_file(export_db):
    """Verify an approved asset is NOT marked 'Ready' if final_file_url and rights check are missing."""
    approved_asset = ContentAsset(
        id="ast_exp_approved_01",
        platform=Platform.LINKEDIN,
        content_format=ContentFormat.TEXT_POST,
        content_pillar="Foundations",
        audience_segment="Founders",
        hook="Approved post hook for testing.",
        main_content="Approved post content body.",
        caption="Approved post caption.",
        hashtags=["#Approved"],
        call_to_action="Visit website.",
        tracking_url=None,
        source_id="src_export_test",
        evidence_references=[],
        review_required=False,
        generation_method=GenerationMethod.MANUAL,
        status=AssetStatus.APPROVED,
    )
    insert_content_asset(export_db, approved_asset)
    export_db.commit()

    csv_bytes = export_assets_to_calendar_csv(export_db)
    csv_text = csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)

    app_row = next(r for r in rows if r["asset_id"] == "ast_exp_approved_01")
    assert app_row["status"] == "Approved"
    assert app_row["status"] != "Ready"


def test_api_export_calendar_endpoint(client_with_export_db: TestClient):
    """Verify GET /api/v1/exports/calendar returns 200, UTF-8 BOM, 23 columns, and attachment header."""
    resp = client_with_export_db.get("/api/v1/exports/calendar")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    assert "attachment; filename=\"incubrix_calendar_" in resp.headers["content-disposition"]
    assert resp.content.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM

    # Verify 23 columns
    csv_text = resp.content.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(csv_text))
    header = next(reader)
    assert header == WORKBOOK_FIELDNAMES
    assert len(header) == 23

    # Verify rows count
    dict_reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(dict_reader)
    assert len(rows) == 3

    # Test filtering by platform
    resp_li = client_with_export_db.get("/api/v1/exports/calendar?platform=LinkedIn")
    assert resp_li.status_code == 200
    li_rows = list(csv.DictReader(io.StringIO(resp_li.content.decode("utf-8-sig"))))
    assert len(li_rows) == 1
    assert li_rows[0]["platform"] == "LinkedIn"

    # Test invalid platform filter returns 400
    resp_err = client_with_export_db.get("/api/v1/exports/calendar?platform=InvalidPlatform")
    assert resp_err.status_code == 400
    assert "Unsupported platform filter" in resp_err.json()["detail"]
