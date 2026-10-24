# Asset Source & Slide Specification: ast_bp_19_li_caro

**Asset ID:** `ast_bp_19_li_caro`  
**Platform:** LinkedIn (Document Carousel PDF)  
**Format:** carousel (6 Slides, 1080x1350 px, 4:5 Aspect Ratio)  
**Content Pillar:** Attribution, UTMs & Data Integrity  
**Audience Segment:** Growth Engineers  
**Production Status:** Planned (Editable Source & Multi-Page PDF Rendered; Final Review Pending)  
**Tracking Link Status:** `Pending Confirmation [https://incubrix.com/data-hygiene-guide?utm_source=linkedin&utm_medium=carousel&utm_campaign=hygiene_guide&utm_content=ast_bp_19_li_caro]`

---

## 1. Slide-by-Slide Copy & Layout Specification

### Slide 1: Cover / Hook
- **Visual Style:** Midnight violet background (`#0F0C20`), neon purple accents (`#A855F7`), badge: `DATA INTEGRITY HANDBOOK`.
- **Primary Headline:** The Growth Engineer's Data Hygiene Guide
- **Subtitle:** Bad data produces bad growth decisions. The 6-step quarterly checklist to audit, clean, and protect your telemetry event pipelines.
- **Footer:** `Swipe to inspect the 6 audits -> [Slide 1/6]`

---

### Slide 2: Audit 1 & 2 — Schema Strictness & Orphan Events
- **Visual Style:** Two structured audit cards with icon indicators.
- **Audit 1: Schema Enforcement at the Edge:**
  - *Problem:* Flexible JSON schemas sound convenient until frontend sends strings where integers are expected.
  - *Fix:* Enforce strict Pydantic or JSON schema validation at the edge. Reject or quarantine malformed payloads before they reach the warehouse.
- **Audit 2: Orphan Event Pruning:**
  - *Problem:* Dead features from 2024 still firing 50,000 events a day, inflating cloud analytics bills.
  - *Fix:* Run monthly query on events with zero dashboard queries or downstream dependencies. Deprecate and sunset.
- **Footer:** `IncuBrix Telemetry Playbook [Slide 2/6]`

---

### Slide 3: Audit 3 & 4 — Timestamp Normalization & Idempotency
- **Visual Style:** Code snippet highlighting UTC conversions and unique index triggers.
- **Audit 3: Mandatory UTC Normalization:**
  - *Problem:* User in Tokyo signs up at 9:00 AM; user in San Francisco signs up at 5:00 PM. Local client timestamps scramble Day-1 retention cohorts.
  - *Fix:* Normalize all timestamps to ISO-8601 UTC at server ingestion time. Never trust client device clocks.
- **Audit 4: Idempotent Event Deduplication:**
  - *Problem:* Mobile connection retries duplicate conversion events, inflating conversion rates.
  - *Fix:* Compute unique content fingerprint or transaction token. Enforce database uniqueness constraints.
- **Footer:** `IncuBrix Telemetry Playbook [Slide 3/6]`

---

### Slide 4: Audit 5 & 6 — UTM Taxonomy & Formula Protection
- **Visual Style:** URL breakdown graphic comparing broken vs. sanitized parameters.
- **Audit 5: Strict Lowercase UTM Taxonomies:**
  - *Problem:* `utm_source=LinkedIn` and `utm_source=linkedin` split traffic into separate reporting buckets.
  - *Fix:* Use programmatic URL builders that enforce lowercase strings and validate allowed platform enums.
- **Audit 6: CSV Formula Injection Defense:**
  - *Problem:* User input starting with `=`, `+`, `-`, or `@` executes malicious formulas when exported to Excel or Google Sheets.
  - *Fix:* Prefix hostile leading characters with a single quote (`'`) during export serialization.
- **Footer:** `IncuBrix Telemetry Playbook [Slide 4/6]`

---

### Slide 5: The Data Health Monitoring Cockpit
- **Visual Style:** Clean UI mockup of an automated telemetry health dashboard.
- **Core Health Metrics to Monitor:**
  - **Schema Validation Failure Rate:** Target $< 0.1\%$.
  - **Duplicate Event Collision Rate:** Target $< 0.5\%$.
  - **Event Ingestion Latency:** p95 $< 25\text{ms}$.
  - **Unattributed Traffic Share:** Target $< 5\%$.
- **Alert Rule:** Trigger PagerDuty or Slack alert if schema failure rate spikes above 1% following any frontend deployment.
- **Footer:** `IncuBrix Telemetry Playbook [Slide 5/6]`

---

### Slide 6: Summary & Audit Template Download
- **Visual Style:** Checklist summary card with prominent CTA badge.
- **Header:** `KEEP YOUR PIPELINES CLEAN`
- **Summary:**
  - 1. Enforce edge schemas.
  - 2. Prune orphan events.
  - 3. Normalize to UTC.
  - 4. Enforce idempotency.
  - 5. Lowercase UTMs.
  - 6. Sanitize export cells.
- **Call to Action:** Save this carousel and download our 25-point Data Hygiene Audit spreadsheet via link.
- **Footer:** `Save for your next sprint retrospective [Slide 6/6]`

---

## 2. Publication-Ready Caption & Metadata

**Post Hook:** Bad data produces bad growth decisions. The 6-step quarterly checklist to audit, clean, and protect your telemetry event pipelines.  
**Full Caption:**  
If your product analytics have been running for more than six months without a data hygiene audit, your growth metrics are almost certainly skewed.

Orphan events from deprecated features inflate warehouse costs, unnormalized client timestamps scramble retention curves, and case differences in UTM links fracture attribution.

Swipe through for the 6-step Data Hygiene Checklist:
- Slide 1: The Cost of Dirty Telemetry
- Slide 2: Schema Enforcement & Orphan Event Pruning
- Slide 3: UTC Normalization & Idempotent Deduplication
- Slide 4: UTM Parameter Governance & CSV Formula Defense
- Slide 5: The Automated Data Health Cockpit
- Slide 6: The Actionable Quarterly Audit Template

Save this post to run with your engineering team during sprint planning.

Download our open-source Data Hygiene Audit spreadsheet template:  
`https://incubrix.com/data-hygiene-guide?utm_source=linkedin&utm_medium=carousel&utm_campaign=hygiene_guide&utm_content=ast_bp_19_li_caro` [Pending Confirmation]

**Hashtags:** `#DataHygiene #GrowthEngineering #Analytics #DataGovernance #SaaS`  
**Call to Action:** Save this carousel; download the Data Hygiene Audit spreadsheet template via link.

---

## 3. Accessible Visual Description (Alt Text)

> **Visual Description:**  
> A 6-slide dark-mode document carousel with midnight violet background and neon purple accents. Details six critical data engineering hygiene audits for SaaS growth pipelines: API edge schema validation, orphan event pruning, UTC timestamp normalization, idempotent deduplication, lowercase UTM taxonomy, and spreadsheet formula injection sanitization. Concludes with an automated telemetry health dashboard specification.

---

## 4. Source Evidence & Claim Verification

- **Claim 1:** "Prefixing formula-triggering characters with a single quote prevents CSV injection in spreadsheet applications."  
  *Status:* **Verified**. Implemented and verified in `app/services/export_service.py` (`sanitize_formula_injection()`).
- **Claim 2:** "Server-side UTC timestamp normalization eliminates timezone skew across cohort retention curves."  
  *Status:* **Verified**. Standard database and distributed systems best practice.
- **IncuBrix Product Claims:** **None**.
