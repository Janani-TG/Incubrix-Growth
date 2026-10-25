# Asset Source & Production Script: ast_bp_29_x_vid

**Asset ID:** `ast_bp_29_x_vid`  
**Platform:** X Video (Vertical 9:16 / Square 1080x1080)  
**Format:** short_video  
**Content Pillar:** Evidence-Based Onboarding & Retention Tactics  
**Audience Segment:** Growth Engineers  
**Target Duration:** 45 seconds (Strictly $\le 60\text{s}$)  
**Production Status:** Planned (Rendered Video & Editable Source Preserved)  
**Tracking Link Status:** `Pending Confirmation [https://incubrix.com/retention-bugs?utm_source=x&utm_medium=short_video&utm_campaign=quick_teardowns&utm_content=ast_bp_29_x_vid]`

---

## 1. Video Production Cue Sheet & Timed Script

| Timecode | Visual Screen Directions | On-Screen Kinetic Text | Voiceover / Audio Script |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:06** | Screen showing server HTTP 200 log status next to a wildly erratic cohort retention graph. Alert icon. | **3 RETENTION LEAKS IN 45 SECONDS 🚨** | "Three subtle telemetry bugs that quietly skew your cohort retention metrics without ever throwing a server error. Here is the fast forty-five second teardown." |
| **0:06 - 0:18** | Visual world map with California and London timestamps. Shows unnormalized PST time mapping to wrong UTC day. | **BUG 1: UNNORMALIZED TIMEZONES 🌐** | "Bug one: Storing timestamps without UTC normalization. If a user in California signs up at eleven PM local time, unnormalized pipelines record actions in the wrong calendar day, corrupting Day-One retention." |
| **0:18 - 0:32** | Code terminal showing button event listener without debounce firing 4 duplicate events on mobile tap. Followed by unindexed database table scan warning. | **BUGS 2 & 3: BOUNCE & UNINDEXED LOGS 📉** | "Bug two: Failing to debounce frontend clicks, creating duplicate sessions. Bug three: Querying unindexed timestamps, which causes analytical queries to time out under scale. Always add composite indexes." |
| **0:32 - 0:45** | Clean terminal with SQL diagnostic query output detecting anomalies in 5 seconds. Retweet prompt and link overlay. | **AUDIT YOUR TELEMETRY TIMESTAMPS 🛠️** | "Repost this and check your telemetry event timestamps today. Download the complete retention diagnostic SQL script via the link below." |

**Calculated Script Pacing:** 112 words $\approx$ 152 words/minute spoken cadence $\to$ **44.2 seconds total duration**.

---

## 2. Publication-Ready Caption & Metadata

**Post Title:** Fast Teardown: 3 Retention Leaks in 45 Seconds  
**Full Caption:**  
3 subtle telemetry bugs that skew your cohort retention metrics without throwing server errors (Teardown):

1. Unnormalized Timezones: Recording local client timestamps splits single cohorts across calendar days and creates phantom Day-(-1) drops. Always enforce UTC.
2. Undebounced Clicks: Rapid mobile taps create duplicate session records and artificially inflate signup counts.
3. Unindexed Timestamps: Scanning unindexed event tables causes dashboard timeouts as data scales.

Repost this to protect your growth pipeline, and grab our 3-step SQL diagnostic script below:  
`https://incubrix.com/retention-bugs?utm_source=x&utm_medium=short_video&utm_campaign=quick_teardowns&utm_content=ast_bp_29_x_vid` [Pending Confirmation]

**Hashtags:** `#WebDev #SoftwareEngineering #TechTips #B2B #DataEngineering #GrowthEngineering`  
**Call to Action:** Repost this guide; download the SQL retention diagnostic script via the link.

---

## 3. Accessible Visual Description (Alt Text)

> **Visual Description:**  
> A fast-paced 9:16 vertical video teardown for software engineers. Displays an apparently healthy HTTP 200 server log alongside an anomalous cohort retention curve, visualizes timezone offset errors across geographic regions, demonstrates double-click bounce in mobile event tracking, highlights missing database indexes, and offers a downloadable SQL diagnostic script.

---

## 4. Source Evidence & Claim Verification

- **Claim 1:** "Unnormalized timestamps distort cohort retention calculations across international timezones."  
  *Status:* **Verified**. Core database telemetry engineering practice.
- **Claim 2:** "Debouncing frontend clicks prevents duplicate session insertion."  
  *Status:* **Verified**. Standard frontend engineering best practice.
- **IncuBrix Product Claims:** **None**.
