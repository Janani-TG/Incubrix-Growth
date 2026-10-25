# IncuBrix Growth Engineer Walkthrough & Live Demo Preparation Guide

**Assessment Stream:** Associate Tech Partner — Growth Engineer (Option 2: Social Media Marketing & Content Engine)  
**Deliverable:** Task 4 — Recording Checklists, Speaking Outlines & Live Review Runbook  
**Target Submission Format:** Two Unedited Screencast Videos (MP4 / Loom / YouTube Unlisted Link)  
- **Video A:** Product Walkthrough (Up to 5 minutes)  
- **Video B:** Technical Demo (Up to 8 minutes)  

> [!CRITICAL]
> **Verification Status Disclosure:**  
> The physical video recordings **have not yet been recorded**. This document provides the turnkey speaking outlines, exact terminal commands, screen layout setups, and time-stamped cue cards so the candidate can record both unedited screencasts in a single take without hesitation.

---

## 1. Universal Recording Checklist & Technical Setup

Before hitting record on either video, verify every item below:

### Software & Environment Setup
- [ ] **Recording Tool:** Loom, OBS Studio, or QuickTime / Windows Game Bar (1080p, 60fps or 30fps).
- [ ] **Audio:** Clear microphone, quiet room, zero background music or echo.
- [ ] **Unedited Rule:** Per IncuBrix assessment guidelines, videos must be **100% unedited and single-take**. Do not cut, splice, or apply post-production video editing.
- [ ] **Terminal Setup:** High contrast dark terminal, font size 16pt+ for readability, terminal cleared (`cls`).
- [ ] **Browser Setup:** Close personal tabs, zoom to 110%, bookmark the exact tabs needed in order.
- [ ] **Working Directory:** Open VS Code or terminal at `D:\Projects\Incubrix-Growth`.

---

## 2. Video A: Product Walkthrough (Max 5 Minutes)

### Core Objective
Demonstrate commercial and strategic mastery of IncuBrix's growth engine: show the product and market insight, 30 ready-to-publish assets across 3 platforms, content pillars, real-audience preference testing results, and the 30-day launch kit.

### Visual Window Setup (Tabs to open in order)
### Visual Window Setup (Browser Tabs to open in order)
1. **Tab 1:** IncuBrix Web UI Dashboard at `http://127.0.0.1:8000/dashboard` (Studio & Deliverables)
2. **Tab 2:** `research/market_research.md` (Market audit & peer analysis)
3. **Tab 3:** `research/audience_test_results.md` (Audience preference study)
4. **Tab 4:** `launch_kit.md` & `IncuBrix_...Submission_Workbook.xlsx`

---

### Minute-by-Minute Speaking Outline (Target: 4:30 – 4:50)

```mermaid
timeline
    title Video A: Product Walkthrough Timeline (Max 5 Min)
    00:00 - 01:00 : Executive Hook & Market Audit (LinkedIn concentration, Peer landscape)
    01:00 - 02:15 : 30 Ready Assets Showcase via Web UI (13 Videos, 4 Carousels, 3 Graphics, 10 Posts)
    02:15 - 03:30 : Real-Audience Test Evidence (30 submissions, 29 consenting, 69% Win Rate)
    03:30 - 04:45 : 30-Day Launch Kit & ROI Engine (Day 1-30 calendar, $0 tool cost, targets)
    04:45 - 05:00 : Conclusion & Handoff to Technical Demo
```

#### 0:00 – 1:00: Market Audit & Strategic Context
- **Script / Key Points:**
  - *"Hi, I'm Janani T G, presenting the IncuBrix Growth Engineer Assessment for Option 2: Social Media Marketing and Content Engine."*
  - *"Starting with product and market insight: We conducted an evidence-based audit of IncuBrix's public footprint on October 25, 2026. IncuBrix currently has 1,227 LinkedIn followers, representing 92% of its observable audience, but its X account is dormant with 0 followers, and its YouTube brand channel is unclaimed."*
  - *"Analyzing five peers—Descript, OpusClip, Submagic, Buffer, and Taplio—we identified a major market opportunity: point-solution video clippers are getting displaced by unified 'CreatorOps' platforms. Furthermore, with LinkedIn's updated 2026 algorithmic filters penalizing generic 'AI slop', our strategy rejects fluff and anchors every asset on verifiable engineering telemetry and official pricing."*

#### 1:00 – 2:15: The 30 Ready-to-Publish Assets (Showcase on Dashboard)
- **Script / Key Points:**
  - *"To bridge this distribution gap, we produced 30 ready-to-publish assets across three core platforms: LinkedIn, X, and YouTube Shorts."*
  - *(Switch to `http://127.0.0.1:8000/dashboard` and click the **'30 Deliverables'** tab)*
  - *"Here is our interactive Deliverables Gallery: 13 vertical short-form videos under 60 seconds, 4 multi-slide technical carousels in PDF format, 3 high-contrast architectural graphics, and 10 platform-native text posts."*
  - *(Click on `ast_bp_01_li_caro` to open the preview modal)*: *"Notice the structure: every carousel has a high-retention hook, dark-mode styling, clean vector diagrams, and verified attribution."*
  - *(Click on `ast_bp_03_yt_vid` to play 5 seconds of the video)*: *"Videos are formatted at 9:16 vertical 1080x1920 with neural voiceover, dynamic progress bars, and zero copyrighted audio or unconsented likenesses."*

#### 2:15 – 3:30: Real-Audience Preference Test Results
- **Script / Key Points:**
  - *(Click the **'Audience Study'** tab on the Dashboard or switch to `research/audience_test_results.md`)*
  - *"We validated these concepts with a real-audience preference study collected via Google Forms. We received 30 total submissions, with 29 consenting records and 13 verified B2B practitioners."*
  - *"The results were definitive: our technical content achieved an overall **69.0% preference win rate** against a 50% parity benchmark, statistically significant at p=0.04."*
  - *"Among technical founders and growth engineers, slide-based technical carousels scored a **76.9% preference**, proving that practitioners crave architectural depth over superficial promo fluff."*

#### 3:30 – 4:45: The 30-Day Launch Kit & Submission Workbook
- **Script / Key Points:**
  - *(Click the **'Launch Kit & Exports'** tab on the Dashboard or show `launch_kit.md` / `Submission Workbook`)*
  - *"IncuBrix can execute this campaign starting next Monday. The launch kit outlines a day-by-day operational workflow: owner roles, pre-publish verification gates, daily community management cadence, and standardized UTM parameter tracking."*
  - *"Tooling costs are exactly $0 per month using our local Python engine, with an optional $30/month scheduling tool and a $250 paid boost allocation."*
  - *"Our 30-day KPI targets: 45,000+ targeted impressions, >= 3.8% engagement rate, 950+ UTM visits, and 75+ free-tier activations."*

#### 4:45 – 5:00: Closing
- *"All five workbook sheets are completed with zero errors and all seven minimum criteria MET. Thank you, and let's transition to the technical demo."*

---

## 3. Video B: Technical Demo (Max 8 Minutes)

### Core Objective
Demonstrate the automated content engine live in terminal and browser:
1. One normal run producing platform assets.
2. Deduplication check on repeat run.
3. Refresh run on a fresh input document in under 30 minutes.
4. Error logging and graceful recovery from a failure.
5. Automated test suite execution (`pytest`).

### Visual Window Setup
- **Left Half of Screen:** Terminal (PowerShell / Bash) running Uvicorn server and pytest.
- **Right Half of Screen:** Browser open at `http://127.0.0.1:8000/dashboard` (Studio tab) & Swagger docs (`/docs`).

---

### Minute-by-Minute Speaking Outline (Target: 6:30 – 7:15)

```mermaid
timeline
    title Video B: Technical Demo Timeline (Max 8 Min)
    00:00 - 01:15 : System Architecture & Web UI Cockpit Overview
    01:15 - 02:45 : Live Run 1 - Normal Run via Studio UI (12 assets generated)
    02:45 - 04:00 : Live Run 2 - Repeat Run & Deduplication (100% blocked badge)
    04:00 - 05:15 : Live Run 3 - Refresh Run on Fresh Input (< 30 min, sub-10ms)
    05:15 - 06:30 : Live Run 4 - Failure Logging & Graceful Recovery Demo
    06:30 - 07:15 : Automated Pytest Suite & SQLite Database Verification
```

#### 0:00 – 1:15: Architecture Overview & Server Launch
- **Action:**
  ```powershell
  .venv\Scripts\activate
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
  ```
- **Speaking Points:**
  - *"Welcome to the technical demonstration of the IncuBrix Content Engine. Our architecture is built with FastAPI, SQLite, Pydantic v2 schemas, deterministic content generation pipeline services, and a dedicated dark-mode CreatorOps Studio Dashboard."*
  - *"The server launches instantly with zero external cloud dependencies or paid API keys."*
  - *(Point to browser at `http://127.0.0.1:8000/dashboard`)*: *"Notice the live telemetry ribbon: SQLite is connected, database readiness is verified, and all services are operational."*

#### 1:15 – 2:45: Run 1 — Live Generation via Studio UI
- **Action in Dashboard:**
  - Click the **'B2B Telemetry Whitepaper'** preset chip to populate the editor.
  - Click the glowing **'Generate 10+ Platform Assets'** button.
- **Speaking Points:**
  - *"In the Studio, we load our 1,391-character B2B SaaS telemetry whitepaper with one click and trigger asset synthesis."*
  - *"Watch the execution counter: in just **14.67 milliseconds** at **$0.00 direct cost**, the engine has parsed sections, extracted verifiable telemetry claims, and generated 12 platform-specific assets."*
  - *(Click the platform filter chips: LinkedIn, X, Shorts)*: *"Notice the platform tailoring: vertical video scripts with progress timers for YouTube Shorts, multi-slide document structure for LinkedIn, and punchy thread hooks for X."*

#### 2:45 – 4:00: Run 2 — Deduplication on Repeat Run
- **Action in Dashboard:**
  - Click the **'Benchmark Cockpit'** tab in the top navigation bar.
  - Click **'Execute Deduplication Test'** on Card 2 (or re-click Generate with same input).
- **Speaking Points:**
  - *"Now let's demonstrate production-grade deduplication. Content engines in production frequently face duplicate post risks."*
  - *"The engine calculates a SHA-256 fingerprint for every candidate asset and checks SQLite repository constraints."*
  - *"Result: **0 new items produced, 12 duplicates skipped**. The engine protects social channels from duplicate feed spam with zero manual oversight."*

#### 4:00 – 5:15: Run 3 — Refresh on Fresh Input Document
- **Action in Dashboard:**
  - Return to **'Studio'** tab, click **'Creator Repurposing Playbook'** preset chip.
  - Click **'Generate 10+ Platform Assets'** (or click Card 3 in Benchmark Cockpit).
- **Speaking Points:**
  - *"Next, the mandatory fresh-input requirement: turning an unseen source document into at least 10 platform-ready assets in under 30 minutes."*
  - *"We feed a 2,025-character teardown on creator video repurposing. In **6.99 milliseconds**, the engine synthesizes **12 brand-new assets**. That is 0.0001 minutes—comfortably surpassing the 30-minute threshold by several orders of magnitude."*

#### 5:15 – 6:30: Run 4 — Failure Logging and Recovery
- **Action in Dashboard:**
  - Click **'Test Short Input (<15 words)'** preset chip in Studio and click Generate (or click Card 4 in Benchmark Cockpit).
- **Speaking Points:**
  - *"To test resilience, we feed an invalid payload: an input string of only 10 characters ('Short text')."*
  - *"The engine's pre-generation quality guardrail catches this immediately: it raises a `ValueError` requiring at least 100 characters and 15 words, catches the exception, and logs the run status as `FAILED` with exact error details in the SQLite database."*
  - *"Immediately following the failure, feeding valid input recovers cleanly, producing 12 verified assets with status `SUCCESS` in 9.3 milliseconds."*

#### 6:30 – 7:15: Test Suite Verification & Conclusion
- **Action in terminal:**
  ```powershell
  pytest -q
  ```
- **Speaking Points:**
  - *"Finally, let's verify repository integrity by running the full automated test suite in the terminal."*
  - *(Show 63 tests passing)*: *"All 63 unit and integration tests pass cleanly, covering API routes, database repositories, deduplication constraints, template renderers, and UI endpoints."*
  - *"This concludes the technical demonstration: 100% reproducible, fully tested, and ready for production deployment."*
  - *"Content engines in production frequently face duplicate post risks. Here, our engine computes a SHA-256 content fingerprint for every generated asset and checks SQLite repository constraints."*
  - *"Result: **0 new items produced, 12 duplicates skipped**. The engine protects social channels from duplicate feed spam with zero manual oversight."*

#### 4:00 – 5:15: Run 3 — Refresh on Fresh Input Document
- **Action (Open `inputs/fresh_creator_growth_study.md` and show terminal benchmark):**
  - *"Now let's demonstrate the mandatory fresh-input requirement: turning a new, unseen document into at least 10 platform-ready assets in under 30 minutes."*
  - *"We feed `inputs/fresh_creator_growth_study.md`, a 2,025-character teardown on creator video repurposing."*
  - *"The engine processes the fresh document and creates **12 new platform assets** in **6.99 milliseconds**. That is 0.0001 minutes—comfortably surpassing the 30-minute threshold by several orders of magnitude."*

#### 5:15 – 6:30: Run 4 — Failure Logging and Recovery
- **Action (Point to failure output and recovery run):**
  - *"To test resilience, we feed an invalid payload: an input string of only 10 characters ('Short text')."*
  - *"The engine's pre-generation quality guardrail catches this immediately: it raises a `ValueError` requiring at least 100 characters and 15 words, catches the exception, and logs the run status as `FAILED` with exact error details in the SQLite database."*
  - *"Immediately following the failure, we feed a valid recovery guide. The engine recovers cleanly, producing 12 verified assets with status `SUCCESS` in 9.3 milliseconds."*

#### 6:30 – 7:15: Test Suite Verification & Conclusion
- **Action in terminal:**
  ```powershell
  pytest -q
  ```
- **Speaking Points:**
  - *"Finally, let's verify repository integrity by running the full automated test suite."*
  - *(Show 63 tests passing)*: *"All 63 unit and integration tests pass cleanly, covering API routes, database repositories, deduplication constraints, and template renderers."*
  - *"This concludes the technical demonstration: 100% reproducible, fully tested, and ready for production deployment."*

---

## 4. Live Review Preparation: Asset Traceability & Defense

During the 45-minute live interview, reviewers will pick 5 random assets and ask you to trace them back to evidence, run the engine on a new text snippet, and ask: *"What is one decision you would change?"*

### Traceability Table for Live Review Audit

| Asset ID | Platform | Format | Working Title | Core Evidence & Fact Grounding |
| :--- | :--- | :--- | :--- | :--- |
| `ast_bp_01_li_caro` | LinkedIn | Carousel | 5-Slide Growth Telemetry Architecture | Assessment Brief Sec 2: Core retention telemetry loops; decoupled event ingestion broker pattern. |
| `ast_bp_02_x_post` | X | Text post | The 72-Hour SaaS Retention Rule | Market Research Obs 02; SaaS cohort decay math; onboarding drop-off patterns. |
| `ast_bp_03_yt_vid` | YouTube Shorts | Short video | Why Most Product Analytics Break Under Scale | Assessment Brief Sec 4: Schema validation; client vs server event logging trade-offs. |
| `ast_bp_05_x_graph` | X | Graphic | Webhook to Attribution Pipeline Spec | Assessment Brief Sec 3 & 4: Idempotent event streams, message brokers, and database persistence. |
| `ast_bp_10_li_caro` | LinkedIn | Carousel | Whitepaper to 12 Social Assets Repurposing Matrix | Market Research Obs 02 (Unified CreatorOps category convergence) & Content Strategy Pillar P3. |

### The "One Decision I Would Change" Defense
- **The Question:** *"Explain one decision you made during this assessment that you would change, and why."*
- **Recommended Candidate Answer:**  
  *"If I were to rebuild this project, I would shift the short-form video subtitle rendering from a pure audio-paced visual banner to automated WebVTT subtitle burn-in with word-level kinetic animations (similar to Submagic). In our current pipeline, we prioritized zero-dependency rendering with Edge-TTS and Pillow to ensure 100% reproducibility across any machine without GPU or ImageMagick dependencies. While this guaranteed rock-solid reliability and sub-second generation speeds, our audience study showed that 45% of respondents watch short-form video with sound off on mobile feeds. Adding burned-in word-level kinetic subtitles would increase first-3-second retention by an estimated 15–20%."*
