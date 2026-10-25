"""Automated test suite verifying Phase 1 content and media production deliverables.

Tests:
1. Asset blueprint integrity (30 unique asset rows, planned status guardrail).
2. Video rendering threshold (>= 10 videos) and technical specs (duration <= 60s, 1080x1920).
3. Carousel rendering specs (multi-page PDF, 1080x1350, >= 5 pages).
4. Graphic rendering specs (PNG, 1200x675).
5. Comprehensive source and final deliverable mapping for all 30 assets.
"""

import csv
import os
import re
import subprocess
from pathlib import Path
import pytest
import imageio_ffmpeg
from PIL import Image
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent.parent
BP_PATH = BASE_DIR / "research" / "asset_blueprint.csv"
SRC_DIR = BASE_DIR / "outputs" / "source"
FIN_DIR = BASE_DIR / "outputs" / "final"


@pytest.fixture(scope="module")
def blueprint_data():
    assert BP_PATH.exists(), f"Blueprint file missing: {BP_PATH}"
    with open(BP_PATH, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def probe_video(video_path: Path):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ffmpeg_exe, "-i", str(video_path)]
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

    return {
        "duration": duration,
        "width": width,
        "height": height,
        "has_audio": "Audio:" in stderr,
        "has_video": "Video:" in stderr,
    }


def test_blueprint_integrity(blueprint_data):
    """Ensure exactly 30 unique asset IDs exist and safety guardrails are preserved."""
    assert len(blueprint_data) == 30
    asset_ids = [r["asset_id"] for r in blueprint_data]
    assert len(set(asset_ids)) == 30, "Duplicate asset IDs detected!"

    # Guardrail: planned assets must not be prematurely marked Ready or Published
    for row in blueprint_data:
        assert row["production_status"] in ["Planned", "Draft", "In Progress"], (
            f"Asset {row['asset_id']} violates readiness guardrail: {row['production_status']}"
        )


def test_rendered_video_deliverables(blueprint_data):
    """Ensure >= 10 short videos are rendered, <= 60s duration, 1080x1920 vertical."""
    video_assets = [r for r in blueprint_data if r["format"] == "short_video"]
    assert len(video_assets) == 13

    rendered_videos = list((FIN_DIR / "videos").glob("*.mp4"))
    assert len(rendered_videos) >= 10, f"Expected >= 10 rendered videos, found {len(rendered_videos)}"
    assert len(rendered_videos) == 13, f"Expected all 13 video assets rendered, found {len(rendered_videos)}"

    for row in video_assets:
        asset_id = row["asset_id"]
        source_file = SRC_DIR / "videos" / f"{asset_id}.md"
        final_file = FIN_DIR / "videos" / f"{asset_id}.mp4"

        assert source_file.exists(), f"Missing video source script for {asset_id}"
        assert source_file.stat().st_size > 100, f"Video script too short for {asset_id}"

        assert final_file.exists(), f"Missing rendered MP4 for {asset_id}"
        assert final_file.stat().st_size > 100_000, f"Rendered video suspiciously small: {final_file}"

        probe = probe_video(final_file)
        assert 5.0 <= probe["duration"] <= 60.0, (
            f"Video {asset_id} duration {probe['duration']:.2f}s violates <= 60s rule!"
        )
        assert probe["width"] == 1080 and probe["height"] == 1920, (
            f"Video {asset_id} resolution {probe['width']}x{probe['height']} != 1080x1920"
        )
        assert probe["has_audio"], f"Video {asset_id} missing audio track"
        assert probe["has_video"], f"Video {asset_id} missing video track"


def test_rendered_carousel_deliverables(blueprint_data):
    """Ensure carousels are multi-page PDFs, 1080x1350, with >= 5 slides."""
    carousel_assets = [r for r in blueprint_data if r["format"] == "carousel"]
    assert len(carousel_assets) == 4

    for row in carousel_assets:
        asset_id = row["asset_id"]
        source_md = SRC_DIR / "carousels" / f"{asset_id}.md"
        source_html = SRC_DIR / "carousels" / f"{asset_id}.html"
        final_pdf = FIN_DIR / "carousels" / f"{asset_id}.pdf"

        assert source_md.exists(), f"Missing carousel markdown spec: {source_md}"
        assert source_html.exists(), f"Missing carousel interactive HTML: {source_html}"
        assert final_pdf.exists(), f"Missing rendered carousel PDF: {final_pdf}"

        reader = PdfReader(str(final_pdf))
        assert len(reader.pages) >= 5, f"Carousel {asset_id} has < 5 pages"

        page = reader.pages[0]
        box = page.mediabox
        assert float(box.width) == 1080 and float(box.height) == 1350, (
            f"Carousel {asset_id} dimensions {box.width}x{box.height} != 1080x1350"
        )


def test_rendered_graphic_deliverables(blueprint_data):
    """Ensure graphics have SVG sources and 1200x675 rendered PNGs."""
    graphic_assets = [r for r in blueprint_data if r["format"] == "graphic"]
    assert len(graphic_assets) == 3

    for row in graphic_assets:
        asset_id = row["asset_id"]
        source_md = SRC_DIR / "graphics" / f"{asset_id}.md"
        source_svg = SRC_DIR / "graphics" / f"{asset_id}.svg"
        final_png = FIN_DIR / "graphics" / f"{asset_id}.png"

        assert source_md.exists(), f"Missing graphic markdown spec: {source_md}"
        assert source_svg.exists(), f"Missing graphic SVG source: {source_svg}"
        assert final_png.exists(), f"Missing rendered graphic PNG: {final_png}"

        with Image.open(str(final_png)) as img:
            assert img.size == (1200, 675), f"Graphic {asset_id} dimensions {img.size} != (1200, 675)"


def test_copy_deliverables(blueprint_data):
    """Ensure all text posts have complete source and final markdown files."""
    copy_assets = [r for r in blueprint_data if r["format"] == "text_post"]
    assert len(copy_assets) == 10

    for row in copy_assets:
        asset_id = row["asset_id"]
        source_file = SRC_DIR / "copy" / f"{asset_id}.md"
        final_file = FIN_DIR / "copy" / f"{asset_id}.md"

        assert source_file.exists(), f"Missing source copy for {asset_id}"
        assert final_file.exists(), f"Missing final copy for {asset_id}"
        assert source_file.stat().st_size > 500, f"Source copy too short for {asset_id}"
        assert final_file.stat().st_size > 500, f"Final copy too short for {asset_id}"


def test_overall_production_thresholds():
    """Verify Phase 1 requirements: >= 10 videos, >= 5 carousels/graphics."""
    video_count = len(list((FIN_DIR / "videos").glob("*.mp4")))
    carousel_count = len(list((FIN_DIR / "carousels").glob("*.pdf")))
    graphic_count = len(list((FIN_DIR / "graphics").glob("*.png")))

    assert video_count >= 10, f"Videos: {video_count} < 10"
    assert (carousel_count + graphic_count) >= 5, f"Carousels + Graphics: {carousel_count + graphic_count} < 5"
    assert (video_count + carousel_count + graphic_count + 10) == 30, "Total final assets count != 30"
