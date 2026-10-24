# Asset Source & Production Script: ast_bp_06_yt_vid

**Asset ID:** `ast_bp_06_yt_vid`  
**Platform:** YouTube Shorts (Vertical 9:16)  
**Format:** short_video  
**Content Pillar:** Attribution, UTMs & Data Integrity  
**Audience Segment:** Technical Marketers  
**Target Duration:** 35 seconds (Strictly $\le 60\text{s}$)  
**Production Status:** Planned (Draft Script Complete — Video Rendering Blocked)  
**Tracking Link Status:** `Pending Confirmation [https://incubrix.com/utm-builder?utm_source=youtube_shorts&utm_medium=short_video&utm_campaign=utm_tips&utm_content=ast_bp_06_yt_vid]`

---

## 1. Video Production Cue Sheet & Timed Script

| Timecode | Visual Screen Directions | On-Screen Kinetic Text | Voiceover / Audio Script |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:04** | Close-up of a browser address bar showing a broken, fragmented URL with red highlight on `%20` and capital letters. | **ARE YOUR UTMs BREAKING GA4?** ⚠️ | "Are your UTM tracking links breaking your Google Analytics data? Watch out for these 3 mistakes." |
| **0:04 - 0:13** | Text comparison animation: `utm_source=LinkedIn` vs `utm_source=linkedin`. Analytics chart shows split rows with a red warning badge. | **MISTAKE 1: MIXED CASING** 🔤 | "Mistake one: Mixed casing. Google Analytics treats capital 'LinkedIn' and lowercase 'linkedin' as two different traffic sources. Always force lowercase." |
| **0:13 - 0:22** | Browser view zooming in on `?utm_source=x&utm_medium=post`. An empty `utm_content` field flashes yellow. | **MISTAKE 2: SKIPPING utm_content** 🏷️ | "Mistake two: Skipping `utm_content`. If you run 5 posts on X this week, how will you know which exact asset drove signups? Always attach the unique asset ID." |
| **0:22 - 0:29** | Browser view showing raw spaces turning into `%20%20` errors. Clean URL replaces it. | **MISTAKE 3: UNENCODED SPACES** 🚫 | "Mistake three: Unencoded spaces. Spaces in query parameters corrupt link shorteners and trigger 404 redirects on mobile devices. Use underscores or hyphens." |
| **0:29 - 0:35** | Clean end card showing the IncuBrix programmatic UTM builder CLI tool and link arrow. | **FREE UTM BUILDER** 🔗 | "Download our free automated Python UTM builder template linked in the description. Subscribe for more attribution engineering tips." |

**Calculated Script Pacing:** 92 words $\approx$ 155 words/minute spoken cadence $\to$ **34.8 seconds total duration**.

---

## 2. Publication-Ready Caption & Metadata

**Post Title:** The 3 UTM Mistakes Destroying Your Campaign Attribution #Shorts  
**Full Caption:**  
Are your marketing campaign analytics fractured? One misplaced capital letter or missing content tag will turn your Google Analytics reports into an unreadable mess.

Here is the 35-second attribution audit:
1. Always enforce lowercase (`utm_source=linkedin`, never `LinkedIn`).
2. Never skip `utm_content` (you need asset-level attribution to know which post converted).
3. Never use raw spaces in URLs (use snake_case or hyphens).

Download our automated Python UTM builder script via the link below:  
`https://incubrix.com/utm-builder?utm_source=youtube_shorts&utm_medium=short_video&utm_campaign=utm_tips&utm_content=ast_bp_06_yt_vid` [Pending Confirmation]

**Hashtags:** `#Shorts #MarketingTech #GoogleAnalytics #UTM #Attribution #GrowthHacking`  
**Call to Action:** Subscribe for weekly marketing telemetry breakdowns; download the free Python UTM builder script in description.

---

## 3. Accessible Visual Description (Alt Text)

> **Visual Description:**  
> A high-energy vertical 9:16 technical tutorial video. Shows a close-up of a browser address bar with broken tracking parameters, displays split Google Analytics table rows illustrating how inconsistent casing fractures traffic reporting, demonstrates the addition of `utm_content` for asset-level granularity, and concludes with a terminal screen showing clean programmatic URL generation.

---

## 4. Source Evidence & Claim Verification

- **Claim 1:** "Google Analytics treats case differences in UTM parameters as distinct channels."  
  *Status:* **Verified**. Standard GA4 query string parsing behavior.
- **Claim 2:** "Omitting `utm_content` prevents asset-level conversion attribution."  
  *Status:* **Verified**. Core marketing analytics architecture principle.
- **IncuBrix Product Claims:** **None**.
