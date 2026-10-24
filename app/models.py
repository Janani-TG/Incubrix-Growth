"""Domain models and Pydantic v2 schemas for the IncuBrix Content Engine."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
import hashlib
import re
from typing import Any
import uuid

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    TypeAdapter,
    field_validator,
    model_validator,
)


def compute_sha256(text: str) -> str:
    """Compute the SHA-256 hexadecimal digest for a given text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Secret patterns to prevent credential leakage in metadata
SECRET_PATTERNS = [
    re.compile(r"(?i)\b(bearer\s+[a-z0-9_\-\.]{15,})\b"),
    re.compile(r"(?i)\b(api[_-]?key\s*[:=]\s*['\"]?[a-z0-9_\-]{16,}['\"]?)\b"),
    re.compile(r"(?i)\b(secret[_-]?key\s*[:=]\s*['\"]?[a-z0-9_\-]{16,}['\"]?)\b"),
    re.compile(r"\b(ghp_[a-zA-Z0-9]{36})\b"),
    re.compile(r"\b(sk-[a-zA-Z0-9]{20,})\b"),
    re.compile(r"(?i)\b(password\s*[:=]\s*['\"]?[^\s'\"]{6,}['\"]?)\b"),
]


# ============================================================================
# 1. Platform & Format Enums
# ============================================================================

class Platform(str, Enum):
    """Supported social media platforms with consistent display names."""
    LINKEDIN = "LinkedIn"
    INSTAGRAM = "Instagram"
    YOUTUBE_SHORTS = "YouTube Shorts"
    TIKTOK = "TikTok"
    X = "X"
    THREADS = "Threads"
    FACEBOOK = "Facebook"
    REDDIT = "Reddit"

    @classmethod
    def _missing_(cls, value: object) -> Platform | None:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in ("twitter", "x.com"):
                return cls.X
            for member in cls:
                if member.value.lower() == normalized:
                    return member
        return None


class ContentFormat(str, Enum):
    """Supported content asset formats."""
    SHORT_VIDEO = "short_video"
    CAROUSEL = "carousel"
    GRAPHIC = "graphic"
    TEXT_POST = "text_post"
    DISCUSSION_POST = "discussion_post"

    @classmethod
    def _missing_(cls, value: object) -> ContentFormat | None:
        if isinstance(value, str):
            normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
            for member in cls:
                if member.value.lower() == normalized:
                    return member
        return None


class GenerationMethod(str, Enum):
    """Method utilized to produce the content asset."""
    TEMPLATE = "template"
    MANUAL = "manual"
    AI = "ai"

    @classmethod
    def _missing_(cls, value: object) -> GenerationMethod | None:
        if isinstance(value, str):
            normalized = value.strip().lower()
            for member in cls:
                if member.value.lower() == normalized:
                    return member
        return None


class AssetStatus(str, Enum):
    """Lifecycle status of a content asset."""
    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    REJECTED = "rejected"

    @classmethod
    def _missing_(cls, value: object) -> AssetStatus | None:
        if isinstance(value, str):
            normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
            for member in cls:
                if member.value.lower() == normalized:
                    return member
        return None


class RunStatus(str, Enum):
    """Execution status of a generation run."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


# ============================================================================
# 2. Evidence Reference Model
# ============================================================================

class EvidenceReference(BaseModel):
    """Structured evidence citation grounding factual claims in source material."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    claim: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="The specific factual claim made in the generated asset.",
    )
    source_quote: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Direct verbatim quote, data point, or citation from the source document.",
    )
    section_or_page: str | None = Field(
        default=None,
        max_length=200,
        description="Optional section header, paragraph, or page reference in the source.",
    )
    is_verified: bool = Field(
        default=True,
        description="Flag indicating if the claim is verified against genuine source material.",
    )
    verification_notes: str | None = Field(
        default=None,
        max_length=500,
        description="Notes regarding verification status or manual review reasons.",
    )

    @field_validator("claim", "source_quote")
    @classmethod
    def validate_non_blank(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"Evidence '{info.field_name}' cannot be empty or whitespace only.")
        return v.strip()


# ============================================================================
# 3. Content Asset Model
# ============================================================================

class ContentAsset(BaseModel):
    """Individual social media content asset with platform constraints and safety guardrails."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    id: str = Field(
        default_factory=lambda: f"ast_{uuid.uuid4().hex[:12]}",
        min_length=1,
        max_length=100,
        description="Unique identifier for the content asset.",
    )
    platform: Platform = Field(
        ...,
        description="Target social media platform.",
    )
    content_format: ContentFormat = Field(
        ...,
        description="Format of the asset (e.g., short_video, carousel, text_post).",
    )
    content_pillar: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Strategic content pillar (e.g., Thought Leadership, Growth Tactics).",
    )
    audience_segment: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Target persona or audience segment (e.g., Seed Founders, Growth Engineers).",
    )
    hook: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Attention-grabbing hook or initial headline.",
    )
    main_content: str = Field(
        ...,
        min_length=1,
        max_length=15000,
        description="Primary copy, slide breakdown, visual prompt, or video script.",
    )
    caption: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Platform post caption or accompanying description.",
    )
    hashtags: list[str] = Field(
        default_factory=list,
        description="List of hashtags stored without duplicates.",
    )
    call_to_action: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Clear call to action for audience conversion.",
    )
    tracking_url: str | None = Field(
        default=None,
        max_length=2048,
        description="Validated UTM tracking URL. Optional during drafting.",
    )
    source_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Identifier of the source document this asset originates from.",
    )
    evidence_references: list[EvidenceReference] = Field(
        default_factory=list,
        description="Structured citations supporting factual claims made in this asset.",
    )
    review_required: bool = Field(
        default=False,
        description="True if human review is required before approval or scheduling.",
    )
    review_notes: str | None = Field(
        default=None,
        max_length=2000,
        description="Explanations for why review is required or notes from reviewer.",
    )
    generation_method: GenerationMethod = Field(
        ...,
        description="Method used to create the asset (template, manual, or ai).",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp in UTC.",
    )
    status: AssetStatus = Field(
        default=AssetStatus.DRAFT,
        description="Current approval/publication status.",
    )
    duration_seconds: float | None = Field(
        default=None,
        description="Duration in seconds. Required and capped at 60s for short_video formats.",
    )

    @field_validator(
        "id",
        "content_pillar",
        "audience_segment",
        "hook",
        "main_content",
        "caption",
        "call_to_action",
        "source_id",
    )
    @classmethod
    def validate_non_blank_strings(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"Field '{info.field_name}' cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("tracking_url", mode="before")
    @classmethod
    def validate_tracking_url(cls, v: Any) -> str | None:
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
        try:
            http_url = TypeAdapter(HttpUrl).validate_python(v)
            return str(http_url)
        except Exception as e:
            raise ValueError(f"Invalid tracking URL: '{v}'. Must be a valid HTTP or HTTPS URL.") from e

    @field_validator("hashtags", mode="before")
    @classmethod
    def normalize_and_deduplicate_hashtags(cls, v: Any) -> list[str]:
        if v is None:
            return []
        if isinstance(v, str):
            tags = [t.strip() for t in v.replace(",", " ").split() if t.strip()]
        elif isinstance(v, (list, tuple, set)):
            tags = [str(t).strip() for t in v if str(t).strip()]
        else:
            raise ValueError("Hashtags must be a list of strings.")

        seen_lower = set()
        deduped = []
        for tag in tags:
            formatted = tag if tag.startswith("#") else f"#{tag}"
            key = formatted.lower()
            if key not in seen_lower:
                seen_lower.add(key)
                deduped.append(formatted)
        return deduped

    @model_validator(mode="after")
    def validate_safety_and_integrity(self) -> ContentAsset:
        # 1. Short-video duration constraints
        if self.content_format == ContentFormat.SHORT_VIDEO:
            if self.duration_seconds is None:
                raise ValueError("Short-video content format requires 'duration_seconds' to be specified.")
            if self.duration_seconds <= 0 or self.duration_seconds > 60:
                raise ValueError(
                    f"Short-video duration must be between 1 and 60 seconds (got {self.duration_seconds}s)."
                )
        elif self.duration_seconds is not None:
            if self.duration_seconds <= 0 or self.duration_seconds > 60:
                raise ValueError(
                    f"Video duration cannot exceed 60 seconds (got {self.duration_seconds}s)."
                )

        # 2. Evidence validation: unverified claims require human review
        has_unverified = any(not ref.is_verified for ref in self.evidence_references)
        if has_unverified:
            self.review_required = True
            note = "[Flagged for review: contains unverified evidence claim]"
            if not self.review_notes:
                self.review_notes = note
            elif note not in self.review_notes:
                self.review_notes = f"{self.review_notes} {note}".strip()

        # 3. Guardrail: Cannot be marked approved or published while review is required
        if self.review_required and self.status in (AssetStatus.APPROVED, AssetStatus.PUBLISHED):
            raise ValueError(
                f"Asset cannot be marked as '{self.status.value}' while review_required is True."
            )

        # 4. Guardrail: Generated content (AI or template) cannot be initialized as approved or published
        if self.generation_method in (GenerationMethod.AI, GenerationMethod.TEMPLATE):
            if self.status in (AssetStatus.APPROVED, AssetStatus.PUBLISHED):
                raise ValueError(
                    f"Generated content ({self.generation_method.value}) cannot be initialized directly as "
                    f"'{self.status.value}'. Explicit human approval is required."
                )

        return self

    @property
    def is_ai_generated(self) -> bool:
        """Helper to clearly identify whether the asset was generated by an AI model."""
        return self.generation_method == GenerationMethod.AI


# ============================================================================
# 4. Source Document Model
# ============================================================================

class SourceDocument(BaseModel):
    """Source input document ingested for content asset generation."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    id: str = Field(
        default_factory=lambda: f"src_{uuid.uuid4().hex[:12]}",
        min_length=1,
        max_length=100,
        description="Unique identifier for the source document.",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Title or headline of the source material.",
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=200000,
        description="Original text content or file body.",
    )
    source_type: str = Field(
        default="document",
        min_length=1,
        max_length=100,
        description="Type of source document (e.g. whitepaper, case_study, product_update).",
    )
    source_url: str | None = Field(
        default=None,
        max_length=2048,
        description="Public URL of the source material, if available.",
    )
    imported_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the source was ingested in UTC.",
    )
    content_hash: str = Field(
        default="",
        description="SHA-256 hash of the content for deduplication and integrity check.",
    )

    @field_validator("id", "title", "content", "source_type")
    @classmethod
    def validate_non_blank_fields(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"Field '{info.field_name}' cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("source_url", mode="before")
    @classmethod
    def validate_source_url(cls, v: Any) -> str | None:
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
        try:
            http_url = TypeAdapter(HttpUrl).validate_python(v)
            return str(http_url)
        except Exception as e:
            raise ValueError(f"Invalid source URL: '{v}'. Must be a valid HTTP or HTTPS URL.") from e

    @model_validator(mode="after")
    def validate_security_and_hash(self) -> SourceDocument:
        # Check metadata for private credentials or leaked secrets
        for field_val in (self.title, self.source_type, self.source_url or ""):
            for pattern in SECRET_PATTERNS:
                if pattern.search(field_val):
                    raise ValueError(
                        "Potential secret, API key, or credential detected in source document metadata."
                    )

        # Validate or calculate content_hash
        computed = compute_sha256(self.content)
        if not self.content_hash:
            self.content_hash = computed
        else:
            provided = self.content_hash.strip().lower()
            if provided != computed:
                raise ValueError(
                    f"Content hash mismatch: provided '{self.content_hash}' does not match "
                    f"computed SHA-256 hash '{computed}'."
                )
            self.content_hash = provided

        return self


# ============================================================================
# 5. Generation Run Model
# ============================================================================

class GenerationRun(BaseModel):
    """Audit record and performance telemetry for a single content generation execution."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    id: str = Field(
        default_factory=lambda: f"run_{uuid.uuid4().hex[:12]}",
        min_length=1,
        max_length=100,
        description="Unique identifier for the generation run.",
    )
    source_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Identifier of the source document processed.",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Run start timestamp in UTC.",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="Run completion timestamp in UTC.",
    )
    runtime_ms: float | None = Field(
        default=None,
        ge=0,
        description="Execution duration in milliseconds.",
    )
    generation_method: GenerationMethod = Field(
        ...,
        description="Method used for generation (template, manual, or ai).",
    )
    assets_created: int = Field(
        default=0,
        ge=0,
        description="Total count of content assets created during this run.",
    )
    review_required_count: int = Field(
        default=0,
        ge=0,
        description="Count of created assets that require human review.",
    )
    status: RunStatus = Field(
        default=RunStatus.PENDING,
        description="Execution status of the generation run.",
    )
    error_details: str | None = Field(
        default=None,
        max_length=5000,
        description="Detailed diagnostic or traceback message if the run failed.",
    )

    @field_validator("id", "source_id")
    @classmethod
    def validate_non_blank_run_fields(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"Field '{info.field_name}' cannot be empty or whitespace only.")
        return v.strip()

    @model_validator(mode="after")
    def validate_run_consistency(self) -> GenerationRun:
        if self.review_required_count > self.assets_created:
            raise ValueError(
                f"review_required_count ({self.review_required_count}) cannot exceed "
                f"assets_created ({self.assets_created})."
            )

        if self.completed_at is not None and self.completed_at < self.started_at:
            raise ValueError("completed_at timestamp cannot be earlier than started_at.")

        if self.status == RunStatus.FAILED:
            if not self.error_details or not self.error_details.strip():
                raise ValueError("error_details must be provided when run status is 'failed'.")

        if self.status == RunStatus.SUCCESS:
            if self.error_details and self.error_details.strip():
                raise ValueError("error_details should not be set when run status is 'success'.")

        return self
