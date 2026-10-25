# Video specifications for all 13 video assets in research/asset_blueprint.csv

VIDEO_SPECS = [
    # 1. ast_bp_03_yt_vid (YouTube Shorts, 45s)
    {
        'asset_id': 'ast_bp_03_yt_vid',
        'platform': 'YouTube Shorts',
        'pillar': 'Growth Architecture',
        'voice': 'en-US-AndrewNeural',
        'scenes': [
            {
                'tag': 'INGESTION BOTTLENECK',
                'headline': 'STOP TRACKING EVERY CLICK 🛑',
                'subtitle': 'Why product analytics crash under scale',
                'window_title': 'analytics_alerts.log',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Total Unindexed Events', 'value': '650+ ❌', 'note': 'Schema drift causing warehouse bloat'},
                    {'title': 'DOM Click Listeners', 'value': 'UNVALIDATED', 'note': 'Frontend button clicks firing noisy payloads'},
                    {'title': 'Database Query Latency', 'value': '4.8s (SLOW)', 'note': 'Unindexed table scans degrading dashboards'},
                ],
                'kinetic_sub': 'Stop tracking every single button click. Here is why your analytics pipeline will crash.',
                'voiceover': 'Stop tracking every single button click. Here is why your product analytics pipeline will crash.',
                'cta': 'Subscribe for weekly architecture teardowns'
            },
            {
                'tag': 'THE CLIENT-SIDE TRAP',
                'headline': 'THE CLIENT-SIDE TRAP ⚠️',
                'subtitle': 'Unstructured DOM listeners leak data',
                'window_title': 'browser_event_loss.log',
                'visual_type': 'comparison',
                'visual_content': [
                    {'title': 'Ad Blocker Interception', 'value': '20% LOSS ❌', 'note': 'Silent drop on client-side requests'},
                    {'title': 'Frontend Double-Clicks', 'value': 'DUPLICATES ❌', 'note': 'Mobile connection retries inflating signups'},
                    {'title': 'Type Safety Enforced', 'value': 'ZERO ❌', 'note': 'Arbitrary null values corrupting cohorts'},
                ],
                'kinetic_sub': 'When developers fire unstructured DOM events, ad blockers drop 20% and databases fill with junk.',
                'voiceover': 'When frontend developers fire unstructured events from DOM buttons, ad blockers drop 20%, users double-click, and your analytics database fills with corrupt, unvalidated junk.',
                'cta': 'Decouple client tracking from ingestion'
            },
            {
                'tag': 'THE ACTIVATION SCHEMA',
                'headline': 'THE 5-EVENT ACTIVATION SCHEMA 📐',
                'subtitle': 'Enforce strict schema validation',
                'window_title': 'activation_schema.json',
                'visual_type': 'code',
                'visual_content': [
                    ('{\n', '#9CA3AF'),
                    ('  "user_id": "usr_94b810ac",', '#60A5FA'),
                    ('  "event_name": "onboarding_completed",', '#34D399'),
                    ('  "timestamp_utc": "2026-10-25T15:45:00Z",', '#FBBF24'),
                    ('  "session_id": "ses_3301aef",', '#60A5FA'),
                    ('  "properties": {', '#9CA3AF'),
                    ('    "time_to_first_value_sec": 420,', '#F472B6'),
                    ('    "activation_milestones": 3,', '#F472B6'),
                    ('    "fingerprint": "sha256_7f1c8e9..."', '#38BDF8'),
                    ('  }', '#9CA3AF'),
                    ('}', '#9CA3AF'),
                ],
                'kinetic_sub': 'Top growth teams enforce a strict 5-event activation schema: User ID, event, timestamp, session, properties.',
                'voiceover': 'Top growth teams do this instead: They enforce a strict 5-event activation schema. User ID, normalized event name, ISO-8601 UTC timestamp, session token, and validated payload properties.',
                'cta': 'Clean schema prevents downstream rot'
            },
            {
                'tag': 'SERVER-SIDE VALIDATION',
                'headline': 'SERVER-SIDE VALIDATION ⚡',
                'subtitle': 'Non-blocking asynchronous edge pipeline',
                'window_title': 'pipeline_architecture.diag',
                'visual_type': 'diagram',
                'visual_content': [
                    {'label': '1. Client Action (HTTP POST)', 'sub': 'Dispatched without blocking UI', 'badge': '< 2ms', 'active': False},
                    {'label': '2. Edge Ingestion Gateway', 'sub': 'FastAPI / Envoy Gateway', 'badge': '< 15ms', 'active': True},
                    {'label': '3. Asynchronous Queue', 'sub': 'Redis / SQS event buffer', 'badge': 'Buffered', 'active': False},
                    {'label': '4. Validation & Dedupe Worker', 'sub': 'SHA-256 fingerprint matching', 'badge': 'Zero Dupe', 'active': True},
                    {'label': '5. Analytics Warehouse', 'sub': 'PostgreSQL / ClickHouse storage', 'badge': 'Immutable', 'active': False},
                ],
                'kinetic_sub': 'Validate events server-side before they ever touch your warehouse. Zero duplicates. Zero schema drift.',
                'voiceover': 'Validate events server-side before they ever touch your analytics warehouse. Zero duplicates. Zero schema drift. 100% data fidelity.',
                'cta': 'Non-blocking and fail-safe'
            },
            {
                'tag': 'ACTIONABLE BLUEPRINT',
                'headline': 'CLONE THE BLUEPRINT ⬇️',
                'subtitle': 'Open-source telemetry schemas & scripts',
                'window_title': 'production_checklist.md',
                'visual_type': 'checklist',
                'visual_content': [
                    {'text': 'Download open-source JSON schema', 'checked': True},
                    {'text': 'Run SQLite SHA-256 deduplication test', 'checked': True},
                    {'text': 'Audit onboarding drop-off in first 72 hours', 'checked': True},
                    {'text': 'Subscribe for weekly Growth Engineering tips', 'checked': True},
                ],
                'kinetic_sub': 'Grab our open-source schema template from description link. Subscribe for more.',
                'voiceover': 'Grab our open-source event schema JSON template from the link in the description. Subscribe for more growth engineering breakdowns.',
                'cta': 'incubrix.com/event-schemas'
            }
        ]
    },

    # 2. ast_bp_06_yt_vid (YouTube Shorts, 35s)
    {
        'asset_id': 'ast_bp_06_yt_vid',
        'platform': 'YouTube Shorts',
        'pillar': 'Attribution & UTMs',
        'voice': 'en-US-AndrewNeural',
        'scenes': [
            {
                'tag': 'UTM AUDIT',
                'headline': 'ARE YOUR UTMs BREAKING GA4? ⚠️',
                'subtitle': 'Three subtle tracking mistakes costing you attribution',
                'window_title': 'browser_url_bar.view',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Traffic Source Split', 'value': 'FRACTURED ❌', 'note': 'Mixed casing creating duplicate buckets'},
                    {'title': 'Asset-Level Tracking', 'value': 'MISSING ❌', 'note': 'Omitting utm_content leaves blind spots'},
                    {'title': 'Link Shortener Redirects', 'value': '404 ERRORS ❌', 'note': 'Unencoded spaces corrupting mobile users'},
                ],
                'kinetic_sub': 'Are your UTM tracking links breaking your Google Analytics data? Watch out for these 3 mistakes.',
                'voiceover': 'Are your UTM tracking links breaking your Google Analytics data? Watch out for these 3 mistakes.',
                'cta': 'Audit your marketing links'
            },
            {
                'tag': 'MISTAKE 1: CASING',
                'headline': 'MISTAKE 1: MIXED CASING 🔤',
                'subtitle': 'Case sensitivity fractures analytics buckets',
                'window_title': 'google_analytics_sources.tbl',
                'visual_type': 'comparison',
                'visual_content': [
                    {'title': 'Row 1: utm_source=LinkedIn', 'value': '1,420 Users ❌', 'note': 'Upper case L creates Bucket A'},
                    {'title': 'Row 2: utm_source=linkedin', 'value': '2,890 Users ❌', 'note': 'Lower case l creates Bucket B'},
                    {'title': 'The Engineering Rule', 'value': 'FORCE LOWERCASE ✅', 'note': 'Always sanitize query strings to lowercase'},
                ],
                'kinetic_sub': 'Mistake one: Mixed casing. Google Analytics treats capital LinkedIn and lowercase linkedin as two different sources.',
                'voiceover': 'Mistake one: Mixed casing. Google Analytics treats capital LinkedIn and lowercase linkedin as two different traffic sources. Always force lowercase.',
                'cta': 'Always enforce lowercase'
            },
            {
                'tag': 'MISTAKE 2 & 3: TAGS & SPACES',
                'headline': 'MISTAKES 2 & 3: TAGS & SPACES 🏷️',
                'subtitle': 'Attach asset IDs and avoid raw spaces',
                'window_title': 'url_sanitizer.py',
                'visual_type': 'checklist',
                'visual_content': [
                    {'text': 'Never skip utm_content (identifies the exact asset ID)', 'checked': True},
                    {'text': 'Never use raw spaces (spaces cause %20 redirect breaks)', 'checked': True},
                    {'text': 'Use snake_case or hyphens for clean parsing', 'checked': True},
                    {'text': 'Automate URL construction programmatically', 'checked': True},
                ],
                'kinetic_sub': 'Mistake two: Skipping utm_content. Mistake three: Unencoded spaces. Use snake_case or hyphens.',
                'voiceover': 'Mistake two: Skipping utm_content. You need asset-level attribution to know which post converted. Mistake three: Unencoded spaces. Spaces corrupt link shorteners and trigger redirects. Use snake_case.',
                'cta': 'Clean URLs guarantee clean data'
            },
            {
                'tag': 'ACTIONABLE TEMPLATE',
                'headline': 'FREE PYTHON UTM BUILDER 🔗',
                'subtitle': 'Sanitize and build links automatically',
                'window_title': 'utm_builder.cli',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Python Script Included', 'value': 'FREE DOWNLOAD ✅', 'note': 'Automated validation, lowercase enforcement, URL encoding'},
                    {'title': 'Excel / Sheets Formula', 'value': 'COMPATIBLE ✅', 'note': 'Formula injection safe (leading apostrophe escape)'},
                    {'title': 'Attribution Accuracy', 'value': '100% RELIABLE ✅', 'note': 'Guaranteed uniform campaign tracking'},
                ],
                'kinetic_sub': 'Download our free automated Python UTM builder template linked in description. Subscribe for more.',
                'voiceover': 'Download our free automated Python UTM builder template linked in the description. Subscribe for more attribution engineering tips.',
                'cta': 'incubrix.com/utm-builder'
            }
        ]
    },

    # 3. ast_bp_07_li_vid (LinkedIn Video, 50s)
    {
        'asset_id': 'ast_bp_07_li_vid',
        'platform': 'LinkedIn',
        'pillar': 'Onboarding & Retention',
        'voice': 'en-US-AndrewNeural',
        'scenes': [
            {
                'tag': 'EXECUTIVE BRIEFING',
                'headline': 'BEFORE YOU SPEND $10K ON ADS... 💸',
                'subtitle': 'The crucial question for B2B engineering leadership',
                'window_title': 'executive_cockpit.view',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Monthly Ad Spend Target', 'value': '$10,000 / mo', 'note': 'Proposed budget for performance marketing'},
                    {'title': 'Measured Time-to-Value', 'value': 'UNMEASURED ⚠️', 'note': 'Onboarding velocity not yet instrumented'},
                    {'title': 'Day-30 Cohort Churn Risk', 'value': 'HIGH 🚨', 'note': 'Acquisition without retention accelerates burnout'},
                ],
                'kinetic_sub': 'Before your leadership team spends another ten thousand dollars on paid acquisition, ask this one question.',
                'voiceover': 'Before your leadership team spends another ten thousand dollars on paid customer acquisition, ask your engineering leads this one question.',
                'cta': 'Measure velocity before scaling spend'
            },
            {
                'tag': 'TIME-TO-VALUE METRIC',
                'headline': 'WHAT IS YOUR TIME-TO-VALUE? ⏱️',
                'subtitle': 'The single strongest predictor of 90-day retention',
                'window_title': 'retention_dropoff_curve.chart',
                'visual_type': 'comparison',
                'visual_content': [
                    {'title': 'Onboarding Under 15 Mins', 'value': '68% RETAINED ✅', 'note': 'Rapid aha moment solidifies habit formation'},
                    {'title': 'Onboarding Over 45 Mins', 'value': '60% CHURN ❌', 'note': 'High friction kills conversion momentum'},
                    {'title': 'Leading Indicator', 'value': 'TTV VELOCITY', 'note': 'Time-to-Value dictates lifetime customer value'},
                ],
                'kinetic_sub': 'What is our Time-to-Value? If onboarding takes over 15 minutes, 50% will never return.',
                'voiceover': 'What is our measured Time-to-First-Value? If your user onboarding takes more than fifteen minutes for a new signup to hit their core aha milestone, fifty percent will never return.',
                'cta': 'Compress time-to-first-value'
            },
            {
                'tag': 'ONBOARDING FRICTION',
                'headline': 'FRICTION DESTROYS RETENTION 📉',
                'subtitle': 'Pumping spend into leaks burns runway',
                'window_title': 'onboarding_friction_audit.md',
                'visual_type': 'checklist',
                'visual_content': [
                    {'text': 'Mandatory email verification before sandbox access', 'checked': False},
                    {'text': 'Forcing team invitations before demonstrating value', 'checked': False},
                    {'text': 'Empty dashboard states with zero sample data', 'checked': False},
                    {'text': 'Pre-populated interactive sandbox with instant preview', 'checked': True},
                ],
                'kinetic_sub': 'Pumping paid traffic into high-friction onboarding burns runway. Every mandatory gate multiplies churn.',
                'voiceover': 'Pumping paid traffic into a high-friction onboarding experience is an expensive way to burn runway. Every mandatory team invite, unverified email gate, or empty state multiplies churn.',
                'cta': 'Remove premature onboarding barriers'
            },
            {
                'tag': 'INSTRUMENT THE LOOP',
                'headline': 'INSTRUMENT THE ACTIVATION LOOP 🔍',
                'subtitle': 'Measure timestamp between signup and first value',
                'window_title': 'telemetry_triggers.sql',
                'visual_type': 'diagram',
                'visual_content': [
                    {'label': '1. Account Created Timestamp', 'sub': 'Record user_registered at edge', 'badge': 'T0', 'active': False},
                    {'label': '2. Onboarding Flow Execution', 'sub': 'Track milestone step timestamps', 'badge': 'Telemetry', 'active': True},
                    {'label': '3. Core Aha Milestone Triggered', 'sub': 'First value creation achieved', 'badge': 'T1', 'active': False},
                    {'label': '4. Calculate Delta: T1 - T0', 'sub': 'Target: Time-to-Value < 15 minutes', 'badge': '< 15m ✅', 'active': True},
                ],
                'kinetic_sub': 'Instrument your core activation loop first. Measure exact time between signup and first action.',
                'voiceover': 'Instrument your core activation loop first. Measure the exact timestamp between account creation and first successful project action. Fix the latency before scaling spend.',
                'cta': 'Data-backed engineering leadership'
            },
            {
                'tag': 'FRAMEWORK DOWNLOAD',
                'headline': 'GET THE TTV BLUEPRINT 📘',
                'subtitle': 'The executive guide to onboarding instrumentation',
                'window_title': 'ttv_framework_v1.pdf',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Complete Audit Framework', 'value': 'PDF DOWNLOAD ✅', 'note': 'Step-by-step telemetry audit checklist'},
                    {'title': 'SQL Query Blueprints', 'value': 'ANSI SQL INCLUDED ✅', 'note': 'Ready for PostgreSQL, ClickHouse, or SQLite'},
                    {'title': 'Industry Benchmark Guide', 'value': 'B2B SAAS NORMS ✅', 'note': 'Target metrics across developer tooling'},
                ],
                'kinetic_sub': 'Download the Time-to-Value Framework and engineering checklist via the link in this post.',
                'voiceover': 'We compiled the engineering checklist for measuring and compressing Time-to-Value in B2B software. Download the framework via the link in this post.',
                'cta': 'incubrix.com/ttv-framework'
            }
        ]
    },

    # 4. ast_bp_09_yt_vid (YouTube Shorts, 55s)
    {
        'asset_id': 'ast_bp_09_yt_vid',
        'platform': 'YouTube Shorts',
        'pillar': 'Growth Architecture',
        'voice': 'en-US-AndrewNeural',
        'scenes': [
            {
                'tag': 'EVENT SCHEMA INTRO',
                'headline': 'BUILD AN EVENT STREAM SCHEMA 📐',
                'subtitle': 'The exact JSON structure high-scale growth teams use',
                'window_title': 'schema_design.json',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Unvalidated Event Streams', 'value': 'DATA ROT ❌', 'note': 'Wild west schemas break downstream analytics'},
                    {'title': 'Standardized Schema', 'value': '100% FIDELITY ✅', 'note': 'Type-safe Pydantic contracts at the API edge'},
                    {'title': 'Target Validation Latency', 'value': '< 5ms ✅', 'note': 'Instant JSON validation without user lag'},
                ],
                'kinetic_sub': 'Here is the exact JSON schema top growth teams use for tracking user milestone events.',
                'voiceover': 'Here is the exact JSON schema top growth teams use for tracking user milestone events and activation loops.',
                'cta': 'Build robust data infrastructure'
            },
            {
                'tag': 'THE 4 CORE FIELDS',
                'headline': 'THE 4 CORE ROOT FIELDS 🔑',
                'subtitle': 'Mandatory identifiers for every event payload',
                'window_title': 'event_root.json',
                'visual_type': 'code',
                'visual_content': [
                    ('{\n', '#9CA3AF'),
                    ('  "event_id": "evt_01b0f1fa4351",', '#60A5FA'),
                    ('  "user_id": "usr_998124ac",', '#34D399'),
                    ('  "event_name": "workspace_activated",', '#FBBF24'),
                    ('  "timestamp_utc": "2026-10-25T15:00:00Z",', '#F472B6'),
                    ('  "session_id": "ses_71092aef",', '#60A5FA'),
                    ('  "platform": "web_desktop",', '#38BDF8'),
                    ('  "schema_version": "1.2.0"', '#34D399'),
                    ('}', '#9CA3AF'),
                ],
                'kinetic_sub': 'A standardized event schema with timestamp, user ID, event name, and context properties.',
                'voiceover': 'Don\'t let event schemas become a wild west. Every event requires four foundational root fields: unique event ID, user ID, normalized snake_case event name, and ISO-8601 UTC timestamp.',
                'cta': 'Never permit unversioned events'
            },
            {
                'tag': 'CONTEXT PROPERTIES',
                'headline': 'TYPED CONTEXT PROPERTIES 📦',
                'subtitle': 'Enforce validation on custom metadata',
                'window_title': 'event_context.json',
                'visual_type': 'code',
                'visual_content': [
                    ('  "context": {\n', '#9CA3AF'),
                    ('    "campaign_source": "linkedin",', '#60A5FA'),
                    ('    "utm_content": "ast_bp_09_yt_vid",', '#34D399'),
                    ('    "milestone_index": 2,', '#FBBF24'),
                    ('    "time_spent_seconds": 184,', '#F472B6'),
                    ('    "invitation_count": 3,', '#60A5FA'),
                    ('    "is_enterprise_domain": true', '#34D399'),
                    ('  }', '#9CA3AF'),
                ],
                'kinetic_sub': 'Custom context must follow strict types: integers, booleans, and sanitized strings.',
                'voiceover': 'Custom properties must reside inside a typed context object. Numbers stay numbers, booleans stay booleans, and strings are sanitized. This guarantees your analytics models never crash on unexpected nulls.',
                'cta': 'Strict Pydantic models at the edge'
            },
            {
                'tag': 'DOWNSTREAM GUARANTEES',
                'headline': 'PREVENT DOWNSTREAM DATA ROT 🛡️',
                'subtitle': 'What happens when schema validation runs at edge',
                'window_title': 'edge_validation_results.log',
                'visual_type': 'comparison',
                'visual_content': [
                    {'title': 'Schema Drift', 'value': 'ZERO DRIFT ✅', 'note': 'API gateway rejects malformed payloads automatically'},
                    {'title': 'Warehouse Cleanup', 'value': 'ZERO SCRUBBING ✅', 'note': 'Data engineers save 15+ hours weekly'},
                    {'title': 'Cohort Trust', 'value': '100% CONFIDENCE ✅', 'note': 'Executive metrics reflect primary source truth'},
                ],
                'kinetic_sub': 'In 55 seconds: how clean event schemas keep your telemetry pipeline healthy.',
                'voiceover': 'When validation happens at the edge, data engineers stop wasting hundreds of hours cleaning corrupted tables. Your analytics warehouse stays pristine.',
                'cta': 'Automate schema governance'
            },
            {
                'tag': 'GRAB THE SCHEMA',
                'headline': 'DOWNLOAD THE SCHEMA TEMPLATE ⬇️',
                'subtitle': 'Open-source JSON schema and Pydantic models',
                'window_title': 'github_repository.view',
                'visual_type': 'checklist',
                'visual_content': [
                    {'text': 'JSON Schema specification (Draft 7 compliant)', 'checked': True},
                    {'text': 'Pydantic v2 validation models in Python', 'checked': True},
                    {'text': 'TypeScript interfaces for frontend tracking', 'checked': True},
                    {'text': 'Subscribe for weekly growth engineering teardowns', 'checked': True},
                ],
                'kinetic_sub': 'Grab the complete JSON schema template from the link in description.',
                'voiceover': 'Grab our open-source event schema JSON template and Python Pydantic models from the link in the description. Subscribe for more developer guides.',
                'cta': 'incubrix.com/schemas'
            }
        ]
    },

    # 5. ast_bp_12_yt_vid (YouTube Shorts, 40s)
    {
        'asset_id': 'ast_bp_12_yt_vid',
        'platform': 'YouTube Shorts',
        'pillar': 'Workflow Engineering',
        'voice': 'en-US-AndrewNeural',
        'scenes': [
            {
                'tag': 'FEED DUPLICATION BUG',
                'headline': 'STOP SPAMMING YOUR FEED 🤖',
                'subtitle': 'Why automated social engines repeat posts',
                'window_title': 'feed_history.log',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Duplicate Post Triggered', 'value': '3X IN 1 WEEK ❌', 'note': 'Same hook posted across consecutive days'},
                    {'title': 'Follower Churn Rate', 'value': '+18% RISK 🚨', 'note': 'Repetitive spam degrades account trust'},
                    {'title': 'Naive Exact Match Check', 'value': 'FAILED ❌', 'note': 'Whitespace and casing changes bypassed filter'},
                ],
                'kinetic_sub': 'Ever see an automated brand account post the exact same content three times in one week? Here is the engineering fix.',
                'voiceover': 'Ever see an automated brand account post the exact same content three times in one week? Here is the engineering fix.',
                'cta': 'Deduplicate before scheduling'
            },
            {
                'tag': 'NORMALIZATION STEP',
                'headline': 'NORMALIZATION PIPELINE 🧹',
                'subtitle': 'Clean strings before hashing',
                'window_title': 'fingerprint_pipeline.py',
                'visual_type': 'code',
                'visual_content': [
                    ('def compute_asset_fingerprint(platform, fmt, hook):\n', '#60A5FA'),
                    ('    # 1. Normalize casing\n', '#6B7280'),
                    ('    p = platform.lower().strip()\n', '#9CA3AF'),
                    ('    f = fmt.lower().strip()\n', '#9CA3AF'),
                    ('    # 2. Strip punctuation & collapse whitespace\n', '#6B7280'),
                    ('    clean_hook = re.sub(r"[^a-z0-9]", "", hook.lower())\n', '#FBBF24'),
                    ('    raw_str = f"{p}|{f}|{clean_hook}"\n', '#34D399'),
                    ('    return hashlib.sha256(raw_str.encode()).hexdigest()\n', '#38BDF8'),
                ],
                'kinetic_sub': 'When you run automated pipelines, naive checks fail on tiny whitespace. You need normalized fingerprinting.',
                'voiceover': 'When you run an automated content pipeline, naive duplicate checks fail because of tiny whitespace or casing differences. You need normalized content fingerprinting.',
                'cta': 'Deterministic string normalization'
            },
            {
                'tag': 'SHA-256 HASH GENERATION',
                'headline': 'SHA-256 HASH GENERATION 🔐',
                'subtitle': 'Generate a unique 64-character fingerprint',
                'window_title': 'hash_output.terminal',
                'visual_type': 'comparison',
                'visual_content': [
                    {'title': 'Normalized Payload', 'value': 'linkedin|carousel|the5slidetelemetry...', 'note': 'Deterministic composite string'},
                    {'title': 'SHA-256 Digest', 'value': '7f1c8e9b40... (64 hex)', 'note': 'Unique immutable content signature'},
                    {'title': 'Database Index', 'value': 'UNIQUE(fingerprint) ✅', 'note': 'Collision-resistant SQLite / Postgres constraint'},
                ],
                'kinetic_sub': 'In our pipeline, we normalize platform, format, and hook into a standardized string and compute a SHA-256 hash.',
                'voiceover': 'In our pipeline, we normalize the platform, format, and core hook text into a standardized string, then compute a deterministic SHA-256 cryptographic hash.',
                'cta': 'Cryptographic duplicate detection'
            },
            {
                'tag': 'DATABASE PROTECTION',
                'headline': 'ZERO DUPLICATE POSTS 🛡️',
                'subtitle': 'Database constraint blocks duplicate insertion',
                'window_title': 'sqlite_protection.sql',
                'visual_type': 'checklist',
                'visual_content': [
                    {'text': 'Check fingerprint index before saving asset', 'checked': True},
                    {'text': 'Reject duplicate inserts automatically at DB level', 'checked': True},
                    {'text': 'Audit logging records duplicate attempt telemetry', 'checked': True},
                    {'text': 'Followers never see repetitive post spam', 'checked': True},
                ],
                'kinetic_sub': 'Before any asset is saved or scheduled, the database checks the index. Zero duplicate spam.',
                'voiceover': 'Before any asset is saved or scheduled, the database checks the fingerprint index. If it already exists, the post is instantly rejected. Zero duplicate spam. Grab the open source code below.',
                'cta': 'incubrix.com/fingerprint-guide'
            }
        ]
    },

    # 6. ast_bp_15_yt_vid (YouTube Shorts, 50s)
    {
        'asset_id': 'ast_bp_15_yt_vid',
        'platform': 'YouTube Shorts',
        'pillar': 'Onboarding & Retention',
        'voice': 'en-US-AndrewNeural',
        'scenes': [
            {
                'tag': 'ACTIVATION TELEMETRY',
                'headline': 'CALCULATE ACTIVATION IN SQL 📊',
                'subtitle': 'Skip $50k enterprise analytics tools',
                'window_title': 'terminal_psql.view',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Enterprise Analytics Bill', 'value': '$50,000 / yr ❌', 'note': 'Bloated SaaS contracts for basic funnel math'},
                    {'title': 'Single SQL Query', 'value': 'FREE & FAST ✅', 'note': 'Runs directly on Postgres or SQLite'},
                    {'title': 'Execution Latency', 'value': '< 120ms ✅', 'note': 'Instant activation cohort breakdown'},
                ],
                'kinetic_sub': 'Here is how to calculate your user activation rate without paying $50,000 for enterprise analytics.',
                'voiceover': 'Here is how to calculate your user activation rate without paying fifty thousand dollars for enterprise analytics software.',
                'cta': 'Master fundamental SQL telemetry'
            },
            {
                'tag': 'THE 3-LINE QUERY',
                'headline': 'THE ACTIVATION SQL QUERY 💻',
                'subtitle': 'Compare signup timestamp to milestone achievement',
                'window_title': 'activation_rate.sql',
                'visual_type': 'code',
                'visual_content': [
                    ('SELECT\n', '#9CA3AF'),
                    ('  date_trunc(\'week\', u.created_at) AS cohort_week,\n', '#60A5FA'),
                    ('  COUNT(u.user_id) AS total_signups,\n', '#FBBF24'),
                    ('  COUNT(m.user_id) FILTER (\n', '#34D399'),
                    ('    WHERE m.achieved_at <= u.created_at + INTERVAL \'72 hours\'\n', '#F472B6'),
                    ('  ) * 100.0 / COUNT(u.user_id) AS activation_pct\n', '#34D399'),
                    ('FROM users u\n', '#60A5FA'),
                    ('LEFT JOIN milestones m ON u.user_id = m.user_id\n', '#38BDF8'),
                    ('GROUP BY 1 ORDER BY 1 DESC;\n', '#9CA3AF'),
                ],
                'kinetic_sub': 'A simple SQL query comparing signup timestamp to first key milestone timestamp reveals activation health.',
                'voiceover': 'You don\'t need bloated enterprise dashboards to measure activation. Here is a simple SQL query that compares user signup timestamps with milestone completion inside the first 72 hours.',
                'cta': 'Clean cohort measurement in SQL'
            },
            {
                'tag': 'READING THE METRICS',
                'headline': 'INTERPRETING THE OUTPUT 📈',
                'subtitle': 'What a healthy activation rate looks like',
                'window_title': 'query_results.tbl',
                'visual_type': 'comparison',
                'visual_content': [
                    {'title': 'Cohort Week Oct 04', 'value': '18.4% (AT RISK) ⚠️', 'note': 'Users dropping off before reaching aha moment'},
                    {'title': 'Cohort Week Oct 11', 'value': '24.1% (IMPROVING)', 'note': 'Onboarding friction partially reduced'},
                    {'title': 'Cohort Week Oct 18', 'value': '42.8% (HEALTHY) ✅', 'note': 'Target milestone reached inside 72 hours'},
                ],
                'kinetic_sub': 'If your activation rate stays below 20%, paid acquisition will only accelerate churn.',
                'voiceover': 'If your 72-hour activation rate stays below twenty percent, scaling paid ads will burn your budget. When activation climbs above forty percent, your growth engine compounds.',
                'cta': 'Fix activation before scaling spend'
            },
            {
                'tag': 'GRAB THE QUERIES',
                'headline': 'DOWNLOAD THE SQL SCRIPTS ⬇️',
                'subtitle': 'Pre-written queries for Postgres, MySQL & SQLite',
                'window_title': 'sql_queries.zip',
                'visual_type': 'checklist',
                'visual_content': [
                    {'text': '72-Hour activation rate query', 'checked': True},
                    {'text': 'Step-by-step onboarding drop-off query', 'checked': True},
                    {'text': 'Cohort Day-7 and Day-30 retention matrices', 'checked': True},
                    {'text': 'Subscribe for weekly SQL telemetry snippets', 'checked': True},
                ],
                'kinetic_sub': 'Copy the SQL queries from the link in description and run them on your DB.',
                'voiceover': 'Copy the full SQL queries from the link in the description and run them on your staging database today. Subscribe for more growth engineering breakdowns.',
                'cta': 'incubrix.com/sql-queries'
            }
        ]
    },

    # 7. ast_bp_16_li_vid (LinkedIn Video, 45s)
    {
        'asset_id': 'ast_bp_16_li_vid',
        'platform': 'LinkedIn',
        'pillar': 'Growth Architecture',
        'voice': 'en-US-AndrewNeural',
        'scenes': [
            {
                'tag': 'THE DISCONNECT',
                'headline': 'ENGINEERING VS MARKETING 💥',
                'subtitle': 'When teams name the same event differently',
                'window_title': 'discrepancy_report.log',
                'visual_type': 'comparison',
                'visual_content': [
                    {'title': 'Engineering Database Event', 'value': 'user_registered', 'note': 'Logged in backend PostgreSQL on auth commit'},
                    {'title': 'Marketing Pixel Event', 'value': 'lead_created', 'note': 'Fired on button click regardless of success'},
                    {'title': 'Attribution Discrepancy', 'value': '32% MISMATCH ❌', 'note': 'Executive dashboards disagree on monthly growth'},
                ],
                'kinetic_sub': 'When engineering calls it user_registered and marketing calls it lead_created, attribution breaks.',
                'voiceover': 'When engineering calls it user_registered and marketing calls it lead_created, attribution breaks. Executive dashboards report conflicting growth numbers.',
                'cta': 'Unify cross-functional taxonomy'
            },
            {
                'tag': 'THE COST OF DRIFT',
                'headline': 'THE COST OF TAXONOMY DRIFT 💸',
                'subtitle': 'Why disconnected data silos waste engineering hours',
                'window_title': 'debugging_hours.chart',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Quarterly Debugging Hours', 'value': '80+ HOURS ❌', 'note': 'Engineers tracking down phantom attribution gaps'},
                    {'title': 'Wasted Ad Spend', 'value': 'MISALLOCATED ❌', 'note': 'Ad algorithms optimizing for fake button clicks'},
                    {'title': 'Resolution SLA', 'value': 'WEEKS ⚠️', 'note': 'Cross-team finger pointing delays roadmap'},
                ],
                'kinetic_sub': 'The costly disconnect between engineering logs and marketing pipelines.',
                'voiceover': 'This disconnect costs engineering teams hundreds of hours debugging phantom discrepancies, while marketing optimizes campaigns against broken data.',
                'cta': 'Shared schemas save engineering time'
            },
            {
                'tag': 'THE UNIFIED TAXONOMY',
                'headline': 'THE UNIFIED TAXONOMY 📐',
                'subtitle': 'A single source of truth for all lifecycle events',
                'window_title': 'unified_event_taxonomy.yaml',
                'visual_type': 'code',
                'visual_content': [
                    ('lifecycle_events:\n', '#9CA3AF'),
                    ('  - name: account_created\n', '#60A5FA'),
                    ('    owner: identity_service\n', '#34D399'),
                    ('    destinations: [database, ga4, hubspot]\n', '#FBBF24'),
                    ('  - name: workspace_provisioned\n', '#60A5FA'),
                    ('    owner: core_backend\n', '#34D399'),
                    ('    destinations: [mixpanel, data_warehouse]\n', '#FBBF24'),
                ],
                'kinetic_sub': 'A single source of truth for event naming eliminates discrepancies.',
                'voiceover': 'The solution is a single version-controlled event taxonomy. One schema definition shared across backend services, analytics pipelines, and marketing webhooks.',
                'cta': 'Code-governed event taxonomy'
            },
            {
                'tag': 'EXECUTIVE ACTION',
                'headline': 'DOWNLOAD THE TAXONOMY CHEAT SHEET 📘',
                'subtitle': 'Standardized event schemas for modern B2B SaaS',
                'window_title': 'event_taxonomy_cheatsheet.pdf',
                'visual_type': 'checklist',
                'visual_content': [
                    {'text': 'Standardized B2B lifecycle event dictionary', 'checked': True},
                    {'text': 'Git-backed schema review workflow for PMs & Devs', 'checked': True},
                    {'text': 'Automated webhook dispatch validation script', 'checked': True},
                    {'text': 'Share with your engineering and marketing leads', 'checked': True},
                ],
                'kinetic_sub': 'Download the unified event taxonomy cheat sheet via the link in this post.',
                'voiceover': 'Download our unified event taxonomy cheat sheet and schema templates via the link in this post. Align your data team once and for all.',
                'cta': 'incubrix.com/event-taxonomy'
            }
        ]
    },

    # 8. ast_bp_18_yt_vid (YouTube Shorts, 30s)
    {
        'asset_id': 'ast_bp_18_yt_vid',
        'platform': 'YouTube Shorts',
        'pillar': 'Attribution & UTMs',
        'voice': 'en-US-AndrewNeural',
        'scenes': [
            {
                'tag': 'STOP MANUAL TYPING',
                'headline': 'STOP TYPING UTM LINKS MANUALLY 🛑',
                'subtitle': 'Typing parameters in browser bars always creates errors',
                'window_title': 'manual_utm_error.view',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Manual Parameter Error Rate', 'value': '35% TYPOS ❌', 'note': 'Misspelled utm_medium or broken ampersands'},
                    {'title': 'Time Spent per Link', 'value': '2 - 3 MINS ⏱️', 'note': 'Tedious copy-pasting slows marketing velocity'},
                    {'title': 'Programmatic Generator', 'value': '< 10 MS ✅', 'note': 'Instant error-free link generation in Python'},
                ],
                'kinetic_sub': 'Stop manually typing UTM links in your browser. Here is the fast, programmatic way.',
                'voiceover': 'Stop manually typing UTM links in your browser. Here is the fast, programmatic way.',
                'cta': 'Automate link attribution'
            },
            {
                'tag': 'THE 5-LINE FUNCTION',
                'headline': 'THE 30-SECOND PYTHON FIX ⚡',
                'subtitle': 'Enforce lowercase, url encoding, and required tags',
                'window_title': 'build_tracking_url.py',
                'visual_type': 'code',
                'visual_content': [
                    ('def build_tracking_url(base, source, medium, campaign, content):\n', '#60A5FA'),
                    ('    params = {\n', '#9CA3AF'),
                    ('        "utm_source": source.lower().strip(),\n', '#34D399'),
                    ('        "utm_medium": medium.lower().strip(),\n', '#34D399'),
                    ('        "utm_campaign": campaign.lower().strip(),\n', '#FBBF24'),
                    ('        "utm_content": content.strip()\n', '#F472B6'),
                    ('    }\n', '#9CA3AF'),
                    ('    return f"{base}?{urllib.parse.urlencode(params)}"\n', '#38BDF8'),
                ],
                'kinetic_sub': 'Automated UTM generation prevents typos and enforces consistent campaign metadata.',
                'voiceover': 'Automated UTM generation prevents typos, encodes special characters, and enforces lowercase casing across every social channel.',
                'cta': 'Never let a broken link go live'
            },
            {
                'tag': 'DOWNLOAD SCRIPT',
                'headline': 'GRAB THE SCRIPT & FORMULAS 🔗',
                'subtitle': 'Python CLI tool and Google Sheets formula generator',
                'window_title': 'utm_tools.view',
                'visual_type': 'checklist',
                'visual_content': [
                    {'text': 'Standalone Python CLI script (zero external dependencies)', 'checked': True},
                    {'text': 'Formula-injection safe Google Sheets template', 'checked': True},
                    {'text': 'Full source code link in description below', 'checked': True},
                    {'text': 'Subscribe for 30-second growth engineering tips', 'checked': True},
                ],
                'kinetic_sub': 'Download the Python UTM script from the link in description.',
                'voiceover': 'Download the Python UTM script from the link in the description. Subscribe for more 30-second growth engineering tips.',
                'cta': 'incubrix.com/python-utm-script'
            }
        ]
    },

    # 9. ast_bp_21_yt_vid (YouTube Shorts, 58s)
    {
        'asset_id': 'ast_bp_21_yt_vid',
        'platform': 'YouTube Shorts',
        'pillar': 'Workflow Engineering',
        'voice': 'en-US-AndrewNeural',
        'scenes': [
            {
                'tag': 'THE WORKFLOW',
                'headline': 'RELEASE NOTES TO SOCIAL POSTS 🚀',
                'subtitle': 'Transform markdown release notes in under 60 seconds',
                'window_title': 'git_release_notes.md',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Raw Markdown Changelog', 'value': 'INPUT TEXT', 'note': 'Technical Git commit logs and release notes'},
                    {'title': 'Fact Extraction Engine', 'value': 'AUTOMATED ✅', 'note': 'Extracts verbatim quotes, latency numbers, and metrics'},
                    {'title': 'Multi-Channel Output', 'value': '3 FORMATS ✅', 'note': 'X thread, LinkedIn breakdown, and Video script'},
                ],
                'kinetic_sub': 'Watch an engineer turn raw git release notes into 3 platform-ready social posts in under 60 seconds.',
                'voiceover': 'Watch an engineer turn raw git release notes into three platform-ready social posts in under sixty seconds.',
                'cta': 'Repurpose engineering documentation'
            },
            {
                'tag': 'STEP 1: FACT EXTRACTION',
                'headline': 'STEP 1: EXTRACT VERBATIM FACTS 🔍',
                'subtitle': 'Syntactic parsing extracts verifiable claims',
                'window_title': 'fact_extraction.py',
                'visual_type': 'code',
                'visual_content': [
                    ('class EvidenceReference(BaseModel):\n', '#60A5FA'),
                    ('    claim: str = Field(min_length=5)\n', '#34D399'),
                    ('    source_quote: str = Field(min_length=5)\n', '#FBBF24'),
                    ('    section_or_page: str\n', '#9CA3AF'),
                    ('    is_verified: bool = True\n', '#38BDF8'),
                    ('\n', '#9CA3AF'),
                    ('# Zero hallucinations: Every claim binds to a quote\n', '#6B7280'),
                ],
                'kinetic_sub': 'Automated fact extraction identifies technical milestones and formats them into developer-friendly updates.',
                'voiceover': 'Step one: The engine parses markdown release notes, extracting verbatim quotes, performance metrics, and architectural updates into structured evidence models. Zero hallucinated claims.',
                'cta': 'Evidence-backed content generation'
            },
            {
                'tag': 'STEP 2: PLATFORM ADAPTATION',
                'headline': 'STEP 2: MULTI-PLATFORM ADAPTATION 📱',
                'subtitle': 'One source generates tailored platform assets',
                'window_title': 'platform_matrix.view',
                'visual_type': 'diagram',
                'visual_content': [
                    {'label': '1. X (Twitter) High-Density Post', 'sub': 'Under 280 chars, code snippet highlight', 'badge': '< 280c', 'active': False},
                    {'label': '2. LinkedIn Thought Leadership Post', 'sub': 'Executive architecture context with takeaways', 'badge': 'Bulleted', 'active': True},
                    {'label': '3. YouTube Shorts Video Script', 'sub': 'Timed 45s script with audio visual cues', 'badge': '45s Script', 'active': False},
                ],
                'kinetic_sub': 'One technical source generates an X post, LinkedIn breakdown, and timed video script.',
                'voiceover': 'Step two: The matrix transforms the extracted facts into platform-native copy: punchy bulleted takeaways for X, technical thought leadership for LinkedIn, and a timed 45-second script for Shorts.',
                'cta': 'Platform-native formatting'
            },
            {
                'tag': 'STEP 3: SCHEDULER EXPORT',
                'headline': 'STEP 3: SCHEDULER-READY EXPORT 📑',
                'subtitle': 'Exports directly to 23-column workbook calendar CSV',
                'window_title': 'calendar_export.csv',
                'visual_type': 'comparison',
                'visual_content': [
                    {'title': 'Excel / Google Sheets CSV', 'value': 'UTF-8 BOM ✅', 'note': 'Formula-injection safe escaping'},
                    {'title': 'Standardized Schema', 'value': '23 COLUMNS ✅', 'note': 'Matches official IncuBrix workbook calendar'},
                    {'title': 'Status Safeguard', 'value': 'PLANNED / DRAFT', 'note': 'Never prematurely marks unrendered assets Ready'},
                ],
                'kinetic_sub': 'Export verified drafts into scheduler-ready CSVs with full UTM attribution.',
                'voiceover': 'Step three: Assets are exported to standard CSV with full UTM attribution and content fingerprints. No manual copy-pasting between spreadsheets.',
                'cta': 'Automated editorial operations'
            },
            {
                'tag': 'EXPLORE REPO',
                'headline': 'CLONE THE PIPELINE ON GITHUB 💻',
                'subtitle': 'Open-source Python content engine repository',
                'window_title': 'incubrix_growth_repo.view',
                'visual_type': 'checklist',
                'visual_content': [
                    {'text': 'Clone the Python content engine repository', 'checked': True},
                    {'text': 'Run pytest test suite (57 passing tests)', 'checked': True},
                    {'text': 'Execute single-command FastAPI development server', 'checked': True},
                    {'text': 'Subscribe and star the repository on GitHub', 'checked': True},
                ],
                'kinetic_sub': 'Subscribe and explore our content engine automation scripts in GitHub.',
                'voiceover': 'The entire content engine is open-source. Explore the repository and test suite on GitHub via the link in the description. Subscribe for more builds.',
                'cta': 'incubrix.com/workflow-automation'
            }
        ]
    },

    # 10. ast_bp_24_yt_vid (YouTube Shorts, 45s)
    {
        'asset_id': 'ast_bp_24_yt_vid',
        'platform': 'YouTube Shorts',
        'pillar': 'Growth Architecture',
        'voice': 'en-US-AndrewNeural',
        'scenes': [
            {
                'tag': 'SIGNUP TRANSACTION LATENCY',
                'headline': 'DON\'T SLOW DOWN SIGNUPS 🛑',
                'subtitle': 'How telemetry events cause 500ms onboarding lags',
                'window_title': 'api_latency_monitor.view',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Synchronous Webhook Dispatch', 'value': '520ms LATENCY ❌', 'note': 'Calling external CRM inside signup request'},
                    {'title': 'User Drop-off Impact', 'value': '+12% CHURN 🚨', 'note': 'Users abandon sluggish registration forms'},
                    {'title': 'Optimal Gateway Latency', 'value': '< 15ms ✅', 'note': 'Offload event dispatch to background workers'},
                ],
                'kinetic_sub': 'How do you trigger welcome sequences without lagging your main signup transaction?',
                'voiceover': 'How do you trigger welcome email sequences and tracking events without adding half a second of latency to your signup transaction? Watch this architecture.',
                'cta': 'Decouple transactions from telemetry'
            },
            {
                'tag': 'ASYNC BACKGROUND WORKERS',
                'headline': 'THE BACKGROUND WORKER PATTERN ⚡',
                'subtitle': 'FastAPI background tasks and Celery/Redis queues',
                'window_title': 'fastapi_signup.py',
                'visual_type': 'code',
                'visual_content': [
                    ('@app.post("/api/v1/auth/signup")\n', '#60A5FA'),
                    ('async def register_user(req: SignupRequest, bg: BackgroundTasks):\n', '#34D399'),
                    ('    # 1. Commit user account in <15ms\n', '#6B7280'),
                    ('    user = await db.create_user(req)\n', '#FBBF24'),
                    ('    # 2. Offload telemetry and CRM to background\n', '#6B7280'),
                    ('    bg.add_task(dispatch_growth_telemetry, user.id)\n', '#F472B6'),
                    ('    return {"status": "created", "user_id": user.id}\n', '#38BDF8'),
                ],
                'kinetic_sub': 'Decouple analytics event dispatch from user-facing transactions using background workers.',
                'voiceover': 'Decouple telemetry dispatch from user transactions. Commit the user account to the database, respond with HTTP 201 in under fifteen milliseconds, and offload event streaming to an asynchronous background worker.',
                'cta': 'Sub-15ms user-facing response'
            },
            {
                'tag': 'WEBHOOK VERIFICATION',
                'headline': 'IDEMPOTENT WEBHOOK HANDLING 🔐',
                'subtitle': 'HMAC signature verification and exponential backoff',
                'window_title': 'webhook_handler.py',
                'visual_type': 'diagram',
                'visual_content': [
                    {'label': '1. Incoming Webhook Payload', 'sub': 'Signed with HMAC-SHA256 signature', 'badge': 'Secure', 'active': False},
                    {'label': '2. Signature Verification Guard', 'sub': 'Reject forged payloads before parsing', 'badge': '< 2ms', 'active': True},
                    {'label': '3. Idempotency Key Validation', 'sub': 'Check database unique constraint', 'badge': 'Zero Dupe', 'active': True},
                    {'label': '4. Exponential Backoff Queue', 'sub': 'Retry failed requests at 2s, 8s, 32s', 'badge': 'Resilient', 'active': False},
                ],
                'kinetic_sub': 'In 45 seconds: Keep your signup latency under 100ms by offloading events to workers.',
                'voiceover': 'Combine background workers with HMAC signature verification and exponential backoff retries. If a downstream CRM experiences an outage, your users never see an error.',
                'cta': 'Zero user-facing downtime'
            },
            {
                'tag': 'GET THE CODE',
                'headline': 'DOWNLOAD THE FASTAPI PATTERN ⬇️',
                'subtitle': 'Production-ready async background worker sample',
                'window_title': 'background_tasks_sample.py',
                'visual_type': 'checklist',
                'visual_content': [
                    {'text': 'FastAPI async background task template', 'checked': True},
                    {'text': 'HMAC-SHA256 webhook verification utility', 'checked': True},
                    {'text': 'Exponential backoff retry decorator', 'checked': True},
                    {'text': 'Subscribe for weekly backend growth engineering builds', 'checked': True},
                ],
                'kinetic_sub': 'Subscribe and download the background worker code pattern in our docs.',
                'voiceover': 'Subscribe and download the background worker code pattern from our documentation in the description below.',
                'cta': 'incubrix.com/background-workers'
            }
        ]
    },

    # 11. ast_bp_25_li_vid (LinkedIn Video, 55s)
    {
        'asset_id': 'ast_bp_25_li_vid',
        'platform': 'LinkedIn',
        'pillar': 'Attribution & UTMs',
        'voice': 'en-US-AndrewNeural',
        'scenes': [
            {
                'tag': 'EXECUTIVE QUESTION',
                'headline': 'MEASURING CONTENT ROI 💰',
                'subtitle': 'Beyond vanity likes and superficial impressions',
                'window_title': 'social_revenue_audit.view',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Total Monthly Social Impressions', 'value': '145,000 👀', 'note': 'Impressions look impressive on vanity slides'},
                    {'title': 'Attributed Closed Revenue', 'value': 'UNKNOWN ❌', 'note': 'Attribution loop disconnected from CRM pipeline'},
                    {'title': 'Executive Decision', 'value': 'BUDGET CUT 🚨', 'note': 'Unmeasured channels face budget clawbacks'},
                ],
                'kinetic_sub': 'How much revenue did your last LinkedIn post generate? If you can\'t answer, your attribution loop is broken.',
                'voiceover': 'How much revenue did your company\'s last LinkedIn post generate? If your growth team cannot answer with specific numbers, your attribution loop is broken.',
                'cta': 'Tie organic reach to pipeline'
            },
            {
                'tag': 'THE 3-TIER ATTRIBUTION',
                'headline': 'THE 3-STAGE ATTRIBUTION LOOP 🔄',
                'subtitle': 'Connecting top-of-funnel social assets directly to CRM deals',
                'window_title': 'attribution_flow.diag',
                'visual_type': 'diagram',
                'visual_content': [
                    {'label': '1. Top-of-Funnel Social Asset', 'sub': 'Tagged with unique utm_content asset ID', 'badge': 'Social', 'active': False},
                    {'label': '2. High-Intent Destination Page', 'sub': 'Interactive blueprint or architecture teardown', 'badge': 'Landing', 'active': True},
                    {'label': '3. CRM Opportunity Created', 'sub': 'UTM parameters mapped to HubSpot / Salesforce deal', 'badge': 'CRM Deal', 'active': True},
                    {'label': '4. Closed-Won Revenue Realized', 'sub': 'Exact pipeline contribution attributed to post', 'badge': 'Revenue ✅', 'active': True},
                ],
                'kinetic_sub': 'Connecting multi-touch UTM parameters to CRM deal stages establishes true pipeline contribution.',
                'voiceover': 'Modern growth engineering establishes a three-stage attribution loop: Granular UTM parameters tag the asset, mid-funnel technical blueprints capture high-intent signups, and CRM integration binds the deal to the original post.',
                'cta': 'Granular multi-touch tracking'
            },
            {
                'tag': 'WHY VANITY METRICS FAIL',
                'headline': 'VANITY METRICS VS PIPELINE 📉',
                'subtitle': 'Impressions do not pay engineering salaries',
                'window_title': 'pipeline_attribution_report.tbl',
                'visual_type': 'comparison',
                'visual_content': [
                    {'title': 'Post A: Generic AI Meme', 'value': '45k Views | $0 Pipeline ❌', 'note': 'High viral reach, zero buyer qualification'},
                    {'title': 'Post B: Architecture Teardown', 'value': '3.2k Views | $48k Pipeline ✅', 'note': 'High-intent technical buyers convert to demos'},
                    {'title': 'Strategic Conclusion', 'value': 'QUALITY > VOLUME', 'note': 'Technical authority beats superficial clicks'},
                ],
                'kinetic_sub': 'Executive briefing: Moving beyond likes to closed-won revenue in your CRM.',
                'voiceover': 'Executive leadership does not care about viral meme likes. A technical architecture breakdown with three thousand views that generates forty-eight thousand dollars in pipeline is ten times more valuable than a generic viral post.',
                'cta': 'High-intent technical authority'
            },
            {
                'tag': 'DOWNLOAD FRAMEWORK',
                'headline': 'DOWNLOAD THE ATTRIBUTION GUIDE 📘',
                'subtitle': 'The Growth Engineer\'s Guide to Social Pipeline Attribution',
                'window_title': 'attribution_framework.pdf',
                'visual_type': 'checklist',
                'visual_content': [
                    {'text': 'UTM parameter taxonomy specification sheet', 'checked': True},
                    {'text': 'HubSpot & Salesforce custom property mapping guide', 'checked': True},
                    {'text': 'SQL attribution modeling queries (First-Touch & W-Shaped)', 'checked': True},
                    {'text': 'Watch the video and download the framework via link', 'checked': True},
                ],
                'kinetic_sub': 'Watch the video and download the social-to-revenue attribution framework.',
                'voiceover': 'Download our social-to-revenue attribution framework and CRM setup guide via the link in this post. Stop guessing your content ROI.',
                'cta': 'incubrix.com/attribution-framework'
            }
        ]
    },

    # 12. ast_bp_27_yt_vid (YouTube Shorts, 50s)
    {
        'asset_id': 'ast_bp_27_yt_vid',
        'platform': 'YouTube Shorts',
        'pillar': 'Workflow Engineering',
        'voice': 'en-US-AndrewNeural',
        'scenes': [
            {
                'tag': 'CHAOTIC SPREADSHEETS',
                'headline': 'YOUR CONTENT CALENDAR IS A MESS 📑',
                'subtitle': 'Why unstructured spreadsheets create operational chaos',
                'window_title': 'messy_content_sheet.view',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Unformatted Content Cells', 'value': 'CHAOTIC ❌', 'note': 'Copy-pasting unvalidated captions across tabs'},
                    {'title': 'Missing Asset Identifiers', 'value': 'NO IDS ❌', 'note': 'No way to link analytics back to source drafts'},
                    {'title': 'Formula Injection Vulnerability', 'value': 'RISK 🚨', 'note': 'Unescaped characters triggering spreadsheet alerts'},
                ],
                'kinetic_sub': 'Here is why your social media calendar looks messy and how to organize it like a software database.',
                'voiceover': 'Here is why your social media calendar looks messy and how to organize it like a professional software database.',
                'cta': 'Treat content assets as database records'
            },
            {
                'tag': 'THE 23-COLUMN SCHEMA',
                'headline': 'THE 23-COLUMN STANDARDIZED SCHEMA 🗄️',
                'subtitle': 'The exact columns required for automated content engines',
                'window_title': 'calendar_schema_23_columns.tbl',
                'visual_type': 'code',
                'visual_content': [
                    ('1. asset_id         8. utm_link            15. scheduled_date\n', '#60A5FA'),
                    ('2. platform         9. final_file_url      16. test_published_url\n', '#34D399'),
                    ('3. format          10. source_file_url     17. impressions_or_views\n', '#FBBF24'),
                    ('4. content_pillar  11. source_input        18. engagement_rate\n', '#9CA3AF'),
                    ('5. hook            12. tools_used          19. clicks\n', '#F472B6'),
                    ('6. caption         13. rights_checked      20. status\n', '#38BDF8'),
                    ('7. cta             14. ai_label_needed     21. notes\n', '#34D399'),
                    ('                                           22. duplicate_check\n', '#FBBF24'),
                    ('                                           23. completeness_check\n', '#60A5FA'),
                ],
                'kinetic_sub': 'Treating social assets as database records with unique IDs, pillars, and verification flags.',
                'voiceover': 'Stop managing content in random documents. In our growth engine, every asset is a database record with twenty-three standardized columns: unique IDs, platform formats, verification flags, and full audit metadata.',
                'cta': 'Automated schema enforcement'
            },
            {
                'tag': 'THE READINESS GUARDRAIL',
                'headline': 'THE READINESS GUARDRAIL 🛡️',
                'subtitle': 'Never mark an asset Ready until all 8 gates pass',
                'window_title': 'readiness_audit.view',
                'visual_type': 'checklist',
                'visual_content': [
                    {'text': 'Hook and platform-native caption verified', 'checked': True},
                    {'text': 'Normalized hashtags and active UTM tracking link verified', 'checked': True},
                    {'text': 'Rendered final file (MP4, PDF, PNG) checked on disk', 'checked': True},
                    {'text': 'Preserved editable source file linked in repository', 'checked': True},
                ],
                'kinetic_sub': 'In 50 seconds: How to structure your content calendar for automated exports.',
                'voiceover': 'This structure enforces the readiness guardrail: An asset is never marked Ready while it remains text-only. Rendered files, editable sources, and rights clearance must be verified first.',
                'cta': 'Rigorous editorial engineering'
            },
            {
                'tag': 'DOWNLOAD TEMPLATE',
                'headline': 'DOWNLOAD THE 23-COLUMN TEMPLATE 📑',
                'subtitle': 'Assessment-workbook-compatible calendar CSV export',
                'window_title': 'calendar_export_preview.csv',
                'visual_type': 'comparison',
                'visual_content': [
                    {'title': 'FastAPI Export Endpoint', 'value': 'GET /exports/calendar ✅', 'note': 'Automated export directly from SQLite database'},
                    {'title': 'Excel & Sheets Ready', 'value': 'UTF-8 BOM ENCODED ✅', 'note': 'Immediate spreadsheet compatibility'},
                    {'title': 'Formula Protection', 'value': 'AUTOMATIC ESCAPING ✅', 'note': 'Safe prefixing for hostile formula characters'},
                ],
                'kinetic_sub': 'Download our official 23-column content calendar template via link in description.',
                'voiceover': 'Download our official twenty-three column content calendar template from the link in the description. Transform your content operations today.',
                'cta': 'incubrix.com/calendar-template'
            }
        ]
    },

    # 13. ast_bp_29_x_vid (X Video, 45s)
    {
        'asset_id': 'ast_bp_29_x_vid',
        'platform': 'X Video',
        'pillar': 'Onboarding & Retention',
        'voice': 'en-US-AndrewNeural',
        'scenes': [
            {
                'tag': 'SILENT RETENTION BUGS',
                'headline': '3 RETENTION LEAKS IN 45 SECONDS 🚨',
                'subtitle': 'Subtle telemetry bugs that skew your cohort retention metrics',
                'window_title': 'retention_anomalies.log',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Server Error Status', 'value': 'HTTP 200 OK (SILENT) ⚠️', 'note': 'Zero crash alerts while metrics skew'},
                    {'title': 'Cohort Retention Variance', 'value': '±28% ERROR ❌', 'note': 'Bad data produces bad engineering decisions'},
                    {'title': 'Time to Diagnostic', 'value': 'WEEKS DELAYED ⏱️', 'note': 'Audit these 3 common flaws today'},
                ],
                'kinetic_sub': '3 subtle telemetry bugs that skew your cohort retention metrics without throwing server errors (Teardown):',
                'voiceover': 'Three subtle telemetry bugs that quietly skew your cohort retention metrics without ever throwing a server error. Here is the fast forty-five second teardown.',
                'cta': 'Audit your cohort telemetry'
            },
            {
                'tag': 'BUG 1: TIMEZONES',
                'headline': 'BUG 1: UNNORMALIZED TIMEZONES 🌐',
                'subtitle': 'Mixing local browser timestamps with UTC server logs',
                'window_title': 'timezone_bug.sql',
                'visual_type': 'comparison',
                'visual_content': [
                    {'title': 'Client Ingestion Timestamp', 'value': '2026-10-25 08:00 (PST) ❌', 'note': 'Local device time offset by -7 hours'},
                    {'title': 'Server Database Timestamp', 'value': '2026-10-25 15:00 (UTC) ✅', 'note': 'True universal coordinated time'},
                    {'title': 'The Churn Artifact', 'value': 'NEGATIVE RETENTION 🚨', 'note': 'Day-0 actions misclassified as Day-(-1)'},
                ],
                'kinetic_sub': 'Timezone offsets corrupt retention cohorts when clients send unnormalized timestamps.',
                'voiceover': 'Bug one: Storing timestamps without UTC normalization. If a user in California signs up at eleven PM local time, unnormalized pipelines record actions in the wrong calendar day, corrupting Day-One retention.',
                'cta': 'Always enforce UTC normalization'
            },
            {
                'tag': 'BUGS 2 & 3: BOUNCE & INDEXES',
                'headline': 'BUGS 2 & 3: BOUNCE & UNINDEXED LOGS 📉',
                'subtitle': 'Frontend event debouncing and database query optimization',
                'window_title': 'telemetry_best_practices.md',
                'visual_type': 'checklist',
                'visual_content': [
                    {'text': 'Debounce frontend button clicks to avoid double-counted sessions', 'checked': True},
                    {'text': 'Index timestamp_utc on all event tables to prevent table scans', 'checked': True},
                    {'text': 'Enforce foreign key constraints between users and events', 'checked': True},
                    {'text': 'Run automated daily cohort verification queries', 'checked': True},
                ],
                'kinetic_sub': 'Duplicate session events and unindexed timestamps corrupt retention cohorts.',
                'voiceover': 'Bug two: Failing to debounce frontend clicks, creating duplicate sessions. Bug three: Querying unindexed timestamps, which causes analytical queries to time out under scale. Always add composite indexes.',
                'cta': 'Clean indexing speeds queries 100x'
            },
            {
                'tag': 'REPOST & AUDIT',
                'headline': 'AUDIT YOUR TELEMETRY TIMESTAMPS 🛠️',
                'subtitle': 'Download the 3-step retention bug diagnostic query',
                'window_title': 'retention_diagnostic.sql',
                'visual_type': 'metrics',
                'visual_content': [
                    {'title': 'Diagnostic SQL Query', 'value': 'READY TO RUN ✅', 'note': 'Detects timezone drift and duplicate events in 5 seconds'},
                    {'title': 'Audit Checklist', 'value': 'INCLUDED ✅', 'note': 'Standard operating procedure for data engineering teams'},
                    {'title': 'Action', 'value': 'REPOST & SAVE 🔁', 'note': 'Share with engineers maintaining growth pipelines'},
                ],
                'kinetic_sub': 'Repost this and check your telemetry event timestamps today.',
                'voiceover': 'Repost this and check your telemetry event timestamps today. Download the complete retention diagnostic SQL script via the link below.',
                'cta': 'incubrix.com/retention-bugs'
            }
        ]
    }
]
