#!/usr/bin/env python3
"""Offline Artifact Evaluation (--replay) script for CRISOL-MBA-x64.

Requires ZERO LLM API keys:
  1. Verifies SHA-256 hashes of frozen pre-registration docs and dataset manifests.
  2. Re-verifies cached PASS outputs from results_*.jsonl using Lean 4 `bv_decide`
     and/or Bitwuzla + Z3 + CaDiCaL LRAT + lrat-check.
  3. Regenerates publication figures from raw CSV/JSON artifacts.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from crisol_mba.expr import canonical_cost
from crisol_mba.oracle_lean import certify_with_lean_bv_decide
from crisol_mba.oracle_smt import SlicePreFilter, verify_candidate
from crisol_mba.parser import parse_expr


REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data"
DOCS_DIR = REPO_ROOT / "docs"


def verify_sha256_file(sha_file: Path) -> None:
    for line in sha_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, rel = line.split(None, 1)
        target = sha_file.parent / rel.strip()
        if not target.exists():
            target = REPO_ROOT / rel.strip()
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            raise AssertionError(f"SHA-256 mismatch for {target}: expected {expected}, got {actual}")
        print(f"  [SHA-256 OK] {target.relative_to(REPO_ROOT)} ({actual[:16]}...)")


def _replay_one(task: tuple[dict, dict, str]) -> tuple[str, str, bool, str]:
    r, d, mode = task
    code = bytes.fromhex(d["bytes_hex"])
    expr = parse_expr(r["best_expr"], expected_width=64)
    max_cost = d["ground_truth_cost"] * 1.10
    if canonical_cost(expr) > max_cost + 1e-9:
        return r["config"], r["instance_id"], False, "FAIL_COST"
    if mode == "lean4":
        lv = certify_with_lean_bv_decide(code, expr, timeout_sec=30.0)
        return r["config"], r["instance_id"], lv.verified, lv.detail
    pf = SlicePreFilter(code)
    v = verify_candidate(code, expr, max_cost=max_cost, prefilter=pf, timeout_sec=30.0, require_lrat=True)
    return r["config"], r["instance_id"], (v.status == "PASS"), v.status


def main() -> None:
    ap = argparse.ArgumentParser(description="CRISOL-MBA-x64 Offline Artifact Evaluation Replay")
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke", help="smoke: 12 slices (~30s); full: all cached PASS verdicts")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    print("=== 1. Verifying Frozen SHA-256 Checksums ===")
    verify_sha256_file(DOCS_DIR / "SHA256SUMS.txt")
    verify_sha256_file(DATA_DIR / "manifest_V.sha256")
    verify_sha256_file(DATA_DIR / "manifest_V_real.sha256")

    frozen_v = json.loads((DATA_DIR / "manifest_V.json").read_text(encoding="utf-8"))
    frozen_real = json.loads((DATA_DIR / "manifest_V_real.json").read_text(encoding="utf-8"))
    by_id_v = {d["instance_id"]: d for d in frozen_v["V_dev"] + frozen_v["V_test"]}
    by_id_real = {d["instance_id"]: d for d in frozen_real["instances"]}

    h_rows = [json.loads(l) for l in (DATA_DIR / "results_test_H_hydrogen.jsonl").read_text().splitlines() if l.strip() and json.loads(l)["passed"]]
    real_rows = [json.loads(l) for l in (DATA_DIR / "results_real_o2.jsonl").read_text().splitlines() if l.strip() and json.loads(l)["passed"] and json.loads(l)["config"] == "H_hydrogen"]

    if args.mode == "smoke":
        tasks = [(r, by_id_v[r["instance_id"]], "lrat") for r in h_rows[:6]] + [
            (r, by_id_real[r["instance_id"]], "lean4") for r in real_rows[:6]
        ]
    else:
        tasks = [(r, by_id_v[r["instance_id"]], "lrat") for r in h_rows] + [
            (r, by_id_real[r["instance_id"]], "lean4") for r in real_rows
        ]

    print(f"=== 2. Offline Re-Verification ({args.mode}: {len(tasks)} cached PASS verdicts, 0 API calls) ===")
    ok = 0
    fails = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as ex:
        for cfg, iid, passed, detail in ex.map(_replay_one, tasks):
            if passed:
                ok += 1
            else:
                fails.append((cfg, iid, detail))
    print(f"  REPLAY_VERIFIED: {ok}/{len(tasks)} (fails={len(fails)})")
    if fails:
        print("  FAILURES:", fails[:5])
        sys.exit(1)

    print("=== 3. Regenerating Publication Figures ===")
    subprocess.run([sys.executable, str(REPO_ROOT / "generate_figures.py")], check=True)
    print("OFFLINE_ARTIFACT_REPLAY: PASS")


if __name__ == "__main__":
    main()
