"""Benchmark runner for content engine Phase 5 readiness audit.

Executes and logs real empirical metrics for:
1. Normal run (sample_growth_document.md)
2. Repeat run (same document -> tests duplicate prevention)
3. Refresh run (fresh_creator_growth_study.md -> tests fresh input generation)
4. Failure & recovery run (invalid/short input -> logs failure, recovers with valid input)
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
import sqlite3
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db
from app.models import SourceDocument
from app.repositories import insert_source_document
from app.services.content_engine import run_generation_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("benchmark")


def run_all_benchmarks():
    db_path = Path("data/benchmark_test.db")
    if db_path.exists():
        db_path.unlink()
    
    init_db(db_path)
    from app.database import get_connection
    conn = get_connection(db_path)

    results = {}

    # 1. Normal run
    with open("inputs/sample_growth_document.md", "r", encoding="utf-8") as f:
        normal_text = f.read()
    
    src_normal = SourceDocument(
        id="src_b2b_telemetry_bench",
        title="Building Scalable Growth Engineering Telemetry for B2B SaaS",
        content=normal_text,
        source_type="whitepaper",
        source_url="https://incubrix.com/whitepapers/growth-telemetry",
    )
    insert_source_document(conn, src_normal)

    t0 = time.perf_counter()
    res_normal = run_generation_service(
        source=src_normal,
        base_tracking_url="https://incubrix.com/blueprint",
        campaign="benchmark_normal",
        conn=conn,
        persist=True,
    )
    t_normal_sec = time.perf_counter() - t0

    results["normal_run"] = {
        "input_size_chars": len(normal_text),
        "input_size_words": len(normal_text.split()),
        "items_produced": res_normal.created_count,
        "items_rejected": res_normal.review_required_count,
        "duplicates_removed": res_normal.skipped_duplicate_count,
        "runtime_seconds": round(t_normal_sec, 4),
        "runtime_minutes": round(t_normal_sec / 60.0, 4),
        "runtime_ms": res_normal.run.runtime_ms,
        "direct_cost": "$0.00 (Local deterministic engine)",
        "run_id": res_normal.run.id,
        "status": res_normal.run.status.value,
    }

    # 2. Repeat run (same input)
    t0 = time.perf_counter()
    res_repeat = run_generation_service(
        source=src_normal,
        base_tracking_url="https://incubrix.com/blueprint",
        campaign="benchmark_normal",
        conn=conn,
        persist=True,
    )
    t_repeat_sec = time.perf_counter() - t0

    results["repeat_run"] = {
        "input_size_chars": len(normal_text),
        "input_size_words": len(normal_text.split()),
        "items_produced": res_repeat.created_count,
        "items_rejected": res_repeat.review_required_count,
        "duplicates_removed": res_repeat.skipped_duplicate_count,
        "runtime_seconds": round(t_repeat_sec, 4),
        "runtime_minutes": round(t_repeat_sec / 60.0, 4),
        "runtime_ms": res_repeat.run.runtime_ms,
        "direct_cost": "$0.00 (Local deterministic engine)",
        "run_id": res_repeat.run.id,
        "status": res_repeat.run.status.value,
    }

    # 3. Refresh run (new input)
    with open("inputs/fresh_creator_growth_study.md", "r", encoding="utf-8") as f:
        fresh_text = f.read()

    src_fresh = SourceDocument(
        id="src_fresh_creator_bench",
        title="Scaling Creator Video Repurposing: The Multi-Platform Distribution Playbook",
        content=fresh_text,
        source_type="case_study",
        source_url="https://incubrix.com/studies/creator-video-repurposing",
    )
    insert_source_document(conn, src_fresh)

    t0 = time.perf_counter()
    res_refresh = run_generation_service(
        source=src_fresh,
        base_tracking_url="https://incubrix.com/creator-playbook",
        campaign="benchmark_refresh",
        conn=conn,
        persist=True,
    )
    t_refresh_sec = time.perf_counter() - t0

    results["refresh_run"] = {
        "input_size_chars": len(fresh_text),
        "input_size_words": len(fresh_text.split()),
        "items_produced": res_refresh.created_count,
        "items_rejected": res_refresh.review_required_count,
        "duplicates_removed": res_refresh.skipped_duplicate_count,
        "runtime_seconds": round(t_refresh_sec, 4),
        "runtime_minutes": round(t_refresh_sec / 60.0, 4),
        "runtime_ms": res_refresh.run.runtime_ms,
        "direct_cost": "$0.00 (Local deterministic engine)",
        "run_id": res_refresh.run.id,
        "status": res_refresh.run.status.value,
    }

    # 4. Failure and recovery run
    invalid_text = "Short text"
    src_invalid = SourceDocument(
        id="src_invalid_short",
        title="Too Short",
        content=invalid_text,
        source_type="note",
        source_url="https://incubrix.com/invalid",
    )
    
    insert_source_document(conn, src_invalid)
    failure_logged = False
    error_msg = ""
    t0 = time.perf_counter()
    try:
        run_generation_service(
            source=src_invalid,
            base_tracking_url="https://incubrix.com/invalid",
            campaign="benchmark_failure",
            conn=conn,
            persist=True,
        )
    except ValueError as e:
        failure_logged = True
        error_msg = str(e)
    t_fail_sec = time.perf_counter() - t0

    # Recovery: retry with valid input
    recovery_text = (
        "# Rapid Telemetry Recovery Guide\n\n"
        "## Resilient Ingestion Architecture\n"
        "When event ingestion pipelines experience malformed payloads or schema violations, "
        "dead-letter queues isolate invalid records while preserving upstream transaction throughput. "
        "Valid records continue processing at sub-50 millisecond latency.\n"
        "- Dead-letter queues prevent system failure.\n"
        "- Automated retries resolve transient network timeouts.\n"
        "- Schema validation ensures 100% data fidelity.\n"
    )
    src_recovery = SourceDocument(
        id="src_recovery_valid",
        title="Rapid Telemetry Recovery Guide",
        content=recovery_text,
        source_type="guide",
        source_url="https://incubrix.com/recovery",
    )
    insert_source_document(conn, src_recovery)
    t0 = time.perf_counter()
    res_recovery = run_generation_service(
        source=src_recovery,
        base_tracking_url="https://incubrix.com/recovery",
        campaign="benchmark_recovery",
        conn=conn,
        persist=True,
    )
    t_recovery_sec = time.perf_counter() - t0

    results["failure_and_recovery"] = {
        "failure_input_chars": len(invalid_text),
        "failure_error": error_msg,
        "failure_logged": failure_logged,
        "recovery_input_chars": len(recovery_text),
        "recovery_items_produced": res_recovery.created_count,
        "recovery_items_rejected": res_recovery.review_required_count,
        "recovery_duplicates_removed": res_recovery.skipped_duplicate_count,
        "recovery_runtime_seconds": round(t_recovery_sec, 4),
        "total_runtime_seconds": round(t_fail_sec + t_recovery_sec, 4),
        "total_runtime_minutes": round((t_fail_sec + t_recovery_sec) / 60.0, 4),
        "direct_cost": "$0.00 (Local deterministic engine)",
        "recovery_run_id": res_recovery.run.id,
        "recovery_status": res_recovery.run.status.value,
    }

    conn.close()
    if db_path.exists():
        db_path.unlink()

    # Output formatted report
    print("\n" + "=" * 60)
    print("CONTENT ENGINE BENCHMARK RESULTS")
    print("=" * 60)
    print(json.dumps(results, indent=2))
    
    # Save benchmark results
    with open("research/engine_benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    run_all_benchmarks()
