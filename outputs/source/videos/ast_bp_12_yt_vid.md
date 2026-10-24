# Asset Source & Production Script: ast_bp_12_yt_vid

**Asset ID:** `ast_bp_12_yt_vid`  
**Platform:** YouTube Shorts (Vertical 9:16)  
**Format:** short_video  
**Content Pillar:** Creator & Marketer Workflow Engineering  
**Audience Segment:** Growth Engineers  
**Target Duration:** 40 seconds (Strictly $\le 60\text{s}$)  
**Production Status:** Planned (Draft Script Complete — Video Rendering Blocked)  
**Tracking Link Status:** `Pending Confirmation [https://incubrix.com/fingerprint-guide?utm_source=youtube_shorts&utm_medium=short_video&utm_campaign=fingerprinting&utm_content=ast_bp_12_yt_vid]`

---

## 1. Video Production Cue Sheet & Timed Script

| Timecode | Visual Screen Directions | On-Screen Kinetic Text | Voiceover / Audio Script |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:04** | Fast-scrolling social media feed showing the exact same hook repeated 3 times from the same company account. Red skull emoji. | **STOP SPAMMING YOUR FEED.** 🤖 | "Ever see an automated brand account post the exact same content three times in one week? Here is the engineering fix." |
| **0:04 - 0:14** | Code terminal in dark mode. A raw social asset text string is passed into a Python function: `compute_asset_fingerprint()`. | **NORMALIZATION PIPELINE** 🧹 | "When you run an automated content pipeline, naive duplicate checks fail because of tiny whitespace or casing differences. You need normalized content fingerprinting." |
| **0:14 - 0:26** | Animation showing string normalization: stripping punctuation, collapsing whitespace, lowercasing platform + format + hook, and hashing via SHA-256. | **SHA-256 HASH GENERATION** 🔐 | "In our pipeline, we normalize the platform, format, and core hook text into a standardized string, then compute a deterministic SHA-256 cryptographic hash." |
| **0:26 - 0:34** | SQLite terminal view: database checks `UNIQUE(content_fingerprint)`. Duplicate insertion attempt triggers a clean rejection log. | **ZERO DUPLICATE POSTS** 🛡️ | "Before any asset is saved or scheduled, the database checks the fingerprint index. If it already exists, the post is instantly rejected. Zero duplicate spam." |
| **0:34 - 0:40** | Python function displayed on screen with link overlay pointing to GitHub repository. | **PYTHON CODE IN DESCRIPTION** 💻 | "The entire Python implementation is open-source. Grab the code from the link in the description and subscribe for more growth engineering builds." |

**Calculated Script Pacing:** 105 words $\approx$ 157 words/minute spoken cadence $\to$ **39.8 seconds total duration**.

---

## 2. Publication-Ready Caption & Metadata

**Post Title:** How to Engineer Duplicate Post Detection in Python #Shorts  
**Full Caption:**  
Automated content engines are great until a bug posts the exact same tweet four times in two days and burns your follower trust.

Here is how growth engineers solve this using normalized SHA-256 content fingerprinting:
1. Normalize platform name and format.
2. Strip markdown, punctuation, and extra whitespace from the hook and body.
3. Compute a deterministic 64-character SHA-256 hash.
4. Enforce a unique index at the database layer before scheduling.

Grab the complete Python code implementation from our open-source guide:  
`https://incubrix.com/fingerprint-guide?utm_source=youtube_shorts&utm_medium=short_video&utm_campaign=fingerprinting&utm_content=ast_bp_12_yt_vid` [Pending Confirmation]

**Hashtags:** `#Shorts #Python #Algorithms #SoftwareEngineering #Automation #DataEngineering`  
**Call to Action:** Subscribe for weekly engineering tutorials; copy the Python fingerprinting function from the description link.

---

## 3. Accessible Visual Description (Alt Text)

> **Visual Description:**  
> A dynamic 9:16 vertical video showing software code and database operations. Demonstrates an undesirable repetitive social feed, transitions to a Python terminal executing string normalization, animates text converting into a 64-character SHA-256 hash string, and displays a SQLite database constraint blocking duplicate records with an integrity error.

---

## 4. Source Evidence & Claim Verification

- **Claim 1:** "Normalized SHA-256 fingerprinting reliably detects duplicate or near-duplicate assets."  
  *Status:* **Verified**. Implemented and verified in `app/repositories.py` (`compute_asset_fingerprint()` and `is_duplicate_asset()`).
- **Claim 2:** "Database-level unique constraint prevents duplicate asset scheduling."  
  *Status:* **Verified**. Enforced by schema index `idx_assets_fingerprint` in `app/database.py`.
- **IncuBrix Product Claims:** **None**.
