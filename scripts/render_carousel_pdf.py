import os

def escape_pdf(text):
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

def generate_carousel_pdf(slides, out_path):
    # PDF 1.4 objects:
    # 1: Catalog
    # 2: Pages
    # 3: Font Helvetica
    # 4: Font Helvetica-Bold
    # 5..: Page objects and Content stream objects
    
    num_slides = len(slides)
    page_obj_ids = [5 + 2 * i for i in range(num_slides)]
    
    lines = [
        "%PDF-1.4",
        "%\xe2\xe3\xcf\xd3",
        "1 0 obj",
        "<< /Type /Catalog /Pages 2 0 R >>",
        "endobj",
        "2 0 obj",
        f"<< /Type /Pages /Kids [{' '.join(f'{pid} 0 R' for pid in page_obj_ids)}] /Count {num_slides} >>",
        "endobj",
        "3 0 obj",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        "endobj",
        "4 0 obj",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
        "endobj"
    ]
    
    for i, slide in enumerate(slides):
        p_obj_id = 5 + 2 * i
        c_obj_id = p_obj_id + 1
        
        badge = slide.get('badge', '')
        title1 = slide.get('title1', '')
        title2 = slide.get('title2', '')
        subtitle1 = slide.get('sub1', '')
        subtitle2 = slide.get('sub2', '')
        card_title = slide.get('card_title', '')
        points = slide.get('points', [])
        page_num_str = f"[{i+1}/{num_slides}]"
        
        # Build stream
        stream = []
        # Background fill (Dark slate #0B0F19 -> 0.043, 0.059, 0.098)
        stream.append("0.043 0.059 0.098 rg 0 0 1080 1350 re f")
        # Top gradient/accent border (Emerald green: 0.063, 0.725, 0.505)
        stream.append("0.063 0.725 0.505 rg 0 1342 1080 8 re f")
        
        # Badge box
        b_w = len(badge) * 11 + 30
        stream.append(f"0.05 0.14 0.12 rg 80 1240 {b_w} 38 re f")
        stream.append(f"0.063 0.725 0.505 RG 1.5 w 80 1240 {b_w} 38 re s")
        stream.append(f"0.063 0.725 0.505 rg\nBT /F2 15 Tf 95 1252 Td ({escape_pdf(badge)}) Tj ET")
        
        # Title
        stream.append(f"1 1 1 rg\nBT /F2 42 Tf 80 1170 Td ({escape_pdf(title1)}) Tj ET")
        if title2:
            stream.append(f"BT /F2 42 Tf 80 1118 Td ({escape_pdf(title2)}) Tj ET")
        
        # Subtitle
        sub_y = 1056 if title2 else 1108
        if subtitle1:
            stream.append(f"0.65 0.72 0.82 rg\nBT /F1 22 Tf 80 {sub_y} Td ({escape_pdf(subtitle1)}) Tj ET")
        if subtitle2:
            stream.append(f"BT /F1 22 Tf 80 {sub_y - 32} Td ({escape_pdf(subtitle2)}) Tj ET")
        
        # Central card box
        card_h = 420
        card_y = 420
        stream.append(f"0.08 0.11 0.18 rg 80 {card_y} 920 {card_h} re f")
        stream.append(f"0.18 0.24 0.35 RG 1 w 80 {card_y} 920 {card_h} re s")
        stream.append(f"0.063 0.725 0.505 rg 80 {card_y} 6 {card_h} re f")
        
        if card_title:
            stream.append(f"0.063 0.725 0.505 rg\nBT /F2 22 Tf 115 {card_y + card_h - 45} Td ({escape_pdf(card_title)}) Tj ET")
            
        py = card_y + card_h - 90
        for pt in points:
            stream.append(f"0.85 0.89 0.94 rg\nBT /F1 18 Tf 115 {py} Td ({escape_pdf(pt)}) Tj ET")
            py -= 42
            
        # Footer
        stream.append("0.15 0.20 0.30 RG 1 w 80 80 920 0 re s")
        stream.append("0.45 0.52 0.62 rg\nBT /F1 16 Tf 80 50 Td (IncuBrix Growth Engineering: 2027 Playbook) Tj ET")
        stream.append(f"0.063 0.725 0.505 rg\nBT /F2 16 Tf 880 50 Td (Swipe -> {escape_pdf(page_num_str)}) Tj ET")
        
        stream_content = "\n".join(stream)
        stream_bytes = stream_content.encode('latin1')
        
        lines.append(f"{p_obj_id} 0 obj")
        lines.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 1080 1350] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {c_obj_id} 0 R >>")
        lines.append("endobj")
        
        lines.append(f"{c_obj_id} 0 obj")
        lines.append(f"<< /Length {len(stream_bytes)} >>")
        lines.append("stream")
        lines.append(stream_content)
        lines.append("endstream")
        lines.append("endobj")

    # Generate xref table
    # Simple reconstruction
    header = lines[0] + "\n" + lines[1] + "\n"
    body_parts = lines[2:]
    
    # We can write directly and calculate offsets
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'wb') as f:
        offsets = {}
        pos = 0
        
        def write_str(s):
            nonlocal pos
            b = s.encode('latin1') + b'\n'
            f.write(b)
            pos += len(b)
            
        write_str(lines[0])
        write_str(lines[1])
        
        idx = 2
        while idx < len(lines):
            line = lines[idx]
            if " 0 obj" in line:
                obj_id = int(line.split()[0])
                offsets[obj_id] = pos
            write_str(line)
            idx += 1
            
        xref_pos = pos
        write_str("xref")
        max_id = max(offsets.keys())
        write_str(f"0 {max_id + 1}")
        write_str("0000000000 65535 f ")
        for i in range(1, max_id + 1):
            if i in offsets:
                write_str(f"{offsets[i]:010d} 00000 n ")
            else:
                write_str("0000000000 65535 f ")
                
        write_str("trailer")
        write_str(f"<< /Size {max_id + 1} /Root 1 0 R >>")
        write_str("startxref")
        write_str(str(xref_pos))
        write_str("%%EOF")
        
    print(f"Rendered vector PDF: {out_path} ({os.path.getsize(out_path)} bytes, {num_slides} pages)")

slides_ast_bp_28 = [
    {
        'badge': 'ANNUAL STRATEGIC BLUEPRINT',
        'title1': 'The 2027 Growth Engineering',
        'title2': 'Playbook',
        'sub1': 'The old growth hacking era of cheap vanity tricks is dead.',
        'sub2': 'Here are the 7 architectural shifts defining modern B2B SaaS growth.',
        'card_title': '7 ARCHITECTURAL SHIFTS FOR SCALING B2B SAAS',
        'points': [
            '  - Shift 1: Telemetry before acquisition ad spend',
            '  - Shift 2: Evidence-backed claims over marketing superlatives',
            '  - Shift 3: Edge Pydantic schema validation at API gateway',
            '  - Shift 4: Idempotent SHA-256 duplicate detection',
            '  - Shift 5: Granular UTM parameters mapped to CRM pipeline',
            '  - Shift 6: Multi-format repurposing (1 source to 12 platform assets)',
            '  - Shift 7: Strict human-in-the-loop editorial readiness gates'
        ]
    },
    {
        'badge': 'PRINCIPLE 01: INSTRUMENTATION FIRST',
        'title1': 'Telemetry Before Spend',
        'title2': '',
        'sub1': 'Never allocate paid budget to an uninstrumented onboarding funnel.',
        'sub2': '',
        'card_title': 'CORE ONBOARDING TELEMETRY CHECKPOINTS:',
        'points': [
            '  - If Time-to-Value exceeds 15 minutes, 60% of new signups never return',
            '  - Measure exact latency between signup commit and first core milestone',
            '  - Identify step-level friction across the first 72-hour onboarding window',
            '  - Ad spend into high-friction onboarding simply accelerates burn rate',
            '  - Rule: Stabilize cohort retention before expanding paid acquisition'
        ]
    },
    {
        'badge': 'PRINCIPLE 02: VERIFIABLE SUBSTANCE',
        'title1': 'Evidence Over Hype',
        'title2': '',
        'sub1': 'Technical buyers (CTOs, engineers) reject marketing superlatives.',
        'sub2': '',
        'card_title': 'HOW TO COMMUNICATE WITH PRACTITIONERS:',
        'points': [
            '  - Eliminate empty phrases: "revolutionary AI" or "10x scale overnight"',
            '  - Share verifiable system architecture diagrams and latency benchmarks',
            '  - Bind every marketing assertion to an exact whitepaper or release note',
            '  - Discuss engineering trade-offs openly to establish authentic authority',
            '  - High-intent enterprise buyers evaluate architecture before requesting demos'
        ]
    },
    {
        'badge': 'PRINCIPLE 03: EDGE DATA HYGIENE',
        'title1': 'Edge Schema Validation',
        'title2': '',
        'sub1': 'Stop letting arbitrary client DOM events pollute your analytics warehouse.',
        'sub2': '',
        'card_title': 'API GATEWAY VALIDATION ARCHITECTURE:',
        'points': [
            '  - Enforce strict typing at the API edge using Pydantic v2 schemas',
            '  - Reject malformed or unindexed event payloads with HTTP 422',
            '  - Mandate ISO-8601 UTC timestamps to prevent timezone cohort drift',
            '  - Save data engineers 15+ hours weekly in manual warehouse scrubbing',
            '  - Pristine event data guarantees trustworthy executive cohort metrics'
        ]
    },
    {
        'badge': 'PRINCIPLE 04: ZERO DUPLICATE RECORDING',
        'title1': 'Idempotent Ingestion',
        'title2': '',
        'sub1': 'Mobile connection retries silently inflate conversions without deduplication.',
        'sub2': '',
        'card_title': 'CRYPTOGRAPHIC FINGERPRINT ENGINE:',
        'points': [
            '  - Normalize platform + format + hook text into standardized string',
            '  - Compute deterministic 64-character SHA-256 cryptographic hash',
            '  - Enforce UNIQUE(content_fingerprint) index at database schema level',
            '  - Duplicate insertion attempts trigger clean rejection logs',
            '  - Zero duplicate social posts and zero double-counted revenue events'
        ]
    },
    {
        'badge': 'PRINCIPLE 05: ATTRIBUTION LOOPS',
        'title1': 'Granular UTM Attribution',
        'title2': '',
        'sub1': 'Move beyond vanity impressions to closed-won CRM pipeline contribution.',
        'sub2': '',
        'card_title': '3-STAGE ATTRIBUTION ARCHITECTURE:',
        'points': [
            '  - Stage 1: Attach unique utm_content asset ID to every social link',
            '  - Stage 2: Funnel social discovery into technical mid-funnel blueprints',
            '  - Stage 3: Pass campaign parameters directly into CRM opportunity fields',
            '  - Track exact pipeline and revenue generated per individual content asset',
            '  - Prove marketing ROI to leadership with verifiable deal attribution'
        ]
    },
    {
        'badge': 'PRINCIPLES 06 & 07: SCALE & GOVERNANCE',
        'title1': 'Scale & Editorial Governance',
        'title2': '',
        'sub1': 'Combine high-velocity repurposing with strict human editorial control.',
        'sub2': '',
        'card_title': 'THE 1-TO-12 REPURPOSING MATRIX & READINESS GATE:',
        'points': [
            '  - Transform 1 engineering document into 12 native multi-platform assets',
            '  - Enforce 8-point readiness gate: hook, copy, tags, CTA, URL, file, source, slot',
            '  - Never mark an asset Ready while it remains text-only or unverified',
            '  - Require human operator approval before public social dispatch',
            '  - Automated content operations with 100% brand safety and compliance'
        ]
    },
    {
        'badge': 'PUTTING IT INTO PRODUCTION',
        'title1': 'Action Plan for Monday',
        'title2': '',
        'sub1': 'Three operational priorities to implement with your team next week.',
        'sub2': '',
        'card_title': 'MONDAY MORNING CHECKLIST:',
        'points': [
            '  - [x] Audit onboarding drop-offs across your first 72-hour user window',
            '  - [x] Standardize event naming schemas between engineering and marketing',
            '  - [x] Deploy the 23-column content calendar export for clean operations',
            '  - Save this carousel for your upcoming quarterly architecture review',
            '  - Download the complete 2027 Growth Engineering Playbook PDF via link'
        ]
    }
]

if __name__ == '__main__':
    out_pdf = os.path.join('outputs', 'final', 'carousels', 'ast_bp_28_li_caro.pdf')
    generate_carousel_pdf(slides_ast_bp_28, out_pdf)
