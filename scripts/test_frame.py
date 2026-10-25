import os
from PIL import Image, ImageDraw, ImageFont

def get_font(name, size):
    font_path = os.path.join(r'C:\Windows\Fonts', name)
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def draw_test_frame():
    W, H = 1080, 1920
    im = Image.new('RGB', (W, H), color='#0B0F19')
    draw = ImageDraw.Draw(im)

    # Ambient glow
    for r in range(400, 0, -20):
        alpha = int(25 * (1 - r / 400))
        # subtle circular glow top-right
        draw.ellipse([800 - r, 300 - r, 800 + r, 300 + r], fill=(16, 185, 129, alpha) if alpha > 0 else None)

    # Top brand bar
    font_mono = get_font('consola.ttf', 24)
    font_bold = get_font('segoeuib.ttf', 52)
    font_sub = get_font('segoeuib.ttf', 32)
    font_body = get_font('segoeui.ttf', 28)
    font_card_mono = get_font('consola.ttf', 28)

    # Top Header
    draw.rounded_rectangle([80, 100, 1000, 180], radius=16, fill='#141C2E', outline='#1E293B', width=2)
    draw.ellipse([110, 133, 126, 149], fill='#10B981') # green dot
    draw.text((145, 125), "INCUBRIX GROWTH ENGINEERING", font=font_mono, fill='#38BDF8')
    draw.text((780, 125), "YOUTUBE SHORTS", font=font_mono, fill='#94A3B8')

    # Content Pillar Badge
    draw.rounded_rectangle([80, 220, 480, 275], radius=12, fill='#1E293B')
    draw.text((105, 235), "[GROWTH ARCHITECTURE]", font=font_mono, fill='#F59E0B')

    # Headline
    headline = "STOP TRACKING EVERY CLICK 🛑"
    draw.text((80, 310), headline, font=font_bold, fill='#FFFFFF')
    draw.text((80, 380), "Why product analytics pipelines crash under scale", font=font_sub, fill='#94A3B8')

    # Visual Code Card Box
    card_top = 460
    card_h = 800
    draw.rounded_rectangle([80, card_top, 1000, card_top + card_h], radius=24, fill='#111827', outline='#374151', width=3)

    # macOS window dots
    draw.ellipse([115, card_top + 25, 131, card_top + 41], fill='#EF4444')
    draw.ellipse([145, card_top + 25, 161, card_top + 41], fill='#F59E0B')
    draw.ellipse([175, card_top + 25, 191, card_top + 41], fill='#10B981')
    draw.text((220, card_top + 20), "telemetry_schema.json", font=font_mono, fill='#6B7280')

    # Code Content
    code_lines = [
        ('{\n', '#9CA3AF'),
        ('  "user_id": "usr_94b810ac",', '#60A5FA'),
        ('  "event_name": "onboarding_completed",', '#34D399'),
        ('  "timestamp_utc": "2026-10-25T15:45:00Z",', '#FBBF24'),
        ('  "session_id": "ses_3301aef",', '#60A5FA'),
        ('  "properties": {', '#9CA3AF'),
        ('    "time_to_first_value_sec": 420,', '#F472B6'),
        ('    "activation_milestones": 3,', '#F472B6'),
        ('    "verification_signature": "sha256_7f1c..."', '#38BDF8'),
        ('  }', '#9CA3AF'),
        ('}', '#9CA3AF'),
    ]

    y_code = card_top + 90
    for line, color in code_lines:
        draw.text((120, y_code), line, font=font_card_mono, fill=color)
        y_code += 48

    # Subtitle / Kinetic Caption Box
    sub_top = 1380
    draw.rounded_rectangle([80, sub_top, 1000, sub_top + 180], radius=20, fill='#1E293B', outline='#38BDF8', width=2)
    draw.text((110, sub_top + 30), "KINETIC SUBTITLES", font=font_mono, fill='#38BDF8')
    draw.text((110, sub_top + 75), "\"Top growth teams enforce a strict 5-event activation schema.\"", font=font_sub, fill='#FDE047')

    # Footer CTA
    draw.text((80, 1650), "Link in description: incubrix.com/schemas", font=font_mono, fill='#38BDF8')
    draw.text((80, 1700), "Subscribe for weekly Growth Engineering breakdowns", font=font_body, fill='#64748B')

    # Progress bar along bottom
    draw.rectangle([0, 1900, 1080, 1920], fill='#1E293B')
    draw.rectangle([0, 1900, 480, 1920], fill='#38BDF8')

    os.makedirs('scratch', exist_ok=True)
    out_path = 'scratch/test_frame.png'
    im.save(out_path)
    print(f"Test frame saved to {out_path}, size={os.path.getsize(out_path)} bytes")

draw_test_frame()
