"""Unit tests for Stage 2 domain models and Pydantic v2 validation rules."""

from datetime import datetime, timedelta, timezone
import pytest
from pydantic import ValidationError

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


# ============================================================================
# 1. Platform Model Tests
# ============================================================================

def test_supported_platforms_and_normalization():
    """Verify all 8 supported platforms and case-insensitive normalization."""
    expected_platforms = {
        "LinkedIn": Platform.LINKEDIN,
        "Instagram": Platform.INSTAGRAM,
        "YouTube Shorts": Platform.YOUTUBE_SHORTS,
        "TikTok": Platform.TIKTOK,
        "X": Platform.X,
        "Threads": Platform.THREADS,
        "Facebook": Platform.FACEBOOK,
        "Reddit": Platform.REDDIT,
    }

    for name, platform_enum in expected_platforms.items():
        assert Platform(name) == platform_enum
        assert Platform(name.lower()) == platform_enum
        assert Platform(name.upper()) == platform_enum
        assert platform_enum.value == name

    # Alias for X / Twitter
    assert Platform("twitter") == Platform.X
    assert Platform("x.com") == Platform.X


def test_unsupported_platform_rejection():
    """Verify that unsupported platforms are strictly rejected."""
    for invalid in ["Pinterest", "Snapchat", "MySpace", "TikTok2", ""]:
        with pytest.raises(ValueError):
            Platform(invalid)


# ============================================================================
# 2. Content Asset Validation Tests
# ============================================================================

def make_valid_asset_data(**kwargs):
    """Helper to generate valid default kwargs for a ContentAsset."""
    data = {
        "id": "ast_test123",
        "platform": Platform.LINKEDIN,
        "content_format": ContentFormat.TEXT_POST,
        "content_pillar": "Engineering Leadership",
        "audience_segment": "CTOs and Growth Engineers",
        "hook": "Stop scaling ad spend before your retention engine is instrumented.",
        "main_content": "3 key strategies for retention instrumentation:\n1. Event audit\n2. Cohort tracking\n3. Lifecycle loops.",
        "caption": "How early-stage engineering teams measure growth loops. Read on for details.",
        "hashtags": ["#GrowthEngineering", "#StartupTech", "#Analytics"],
        "call_to_action": "Check out the case study at the link below.",
        "tracking_url": "https://incubrix.com/growth-study?utm_source=linkedin",
        "source_id": "src_whitepaper_01",
        "evidence_references": [
            EvidenceReference(
                claim="Retention instrumentation precedes scaling ad spend.",
                source_quote="Teams must verify cohort retention loops prior to capital allocation.",
                section_or_page="Section 3: Retention Frameworks",
                is_verified=True,
            )
        ],
        "review_required": False,
        "generation_method": GenerationMethod.TEMPLATE,
        "status": AssetStatus.DRAFT,
    }
    data.update(kwargs)
    return data


def test_valid_asset_creation():
    """Verify successful creation of a fully specified valid content asset."""
    data = make_valid_asset_data()
    asset = ContentAsset(**data)
    assert asset.id == "ast_test123"
    assert asset.platform == Platform.LINKEDIN
    assert asset.content_format == ContentFormat.TEXT_POST
    assert asset.status == AssetStatus.DRAFT
    assert len(asset.evidence_references) == 1
    assert asset.evidence_references[0].is_verified is True
    assert asset.review_required is False


def test_blank_required_fields_rejection():
    """Verify that required text fields cannot be blank or whitespace only."""
    required_fields = [
        "content_pillar",
        "audience_segment",
        "hook",
        "main_content",
        "caption",
        "call_to_action",
        "source_id",
    ]

    for field in required_fields:
        bad_data = make_valid_asset_data(**{field: "   "})
        with pytest.raises(ValidationError) as exc_info:
            ContentAsset(**bad_data)
        assert field in str(exc_info.value) or "empty or whitespace" in str(exc_info.value)


def test_tracking_url_validation():
    """Verify valid tracking URLs, optional presence during drafting, and invalid URL rejection."""
    # Absent tracking URL during drafting is completely valid
    asset_no_url = ContentAsset(**make_valid_asset_data(tracking_url=None))
    assert asset_no_url.tracking_url is None

    # Empty string is normalized to None
    asset_empty_url = ContentAsset(**make_valid_asset_data(tracking_url="   "))
    assert asset_empty_url.tracking_url is None

    # Valid tracking URL with UTM parameters
    valid_url = "https://incubrix.com/demo?utm_source=x&utm_campaign=launch"
    asset_with_url = ContentAsset(**make_valid_asset_data(tracking_url=valid_url))
    assert asset_with_url.tracking_url == valid_url

    # Invalid tracking URL formats
    for bad_url in ["not-a-valid-url", "ftp://invalidscheme.com", "http://", "www.missing-scheme.com"]:
        with pytest.raises(ValidationError) as exc_info:
            ContentAsset(**make_valid_asset_data(tracking_url=bad_url))
        assert "Invalid tracking URL" in str(exc_info.value) or "URL" in str(exc_info.value)


def test_duplicate_hashtag_normalization():
    """Verify hashtags are deduplicated case-insensitively and standardized with '#'."""
    raw_tags = ["growth", "#GROWTH", "engineering", "#Engineering", "Startup", "#startup", "#growth"]
    asset = ContentAsset(**make_valid_asset_data(hashtags=raw_tags))
    # Should contain exactly 3 unique tags (case-insensitive deduplication)
    assert len(asset.hashtags) == 3
    assert asset.hashtags == ["#growth", "#engineering", "#Startup"]


def test_short_video_duration_validation():
    """Verify short-video scripts require duration_seconds and are capped at 60 seconds."""
    # Valid short video (e.g. 45 seconds)
    valid_video = ContentAsset(
        **make_valid_asset_data(
            content_format=ContentFormat.SHORT_VIDEO,
            duration_seconds=45,
        )
    )
    assert valid_video.duration_seconds == 45

    # Short video exceeding 60 seconds must be rejected
    with pytest.raises(ValidationError) as exc_info:
        ContentAsset(
            **make_valid_asset_data(
                content_format=ContentFormat.SHORT_VIDEO,
                duration_seconds=61,
            )
        )
    assert "maximum of 60 seconds" in str(exc_info.value) or "60" in str(exc_info.value)

    # Short video with missing duration must be rejected
    with pytest.raises(ValidationError) as exc_info:
        ContentAsset(
            **make_valid_asset_data(
                content_format=ContentFormat.SHORT_VIDEO,
                duration_seconds=None,
            )
        )
    assert "duration_seconds" in str(exc_info.value)

    # Non-video asset with duration > 60 must also be rejected
    with pytest.raises(ValidationError):
        ContentAsset(
            **make_valid_asset_data(
                content_format=ContentFormat.TEXT_POST,
                duration_seconds=90,
            )
        )


def test_evidence_and_unverified_claims_trigger_review():
    """Verify unverified evidence references force review_required and prevent auto-approval."""
    unverified_ref = EvidenceReference(
        claim="Our platform increases customer conversion by 300%.",
        source_quote="Competitor benchmark claim needs validation against primary analytics.",
        is_verified=False,
        verification_notes="Unverified metric from third-party commentary.",
    )

    asset = ContentAsset(
        **make_valid_asset_data(
            evidence_references=[unverified_ref],
            review_required=False,  # Validator should override this to True
        )
    )
    assert asset.review_required is True
    assert "unverified" in (asset.review_notes or "").lower()

    # Asset requiring review cannot be marked as approved or published
    with pytest.raises(ValidationError) as exc_info:
        ContentAsset(
            **make_valid_asset_data(
                evidence_references=[unverified_ref],
                status=AssetStatus.APPROVED,
            )
        )
    assert "review_required" in str(exc_info.value)


def test_ai_generated_content_identification():
    """Verify AI-generated content is clearly identified via generation_method and helper property."""
    ai_asset = ContentAsset(
        **make_valid_asset_data(
            generation_method=GenerationMethod.AI,
        )
    )
    assert ai_asset.generation_method == GenerationMethod.AI
    assert ai_asset.is_ai_generated is True

    template_asset = ContentAsset(
        **make_valid_asset_data(
            generation_method=GenerationMethod.TEMPLATE,
        )
    )
    assert template_asset.generation_method == GenerationMethod.TEMPLATE
    assert template_asset.is_ai_generated is False


def test_generated_content_not_approved_automatically():
    """Verify that generated assets (AI or template) cannot be initialized as approved or published."""
    # Attempting to directly initialize AI content as approved must fail
    with pytest.raises(ValidationError) as exc_info:
        ContentAsset(
            **make_valid_asset_data(
                generation_method=GenerationMethod.AI,
                status=AssetStatus.APPROVED,
            )
        )
    assert "Generated content" in str(exc_info.value) or "approved" in str(exc_info.value)

    # Attempting to directly initialize template content as published must fail
    with pytest.raises(ValidationError) as exc_info:
        ContentAsset(
            **make_valid_asset_data(
                generation_method=GenerationMethod.TEMPLATE,
                status=AssetStatus.PUBLISHED,
            )
        )
    assert "Generated content" in str(exc_info.value) or "published" in str(exc_info.value)

    # Manual creation can be draft or needs_review, and can be approved if review_required is False
    manual_asset = ContentAsset(
        **make_valid_asset_data(
            generation_method=GenerationMethod.MANUAL,
            status=AssetStatus.APPROVED,
            review_required=False,
        )
    )
    assert manual_asset.status == AssetStatus.APPROVED


# ============================================================================
# 3. Source Document Model Tests
# ============================================================================

def test_source_document_creation_and_hash_computation():
    """Verify source document creation and automatic SHA-256 content hash generation."""
    text = "IncuBrix Growth Engineering technical document content."
    expected_hash = compute_sha256(text)

    doc = SourceDocument(
        id="src_doc_100",
        title="Engineering Whitepaper: Growth Infrastructure",
        content=text,
        source_type="whitepaper",
        source_url="https://incubrix.com/resources/whitepaper-01",
    )
    assert doc.content_hash == expected_hash
    assert doc.title == "Engineering Whitepaper: Growth Infrastructure"
    assert doc.source_url == "https://incubrix.com/resources/whitepaper-01"


def test_source_document_hash_validation():
    """Verify matching hash passes and mismatched hash raises ValidationError."""
    text = "Source content for hash validation."
    valid_hash = compute_sha256(text)
    invalid_hash = "a" * 64

    # Valid provided hash
    doc = SourceDocument(
        title="Verified Doc",
        content=text,
        content_hash=valid_hash,
    )
    assert doc.content_hash == valid_hash

    # Invalid provided hash mismatch
    with pytest.raises(ValidationError) as exc_info:
        SourceDocument(
            title="Tampered Doc",
            content=text,
            content_hash=invalid_hash,
        )
    assert "Content hash mismatch" in str(exc_info.value)


def test_source_document_credential_leak_prevention():
    """Verify source metadata rejects embedded API keys or credentials."""
    for secret_sample in [
        "IncuBrix Notes api_key=ab12cd34ef56gh78ij90",
        "Document bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "Config sk-123456789012345678901234",
    ]:
        with pytest.raises(ValidationError) as exc_info:
            SourceDocument(
                title=secret_sample,
                content="Valid content without credentials.",
            )
        assert "Potential secret" in str(exc_info.value)


# ============================================================================
# 4. Generation Run Model Tests
# ============================================================================

def test_successful_generation_run_metadata():
    """Verify valid generation run record with success status, runtime, and asset counts."""
    now = datetime.now(timezone.utc)
    run = GenerationRun(
        id="run_abc123",
        source_id="src_doc_100",
        started_at=now,
        completed_at=now + timedelta(seconds=2.45),
        runtime_ms=2450.0,
        generation_method=GenerationMethod.AI,
        assets_created=10,
        review_required_count=2,
        status=RunStatus.SUCCESS,
        error_details=None,
    )
    assert run.status == RunStatus.SUCCESS
    assert run.runtime_ms == 2450.0
    assert run.assets_created == 10
    assert run.review_required_count == 2
    assert run.error_details is None


def test_failed_generation_run_metadata():
    """Verify failed generation run captures required diagnostic error details."""
    now = datetime.now(timezone.utc)
    # Valid failed run with error details
    run = GenerationRun(
        id="run_failed_1",
        source_id="src_doc_100",
        started_at=now,
        completed_at=now + timedelta(seconds=0.5),
        runtime_ms=500.0,
        generation_method=GenerationMethod.TEMPLATE,
        assets_created=0,
        review_required_count=0,
        status=RunStatus.FAILED,
        error_details="Document parsing failed: unsupported document encoding.",
    )
    assert run.status == RunStatus.FAILED
    assert "Document parsing failed" in run.error_details

    # Failed run missing error details must be rejected
    with pytest.raises(ValidationError) as exc_info:
        GenerationRun(
            source_id="src_doc_100",
            generation_method=GenerationMethod.TEMPLATE,
            status=RunStatus.FAILED,
            error_details=None,
        )
    assert "error_details must be provided" in str(exc_info.value)


def test_generation_run_metric_validation():
    """Verify validation of runtime, timestamps, and review count constraints."""
    now = datetime.now(timezone.utc)

    # Negative runtime
    with pytest.raises(ValidationError):
        GenerationRun(
            source_id="src_1",
            generation_method=GenerationMethod.TEMPLATE,
            runtime_ms=-50.0,
        )

    # review_required_count > assets_created
    with pytest.raises(ValidationError) as exc_info:
        GenerationRun(
            source_id="src_1",
            generation_method=GenerationMethod.TEMPLATE,
            assets_created=3,
            review_required_count=5,
        )
    assert "review_required_count" in str(exc_info.value)

    # completed_at before started_at
    with pytest.raises(ValidationError) as exc_info:
        GenerationRun(
            source_id="src_1",
            generation_method=GenerationMethod.TEMPLATE,
            started_at=now,
            completed_at=now - timedelta(seconds=10),
        )
    assert "completed_at" in str(exc_info.value)
