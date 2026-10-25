import os
import sys
import time

sys.path.insert(0, os.path.abspath('.'))

from scripts.video_specs import VIDEO_SPECS
from scripts.video_engine import render_video_asset, get_audio_duration

def main():
    print("=" * 60)
    print("INCUBRIX VIDEO PRODUCTION PIPELINE")
    print(f"Total video assets to process: {len(VIDEO_SPECS)}")
    print("=" * 60)

    out_dir = os.path.join('outputs', 'final', 'videos')
    os.makedirs(out_dir, exist_ok=True)

    results = []

    for idx, spec in enumerate(VIDEO_SPECS, start=1):
        asset_id = spec['asset_id']
        mp4_path = os.path.join(out_dir, f"{asset_id}.mp4")

        print(f"\n[{idx}/{len(VIDEO_SPECS)}] Processing {asset_id}...")
        
        # Check if already rendered and valid
        if os.path.exists(mp4_path) and os.path.getsize(mp4_path) > 100000:
            dur = get_audio_duration(mp4_path)
            if dur <= 60.0:
                print(f"  -> Already exists and valid: {dur:.2f}s ({os.path.getsize(mp4_path)} bytes)")
                results.append((asset_id, dur, os.path.getsize(mp4_path), "EXISTS"))
                continue

        t0 = time.time()
        try:
            dur = render_video_asset(spec, mp4_path)
            elapsed = time.time() - t0
            size = os.path.getsize(mp4_path)
            status = "PASS" if dur <= 60.0 else "FAIL_DURATION"
            print(f"  -> Rendered in {elapsed:.1f}s. Duration: {dur:.2f}s (Size: {size} bytes). Status: {status}")
            results.append((asset_id, dur, size, status))
        except Exception as e:
            print(f"  -> ERROR rendering {asset_id}: {e}")
            results.append((asset_id, 0, 0, f"ERROR: {e}"))

    print("\n" + "=" * 60)
    print("VIDEO PRODUCTION PIPELINE REPORT")
    print("=" * 60)
    print(f"{'Asset ID':<22} | {'Duration (s)':<12} | {'Size (KB)':<12} | {'Status':<10}")
    print("-" * 62)
    for a_id, dur, size, st in results:
        size_kb = f"{size / 1024:.1f}" if size > 0 else "0"
        dur_str = f"{dur:.2f}" if dur > 0 else "N/A"
        print(f"{a_id:<22} | {dur_str:<12} | {size_kb:<12} | {st:<10}")

    success_count = sum(1 for _, dur, _, st in results if st in ("PASS", "EXISTS") and dur <= 60.0)
    print(f"\nFinished: {success_count}/{len(VIDEO_SPECS)} videos rendered successfully (all <= 60 seconds).")

if __name__ == '__main__':
    main()
