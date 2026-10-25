import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from scripts.video_engine import render_video_asset

spec_ast_bp_03 = {
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
}

out_path = os.path.join('outputs', 'final', 'videos', 'ast_bp_03_yt_vid.mp4')
dur = render_video_asset(spec_ast_bp_03, out_path)
print(f"SUCCESS: Rendered ast_bp_03_yt_vid.mp4 with duration {dur:.2f}s")
