import asyncio
import os
import shutil
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont
import edge_tts
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def get_font(name, size):
    font_path = os.path.join(r'C:\Windows\Fonts', name)
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def render_scene_frame(asset_id, platform, pillar, scene, scene_idx, total_scenes, out_png_path):
    W, H = 1080, 1920
    im = Image.new('RGB', (W, H), color='#0B0F19')
    draw = ImageDraw.Draw(im)

    # Ambient gradient corner glow
    glow_color = (56, 189, 248) if scene.get('type') == 'code' else (16, 185, 129)
    for r in range(350, 0, -25):
        alpha = int(18 * (1 - r / 350))
        draw.ellipse([850 - r, 280 - r, 850 + r, 280 + r], fill=glow_color + (alpha,) if alpha > 0 else None)

    font_mono = get_font('consola.ttf', 24)
    font_mono_card = get_font('consola.ttf', 26)
    font_bold = get_font('segoeuib.ttf', 50)
    font_h2 = get_font('segoeuib.ttf', 32)
    font_body = get_font('segoeui.ttf', 28)
    font_body_bold = get_font('segoeuib.ttf', 28)

    # 1. Header Bar
    draw.rounded_rectangle([80, 100, 1000, 180], radius=16, fill='#141C2E', outline='#1E293B', width=2)
    draw.ellipse([110, 133, 126, 149], fill='#10B981')
    draw.text((145, 125), "INCUBRIX GROWTH ENGINEERING", font=font_mono, fill='#38BDF8')
    plat_text = platform.upper()[:15]
    draw.text((780, 125), plat_text, font=font_mono, fill='#94A3B8')

    # 2. Pillar & Scene Tag Badge
    badge_text = f"[{pillar.upper()}]"
    draw.rounded_rectangle([80, 215, 80 + len(badge_text)*18, 270], radius=12, fill='#1E293B')
    draw.text((105, 230), badge_text, font=font_mono, fill='#F59E0B')

    scene_tag = f"SCENE {scene_idx}/{total_scenes}: {scene.get('tag', 'INSIGHT')}"
    draw.text((560, 230), scene_tag, font=font_mono, fill='#64748B')

    # 3. Headline & Subtitle
    headline = scene.get('headline', '')
    draw.text((80, 305), headline, font=font_bold, fill='#FFFFFF')
    subtitle = scene.get('subtitle', '')
    if subtitle:
        draw.text((80, 375), subtitle, font=font_h2, fill='#94A3B8')

    # 4. Center Visual Card (Y: 450 to 1340)
    card_top = 450
    card_h = 880
    draw.rounded_rectangle([80, card_top, 1000, card_top + card_h], radius=24, fill='#111827', outline='#374151', width=3)

    v_type = scene.get('visual_type', 'metrics')
    v_content = scene.get('visual_content', [])

    # Card Window Header
    draw.ellipse([115, card_top + 25, 131, card_top + 41], fill='#EF4444')
    draw.ellipse([145, card_top + 25, 161, card_top + 41], fill='#F59E0B')
    draw.ellipse([175, card_top + 25, 191, card_top + 41], fill='#10B981')
    window_title = scene.get('window_title', 'telemetry_system_view')
    draw.text((220, card_top + 20), window_title, font=font_mono, fill='#9CA3AF')

    y_pos = card_top + 80

    if v_type == 'code':
        for line, col in v_content:
            draw.text((120, y_pos), line, font=font_mono_card, fill=col)
            y_pos += 46
    elif v_type == 'diagram':
        # Flowchart boxes
        for item in v_content:
            box_label = item.get('label', '')
            box_sub = item.get('sub', '')
            box_badge = item.get('badge', '')
            is_active = item.get('active', False)
            bg = '#1F2937' if not is_active else '#1E3A8A'
            border = '#374151' if not is_active else '#38BDF8'
            
            draw.rounded_rectangle([130, y_pos, 950, y_pos + 105], radius=16, fill=bg, outline=border, width=2)
            draw.text((160, y_pos + 20), box_label, font=font_body_bold, fill='#F9FAFB')
            if box_sub:
                draw.text((160, y_pos + 60), box_sub, font=font_mono, fill='#9CA3AF')
            if box_badge:
                draw.rounded_rectangle([760, y_pos + 22, 920, y_pos + 62], radius=8, fill='#111827')
                draw.text((775, y_pos + 28), box_badge, font=font_mono, fill='#34D399')
            y_pos += 120
            if item != v_content[-1]:
                draw.text((530, y_pos - 12), "↓", font=font_bold, fill='#38BDF8')
                y_pos += 25
    elif v_type == 'metrics' or v_type == 'comparison':
        for item in v_content:
            title = item.get('title', '')
            val = item.get('value', '')
            note = item.get('note', '')
            status_col = item.get('status_col', '#EF4444' if '❌' in val else '#10B981')
            
            draw.rounded_rectangle([120, y_pos, 960, y_pos + 130], radius=16, fill='#1F2937', outline='#374151', width=2)
            draw.text((150, y_pos + 25), title, font=font_body_bold, fill='#F3F4F6')
            draw.text((150, y_pos + 75), note, font=font_mono, fill='#9CA3AF')
            draw.text((760, y_pos + 40), val, font=font_bold, fill=status_col)
            y_pos += 155
    elif v_type == 'checklist':
        for item in v_content:
            text = item.get('text', '')
            checked = item.get('checked', True)
            icon = "✓" if checked else "○"
            icon_col = '#10B981' if checked else '#9CA3AF'
            
            draw.rounded_rectangle([120, y_pos, 960, y_pos + 115], radius=16, fill='#1F2937', outline='#374151', width=2)
            draw.text((155, y_pos + 35), icon, font=font_bold, fill=icon_col)
            draw.text((215, y_pos + 40), text, font=font_body, fill='#F9FAFB')
            y_pos += 135

    # 5. Kinetic Subtitles Box (Y: 1370 to 1600)
    sub_top = 1370
    draw.rounded_rectangle([80, sub_top, 1000, sub_top + 210], radius=20, fill='#1E293B', outline='#38BDF8', width=2)
    draw.text((110, sub_top + 20), "KINETIC SUBTITLES", font=font_mono, fill='#38BDF8')
    
    sub_text = scene.get('kinetic_sub', scene.get('voiceover', ''))
    wrapped_subs = wrap_text(f'"{sub_text}"', font_h2, 850, draw)
    sub_y = sub_top + 65
    for s_line in wrapped_subs[:3]:
        draw.text((110, sub_y), s_line, font=font_h2, fill='#FDE047')
        sub_y += 42

    # 6. Footer (Y: 1640 to 1860)
    draw.text((80, 1630), "INCUBRIX CONTENT ENGINE • VERIFIED TELEMETRY", font=font_mono, fill='#38BDF8')
    cta_text = scene.get('cta', 'Download full blueprint at incubrix.com/blueprint')
    draw.text((80, 1675), cta_text, font=font_body, fill='#94A3B8')

    # Progress Bar along bottom
    prog_pct = (scene_idx) / total_scenes
    draw.rectangle([0, 1890, 1080, 1920], fill='#1E293B')
    draw.rectangle([0, 1890, int(1080 * prog_pct), 1920], fill='#38BDF8')

    im.save(out_png_path, 'PNG')

async def synthesize_speech(text, voice, out_mp3_path):
    comm = edge_tts.Communicate(text, voice, rate="+10%")
    await comm.save(out_mp3_path)

def get_audio_duration(audio_path):
    cmd = [FFMPEG_EXE, '-i', audio_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    import re
    match = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', res.stderr)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 5.0 # fallback

def render_video_asset(asset_spec, output_mp4_path):
    asset_id = asset_spec['asset_id']
    platform = asset_spec['platform']
    pillar = asset_spec['pillar']
    scenes = asset_spec['scenes']
    voice = asset_spec.get('voice', 'en-US-AndrewNeural')

    temp_dir = tempfile.mkdtemp(prefix=f"vid_{asset_id}_")
    try:
        scene_mp4s = []
        total_scenes = len(scenes)

        for i, scene in enumerate(scenes, start=1):
            frame_png = os.path.join(temp_dir, f"frame_{i}.png")
            render_scene_frame(asset_id, platform, pillar, scene, i, total_scenes, frame_png)

            scene_mp3 = os.path.join(temp_dir, f"audio_{i}.mp3")
            asyncio.run(synthesize_speech(scene['voiceover'], voice, scene_mp3))

            dur = get_audio_duration(scene_mp3)

            scene_mp4 = os.path.join(temp_dir, f"scene_{i}.mp4")
            # FFmpeg render static image with audio to mp4
            cmd = [
                FFMPEG_EXE, '-y',
                '-loop', '1',
                '-framerate', '30',
                '-i', frame_png,
                '-i', scene_mp3,
                '-c:v', 'libx264',
                '-tune', 'stillimage',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                scene_mp4
            ]
            res = subprocess.run(cmd, capture_output=True)
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg scene error: {res.stderr.decode('utf-8', errors='ignore')}")
            scene_mp4s.append(scene_mp4)

        # Concatenate scenes using concat demuxer
        concat_txt = os.path.join(temp_dir, "concat.txt")
        with open(concat_txt, 'w', encoding='utf-8') as f:
            for s_mp4 in scene_mp4s:
                # normalize path with forward slashes for ffmpeg concat
                clean_path = s_mp4.replace('\\', '/')
                f.write(f"file '{clean_path}'\n")

        os.makedirs(os.path.dirname(output_mp4_path), exist_ok=True)
        concat_cmd = [
            FFMPEG_EXE, '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_txt,
            '-c', 'copy',
            output_mp4_path
        ]
        res = subprocess.run(concat_cmd, capture_output=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg concat error: {res.stderr.decode('utf-8', errors='ignore')}")

        final_dur = get_audio_duration(output_mp4_path)
        print(f"Rendered {asset_id} -> {output_mp4_path} ({final_dur:.2f}s, {os.path.getsize(output_mp4_path)} bytes)")
        return final_dur
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
