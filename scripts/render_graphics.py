import os
from PIL import Image, ImageDraw, ImageFont

def get_font(name, size):
    font_path = os.path.join(r'C:\Windows\Fonts', name)
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def render_graphic_11():
    # 1. Render PNG
    W, H = 1200, 675
    im = Image.new('RGB', (W, H), color='#070A12')
    draw = ImageDraw.Draw(im)

    font_mono = get_font('consola.ttf', 16)
    font_bold = get_font('segoeuib.ttf', 30)
    font_sub = get_font('segoeui.ttf', 16)
    font_card_h = get_font('segoeuib.ttf', 20)
    font_card_b = get_font('segoeui.ttf', 14)
    font_card_bold = get_font('segoeuib.ttf', 14)

    # Header Bar
    draw.rounded_rectangle([50, 30, 1150, 75], radius=10, fill='#141C2E', outline='#1E293B', width=1)
    draw.ellipse([70, 46, 82, 58], fill='#10B981')
    draw.text((95, 42), "INCUBRIX GROWTH TELEMETRY", font=font_mono, fill='#38BDF8')
    draw.text((850, 42), "SAAS RETENTION DYNAMICS", font=font_mono, fill='#94A3B8')

    # Title
    draw.text((50, 95), "Cohort Retention Trajectories: Scalable Engine vs Churn Trap", font=font_bold, fill='#FFFFFF')
    draw.text((50, 140), "Why capital efficiency requires a flattening retention curve before scaling paid customer acquisition spend", font=font_sub, fill='#94A3B8')

    # Left Card: Chart A (Scalable)
    draw.rounded_rectangle([50, 180, 585, 570], radius=16, fill='#0E1626', outline='#059669', width=2)
    # Badge
    draw.rounded_rectangle([75, 205, 340, 240], radius=6, fill='#064E3B')
    draw.text((85, 212), "CHART A: SCALABLE ENGINE", font=font_mono, fill='#34D399')
    draw.text((75, 255), "Curve Flattens at 24% Retention", font=font_card_h, fill='#F9FAFB')
    draw.text((75, 285), "Sustainable Product-Market Fit • Safe to scale paid spend", font=font_card_b, fill='#94A3B8')

    # Chart A axes & curve
    ox, oy = 80, 500
    cw, ch = 470, 180
    draw.line([ox, oy, ox + cw, oy], fill='#374151', width=2) # X axis
    draw.line([ox, oy, ox, oy - ch], fill='#374151', width=2) # Y axis
    draw.text((ox + cw - 50, oy + 8), "Day 30", font=font_mono, fill='#9CA3AF')
    draw.text((ox, oy + 8), "Day 0", font=font_mono, fill='#9CA3AF')
    draw.text((ox - 35, oy - ch), "100%", font=font_mono, fill='#9CA3AF')
    draw.text((ox - 30, oy - 45), "24%", font=font_mono, fill='#34D399')

    # Plateau guide line
    draw.line([ox, oy - 43, ox + cw, oy - 43], fill='#064E3B', width=1)

    # Green curve
    pts_a = [
        (ox, oy - 180),
        (ox + 50, oy - 90),
        (ox + 110, oy - 62),
        (ox + 200, oy - 48),
        (ox + 320, oy - 43),
        (ox + cw, oy - 43)
    ]
    for k in range(len(pts_a) - 1):
        draw.line([pts_a[k], pts_a[k+1]], fill='#10B981', width=4)

    draw.text((ox + 160, oy - 80), "FLATTENING PLATEAU", font=font_mono, fill='#10B981')
    draw.text((ox + 160, oy - 60), "Core retained user habit formed", font=font_card_b, fill='#D1D5DB')

    # Right Card: Chart B (Leaky Bucket)
    draw.rounded_rectangle([615, 180, 1150, 570], radius=16, fill='#0E1626', outline='#DC2626', width=2)
    # Badge
    draw.rounded_rectangle([640, 205, 910, 240], radius=6, fill='#7F1D1D')
    draw.text((650, 212), "CHART B: THE CHURN TRAP", font=font_mono, fill='#F87171')
    draw.text((640, 255), "Curve Decays Continuously to 0%", font=font_card_h, fill='#F9FAFB')
    draw.text((640, 285), "Leaky Bucket • Paid ad dollars burn capital with zero payback", font=font_card_b, fill='#94A3B8')

    # Chart B axes & curve
    ox2, oy2 = 645, 500
    draw.line([ox2, oy2, ox2 + cw, oy2], fill='#374151', width=2)
    draw.line([ox2, oy2, ox2, oy2 - ch], fill='#374151', width=2)
    draw.text((ox2 + cw - 50, oy2 + 8), "Day 30", font=font_mono, fill='#9CA3AF')
    draw.text((ox2, oy2 + 8), "Day 0", font=font_mono, fill='#9CA3AF')
    draw.text((ox2 - 35, oy2 - ch), "100%", font=font_mono, fill='#9CA3AF')
    draw.text((ox2 - 25, oy2 - 10), "2%", font=font_mono, fill='#F87171')

    # Red decaying curve
    pts_b = [
        (ox2, oy2 - 180),
        (ox2 + 50, oy2 - 60),
        (ox2 + 120, oy2 - 32),
        (ox2 + 220, oy2 - 18),
        (ox2 + 340, oy2 - 10),
        (ox2 + cw, oy2 - 5)
    ]
    for k in range(len(pts_b) - 1):
        draw.line([pts_b[k], pts_b[k+1]], fill='#EF4444', width=4)

    draw.text((ox2 + 160, oy2 - 75), "CONTINUOUS DECAY", font=font_mono, fill='#EF4444')
    draw.text((ox2 + 160, oy2 - 55), "Product novelty fades without retention", font=font_card_b, fill='#D1D5DB')

    # Bottom Takeaway Bar
    draw.rounded_rectangle([50, 590, 1150, 645], radius=10, fill='#141C2E', outline='#1E293B', width=1)
    draw.text((70, 608), "GROWTH PRINCIPLE:", font=font_mono, fill='#F59E0B')
    draw.text((250, 608), "Never pump performance ad spend into Chart B. Fix onboarding Time-to-Value first.", font=font_card_bold, fill='#F8FAFC')
    draw.text((940, 608), "incubrix.com/cohorts", font=font_mono, fill='#38BDF8')

    out_png = 'outputs/final/graphics/ast_bp_11_x_graph.png'
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    im.save(out_png)
    print(f"Rendered PNG: {out_png} ({os.path.getsize(out_png)} bytes)")

    # 2. Render SVG
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" width="1200" height="675">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070A12"/>
      <stop offset="100%" stop-color="#0A1128"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="675" fill="url(#bgGrad)"/>
  <rect x="50" y="30" width="1100" height="45" rx="10" fill="#141C2E" stroke="#1E293B"/>
  <circle cx="76" cy="52" r="6" fill="#10B981"/>
  <text x="95" y="58" font-family="monospace" font-size="16" fill="#38BDF8">INCUBRIX GROWTH TELEMETRY</text>
  <text x="850" y="58" font-family="monospace" font-size="16" fill="#94A3B8">SAAS RETENTION DYNAMICS</text>
  <text x="50" y="125" font-family="sans-serif" font-weight="bold" font-size="30" fill="#FFFFFF">Cohort Retention Trajectories: Scalable Engine vs Churn Trap</text>
  <text x="50" y="155" font-family="sans-serif" font-size="16" fill="#94A3B8">Why capital efficiency requires a flattening retention curve before scaling paid customer acquisition spend</text>
  
  <!-- Chart A -->
  <rect x="50" y="180" width="535" height="390" rx="16" fill="#0E1626" stroke="#059669" stroke-width="2"/>
  <rect x="75" y="205" width="265" height="35" rx="6" fill="#064E3B"/>
  <text x="85" y="228" font-family="monospace" font-size="14" fill="#34D399">CHART A: SCALABLE ENGINE</text>
  <text x="75" y="275" font-family="sans-serif" font-weight="bold" font-size="20" fill="#F9FAFB">Curve Flattens at 24% Retention</text>
  <path d="M 80 320 Q 130 410 200 440 T 550 457" fill="none" stroke="#10B981" stroke-width="4"/>
  <line x1="80" y1="500" x2="550" y2="500" stroke="#374151" stroke-width="2"/>
  
  <!-- Chart B -->
  <rect x="615" y="180" width="535" height="390" rx="16" fill="#0E1626" stroke="#DC2626" stroke-width="2"/>
  <rect x="640" y="205" width="270" height="35" rx="6" fill="#7F1D1D"/>
  <text x="650" y="228" font-family="monospace" font-size="14" fill="#F87171">CHART B: THE CHURN TRAP</text>
  <text x="640" y="275" font-family="sans-serif" font-weight="bold" font-size="20" fill="#F9FAFB">Curve Decays Continuously to 0%</text>
  <path d="M 645 320 Q 695 440 765 470 T 1115 495" fill="none" stroke="#EF4444" stroke-width="4"/>
  <line x1="645" y1="500" x2="1115" y2="500" stroke="#374151" stroke-width="2"/>

  <!-- Footer -->
  <rect x="50" y="590" width="1100" height="55" rx="10" fill="#141C2E" stroke="#1E293B"/>
  <text x="70" y="625" font-family="monospace" font-size="15" fill="#F59E0B">GROWTH PRINCIPLE:</text>
  <text x="250" y="625" font-family="sans-serif" font-weight="bold" font-size="14" fill="#F8FAFC">Never pump performance ad spend into Chart B. Fix onboarding Time-to-Value first.</text>
  <text x="940" y="625" font-family="monospace" font-size="14" fill="#38BDF8">incubrix.com/cohorts</text>
</svg>'''
    out_svg = 'outputs/source/graphics/ast_bp_11_x_graph.svg'
    os.makedirs(os.path.dirname(out_svg), exist_ok=True)
    with open(out_svg, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Rendered SVG: {out_svg} ({os.path.getsize(out_svg)} bytes)")

def render_graphic_17():
    # 1. Render PNG
    W, H = 1200, 675
    im = Image.new('RGB', (W, H), color='#070A12')
    draw = ImageDraw.Draw(im)

    font_mono = get_font('consola.ttf', 16)
    font_bold = get_font('segoeuib.ttf', 30)
    font_sub = get_font('segoeui.ttf', 16)
    font_card_h = get_font('segoeuib.ttf', 20)
    font_card_b = get_font('segoeui.ttf', 14)
    font_card_bold = get_font('segoeuib.ttf', 14)

    # Header Bar
    draw.rounded_rectangle([50, 30, 1150, 75], radius=10, fill='#141C2E', outline='#1E293B', width=1)
    draw.ellipse([70, 46, 82, 58], fill='#38BDF8')
    draw.text((95, 42), "INCUBRIX ARCHITECTURE TEARDOWN", font=font_mono, fill='#38BDF8')
    draw.text((850, 42), "DATA INTEGRITY & INGESTION", font=font_mono, fill='#94A3B8')

    # Title
    draw.text((50, 95), "Client-Side vs. Server-Side Telemetry Ingestion", font=font_bold, fill='#FFFFFF')
    draw.text((50, 140), "How modern growth engineering architectures eliminate ad blocker interception and duplicate metrics", font=font_sub, fill='#94A3B8')

    # Left Column: Client-Side (Brittle)
    draw.rounded_rectangle([50, 180, 585, 570], radius=16, fill='#0E1626', outline='#EF4444', width=2)
    draw.rounded_rectangle([75, 205, 340, 240], radius=6, fill='#7F1D1D')
    draw.text((85, 212), "CLIENT-SIDE INGESTION", font=font_mono, fill='#F87171')
    draw.text((75, 255), "Brittle Browser DOM Listeners", font=font_card_h, fill='#F9FAFB')
    draw.text((75, 285), "High vulnerability to ad blockers and network drops", font=font_card_b, fill='#94A3B8')

    # Client-side items
    c_items = [
        ('15% - 25% Data Loss', 'Ad blockers silently block client analytics requests', '#EF4444'),
        ('Duplicate Conversions', 'Mobile user retries fire multiple click events', '#EF4444'),
        ('Schema Drift', 'Frontend button refactors break tracking without error', '#EF4444'),
        ('Third-Party Pixel Bloat', 'Heavy JS bundles add 400ms+ page load latency', '#F59E0B')
    ]
    cy = 320
    for title, desc, col in c_items:
        draw.rounded_rectangle([75, cy, 560, cy + 50], radius=8, fill='#141C2E')
        draw.text((90, cy + 8), f"❌ {title}", font=font_card_bold, fill=col)
        draw.text((90, cy + 28), desc, font=font_mono, fill='#9CA3AF')
        cy += 60

    # Right Column: Server-Side (Fidelity)
    draw.rounded_rectangle([615, 180, 1150, 570], radius=16, fill='#0E1626', outline='#10B981', width=2)
    draw.rounded_rectangle([640, 205, 920, 240], radius=6, fill='#064E3B')
    draw.text((650, 212), "SERVER-SIDE VALIDATED", font=font_mono, fill='#34D399')
    draw.text((640, 255), "Edge Gateway & Message Queue", font=font_card_h, fill='#F9FAFB')
    draw.text((640, 285), "100% data fidelity with sub-15ms user-facing response", font=font_card_b, fill='#94A3B8')

    # Server-side items
    s_items = [
        ('100% Data Fidelity', 'Zero ad blocker interception; direct API-to-API dispatch', '#10B981'),
        ('SHA-256 Deduplication', 'Deterministic fingerprinting blocks duplicate retries', '#10B981'),
        ('Type-Safe Pydantic Schemas', 'API gateway validates payloads before warehouse storage', '#10B981'),
        ('Zero User Lag (<15ms)', 'FastAPI background worker decouples analytics from UI', '#38BDF8')
    ]
    sy = 320
    for title, desc, col in s_items:
        draw.rounded_rectangle([640, sy, 1125, sy + 50], radius=8, fill='#141C2E')
        draw.text((655, sy + 8), f"✅ {title}", font=font_card_bold, fill=col)
        draw.text((655, sy + 28), desc, font=font_mono, fill='#9CA3AF')
        sy += 60

    # Bottom Hybrid Takeaway Bar
    draw.rounded_rectangle([50, 590, 1150, 645], radius=10, fill='#141C2E', outline='#1E293B', width=1)
    draw.text((70, 608), "RECOMMENDED ARCHITECTURE:", font=font_mono, fill='#38BDF8')
    draw.text((340, 608), "The Hybrid Model: Browser for UX heatmaps • Server-side for revenue & activation.", font=font_card_bold, fill='#F8FAFC')
    draw.text((940, 608), "incubrix.com/hybrid", font=font_mono, fill='#38BDF8')

    out_png = 'outputs/final/graphics/ast_bp_17_x_graph.png'
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    im.save(out_png)
    print(f"Rendered PNG: {out_png} ({os.path.getsize(out_png)} bytes)")

    # 2. Render SVG
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" width="1200" height="675">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070A12"/>
      <stop offset="100%" stop-color="#0A1128"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="675" fill="url(#bgGrad)"/>
  <rect x="50" y="30" width="1100" height="45" rx="10" fill="#141C2E" stroke="#1E293B"/>
  <circle cx="76" cy="52" r="6" fill="#38BDF8"/>
  <text x="95" y="58" font-family="monospace" font-size="16" fill="#38BDF8">INCUBRIX ARCHITECTURE TEARDOWN</text>
  <text x="850" y="58" font-family="monospace" font-size="16" fill="#94A3B8">DATA INTEGRITY &amp; INGESTION</text>
  <text x="50" y="125" font-family="sans-serif" font-weight="bold" font-size="30" fill="#FFFFFF">Client-Side vs. Server-Side Telemetry Ingestion</text>
  <text x="50" y="155" font-family="sans-serif" font-size="16" fill="#94A3B8">How modern growth engineering architectures eliminate ad blocker interception and duplicate metrics</text>
  
  <!-- Left Column: Client-Side -->
  <rect x="50" y="180" width="535" height="390" rx="16" fill="#0E1626" stroke="#EF4444" stroke-width="2"/>
  <rect x="75" y="205" width="265" height="35" rx="6" fill="#7F1D1D"/>
  <text x="85" y="228" font-family="monospace" font-size="14" fill="#F87171">CLIENT-SIDE INGESTION</text>
  <text x="75" y="275" font-family="sans-serif" font-weight="bold" font-size="20" fill="#F9FAFB">Brittle Browser DOM Listeners</text>
  <text x="75" y="300" font-family="sans-serif" font-size="14" fill="#94A3B8">15-25% Data Loss via Ad Blockers &amp; Network Retries</text>
  
  <!-- Right Column: Server-Side -->
  <rect x="615" y="180" width="535" height="390" rx="16" fill="#0E1626" stroke="#10B981" stroke-width="2"/>
  <rect x="640" y="205" width="280" height="35" rx="6" fill="#064E3B"/>
  <text x="650" y="228" font-family="monospace" font-size="14" fill="#34D399">SERVER-SIDE VALIDATED</text>
  <text x="640" y="275" font-family="sans-serif" font-weight="bold" font-size="20" fill="#F9FAFB">Edge Gateway &amp; Message Queue</text>
  <text x="640" y="300" font-family="sans-serif" font-size="14" fill="#94A3B8">100% Data Fidelity with Sub-15ms Response Time</text>

  <!-- Footer -->
  <rect x="50" y="590" width="1100" height="55" rx="10" fill="#141C2E" stroke="#1E293B"/>
  <text x="70" y="625" font-family="monospace" font-size="14" fill="#38BDF8">RECOMMENDED ARCHITECTURE:</text>
  <text x="340" y="625" font-family="sans-serif" font-weight="bold" font-size="14" fill="#F8FAFC">The Hybrid Model: Browser for UX heatmaps • Server-side for revenue &amp; activation.</text>
  <text x="940" y="625" font-family="monospace" font-size="14" fill="#38BDF8">incubrix.com/hybrid</text>
</svg>'''
    out_svg = 'outputs/source/graphics/ast_bp_17_x_graph.svg'
    os.makedirs(os.path.dirname(out_svg), exist_ok=True)
    with open(out_svg, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Rendered SVG: {out_svg} ({os.path.getsize(out_svg)} bytes)")

if __name__ == '__main__':
    render_graphic_11()
    render_graphic_17()
