# IncuBrix Social Media Marketing and Content Engine

Growth Engineering assessment project: Option 2 — Social Media Marketing and Content Engine.

## Project Overview

The IncuBrix Content Engine is an automated system designed to transform long-form source documents (product updates, case studies, technical whitepapers) into structured, platform-optimized social media assets across multiple platforms (e.g., LinkedIn, X / Twitter, Instagram).

### Core Capabilities (Planned Architecture)
- **Document Ingestion**: Accepts long-form source documents as input.
- **Multi-Platform Generation**: Produces platform-tailored assets (captions, short-video scripts, carousel/graphic concepts, hashtags, CTAs, and UTM tracking-link fields).
- **Asset Validation**: Enforces structured Pydantic data schemas for content safety and platform compliance.
- **Evidence-Based Content Guardrails**: Prohibits invented product features, unverified metrics, fake customer testimonials, or simulated marketing results. Flags unverified claims for manual review.
- **Duplicate Detection**: Computes content signatures and detects duplicate or near-duplicate assets before storage or scheduling.
- **Persistence & Audit Trail**: Stores generation runs, execution runtime, errors, generation methods (rule-based template vs. LLM), and asset records in SQLite.
- **Exporting**: Exports validated assets into standard CSV and JSON formats for external scheduling workflows.
- **Approval Guardrail**: Does not publish content automatically to public accounts without explicit human authorization.

---

## Directory Structure

```text
Incubrix-Growth/
│
├── .venv/                  # Python 3.13 virtual environment
├── app/
│   ├── __init__.py         # App package
│   ├── database.py         # SQLite connection, transaction, and schema management
│   ├── main.py             # FastAPI entrypoint and health check endpoints
│   ├── models.py           # Pydantic v2 domain schemas (assets, sources, runs)
│   ├── repositories.py     # Persistence, querying, filtering, and deduplication
│   ├── services/           # Content generation, validation, and export services
│   │   ├── __init__.py
│   │   ├── content_engine.py
│   │   └── export_service.py
│   └── templates/          # Platform-specific prompt and copy templates
│
├── data/                   # SQLite database storage (git-ignored)
├── inputs/                 # Source documents for processing
├── outputs/                # Exported CSV / JSON assets (git-ignored)
├── tests/
│   ├── __init__.py         # Test package
│   ├── test_content_engine.py # Generation engine, fact extraction, and API test suite
│   ├── test_database.py    # SQLite schema and repository unit test suite
│   ├── test_exports.py     # CSV and JSON export services and API endpoints test suite
│   ├── test_main.py        # Health endpoint test suite
│   └── test_models.py      # Domain model and Pydantic validation test suite
│
├── .gitignore              # Ignored files (venv, db, caches, secrets)
├── requirements.txt        # Pinned core dependencies
└── README.md               # Setup, usage, and troubleshooting documentation
```

---

## Core Domain Models & Validation Rules

Stage 2 establishes strict Pydantic v2 domain models in `app/models.py`:

- **Platform (`Platform`)**:
  Supports `LinkedIn`, `Instagram`, `YouTube Shorts`, `TikTok`, `X`, `Threads`, `Facebook`, and `Reddit`. Normalizes input case-insensitively and standardizes canonical platform names. Rejects unsupported platforms.
- **Content Asset (`ContentAsset`)**:
  - Enforces formats: `short_video`, `carousel`, `graphic`, `text_post`, `discussion_post`.
  - Enforces non-blank strings across all required fields (`hook`, `caption`, `main_content`, `call_to_action`, `content_pillar`, `audience_segment`, `source_id`).
  - Limits short videos to $\le 60$ seconds with strict `duration_seconds` checks.
  - Normalizes and deduplicates hashtags case-insensitively, prepending `#`.
  - Validates `tracking_url` as an HTTP/HTTPS URL when provided, while permitting `None` during initial drafting.
  - Links structured `evidence_references` (`EvidenceReference`). Any unverified claim automatically marks `review_required = True`.
  - **Approval Guardrail**: Assets cannot be marked `approved` or `published` while `review_required` is True. Newly generated assets (`ai` or `template`) cannot be directly initialized as approved/published.
  - AI identification: assets have `generation_method = ai` and an `is_ai_generated` helper property.
- **Source Document (`SourceDocument`)**:
  - Automatically computes SHA-256 `content_hash` for deduplication. Rejects mismatched hashes.
  - Detects and rejects accidental credential leaks (API keys, bearer tokens, passwords) in metadata.
- **Generation Run (`GenerationRun`)**:
  - Tracks execution telemetry: `runtime_ms`, `assets_created`, `review_required_count`, and `status`.
  - Requires `error_details` on failed runs; ensures review count does not exceed assets created.

---

## SQLite Persistence & Repository Layer

Stage 3 implements lightweight, dependency-free database storage using Python's standard library `sqlite3`:

### Database Configuration
- **Default Database Path**: `data/incubrix_growth.db` (auto-creates directory on initialization).
- **Environment Override**: Configurable via `DATABASE_PATH` environment variable.
- **Foreign Key Enforcement**: `PRAGMA foreign_keys = ON;` is strictly enforced on all connections.
- **Transactions**: Thread-safe connection context managers with automatic rollback on error.
- **Security**: 100% parameterized SQL queries to prevent SQL injection; zero logging of credentials or sensitive document bodies.

### Database Tables & Indexes
1. `source_documents`:
   - Primary Key: `source_id`
   - Fields: `title`, `source_type`, `source_url`, `content_hash` (UNIQUE), `content`, `imported_at`.
   - Indexes: `idx_source_content_hash`, `idx_source_imported_at`.
2. `content_assets`:
   - Primary Key: `asset_id`
   - Foreign Key: `source_id` references `source_documents(source_id)` ON DELETE CASCADE.
   - Fields: `platform`, `content_format`, `content_pillar`, `audience_segment`, `hook`, `main_content`, `caption`, `hashtags` (JSON list), `call_to_action`, `tracking_url`, `evidence_references` (JSON list of models), `review_required` (0 or 1), `review_notes`, `generation_method`, `created_at`, `status`, `duration_seconds`, `content_fingerprint`.
   - Indexes: `idx_assets_platform`, `idx_assets_status`, `idx_assets_source_id`, `idx_assets_fingerprint`, `idx_assets_created_at`.
3. `generation_runs`:
   - Primary Key: `run_id`
   - Foreign Key: `input_source_id` references `source_documents(source_id)` ON DELETE CASCADE.
   - Fields: `started_at`, `completed_at`, `runtime_ms`, `generation_method`, `assets_created`, `review_required_count`, `status`, `error_details`.
   - Indexes: `idx_runs_source_id`, `idx_runs_status`, `idx_runs_started_at`.

### Deduplication Strategies
- **Source Documents**: Deduplicated via SHA-256 `content_hash` at schema and repository level.
- **Content Assets**: Deduplicated using a deterministic normalized content fingerprint (`compute_asset_fingerprint`) combining platform, format, and normalized hook/content text.

### Repository Operations (`app/repositories.py`)
- `insert_source_document` / `get_source_document_by_id` / `get_source_document_by_hash` / `is_duplicate_source`
- `insert_content_asset` / `get_content_asset_by_id` / `list_content_assets` (with platform/status/source filtering) / `is_duplicate_asset`
- `insert_generation_run` / `get_generation_run_by_id` / `update_generation_run`

---

## Evidence-Based Content Generation Engine (Stage 4)

Stage 4 introduces deterministic, explainable content generation in `app/services/content_engine.py` without external AI API dependencies:

### Automated Fact Extraction
- Breaks source text into logical sections and paragraphs.
- Detects factual assertions using structural indicators (headings, numbered/bulleted lists, quantitative metrics, percentages, multipliers, latency figures, and technical growth keywords).
- Retains verbatim substrings as `source_quote` in structured `EvidenceReference` records.
- Associates stable section labels (e.g. `Section 1: The Core Retention Telemetry Loop (¶2)`).

### Explicit Limits of Automated Fact Extraction
> [!IMPORTANT]
> **Operational Boundaries & Limitations:**
> 1. **No External Semantic Verification**: Automated extraction evaluates only syntactic and keyword patterns present in the provided document. It does not browse the web or verify third-party claims.
> 2. **Contextual Dependence**: Statements phrased ambiguously or metaphorically might be extracted if they contain numerical figures; human editorial review is required.
> 3. **Unverified Claims Policy**: Any generated assertion not directly substantiated by verbatim document quotes is flagged with `review_required = True` and assigned `AssetStatus.NEEDS_REVIEW`.
> 4. **No Automated Publishing**: Assets are saved strictly as `draft` or `needs_review`. Direct publication requires explicit human operator sign-off.
> 5. **No Feature Invention**: If a feature or customer outcome is not present in the input document, the engine will never generate claims asserting its existence.

### Platform-Specific Asset Generation Matrix
A single input document yields 12 distinct, platform-adapted assets across 5 social platforms:
1. **LinkedIn Text Post**: Technical thought leadership with bulleted takeaways.
2. **LinkedIn Carousel Concept**: 6-slide visual framework breakdown.
3. **LinkedIn Short Video Script**: 45-second executive briefing with visual and audio cues.
4. **X (Twitter) Concise Post**: Punchy, high-density takeaway ($\le 280$ characters).
5. **X (Twitter) Graphic Concept**: Visual design brief for a system architecture diagram.
6. **Instagram Carousel Guide**: 5-card swipeable step-by-step visual tutorial.
7. **Instagram Infographic Quote Card**: Dark-mode pull-quote typography visual brief.
8. **Instagram Reel Script**: 30-second tactical tip with screen overlay cues.
9. **YouTube Shorts 30s Script**: Fast-paced breakdown with split-screen visual cues.
10. **YouTube Shorts 55s Script**: Comprehensive technical deep dive.
11. **Reddit AMA / Discussion Post**: Technical discourse for engineering subreddits.
12. **Reddit In-Depth Case Teardown**: Detailed technical post with manual review flag for external industry claims.

### REST API Endpoints (`app/main.py`)
- `POST /api/v1/sources`: Ingests and validates source text (returns `201 Created` or `409 Conflict` on duplicates).
- `POST /api/v1/generations`: Generates assets from an ingested source ID with UTM parameters and saves to SQLite.
- `GET /api/v1/assets`: Lists assets with optional `platform`, `status`, and `source_id` filtering.
- `GET /api/v1/assets/{asset_id}`: Retrieves an individual asset by ID.
- `GET /api/v1/runs/{run_id}`: Retrieves telemetry and execution status for a generation run.

---

## Export Services & Scheduling Packaging (Stage 5)

Stage 5 introduces generic scheduler-ready CSV and structured JSON asset export services in `app/services/export_service.py` and dedicated download endpoints in `app/main.py`:

### 1. Generic Scheduler-Ready CSV Export
- **File Encoding**: `UTF-8 with BOM` (`utf-8-sig`) for native compatibility with Microsoft Excel, Google Sheets, and standard spreadsheet applications.
- **Deterministic Field Order (19 Columns)**:
  `asset_id`, `platform`, `content_format`, `content_pillar`, `audience_segment`, `hook`, `main_content`, `caption`, `hashtags`, `call_to_action`, `tracking_url`, `source_id`, `evidence_references`, `review_required`, `review_notes`, `generation_method`, `created_at`, `status`, `duration_seconds`.
- **Complex Field Serialization**: `hashtags` and `evidence_references` are serialized as structured JSON strings within cell boundaries.
- **Formula Injection Mitigation Policy**:
  Any field value starting with spreadsheet formula-leading characters (`=`, `+`, `-`, `@`, `\t`, `\r`) is prefixed with a single quotation mark (`'`). This prevents Excel, Google Sheets, and LibreOffice Calc from executing dynamic formula expressions or DDE commands.
- **Scheduler Compatibility Caveat**:
  > [!NOTE]
  > This export provides a **generic scheduler-ready CSV format**. Do not assume direct zero-configuration import into proprietary schedulers (such as Buffer, Hootsuite, or Sprout Social) without verifying their active schema requirements, column mappings, and date/time formatting rules.
  >
  > Assets exported with `review_required = true` or `status = needs_review` must be reviewed and verified by a human operator prior to manual scheduling. Exporting assets does **not** mark them as approved or published.

### 2. Structured JSON Export
Provides a machine-readable JSON structure with audit metadata:
```json
{
  "export_metadata": {
    "exported_at": "2026-10-24T18:05:00.123456+00:00",
    "generator": "incubrix-content-engine",
    "engine_version": "0.1.0"
  },
  "schema_version": "1.0.0",
  "applied_filters": {
    "platform": "LinkedIn",
    "status": "draft",
    "source_id": null
  },
  "asset_count": 3,
  "assets": [ ... ]
}
```

### 3. Assessment-Workbook-Compatible Calendar Export (Official `02_ASSETS` Tab)

The engine provides an assessment-workbook-compatible content calendar CSV export matching the official IncuBrix workbook's `02_ASSETS` tab with the exact 23 columns in required order.

- **Exact Endpoint**: `GET /api/v1/exports/calendar`
- **Media Type**: `text/csv; charset=utf-8` (encoded with UTF-8 BOM `utf-8-sig` for immediate Microsoft Excel / Google Sheets compatibility)
- **Supported Query Filters**: `platform` (e.g. `LinkedIn`, `X`, `Instagram`), `status` (e.g. `draft`, `needs_review`), `source_id`

#### The Exact 23 Columns (in required order):
1. `asset_id` — Unique asset identifier (e.g. `ast_01b0f1fa4351`)
2. `platform` — Canonical platform name (e.g. `LinkedIn`, `Instagram`, `X`)
3. `format` — Content format (`text_post`, `carousel`, `short_video`, `graphic`, `discussion_post`)
4. `content_pillar` — Content strategy pillar (e.g. `Architecture`, `Tactics`, `Foundations`)
5. `hook` — Attention hook or headline
6. `caption` — Post caption with relevant hashtags
7. `cta` — Call to action
8. `utm_link` — UTM-tagged campaign link (or empty string if not generated)
9. `final_file_url` — **Left strictly blank** (unavailable for generated drafts; never fabricated)
10. `source_file_url` — Legitimate origin source document URL if supplied, otherwise blank
11. `source_input` — Origin source document identifier (`source_id`)
12. `tools_used` — Engine provenance and method (e.g. `IncuBrix Content Engine (template)`)
13. `rights_checked` — Marked `Pending` (rights clearance is never claimed without actual human verification)
14. `ai_label_needed` — Explicit AI disclosure: `Yes` if AI generated, `No` if rule/template generated
15. `scheduled_date` — **Left strictly blank** (unavailable for drafts; never fabricated)
16. `test_published_url` — **Left strictly blank** (no simulated or unauthorized publication)
17. `impressions_or_views` — **Left strictly blank** (no fabricated audience analytics)
18. `engagement_rate` — **Left strictly blank** (no fabricated engagement metrics)
19. `clicks` — **Left strictly blank** (no fabricated traffic metrics)
20. `status` — Faithful lifecycle status (`Draft`, `Needs Review`, `Approved`, `Scheduled`, `Published`, `Rejected`). **Generated drafts are never marked 'Ready'**.
21. `notes` — Review notes and verification flags
22. `duplicate_check` — Duplicate status based on normalized content fingerprint (`Passed (Unique Fingerprint)` or `Duplicate Detected`)
23. `completeness_check` — Verification of required core copy fields (`Complete Draft` or `Incomplete`)

### 4. Export API Endpoints & Example Commands

#### Download Official Workbook Calendar CSV Export (Exact 23 Columns)
```powershell
# Export all assets to official assessment workbook calendar CSV
curl.exe -OJ "http://127.0.0.1:8000/api/v1/exports/calendar"

# Export filtered by platform
curl.exe -OJ "http://127.0.0.1:8000/api/v1/exports/calendar?platform=LinkedIn"

# Export using PowerShell Invoke-RestMethod
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/exports/calendar" -OutFile "outputs/incubrix_workbook_calendar.csv"
```

#### Download Generic Scheduler-Ready CSV Export (19 Columns)
```powershell
# Export all assets to generic scheduler CSV
curl.exe -OJ "http://127.0.0.1:8000/api/v1/exports/csv"

# Export filtered by platform and status
curl.exe -OJ "http://127.0.0.1:8000/api/v1/exports/csv?platform=LinkedIn&status=draft"
```

#### Download Structured JSON Export
```powershell
# Export all assets to JSON
curl.exe -OJ "http://127.0.0.1:8000/api/v1/exports/json"

# Export filtered by source ID
curl.exe -OJ "http://127.0.0.1:8000/api/v1/exports/json?source_id=src_growth_whitepaper"
```

### 5. File Locations & Security
- Export files generated programmatically are written to the `outputs/` directory using safe, timestamped, collision-resistant filenames (`incubrix_assets_YYYYMMDD_HHMMSS_xxxxxx.csv/json`).
- Path traversal attacks via filenames or output directories are strictly blocked.
- Asset status and database records are strictly immutable during exports (drafts remain drafts).

---

## Prerequisites

- **Python**: Version 3.13
- **Operating System**: Windows (PowerShell commands documented below)
- Virtual environment at `.venv`

---

## Setup & Installation

If using the existing `.venv` environment:
```powershell
# Activate virtual environment in PowerShell
.\.venv\Scripts\Activate.ps1

# Ensure dependencies are installed
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## Single Reliable Startup Command

To launch the FastAPI development server with live reload:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, access:
- **Interactive API Docs (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Testing

Execute the test suite using pytest:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

---

## Health Check Verification

Verify the server status via PowerShell `curl` (or `Invoke-RestMethod`):

```powershell
curl http://127.0.0.1:8000/health
```

Expected JSON response:
```json
{
  "status": "healthy",
  "service": "incubrix-content-engine",
  "version": "0.1.0"
}
```

---

## Phase 1 Media Production & Video Rendering Pipeline

Phase 1 completes the end-to-end production of all 30 social media assets documented in [`research/asset_blueprint.csv`](research/asset_blueprint.csv), including automated vertical video rendering, multi-page vector carousel PDFs, architecture diagrams, and publication-ready copy.

### 1. Deliverable Summary (30 Assets Total)
- **13 Short Videos (`short_video`)**: 1080x1920 vertical MP4s ($\le 60$s), neural voiceover, synchronized dynamic captions, code and telemetry graphics.
  - Formats: Source markdown scripts in `outputs/source/videos/`, rendered MP4s in `outputs/final/videos/`.
  - Platforms: YouTube Shorts (9), LinkedIn (3), X (1).
- **4 Carousels (`carousel`)**: 1080x1350 multi-page dark-mode slide decks (5–8 slides each).
  - Formats: Markdown spec + HTML interactive viewer in `outputs/source/carousels/`, vector PDF in `outputs/final/carousels/`.
  - Platform: LinkedIn (4).
- **3 Graphics (`graphic`)**: 1200x675 high-resolution architectural infographics and retention charts.
  - Formats: Markdown spec + SVG vector source in `outputs/source/graphics/`, rendered PNG in `outputs/final/graphics/`.
  - Platform: X (3).
- **10 Text Posts (`text_post`)**: Publication-ready long-form copy and threaded posts with character counts and verified evidence tags.
  - Formats: Markdown specs in `outputs/source/copy/` and `outputs/final/copy/`.
  - Platforms: LinkedIn (4), X (6).

### 2. Reproducible Generation Commands

#### Batch Render All 13 Short Videos:
```powershell
.\.venv\Scripts\python.exe scripts/render_all_videos.py
```
*Note: Uses `edge-tts` (Microsoft neural TTS) for clear voiceover, `Pillow` for frame synthesis with kinetic captions, and `imageio-ffmpeg` for H.264/AAC MP4 encoding.*

#### Render Multi-Page Carousel PDFs:
```powershell
.\.venv\Scripts\python.exe scripts/render_carousel_pdf.py
```
*Note: Generates vector PDF 1.4 documents (1080x1350 pt) natively in Python.*

#### Render Graphic PNGs:
```powershell
.\.venv\Scripts\python.exe scripts/render_graphics.py
```
*Note: Renders crisp 1200x675 PNG diagrams with Pillow.*

#### Run Phase 1 Technical Validation Audit:
```powershell
.\.venv\Scripts\python.exe scripts/validate_phase1.py
```
*Verifies all 30 assets, video durations $\le 60$s, resolutions (1080x1920, 1080x1350, 1200x675), audio/video streams, and source-to-final traceability.*

### 3. Remaining Manual Tasks
1. **Live Product Demo Screencasts (2 Unedited Videos)**:
   The assessment Option 2 specification requires two unedited walkthrough videos demonstrating:
   - Video A: Ingestion of source documents and automated generation of multi-platform social assets.
   - Video B: Duplicate detection, evidence reference verification, and CSV/JSON export workflows.
   *Status: Requires interactive desktop screen recording with the operator's microphone.*
2. **Phase 2 Content Calendar Review**:
   Review and schedule the 30 planned assets into the editorial calendar once public posting channels and UTM parameters are confirmed.

---

## Content Safety & Editorial Guardrails

1. **Evidence-Based Copy**: All claims, metrics, and capabilities must originate strictly from the provided source document.
2. **Review Flags**: Any generated assertion that cannot be verified directly in the source document is tagged with `review_required: true`.
3. **No Automatic Public Dispatch**: Content generation is isolated to local staging, export files, and review interfaces. Public publishing requires explicit operator approval.
4. **Environment Isolation**: Secrets, API keys, and environment-specific configs must reside exclusively in `.env` or system environment variables.

---

## Troubleshooting

- **Port already in use**:
  If port 8000 is occupied, run Uvicorn on another port:
  ```powershell
  .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8080
  ```
- **PowerShell Execution Policy Error**:
  If `.venv\Scripts\Activate.ps1` gives an execution policy error, run directly via python executable without activating:
  ```powershell
  .\.venv\Scripts\python.exe -m pytest -v
  ```
