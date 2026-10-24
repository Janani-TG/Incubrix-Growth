# Asset Source & Slide Specification: ast_bp_10_li_caro

**Asset ID:** `ast_bp_10_li_caro`  
**Platform:** LinkedIn (Document Carousel PDF)  
**Format:** carousel (6 Slides, 1080x1350 px, 4:5 Aspect Ratio)  
**Content Pillar:** Creator & Marketer Workflow Engineering  
**Audience Segment:** Technical Marketers  
**Production Status:** Planned (Editable Source & Multi-Page PDF Rendered; Final Review Pending)  
**Tracking Link Status:** `Pending Confirmation [https://incubrix.com/matrix-template?utm_source=linkedin&utm_medium=carousel&utm_campaign=content_matrix&utm_content=ast_bp_10_li_caro]`

---

## 1. Slide-by-Slide Copy & Layout Specification

### Slide 1: Cover / Hook
- **Visual Style:** Deep charcoal background (`#111827`), emerald green accents (`#10B981`), badge: `CONTENT REPURPOSING PLAYBOOK`.
- **Primary Headline:** Whitepaper to 12 Social Assets: The Repurposing Matrix
- **Subtitle:** Stop writing 10 separate posts from scratch. Here is how growth teams systematically extract high-density social assets from single technical source documents.
- **Footer:** `Swipe to explore the matrix -> [Slide 1/6]`

---

### Slide 2: The Core Problem (The Content Treadmill)
- **Visual Style:** Two-column pain-point breakdown.
- **Header:** `THE REPURPOSING BOTTLENECK`
- **Pain Points:**
  - **Manual Rewrite Fatigue:** Marketing teams spend 12 hours rewording release notes into generic tweets.
  - **Context Dilution:** Outsourced copywriters butcher technical accuracy to make copy "punchy."
  - **Channel Fragmentation:** Copy-pasting identical text across LinkedIn, X, and YouTube ignores native algorithmic formats.
- **The Solution:** A deterministic content matrix that maps source sections to platform-adapted asset schemas.
- **Footer:** `IncuBrix Growth Framework [Slide 2/6]`

---

### Slide 3: Step 1 — Automated Fact & Evidence Extraction
- **Visual Style:** Graphic showing source whitepaper text highlighted with structured tags.
- **Header:** `STEP 1: FACT-BASED INGESTION`
- **Extraction Workflow:**
  - **Structural Parsing:** Split whitepaper into titled sections, paragraphs, and lists.
  - **Metric Detection:** Flag quantitative metrics (percentages, latencies, multipliers).
  - **Verbatim Citations:** Retain the exact source sentence as an `EvidenceReference` model.
- **Guardrail:** Never allow generative tools to hallucinate features or customer outcomes not present in the source text.
- **Footer:** `IncuBrix Growth Framework [Slide 3/6]`

---

### Slide 4: The 12-Asset Platform Matrix
- **Visual Style:** High-density 3-column table showing format distribution.
- **Header:** `STEP 2: THE MULTI-PLATFORM MATRIX`
- **Asset Distribution from 1 Document:**
  - **LinkedIn (3 Assets):** 1 Technical Thought Leadership Post, 1 Visual Framework Carousel, 1 45s Executive Briefing Video.
  - **X / Twitter (2 Assets):** 1 Concise Metric Takeaway ($\le 280$ chars), 1 System Architecture Graphic.
  - **Instagram (3 Assets):** 1 Visual Step-by-Step Carousel, 1 Infographic Card, 1 30s Tactical Reel.
  - **YouTube Shorts (2 Assets):** 1 30s Fast Breakdown, 1 55s In-Depth Code Teardown.
  - **Developer Forums / Reddit (2 Assets):** 1 Technical Discussion Post, 1 Deep-Dive Architectural Teardown.
- **Footer:** `IncuBrix Growth Framework [Slide 4/6]`

---

### Slide 5: Quality Assurance & Readiness Gates
- **Visual Style:** 4-step sequential quality gate diagram.
- **Header:** `STEP 3: EDITORIAL GUARDRAILS`
- **Readiness Protocol:**
  - **Gate 1 (Evidence Check):** Unverified claims automatically trigger `review_required = True`.
  - **Gate 2 (AI Disclosure):** Machine-assisted copy is transparently labeled (`ai_label_needed = Yes`).
  - **Gate 3 (Rights Clearance):** Media licenses marked `Pending` until explicit human sign-off.
  - **Gate 4 (Deduplication):** SHA-256 fingerprinting guarantees zero duplicate posts.
- **Footer:** `IncuBrix Growth Framework [Slide 5/6]`

---

### Slide 6: Summary & Actionable Download
- **Visual Style:** Highlighted summary card with download prompt.
- **Header:** `SYSTEMATIZE YOUR CONTENT ENGINE`
- **Action Plan:**
  - Take your best technical engineering whitepaper.
  - Extract the 5 core architectural assertions.
  - Map into the 12-asset repurposing matrix.
  - Enforce server-side UTM attribution on every CTA.
- **Call to Action:** Save this carousel and download the 12-Asset Content Repurposing Matrix template via link.
- **Footer:** `Save for your next content sprint [Slide 6/6]`

---

## 2. Publication-Ready Caption & Metadata

**Post Hook:** Stop writing 10 separate posts from scratch. Here is how to turn 1 technical whitepaper into 12 distinct, platform-native social assets.  
**Full Caption:**  
The biggest bottleneck in B2B technical content marketing isn't writing—it's distribution.

Engineering teams spend weeks drafting comprehensive documentation, only for marketing to tweet a single generic link that nobody clicks.

Swipe through for the 6-slide Repurposing Matrix:
- Slide 1: The Content Treadmill
- Slide 2: Why Manual Rewrites Fail
- Slide 3: Fact-Based Evidence Extraction
- Slide 4: The 12-Asset Platform Matrix (LinkedIn, X, YouTube, Reddit)
- Slide 5: The 4 Editorial Quality Gates
- Slide 6: The Actionable Execution Checklist

Save this document to reference during your next product launch.

Download our open-source 12-Asset Repurposing Matrix spreadsheet template:  
`https://incubrix.com/matrix-template?utm_source=linkedin&utm_medium=carousel&utm_campaign=content_matrix&utm_content=ast_bp_10_li_caro` [Pending Confirmation]

**Hashtags:** `#ContentStrategy #GrowthMarketing #ContentRepurposing #B2BSaaS #DevRel`  
**Call to Action:** Save this carousel; download the free Content Repurposing Matrix spreadsheet template via link.

---

## 3. Accessible Visual Description (Alt Text)

> **Visual Description:**  
> A 6-slide dark-mode PDF document carousel with emerald green accents. Details how a technical whitepaper is ingested, parsed for factual claims with verbatim quotes, and transformed into 12 distinct platform-native assets across LinkedIn, X, Instagram, YouTube Shorts, and Reddit. Displays a structured matrix table and an editorial quality gate protocol.

---

## 4. Source Evidence & Claim Verification

- **Claim 1:** "A structured repurposing matrix yields 12 distinct platform assets from a single document."  
  *Status:* **Verified**. Implemented and verified in `app/services/content_engine.py` (`run_generation_service()`).
- **Claim 2:** "Automated fact extraction retains verbatim quotes as structured evidence references."  
  *Status:* **Verified**. Verified by unit test suite in `tests/test_content_engine.py`.
- **IncuBrix Product Claims:** **None**. Content reflects repository engine architecture.
