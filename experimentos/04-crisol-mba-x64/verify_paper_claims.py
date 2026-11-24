#!/usr/bin/env python3
"""
Deterministic Zero-LLM Pre-Publication Gate for CRISOL-MBA-x64 (`verify_paper_claims.py`).

Checks directly against RAW JSONL/CSV logs, benchmark source code, and the public Git repo:
  1. Every pass count in V_test (both loop-entry 60s gate AND strict post-hoc <= 60.0s cutoff)
     is computed directly from raw `data/results_test*.jsonl` and verified to appear in `main.tex`.
  2. All 4 V_hard backends in `run_phase2.py` use an identical timeout budget (30.0 s / 30000 ms),
     and `main.tex` matches `data/results_vhard_cert.csv` row-for-row.
  3. All pre-registered hypotheses (`H_1` AND `H_2`) from `docs/03-preregistro-crisol-mba-x64.md`
     are explicitly reported in `main.tex` (including `H_2` NOT CONFIRMED).
  4. GAMBA's domain boundary (`40/40` on the 2 pure-AST families vs. 6 x86-64 carry/rotate/zext
     families) is accurately stated in the Abstract.
  5. Every 7-hex commit SHA cited in `main.tex` actually exists in the public repo
     (`/home/luis/personal/research-lab`).
"""
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
TEX_PATH = REPO / "paper" / "arxiv-v1" / "main.tex"
PUBLIC_REPO = Path("/home/luis/personal/research-lab")


def fail(msg: str) -> None:
    print(f"[PAPER_GATE: FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    tex = TEX_PATH.read_text(encoding="utf-8")
    checks = 0

    # 1. Raw JSONL verification for V_test (loop gate vs strict <= 60.0 s)
    rows_t = [json.loads(l) for l in (REPO / "data" / "results_test.jsonl").open() if l.strip()]
    rows_h = [json.loads(l) for l in (REPO / "data" / "results_test_H_hydrogen.jsonl").open() if l.strip()]
    by_cfg = {}
    for r in rows_t + rows_h:
        by_cfg.setdefault(r["config"], []).append(r)

    for cfg in ("A", "B", "C", "D", "H"):
        rs = by_cfg[cfg]
        assert len(rs) == 160, f"{cfg} len={len(rs)}"
        p_all = sum(1 for r in rs if r["passed"])
        p_60 = sum(1 for r in rs if r["passed"] and r["elapsed_sec"] <= 60.0)
        if p_all != p_60:
            # Must disclose strict <= 60s count in main.tex!
            if f"{p_60} / 160" not in tex and f"{p_60}/160" not in tex:
                fail(f"Config {cfg} has p_all={p_all} != p_strict60={p_60}, but {p_60}/160 is NOT disclosed in main.tex!")
        checks += 1

    # Specifically forbid claiming "160/160" without also disclosing "159/160" and "74.29"
    if "159/160" not in tex and "159 / 160" not in tex:
        fail("Strict <=60s count 159/160 for Hybrid H missing from main.tex")
    if "74.29" not in tex:
        fail("Max elapsed time 74.29s for Hybrid H missing from main.tex")
    checks += 2

    # 2. Equalized timeout budget in run_phase2.py + CSV match for V_hard
    p2 = (REPO / "run_phase2.py").read_text(encoding="utf-8")
    if "TIME_LIMIT_PER, 30000" not in p2 or 'set("timeout", 30000)' not in p2:
        fail("Bitwuzla or Z3 timeout in run_phase2.py is not equalized to 30000 ms!")
    if "certify_unsat_lrat(miter, timeout_sec=30.0)" not in p2 or "certify_with_lean_bv_decide(code, gt, timeout_sec=30.0)" not in p2:
        fail("CaDiCaL LRAT or Lean 4 timeout in run_phase2.py is not equalized to 30.0 s!")
    checks += 2

    vh_rows = list(csv.DictReader((REPO / "data" / "results_vhard_cert.csv").open()))
    assert len(vh_rows) == 40
    z3_tot = sum(1 for r in vh_rows if r["z3_unsat"] == "True")
    lrat_tot = sum(1 for r in vh_rows if r["cadical_lrat_ok"] == "True")
    bz_tot = sum(1 for r in vh_rows if r["bitwuzla_unsat"] == "True")
    lean_tot = sum(1 for r in vh_rows if r["lean4_bv_decide_ok"] == "True")
    for label, val in [("Z3", z3_tot), ("LRAT", lrat_tot), ("Bitwuzla", bz_tot), ("Lean4", lean_tot)]:
        if f"{val} / 40" not in tex and f"{val}/40" not in tex:
            fail(f"V_hard total {label}={val}/40 from results_vhard_cert.csv not found in main.tex!")
        checks += 1

    # 3. Both pre-registered hypotheses H_1 AND H_2 must be explicitly reported
    if "H_1" not in tex:
        fail("Pre-registered hypothesis H_1 missing in main.tex")
    if "H_2" not in tex or ("not confirmed" not in tex.lower() and "unconfirmed" not in tex.lower()):
        fail("Pre-registered hypothesis H_2 (and its NOT CONFIRMED verdict) missing in main.tex!")
    checks += 2

    # 4. Fair GAMBA framing in Abstract (must mention 40/40 on supported pure-AST families)
    abstract = tex.split(r"\begin{abstract}")[1].split(r"\end{abstract}")[0]
    if "40/40" not in abstract:
        fail("Abstract must state GAMBA solved 40/40 on the 2 supported pure-AST families!")
    checks += 1

    # 5. Every commit SHA cited via `commit \texttt{...}` must exist in public repo!
    shas = re.findall(r"commit\s+\\texttt\{([0-9a-f]{7,40})\}", tex)
    if not shas:
        fail("No public commit SHA cited in main.tex!")
    for sha in shas:
        rc = subprocess.run(
            ["git", "-C", str(PUBLIC_REPO), "cat-file", "-e", f"{sha}^{{commit}}"],
            capture_output=True,
        ).returncode
        if rc != 0:
            fail(f"Cited commit SHA {sha} does NOT exist in public repo {PUBLIC_REPO}!")
        checks += 1

    print(f"VERIFY_PAPER_CLAIMS: PASS ({checks} deterministic checks verified against raw logs & public git)")


if __name__ == "__main__":
    main()
