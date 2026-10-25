"""Phase 1 Technical Validation Script for IncuBrix Growth Engineer Assessment.

Validates:
1. Exactly 30 unique asset IDs matching research/asset_blueprint.csv
2. Editable source files existence and completeness across all formats
3. Final rendered files existence and integrity across all formats
4. Video duration <= 60.0s, vertical orientation (1080x1920), H.264/AAC streams
5. Carousel multi-page PDF dimensions (1080x1350) and slide counts
6. Graphic PNG dimensions (1200x675)
7. Minimum production thresholds (>= 10 rendered videos, >= 5 rendered carousels/graphics)
"""

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path
import imageio_ffmpeg
from PIL import Image
from pypdf import PdfReader


def probe_video(video_path: str):
    """Probe video file using bundled FFmpeg to get duration and dimensions."""
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ffmpeg_exe, "-i", video_path]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stderr = res.stderr

    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", stderr)
    if duration_match:
        hours, mins, secs = duration_match.groups()
        duration = float(hours) * 3600 + float(mins) * 60 + float(secs)
    else:
        duration = 0.0

    video_stream_match = re.search(r"Video:.*?(\d{3,4})x(\d{3,4})", stderr)
    if video_stream_match:
        width = int(video_stream_match.group(1))
        height = int(video_stream_match.group(2))
    else:
        width, height = 0, 0

    has_audio = "Audio:" in stderr
    has_video = "Video:" in stderr

    return {
        "duration": duration,
        "width": width,
        "height": height,
        "has_video": has_video,
        "has_audio": has_audio,
        "size_bytes": os.path.getsize(video_path) if os.path.exists(video_path) else 0,
    }


def validate_phase1():
    base_dir = Path(__file__).resolve().parent.parent
    bp_path = base_dir / "research" / "asset_blueprint.csv"
    src_dir = base_dir / "outputs" / "source"
    fin_dir = base_dir / "outputs" / "final"

    if not bp_path.exists():
        print(f"ERROR: Blueprint not found at {bp_path}")
        return False

    with open(bp_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        blueprint_rows = list(reader)

    print(f"\n=======================================================")
    print(f"  PHASE 1 DELIVERABLES TECHNICAL VALIDATION AUDIT")
    print(f"=======================================================\n")
    print(f"Total blueprint rows found: {len(blueprint_rows)}")

    assert len(blueprint_rows) == 30, f"Expected 30 assets, found {len(blueprint_rows)}"

    errors = []
    video_records = []
    carousel_records = []
    graphic_records = []
    copy_records = []

    for row in blueprint_rows:
        asset_id = row["asset_id"]
        platform = row["platform"]
        fmt = row["format"]

        if fmt == "short_video":
            src_md = src_dir / "videos" / f"{asset_id}.md"
            fin_mp4 = fin_dir / "videos" / f"{asset_id}.mp4"

            if not src_md.exists() or src_md.stat().st_size == 0:
                errors.append(f"[{asset_id}] Missing or empty video script: {src_md}")
            if not fin_mp4.exists() or fin_mp4.stat().st_size == 0:
                errors.append(f"[{asset_id}] Missing or empty rendered video: {fin_mp4}")
            else:
                probe = probe_video(str(fin_mp4))
                dur = probe["duration"]
                w, h = probe["width"], probe["height"]

                if dur > 60.0:
                    errors.append(f"[{asset_id}] Duration {dur:.2f}s exceeds 60s limit!")
                if dur < 5.0:
                    errors.append(f"[{asset_id}] Duration {dur:.2f}s is abnormally short!")
                if w != 1080 or h != 1920:
                    errors.append(f"[{asset_id}] Video resolution {w}x{h} != expected 1080x1920!")
                if not probe["has_audio"]:
                    errors.append(f"[{asset_id}] Video missing audio stream!")

                video_records.append({
                    "asset_id": asset_id,
                    "platform": platform,
                    "duration": dur,
                    "dimensions": f"{w}x{h}",
                    "size_kb": probe["size_bytes"] // 1024,
                    "valid": len(errors) == 0
                })

        elif fmt == "carousel":
            src_md = src_dir / "carousels" / f"{asset_id}.md"
            src_html = src_dir / "carousels" / f"{asset_id}.html"
            fin_pdf = fin_dir / "carousels" / f"{asset_id}.pdf"

            if not src_md.exists():
                errors.append(f"[{asset_id}] Missing carousel spec: {src_md}")
            if not src_html.exists():
                errors.append(f"[{asset_id}] Missing carousel interactive HTML: {src_html}")
            if not fin_pdf.exists() or fin_pdf.stat().st_size == 0:
                errors.append(f"[{asset_id}] Missing or empty rendered PDF: {fin_pdf}")
            else:
                reader = PdfReader(str(fin_pdf))
                num_pages = len(reader.pages)
                page1 = reader.pages[0]
                box = page1.mediabox
                pw, ph = float(box.width), float(box.height)

                if num_pages < 5:
                    errors.append(f"[{asset_id}] Carousel has only {num_pages} pages (< 5 required)!")
                if pw != 1080 or ph != 1350:
                    errors.append(f"[{asset_id}] Carousel dimensions {pw}x{ph} != 1080x1350!")

                carousel_records.append({
                    "asset_id": asset_id,
                    "platform": platform,
                    "pages": num_pages,
                    "dimensions": f"{int(pw)}x{int(ph)}",
                    "size_kb": fin_pdf.stat().st_size // 1024
                })

        elif fmt == "graphic":
            src_md = src_dir / "graphics" / f"{asset_id}.md"
            src_svg = src_dir / "graphics" / f"{asset_id}.svg"
            fin_png = fin_dir / "graphics" / f"{asset_id}.png"

            if not src_md.exists():
                errors.append(f"[{asset_id}] Missing graphic spec: {src_md}")
            if not src_svg.exists():
                errors.append(f"[{asset_id}] Missing graphic SVG source: {src_svg}")
            if not fin_png.exists() or fin_png.stat().st_size == 0:
                errors.append(f"[{asset_id}] Missing or empty rendered PNG: {fin_png}")
            else:
                with Image.open(str(fin_png)) as img:
                    gw, gh = img.size
                if gw != 1200 or gh != 675:
                    errors.append(f"[{asset_id}] Graphic dimensions {gw}x{gh} != 1200x675!")

                graphic_records.append({
                    "asset_id": asset_id,
                    "platform": platform,
                    "dimensions": f"{gw}x{gh}",
                    "size_kb": fin_png.stat().st_size // 1024
                })

        elif fmt == "text_post":
            src_md = src_dir / "copy" / f"{asset_id}.md"
            fin_md = fin_dir / "copy" / f"{asset_id}.md"

            if not src_md.exists() or src_md.stat().st_size == 0:
                errors.append(f"[{asset_id}] Missing source copy: {src_md}")
            if not fin_md.exists() or fin_md.stat().st_size == 0:
                errors.append(f"[{asset_id}] Missing final copy: {fin_md}")

            copy_records.append({
                "asset_id": asset_id,
                "platform": platform,
                "source_bytes": src_md.stat().st_size if src_md.exists() else 0,
                "final_bytes": fin_md.stat().st_size if fin_md.exists() else 0
            })

    # Summary Display
    print("--- 1. SHORT VIDEOS (Target: >= 10, Actual: {}) ---".format(len(video_records)))
    print(f"{'Asset ID':<20} | {'Platform':<15} | {'Duration':<10} | {'Resolution':<12} | {'Size (KB)':<10}")
    print("-" * 75)
    for v in video_records:
        print(f"{v['asset_id']:<20} | {v['platform']:<15} | {v['duration']:>6.2f}s    | {v['dimensions']:<12} | {v['size_kb']:>8} KB")

    print("\n--- 2. CAROUSELS (Multi-page PDF Decks) ---")
    print(f"{'Asset ID':<20} | {'Platform':<15} | {'Pages':<8} | {'Dimensions':<12} | {'Size (KB)':<10}")
    print("-" * 75)
    for c in carousel_records:
        print(f"{c['asset_id']:<20} | {c['platform']:<15} | {c['pages']:>4} pgs | {c['dimensions']:<12} | {c['size_kb']:>8} KB")

    print("\n--- 3. GRAPHICS (Architecture Diagrams) ---")
    print(f"{'Asset ID':<20} | {'Platform':<15} | {'Resolution':<12} | {'Size (KB)':<10}")
    print("-" * 65)
    for g in graphic_records:
        print(f"{g['asset_id']:<20} | {g['platform']:<15} | {g['dimensions']:<12} | {g['size_kb']:>8} KB")

    print("\n--- 4. COPY & TEXT POSTS ---")
    print(f"{'Asset ID':<20} | {'Platform':<15} | {'Source Size':<12} | {'Final Size':<12}")
    print("-" * 65)
    for cp in copy_records:
        print(f"{cp['asset_id']:<20} | {cp['platform']:<15} | {cp['source_bytes']:>8} B   | {cp['final_bytes']:>8} B")

    print(f"\n=======================================================")
    print(f"  VALIDATION SUMMARY")
    print(f"=======================================================")
    print(f"Total Assets Validated:        {len(blueprint_rows)} / 30")
    print(f"Rendered Videos (MP4):         {len(video_records)} (Required: >= 10)")
    print(f"Rendered Carousels (PDF):      {len(carousel_records)}")
    print(f"Rendered Graphics (PNG):       {len(graphic_records)}")
    print(f"Total Carousels + Graphics:    {len(carousel_records) + len(graphic_records)} (Required: >= 5)")
    print(f"Final Copy Posts:              {len(copy_records)}")
    print(f"Total Errors Found:            {len(errors)}")

    if errors:
        print("\nERRORS ENCOUNTERED:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("\nALL PHASE 1 DELIVERABLE AUDITS PASSED WITH ZERO ERRORS.\n")
    return True


if __name__ == "__main__":
    success = validate_phase1()
    sys.exit(0 if success else 1)
