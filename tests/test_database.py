"""Unit tests for Stage 3 SQLite persistence, schema initialization, and repository functions."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from app.database import (
    check_db_readiness,
    get_connection,
    get_db_connection,
    init_db,
    transaction,
)
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
    compute_sha256,
)
from app.repositories import (
    DatabaseConstraintError,
    DuplicateRecordError,
    RecordNotFoundError,
    compute_asset_fingerprint,
    get_content_asset_by_id,
    get_generation_run_by_id,
    get_source_document_by_hash,
    get_source_document_by_id,
    insert_content_asset,
    insert_generation_run,
    insert_source_document,
    is_duplicate_asset,
    is_duplicate_source,
    list_content_assets,
    update_generation_run,
)


@pytest.fixture
def test_db_path(tmp_path: Path) -> Path:
    """Fixture providing a temporary, isolated SQLite database file."""
    db_file = tmp_path / "test_growth.db"
    init_db(db_file)
    return db_file


@pytest.fixture
def test_db(test_db_path: Path):
    """Fixture providing an active connection to an isolated temporary SQLite database."""
    conn = get_connection(test_db_path)
    try:
        yield conn
    finally:
        conn.close()


def make_sample_source(source_id: str = "src_sample_01", content: str = "Test source content body.") -> SourceDocument:
    """Helper to produce a valid SourceDocument."""
    return SourceDocument(
        id=source_id,
        title="Sample Technical Document",
        content=content,
        source_type="whitepaper",
        source_url="https://incubrix.com/whitepaper",
    )


def make_sample_asset(
    source_id: str,
    asset_id: str = "ast_sample_01",
    platform: Platform = Platform.LINKEDIN,
    content_format: ContentFormat = ContentFormat.TEXT_POST,
    hook: str = "Growth loops unlock sustainable unit economics.",
    main_content: str = "Here is the 3-step breakdown of growth loops...",
    status: AssetStatus = AssetStatus.DRAFT,
) -> ContentAsset:
    """Helper to produce a valid ContentAsset."""
    return ContentAsset(
        id=asset_id,
        platform=platform,
        content_format=content_format,
        content_pillar="Product Growth",
        audience_segment="Growth Engineers",
        hook=hook,
        main_content=main_content,
        caption="A deep dive into growth engineering frameworks.",
        hashtags=["#growth", "#engineering", "#b2b"],
        call_to_action="Read the full breakdown in our documentation.",
        tracking_url="https://incubrix.com/docs?utm_source=linkedin",
        source_id=source_id,
        evidence_references=[
            EvidenceReference(
                claim="Growth loops unlock unit economics.",
                source_quote="Retention loops compound capital efficiency.",
                section_or_page="Page 4",
                is_verified=True,
            )
        ],
        review_required=False,
        generation_method=GenerationMethod.TEMPLATE,
        status=status,
    )


# ============================================================================
# 1. Schema Initialization Tests
# ============================================================================

def test_schema_initialization_and_repeat_initialization(tmp_path: Path):
    """Verify that init_db creates all required tables/indexes and is idempotent."""
    db_file = tmp_path / "idempotent_test.db"

    # First initialization
    init_db(db_file)
    assert check_db_readiness(db_file) is True

    # Repeat initialization must succeed without error
    init_db(db_file)

    conn = get_connection(db_file)
    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        ).fetchall()
        table_names = [row["name"] for row in tables]
        assert "source_documents" in table_names
        assert "content_assets" in table_names
        assert "generation_runs" in table_names

        # Verify indexes exist
        indexes = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name;"
        ).fetchall()
        index_names = [row["name"] for row in indexes]
        assert "idx_source_content_hash" in index_names
        assert "idx_assets_platform" in index_names
        assert "idx_assets_fingerprint" in index_names
    finally:
        conn.close()


# ============================================================================
# 2. Source Document Repository Tests
# ============================================================================

def test_source_insertion_retrieval_and_duplicate_detection(test_db):
    """Verify inserting, retrieving by ID or hash, and detecting duplicate sources."""
    source = make_sample_source("src_101", "Unique source body content.")
    insert_source_document(test_db, source)

    # Retrieve by ID
    retrieved_by_id = get_source_document_by_id(test_db, "src_101")
    assert retrieved_by_id is not None
    assert retrieved_by_id.id == "src_101"
    assert retrieved_by_id.title == source.title
    assert retrieved_by_id.content_hash == source.content_hash

    # Retrieve by hash
    retrieved_by_hash = get_source_document_by_hash(test_db, source.content_hash)
    assert retrieved_by_hash is not None
    assert retrieved_by_hash.id == "src_101"

    # Duplicate detection check
    assert is_duplicate_source(test_db, source.content_hash) is True
    assert is_duplicate_source(test_db, "non_existent_hash_000") is False


def test_source_hash_uniqueness(test_db):
    """Verify that inserting a document with a duplicate content_hash raises DuplicateRecordError."""
    source1 = make_sample_source("src_orig", "Identical source body.")
    insert_source_document(test_db, source1)

    # Second document with different ID but same content (and therefore same hash)
    source2 = SourceDocument(
        id="src_duplicate",
        title="Duplicate Title",
        content="Identical source body.",
        source_type="article",
    )

    with pytest.raises(DuplicateRecordError) as exc_info:
        insert_source_document(test_db, source2)
    assert "already exists" in str(exc_info.value)


# ============================================================================
# 3. Content Asset Repository Tests
# ============================================================================

def test_asset_insertion_and_retrieval(test_db):
    """Verify inserting and retrieving a ContentAsset with nested JSON fields."""
    source = make_sample_source("src_parent")
    insert_source_document(test_db, source)

    asset = make_sample_asset("src_parent", "ast_asset_01")
    insert_content_asset(test_db, asset)

    retrieved = get_content_asset_by_id(test_db, "ast_asset_01")
    assert retrieved is not None
    assert retrieved.id == "ast_asset_01"
    assert retrieved.platform == Platform.LINKEDIN
    assert retrieved.content_format == ContentFormat.TEXT_POST
    assert retrieved.hashtags == ["#growth", "#engineering", "#b2b"]
    assert len(retrieved.evidence_references) == 1
    assert retrieved.evidence_references[0].claim == "Growth loops unlock unit economics."
    assert retrieved.review_required is False
    assert retrieved.status == AssetStatus.DRAFT


def test_platform_and_status_filtering(test_db):
    """Verify listing assets filtered by platform, status, and source_id."""
    source = make_sample_source("src_filter_test")
    insert_source_document(test_db, source)

    # Create assets across multiple platforms and statuses
    a1 = make_sample_asset("src_filter_test", "ast_li_1", platform=Platform.LINKEDIN, status=AssetStatus.DRAFT)
    a2 = make_sample_asset(
        "src_filter_test",
        "ast_li_2",
        platform=Platform.LINKEDIN,
        status=AssetStatus.NEEDS_REVIEW,
        hook="Different hook for review",
        main_content="Different main content for review",
    )
    a3 = make_sample_asset(
        "src_filter_test",
        "ast_x_1",
        platform=Platform.X,
        status=AssetStatus.DRAFT,
        hook="Short X hook",
        main_content="Short X post content",
    )

    insert_content_asset(test_db, a1)
    insert_content_asset(test_db, a2)
    insert_content_asset(test_db, a3)

    # Filter by platform
    li_assets = list_content_assets(test_db, platform=Platform.LINKEDIN)
    assert len(li_assets) == 2
    assert all(a.platform == Platform.LINKEDIN for a in li_assets)

    # Filter by status
    review_assets = list_content_assets(test_db, status=AssetStatus.NEEDS_REVIEW)
    assert len(review_assets) == 1
    assert review_assets[0].id == "ast_li_2"

    # Filter by both platform and status
    li_drafts = list_content_assets(test_db, platform=Platform.LINKEDIN, status=AssetStatus.DRAFT)
    assert len(li_drafts) == 1
    assert li_drafts[0].id == "ast_li_1"

    # Filter by source_id
    src_assets = list_content_assets(test_db, source_id="src_filter_test")
    assert len(src_assets) == 3


def test_asset_duplicate_detection(test_db):
    """Verify deterministic normalized content fingerprinting and duplicate detection."""
    source = make_sample_source("src_dup_test")
    insert_source_document(test_db, source)

    asset1 = make_sample_asset(
        source_id="src_dup_test",
        asset_id="ast_original",
        platform=Platform.LINKEDIN,
        content_format=ContentFormat.TEXT_POST,
        hook="Top 3 Growth Tactics For Seed Startups",
        main_content="Tactic 1: Instrument analytics early.\nTactic 2: Talk to users daily.",
    )
    insert_content_asset(test_db, asset1)

    # Verify duplicate is detected for identical copy
    assert is_duplicate_asset(test_db, asset1) is True

    # Verify duplicate is detected even with whitespace/casing variations
    fp_variant = compute_asset_fingerprint(
        platform=Platform.LINKEDIN,
        content_format=ContentFormat.TEXT_POST,
        hook="  top 3 growth tactics for seed startups  ",
        main_content="Tactic 1: instrument analytics early.\nTactic 2: talk to users daily.  ",
    )
    assert is_duplicate_asset(test_db, fp_variant, platform=Platform.LINKEDIN) is True

    # Attempting to insert duplicate without allow_duplicate must raise DuplicateRecordError
    asset2_duplicate = make_sample_asset(
        source_id="src_dup_test",
        asset_id="ast_copycat",
        platform=Platform.LINKEDIN,
        content_format=ContentFormat.TEXT_POST,
        hook="Top 3 Growth Tactics For Seed Startups",
        main_content="Tactic 1: Instrument analytics early.\nTactic 2: Talk to users daily.",
    )
    with pytest.raises(DuplicateRecordError) as exc_info:
        insert_content_asset(test_db, asset2_duplicate, allow_duplicate=False)
    assert "Duplicate asset detected" in str(exc_info.value)

    # Different platform is NOT a duplicate
    fp_x = compute_asset_fingerprint(
        platform=Platform.X,
        content_format=ContentFormat.TEXT_POST,
        hook="Top 3 Growth Tactics For Seed Startups",
        main_content="Tactic 1: Instrument analytics early.\nTactic 2: Talk to users daily.",
    )
    assert is_duplicate_asset(test_db, fp_x, platform=Platform.X) is False


# ============================================================================
# 4. Generation Run Repository Tests
# ============================================================================

def test_generation_run_insertion_and_completion_updates(test_db):
    """Verify insertion of running generation record and atomic metric completion updates."""
    source = make_sample_source("src_run_test")
    insert_source_document(test_db, source)

    now = datetime.now(timezone.utc)
    run = GenerationRun(
        id="run_test_001",
        source_id="src_run_test",
        started_at=now,
        generation_method=GenerationMethod.AI,
        status=RunStatus.PENDING,
    )
    insert_generation_run(test_db, run)

    fetched = get_generation_run_by_id(test_db, "run_test_001")
    assert fetched is not None
    assert fetched.status == RunStatus.PENDING
    assert fetched.runtime_ms is None

    # Update completion
    completed_time = now + timedelta(seconds=1.85)
    updated = update_generation_run(
        conn=test_db,
        run_id="run_test_001",
        status=RunStatus.SUCCESS,
        completed_at=completed_time,
        runtime_ms=1850.0,
        assets_created=10,
        review_required_count=2,
    )

    assert updated.status == RunStatus.SUCCESS
    assert updated.runtime_ms == 1850.0
    assert updated.assets_created == 10
    assert updated.review_required_count == 2
    assert updated.error_details is None


# ============================================================================
# 5. Integrity, Foreign Keys, Transactions & Resilience Tests
# ============================================================================

def test_foreign_key_enforcement(test_db):
    """Verify SQLite foreign key enforcement prevents orphaned records."""
    orphan_asset = make_sample_asset("non_existent_source_id", "ast_orphan")
    with pytest.raises(DatabaseConstraintError) as exc_info:
        insert_content_asset(test_db, orphan_asset)
    assert "Foreign key violation" in str(exc_info.value)

    orphan_run = GenerationRun(
        id="run_orphan",
        source_id="non_existent_source_id",
        generation_method=GenerationMethod.TEMPLATE,
        status=RunStatus.PENDING,
    )
    with pytest.raises(DatabaseConstraintError) as exc_info:
        insert_generation_run(test_db, orphan_run)
    assert "Foreign key violation" in str(exc_info.value)


def test_transaction_rollback_on_failure(test_db_path: Path):
    """Verify that failed transaction blocks roll back completely."""
    # Attempt a multi-operation block that fails mid-way
    with pytest.raises(RuntimeError):
        with get_db_connection(test_db_path) as conn:
            source = make_sample_source("src_trans_test", "Content that will be rolled back.")
            insert_source_document(conn, source)
            raise RuntimeError("Forced simulation error during transaction.")

    # Re-open and verify rollback: source document must not exist
    conn = get_connection(test_db_path)
    try:
        assert get_source_document_by_id(conn, "src_trans_test") is None
    finally:
        conn.close()


def test_persistence_after_closing_and_reopening(test_db_path: Path):
    """Verify data is persisted to disk and accessible after closing connections."""
    source = make_sample_source("src_persist_test", "Permanent document content.")
    with get_db_connection(test_db_path) as conn:
        insert_source_document(conn, source)

    # Open fresh connection to the same file
    conn2 = get_connection(test_db_path)
    try:
        retrieved = get_source_document_by_id(conn2, "src_persist_test")
        assert retrieved is not None
        assert retrieved.content == "Permanent document content."
    finally:
        conn2.close()


def test_missing_id_behavior(test_db):
    """Verify repository functions handle non-existent IDs predictably."""
    assert get_source_document_by_id(test_db, "missing_source") is None
    assert get_source_document_by_hash(test_db, "missing_hash") is None
    assert get_content_asset_by_id(test_db, "missing_asset") is None
    assert get_generation_run_by_id(test_db, "missing_run") is None

    with pytest.raises(RecordNotFoundError):
        update_generation_run(test_db, "missing_run", status=RunStatus.SUCCESS)


def test_parameterized_handling_of_hostile_inputs(test_db):
    """Verify that inputs containing quotes, semicolons, and SQL keywords are treated as literal text."""
    hostile_text = "'; DROP TABLE content_assets; -- SELECT * FROM users WHERE '1'='1"
    hostile_source = make_sample_source("src_hostile_01", hostile_text)
    insert_source_document(test_db, hostile_source)

    retrieved_source = get_source_document_by_id(test_db, "src_hostile_01")
    assert retrieved_source is not None
    assert retrieved_source.content == hostile_text

    # Verify tables still exist
    tables = test_db.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    table_names = [r["name"] for r in tables]
    assert "content_assets" in table_names
    assert "source_documents" in table_names
