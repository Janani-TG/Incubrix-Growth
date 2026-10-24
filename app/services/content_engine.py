"""Evidence-based content generation engine and template service."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import re
import sqlite3
import time
import urllib.parse
import uuid

from pydantic import BaseModel, Field

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
from app.repositories import (
    DuplicateRecordError,
    compute_asset_fingerprint,
    insert_content_asset,
    insert_generation_run,
    is_duplicate_asset,
    update_generation_run,
)

logger = logging.getLogger("incubrix.content_engine")

MIN_SOURCE_CHARS = 100
MIN_SOURCE_WORDS = 15


# ============================================================================
# Fact Extraction Models & Helpers
# ============================================================================

class ExtractedFact(BaseModel):
    """Deterministic fact extracted from a source document."""
    claim: str
    source_quote: str
    section_or_page: str
    is_verified: bool = True
    confidence: float = 1.0


def extract_sections_and_facts(content: str) -> list[ExtractedFact]:
    """Split long-form text into sections and extract deterministic candidate facts."""
    stripped = content.strip()
    if len(stripped) < MIN_SOURCE_CHARS:
        raise ValueError(
            f"Input text is too short ({len(stripped)} chars). "
            f"Minimum {MIN_SOURCE_CHARS} characters required for content generation."
        )

    words = stripped.split()
    if len(words) < MIN_SOURCE_WORDS:
        raise ValueError(
            f"Input text contains too few words ({len(words)} words). "
            f"Minimum {MIN_SOURCE_WORDS} words required."
        )

    lines = [line.strip() for line in stripped.splitlines()]
    current_section = "Overview"
    extracted_facts: list[ExtractedFact] = []

    # Patterns indicating factual quantitative data or engineering principles
    metric_pattern = re.compile(r"(\d+[\d\.,]*%?|\b[0-9]+x\b|\$[0-9]+|\b\d+\b)")
    principle_keywords = {
        "retention", "growth", "conversion", "framework", "architecture",
        "benchmark", "latency", "pipeline", "instrument", "telemetry",
        "acquisition", "cohort", "onboarding", "churn", "engagement"
    }

    paragraph_index = 0
    for line in lines:
        if not line:
            continue

        # Detect section headings
        if line.startswith("#"):
            current_section = line.lstrip("#").strip()
            continue
        elif line.endswith(":") and len(line) < 80:
            current_section = line.rstrip(":").strip()
            continue

        paragraph_index += 1
        sentences = re.split(r"(?<=[.!?])\s+", line)
        for sent in sentences:
            sent_clean = sent.strip()
            if len(sent_clean) < 25:
                continue

            has_metric = bool(metric_pattern.search(sent_clean))
            has_keyword = any(kw in sent_clean.lower() for kw in principle_keywords)
            is_bullet = sent_clean.startswith(("-", "*", "•", "1.", "2.", "3."))

            if has_metric or has_keyword or is_bullet:
                claim_summary = sent_clean.lstrip("-*• 0123456789.")
                if len(claim_summary) > 250:
                    claim_summary = claim_summary[:247] + "..."

                extracted_facts.append(
                    ExtractedFact(
                        claim=claim_summary.strip(),
                        source_quote=sent_clean,
                        section_or_page=f"{current_section} (¶{paragraph_index})",
                        is_verified=True,
                    )
                )

    # Fallback if specific keywords are scarce: capture top descriptive sentences
    if not extracted_facts:
        for idx, line in enumerate(lines[:5], start=1):
            if len(line) >= 40:
                extracted_facts.append(
                    ExtractedFact(
                        claim=line[:250],
                        source_quote=line,
                        section_or_page=f"Section 1 (¶{idx})",
                        is_verified=True,
                    )
                )

    return extracted_facts


# ============================================================================
# UTM Tracking Link Generator
# ============================================================================

def build_tracking_url(
    base_url: str | None,
    platform: Platform,
    content_format: ContentFormat,
    campaign: str = "growth_engine",
    asset_id: str | None = None,
) -> str | None:
    """Build a validated UTM tracking URL with deterministic parameters."""
    if not base_url or not base_url.strip():
        return None

    clean_base = base_url.strip()
    parsed = urllib.parse.urlparse(clean_base)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(
            f"Invalid base tracking URL: '{base_url}'. Must include valid http:// or https:// scheme."
        )

    plat_slug = platform.value.lower().replace(" ", "_").replace(".", "")
    medium_map = {
        ContentFormat.SHORT_VIDEO: "video",
        ContentFormat.CAROUSEL: "carousel",
        ContentFormat.GRAPHIC: "graphic",
        ContentFormat.TEXT_POST: "social_post",
        ContentFormat.DISCUSSION_POST: "community",
    }
    medium = medium_map.get(content_format, "social")
    content_tag = f"{content_format.value}_{asset_id[:8]}" if asset_id else content_format.value

    params = [
        ("utm_source", plat_slug),
        ("utm_medium", medium),
        ("utm_campaign", campaign.lower().strip()),
        ("utm_content", content_tag),
    ]

    existing_query = urllib.parse.parse_qsl(parsed.query)
    combined_query = urllib.parse.urlencode(existing_query + params)

    return urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        combined_query,
        parsed.fragment,
    ))


# ============================================================================
# Content Generation Engine
# ============================================================================

class GenerationResult(BaseModel):
    """Result summary of a content generation execution."""
    run: GenerationRun
    assets: list[ContentAsset]
    created_count: int
    skipped_duplicate_count: int
    review_required_count: int


def generate_assets_from_source(
    source: SourceDocument,
    base_tracking_url: str | None = None,
    campaign: str = "growth_engine",
    flag_unverified_sample: bool = True,
) -> list[ContentAsset]:
    """Generate at least 10 distinct, platform-tailored content assets from a source document."""
    facts = extract_sections_and_facts(source.content)
    if not facts:
        raise ValueError("Could not extract any factual statements from the source document.")

    # Cycle through extracted facts to ground each asset
    f0 = facts[0]
    f1 = facts[1] if len(facts) > 1 else f0
    f2 = facts[2] if len(facts) > 2 else f0
    f3 = facts[3] if len(facts) > 3 else f1

    assets: list[ContentAsset] = []

    def make_ev_ref(fact: ExtractedFact) -> EvidenceReference:
        return EvidenceReference(
            claim=fact.claim,
            source_quote=fact.source_quote,
            section_or_page=fact.section_or_page,
            is_verified=fact.is_verified,
        )

    # -------------------------------------------------------------------------
    # 1. LinkedIn Thought Leadership Text Post
    # -------------------------------------------------------------------------
    aid1 = f"ast_li_text_{uuid.uuid4().hex[:8]}"
    assets.append(
        ContentAsset(
            id=aid1,
            platform=Platform.LINKEDIN,
            content_format=ContentFormat.TEXT_POST,
            content_pillar="Growth Engineering Frameworks",
            audience_segment="Technical Founders & Growth Engineers",
            hook=f"Engineering leaders: {f0.claim}",
            main_content=(
                f"Most early-stage teams attempt to scale acquisition too quickly.\n\n"
                f"Key data points from our latest technical teardown:\n"
                f"1. {f0.claim}\n"
                f"2. {f1.claim}\n\n"
                f"Telemetry loops must be established before capital is committed to expansion."
            ),
            caption="Key learnings from our technical architecture review. Details in the post.",
            hashtags=["#GrowthEngineering", "#B2BTech", "#ProductLedGrowth", "#SaaSMetrics"],
            call_to_action="How does your team instrument these telemetry loops? Share your thoughts below.",
            tracking_url=build_tracking_url(base_tracking_url, Platform.LINKEDIN, ContentFormat.TEXT_POST, campaign, aid1),
            source_id=source.id,
            evidence_references=[make_ev_ref(f0), make_ev_ref(f1)],
            review_required=False,
            generation_method=GenerationMethod.TEMPLATE,
            status=AssetStatus.DRAFT,
        )
    )

    # -------------------------------------------------------------------------
    # 2. LinkedIn Carousel Concept (5-Slide Breakdown)
    # -------------------------------------------------------------------------
    aid2 = f"ast_li_caro_{uuid.uuid4().hex[:8]}"
    assets.append(
        ContentAsset(
            id=aid2,
            platform=Platform.LINKEDIN,
            content_format=ContentFormat.CAROUSEL,
            content_pillar="Engineering Playbooks",
            audience_segment="Technical Product Managers",
            hook="The 5-Slide Technical Growth Architecture (Swipeable Guide)",
            main_content=(
                f"Slide 1 [Cover]: The Architecture Behind Growth Telemetry\n"
                f"Slide 2 [Context]: Why unmonitored acquisition burns engineering bandwidth.\n"
                f"Slide 3 [Core Finding]: {f0.claim}\n"
                f"Slide 4 [Implementation]: {f1.claim}\n"
                f"Slide 5 [Checklist]: Audit onboarding events, establish cohort tracking, review weekly.\n"
                f"Slide 6 [Outro]: Save this slide deck for sprint planning."
            ),
            caption="Swipe through for the 5-step technical framework on growth telemetry.",
            hashtags=["#SaaSGrowth", "#SoftwareEngineering", "#ProductManagement", "#Carousel"],
            call_to_action="Save this carousel for your next product planning sprint.",
            tracking_url=build_tracking_url(base_tracking_url, Platform.LINKEDIN, ContentFormat.CAROUSEL, campaign, aid2),
            source_id=source.id,
            evidence_references=[make_ev_ref(f0), make_ev_ref(f1)],
            review_required=False,
            generation_method=GenerationMethod.TEMPLATE,
            status=AssetStatus.DRAFT,
        )
    )

    # -------------------------------------------------------------------------
    # 3. LinkedIn Short Video Script (45s Executive Briefing)
    # -------------------------------------------------------------------------
    aid3 = f"ast_li_vid_{uuid.uuid4().hex[:8]}"
    assets.append(
        ContentAsset(
            id=aid3,
            platform=Platform.LINKEDIN,
            content_format=ContentFormat.SHORT_VIDEO,
            duration_seconds=45.0,
            content_pillar="Executive Briefings",
            audience_segment="CTOs & Engineering Directors",
            hook="Before scaling ad spend, check this one critical engineering metric.",
            main_content=(
                f"[0:00 - 0:10] (Direct to camera) Scaling acquisition without retention telemetry is a trap.\n"
                f"[0:10 - 0:28] (B-roll of metric dashboard) Here is the evidence: {f0.claim}. Without this, growth loops stall.\n"
                f"[0:28 - 0:45] (Direct to camera) Instrument your core lifecycle events first. Details in the comments."
            ),
            caption="A 45-second executive briefing on growth telemetry and cohort monitoring.",
            hashtags=["#EngineeringLeadership", "#CTO", "#TechStrategy", "#VideoScript"],
            call_to_action="Watch the full briefing and join the discussion in the comments.",
            tracking_url=build_tracking_url(base_tracking_url, Platform.LINKEDIN, ContentFormat.SHORT_VIDEO, campaign, aid3),
            source_id=source.id,
            evidence_references=[make_ev_ref(f0)],
            review_required=False,
            generation_method=GenerationMethod.TEMPLATE,
            status=AssetStatus.DRAFT,
        )
    )

    # -------------------------------------------------------------------------
    # 4. X (Twitter) Concise Takeaway
    # -------------------------------------------------------------------------
    aid4 = f"ast_x_post_{uuid.uuid4().hex[:8]}"
    assets.append(
        ContentAsset(
            id=aid4,
            platform=Platform.X,
            content_format=ContentFormat.TEXT_POST,
            content_pillar="Growth Engineering Insights",
            audience_segment="Founders & Builders",
            hook="Hard reality about engineering-led growth:",
            main_content=(
                f"{f0.claim}\n\n"
                f"Scaling traffic before instrumenting retention is the fastest way to burn capital."
            ),
            caption="Key takeaway from our latest technical analysis.",
            hashtags=["#BuildInPublic", "#GrowthHacking", "#TechTwitter"],
            call_to_action="Repost if your team prioritizes retention over vanity metrics.",
            tracking_url=build_tracking_url(base_tracking_url, Platform.X, ContentFormat.TEXT_POST, campaign, aid4),
            source_id=source.id,
            evidence_references=[make_ev_ref(f0)],
            review_required=False,
            generation_method=GenerationMethod.TEMPLATE,
            status=AssetStatus.DRAFT,
        )
    )

    # -------------------------------------------------------------------------
    # 5. X (Twitter) Graphic Concept
    # -------------------------------------------------------------------------
    aid5 = f"ast_x_graph_{uuid.uuid4().hex[:8]}"
    assets.append(
        ContentAsset(
            id=aid5,
            platform=Platform.X,
            content_format=ContentFormat.GRAPHIC,
            content_pillar="Architecture Diagrams",
            audience_segment="Software Developers & Data Engineers",
            hook="Architecture diagram: How telemetry loops compound over time.",
            main_content=(
                f"Visual Design Brief:\n"
                f"- Dark background (#0D1117), crisp lime/cyan accents.\n"
                f"- Central flow diagram: User Ingestion -> Lifecycle Telemetry -> Cohort Analysis.\n"
                f"- Callout stat card quoting: '{f1.claim}'\n"
                f"- Minimalist IncuBrix badge in the lower-right corner."
            ),
            caption="Visualizing the telemetry architecture outlined in our recent documentation.",
            hashtags=["#DataEngineering", "#Architecture", "#SystemsDesign"],
            call_to_action="Check the full architecture doc via the link below.",
            tracking_url=build_tracking_url(base_tracking_url, Platform.X, ContentFormat.GRAPHIC, campaign, aid5),
            source_id=source.id,
            evidence_references=[make_ev_ref(f1)],
            review_required=False,
            generation_method=GenerationMethod.TEMPLATE,
            status=AssetStatus.DRAFT,
        )
    )

    # -------------------------------------------------------------------------
    # 6. Instagram Visual Carousel Guide
    # -------------------------------------------------------------------------
    aid6 = f"ast_ig_caro_{uuid.uuid4().hex[:8]}"
    assets.append(
        ContentAsset(
            id=aid6,
            platform=Platform.INSTAGRAM,
            content_format=ContentFormat.CAROUSEL,
            content_pillar="Visual Growth Guides",
            audience_segment="Tech Entrepreneurs & Designers",
            hook="Why early growth stalls: 4 data points every founder should know 📊",
            main_content=(
                f"Card 1: Bold cover graphic - 'The Anatomy of a Leaky Funnel'\n"
                f"Card 2: Primary finding - '{f0.claim}'\n"
                f"Card 3: Secondary observation - '{f1.claim}'\n"
                f"Card 4: Diagnostic checklist for engineering leads.\n"
                f"Card 5: Summary takeaway and save prompt."
            ),
            caption="Don't scale ad spend on unmeasured funnels. Here is what the numbers teach us about retention.",
            hashtags=["#TechStartups", "#Infographic", "#StartupLife", "#DataDriven"],
            call_to_action="Save this post for your next growth review meeting.",
            tracking_url=build_tracking_url(base_tracking_url, Platform.INSTAGRAM, ContentFormat.CAROUSEL, campaign, aid6),
            source_id=source.id,
            evidence_references=[make_ev_ref(f0), make_ev_ref(f1)],
            review_required=False,
            generation_method=GenerationMethod.TEMPLATE,
            status=AssetStatus.DRAFT,
        )
    )

    # -------------------------------------------------------------------------
    # 7. Instagram Graphic Concept (Pull Quote Card)
    # -------------------------------------------------------------------------
    aid7 = f"ast_ig_graph_{uuid.uuid4().hex[:8]}"
    assets.append(
        ContentAsset(
            id=aid7,
            platform=Platform.INSTAGRAM,
            content_format=ContentFormat.GRAPHIC,
            content_pillar="Data Highlights",
            audience_segment="Startup Engineers",
            hook="The single metric that shifts the equation:",
            main_content=(
                f"Visual Graphic Spec:\n"
                f"- High-contrast typography on charcoal background.\n"
                f"- Large quote text: '{f2.claim}'\n"
                f"- Attribution: Source documentation, {f2.section_or_page}."
            ),
            caption="Direct finding from our technical research. Link in bio for the full document.",
            hashtags=["#TechQuotes", "#EngineeringMindset", "#ProductDesign", "#Data"],
            call_to_action="Share this with a founder or engineer who is scaling their stack.",
            tracking_url=build_tracking_url(base_tracking_url, Platform.INSTAGRAM, ContentFormat.GRAPHIC, campaign, aid7),
            source_id=source.id,
            evidence_references=[make_ev_ref(f2)],
            review_required=False,
            generation_method=GenerationMethod.TEMPLATE,
            status=AssetStatus.DRAFT,
        )
    )

    # -------------------------------------------------------------------------
    # 8. Instagram Reel (30-second Tactical Tip)
    # -------------------------------------------------------------------------
    aid8 = f"ast_ig_vid_{uuid.uuid4().hex[:8]}"
    assets.append(
        ContentAsset(
            id=aid8,
            platform=Platform.INSTAGRAM,
            content_format=ContentFormat.SHORT_VIDEO,
            duration_seconds=30.0,
            content_pillar="Tactical Reels",
            audience_segment="Growth Marketers & Indie Builders",
            hook="Stop optimizing ads until you check this one thing.",
            main_content=(
                f"[0-5s] (Screen recording of code/terminal) On-screen text: 'The #1 growth blindspot'\n"
                f"[5-20s] (Voiceover) According to engineering data: '{f0.claim}'\n"
                f"[20-30s] (On-screen checklist) Fix your event tracking first. Save this Reel!"
            ),
            caption="30-second breakdown on measuring user activation before scaling spend. Save for later!",
            hashtags=["#ReelsTech", "#GrowthTips", "#SaaS", "#Startups"],
            call_to_action="Follow for more technical engineering breakdowns.",
            tracking_url=build_tracking_url(base_tracking_url, Platform.INSTAGRAM, ContentFormat.SHORT_VIDEO, campaign, aid8),
            source_id=source.id,
            evidence_references=[make_ev_ref(f0)],
            review_required=False,
            generation_method=GenerationMethod.TEMPLATE,
            status=AssetStatus.DRAFT,
        )
    )

    # -------------------------------------------------------------------------
    # 9. YouTube Shorts Script (30-second Fast-Paced Breakdown)
    # -------------------------------------------------------------------------
    aid9 = f"ast_yt_30_{uuid.uuid4().hex[:8]}"
    assets.append(
        ContentAsset(
            id=aid9,
            platform=Platform.YOUTUBE_SHORTS,
            content_format=ContentFormat.SHORT_VIDEO,
            duration_seconds=30.0,
            content_pillar="Shorts Teardowns",
            audience_segment="Developers & Startup Teams",
            hook="Why 80% of growth experiments fail before they even start.",
            main_content=(
                f"[0:00 - 0:05] (Hook visual with flashing alert) Why do most growth experiments fail?\n"
                f"[0:05 - 0:20] (Visual diagram) Because: {f0.claim}. Without baseline telemetry, you cannot isolate lift.\n"
                f"[0:20 - 0:30] (Host on camera) Instrument first, experiment second. Subscribe for weekly teardowns."
            ),
            caption="The engineering data behind experiment success rates. Subscribe for weekly breakdowns!",
            hashtags=["#Shorts", "#Programming", "#TechExplained", "#Developer"],
            call_to_action="Subscribe for more technical engineering teardowns.",
            tracking_url=build_tracking_url(base_tracking_url, Platform.YOUTUBE_SHORTS, ContentFormat.SHORT_VIDEO, campaign, aid9),
            source_id=source.id,
            evidence_references=[make_ev_ref(f0)],
            review_required=False,
            generation_method=GenerationMethod.TEMPLATE,
            status=AssetStatus.DRAFT,
        )
    )

    # -------------------------------------------------------------------------
    # 10. YouTube Shorts Script (55-second Deep Dive Breakdown)
    # -------------------------------------------------------------------------
    aid10 = f"ast_yt_60_{uuid.uuid4().hex[:8]}"
    assets.append(
        ContentAsset(
            id=aid10,
            platform=Platform.YOUTUBE_SHORTS,
            content_format=ContentFormat.SHORT_VIDEO,
            duration_seconds=55.0,
            content_pillar="In-Depth Technical Teardowns",
            audience_segment="Senior Software Engineers",
            hook="Here is the exact telemetry framework high-scale engineering teams use.",
            main_content=(
                f"[0:00 - 0:10] (Setup) Let's examine how scalable engineering architectures measure retention.\n"
                f"[0:10 - 0:25] (Metric inspection) Fact: {f1.claim}. Without this, cohort curves cannot be tracked.\n"
                f"[0:25 - 0:40] (Architecture deep dive) Also observe: {f2.claim}.\n"
                f"[0:40 - 0:55] (Conclusion) Build the data loops first. Link in the description for the full source paper."
            ),
            caption="Deep dive on telemetry architecture for scalable retention loops. Link in description.",
            hashtags=["#Shorts", "#EngineeringLeadership", "#TechTutorial", "#SystemDesign"],
            call_to_action="Check the video description for the complete source documentation.",
            tracking_url=build_tracking_url(base_tracking_url, Platform.YOUTUBE_SHORTS, ContentFormat.SHORT_VIDEO, campaign, aid10),
            source_id=source.id,
            evidence_references=[make_ev_ref(f1), make_ev_ref(f2)],
            review_required=False,
            generation_method=GenerationMethod.TEMPLATE,
            status=AssetStatus.DRAFT,
        )
    )

    # -------------------------------------------------------------------------
    # 11. Reddit Technical AMA / Discussion Post
    # -------------------------------------------------------------------------
    aid11 = f"ast_rd_disc_{uuid.uuid4().hex[:8]}"
    assets.append(
        ContentAsset(
            id=aid11,
            platform=Platform.REDDIT,
            content_format=ContentFormat.DISCUSSION_POST,
            content_pillar="Engineering Discourse",
            audience_segment="r/softwareengineering & r/startups Community",
            hook="What are your team's hard criteria before scaling channel acquisition?",
            main_content=(
                f"We recently analyzed growth telemetry frameworks and wanted to open a technical discussion.\n\n"
                f"The source findings noted: '{f0.source_quote}'\n\n"
                f"In our experience, teams often skip event verification during early sprints, leading to noisy attribution.\n\n"
                f"Questions for the community:\n"
                f"- What event schema standards do you enforce for user activation?\n"
                f"- How do you handle cohort retention degradation in early releases?"
            ),
            caption="Technical community discussion on telemetry criteria before channel expansion.",
            hashtags=["#SoftwareEngineering", "#Architecture", "#Discussion"],
            call_to_action="Curious to hear how other teams handle this in production.",
            tracking_url=build_tracking_url(base_tracking_url, Platform.REDDIT, ContentFormat.DISCUSSION_POST, campaign, aid11),
            source_id=source.id,
            evidence_references=[make_ev_ref(f0)],
            review_required=False,
            generation_method=GenerationMethod.TEMPLATE,
            status=AssetStatus.DRAFT,
        )
    )

    # -------------------------------------------------------------------------
    # 12. Reddit In-Depth Case Teardown (with Safety Review Flag)
    # -------------------------------------------------------------------------
    aid12 = f"ast_rd_text_{uuid.uuid4().hex[:8]}"
    unverified_claim_ref = EvidenceReference(
        claim="Early activation optimization reduces customer acquisition costs by 40%.",
        source_quote="Generic industry benchmark claim requiring verification against primary source data.",
        section_or_page="General Industry Speculation",
        is_verified=False,
        verification_notes="Unverified industry percentage claim flagged for manual human verification.",
    )

    assets.append(
        ContentAsset(
            id=aid12,
            platform=Platform.REDDIT,
            content_format=ContentFormat.TEXT_POST,
            content_pillar="Technical Case Studies",
            audience_segment="r/SaaS & r/GrowthHacking Community",
            hook="Technical Teardown: How telemetry loops compound engineering output",
            main_content=(
                f"Detailed breakdown of findings from source document '{source.title}':\n\n"
                f"1. Core Observation: {f1.claim}\n"
                f"2. Methodological note: {f3.claim}\n\n"
                f"Industry benchmark note: While some external reports claim 40% cost reductions, "
                f"this assertion requires verification against primary engineering metrics.\n\n"
                f"Sharing this without sales pitch to get peer feedback on implementation trade-offs."
            ),
            caption="Analytical teardown analyzing telemetry models and cohort measurement.",
            hashtags=["#SaaS", "#CaseStudy", "#Engineering"],
            call_to_action="Open to technical feedback and questions in the comments.",
            tracking_url=build_tracking_url(base_tracking_url, Platform.REDDIT, ContentFormat.TEXT_POST, campaign, aid12),
            source_id=source.id,
            evidence_references=[make_ev_ref(f1), make_ev_ref(f3), unverified_claim_ref],
            review_required=True,  # Explicitly requires review due to unverified claim
            review_notes="Flagged for manual review: contains unverified benchmark claim.",
            generation_method=GenerationMethod.TEMPLATE,
            status=AssetStatus.NEEDS_REVIEW,
        )
    )

    return assets


# ============================================================================
# Service Layer Orchestrator
# ============================================================================

def run_generation_service(
    source: SourceDocument,
    base_tracking_url: str | None = None,
    campaign: str = "growth_engine",
    conn: sqlite3.Connection | None = None,
    persist: bool = True,
) -> GenerationResult:
    """Orchestrate content asset generation from a source document with persistence and deduplication."""
    start_time = time.perf_counter()
    now_utc = datetime.now(timezone.utc)
    run_id = f"run_{uuid.uuid4().hex[:12]}"

    if persist and conn is None:
        raise ValueError("A database connection must be provided when persist=True.")

    # Initialize the run record
    run_record = GenerationRun(
        id=run_id,
        source_id=source.id,
        started_at=now_utc,
        generation_method=GenerationMethod.TEMPLATE,
        status=RunStatus.PENDING,
    )

    if persist and conn is not None:
        insert_generation_run(conn, run_record)

    try:
        candidate_assets = generate_assets_from_source(
            source=source,
            base_tracking_url=base_tracking_url,
            campaign=campaign,
        )

        persisted_assets: list[ContentAsset] = []
        created_count = 0
        skipped_count = 0
        review_count = 0

        for asset in candidate_assets:
            if persist and conn is not None:
                # Check for existing duplicate fingerprint
                if is_duplicate_asset(conn, asset):
                    logger.info("Skipping duplicate asset for platform %s.", asset.platform.value)
                    skipped_count += 1
                    continue

                insert_content_asset(conn, asset, allow_duplicate=False)
                persisted_assets.append(asset)
                created_count += 1
                if asset.review_required:
                    review_count += 1
            else:
                persisted_assets.append(asset)
                created_count += 1
                if asset.review_required:
                    review_count += 1

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        completed_utc = datetime.now(timezone.utc)

        if persist and conn is not None:
            updated_run = update_generation_run(
                conn=conn,
                run_id=run_id,
                status=RunStatus.SUCCESS,
                completed_at=completed_utc,
                runtime_ms=elapsed_ms,
                assets_created=created_count,
                review_required_count=review_count,
            )
        else:
            updated_run = GenerationRun(
                id=run_id,
                source_id=source.id,
                started_at=now_utc,
                completed_at=completed_utc,
                runtime_ms=elapsed_ms,
                generation_method=GenerationMethod.TEMPLATE,
                assets_created=created_count,
                review_required_count=review_count,
                status=RunStatus.SUCCESS,
            )

        return GenerationResult(
            run=updated_run,
            assets=persisted_assets,
            created_count=created_count,
            skipped_duplicate_count=skipped_count,
            review_required_count=review_count,
        )

    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        if persist and conn is not None:
            try:
                update_generation_run(
                    conn=conn,
                    run_id=run_id,
                    status=RunStatus.FAILED,
                    completed_at=datetime.now(timezone.utc),
                    runtime_ms=elapsed_ms,
                    error_details=f"{exc.__class__.__name__}: {str(exc)}",
                )
            except Exception as update_err:
                logger.error("Failed to update run status: %s", update_err)
        raise
