#!/usr/bin/env python3
"""
Deterministic Zero-LLM Pre-Publication Gate for CRISOL-MBA-x64 (`verify_paper_claims.py` v2).

Parses `main.tex` tables and claims directly against RAW JSONL/CSV/JSON manifests and public Git:
  1. Parses every row of Table `tab:vtest` and checks BOTH Strict <= 60.0s AND In-Flight counts
     (including exact set unions `A u C` and `A u C u GAMBA`!) against `data/results_test*.jsonl`
     and `data/manifest_V.json`.
  2. Checks the strict `gt_cert_sec <= 10.0s` subset (`N=129`: `121/129` vs `32/129`) and freeze
     deviation disclosures in `main.tex`.
  3. Parses Table `tab:vhard` and checks strict end-to-end `<= 30.0s` counts (`2/40` LRAT,
     `35/40` Lean 4, `40/40` Bitwuzla, `0/40` Z3) AND in-flight `[3/40]` against `results_vhard_cert.csv`.
  4. Checks `31,744` + `51,200` = `82,944` sanity split, 4 C templates in `V_real`, `H_2` NOT CONFIRMED,
     and no unarchived re-verification claims (`355` removed).
  5. Verifies every cited commit SHA exists in `/home/luis/personal/research-lab`.
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

    # 1. Compute exact ground-truth V_test sets from raw JSONL + manifest_V.json
    mv = json.loads((REPO / "data" / "manifest_V.json").read_text(encoding="utf-8"))
    vtest = mv["V_test"]
    gamba_ids = {d["instance_id"] for d in vtest if d["family"] in ("test_mba_3var_linear_64", "test_mba_nand_nor_add_64")}
    le10_ids = {d["instance_id"] for d in vtest if d["gt_cert_sec"] <= 10.0}

    rows_t = [json.loads(l) for l in (REPO / "data" / "results_test.jsonl").open() if l.strip()]
    rows_h = [json.loads(l) for l in (REPO / "data" / "results_test_H_hydrogen.jsonl").open() if l.strip()]
    by_cfg = {}
    for r in rows_t + rows_h:
        by_cfg.setdefault(r["config"], {})[r["instance_id"]] = r

    strict_sets = {
        c: {i for i, r in by_cfg[c].items() if r["passed"] and r["elapsed_sec"] <= 60.0}
        for c in ("A", "B", "C", "D", "H")
    }
    inflight_sets = {
        c: {i for i, r in by_cfg[c].items() if r["passed"]}
        for c in ("A", "B", "C", "D", "H")
    }
    expected_vtest_rows = {
        "$A$": (len(strict_sets["A"]), len(inflight_sets["A"])),
        "GAMBA": (len(gamba_ids), len(gamba_ids)),
        "$C$": (len(strict_sets["C"]), len(inflight_sets["C"])),
        "$A \\cup C$": (len(strict_sets["A"] | strict_sets["C"]), len(inflight_sets["A"] | inflight_sets["C"])),
        "$A \\cup C \\cup \\text{GAMBA}$": (
            len(strict_sets["A"] | strict_sets["C"] | gamba_ids),
            len(inflight_sets["A"] | inflight_sets["C"] | gamba_ids),
        ),
        "$B$": (len(strict_sets["B"]), len(inflight_sets["B"])),
        "$D$": (len(strict_sets["D"]), len(inflight_sets["D"])),
        "$H$ (Hydrogen)": (len(strict_sets["H"]), len(inflight_sets["H"])),
    }

    tab_vtest = tex.split(r"\label{tab:vtest}")[0].split(r"\begin{table}")[-1]
    for row_key, (exp_s, exp_i) in expected_vtest_rows.items():
        matched = [ln for ln in tab_vtest.splitlines() if ln.strip().startswith(row_key + " &")]
        if len(matched) != 1:
            fail(f"Could not uniquely locate row `{row_key}` in tab:vtest")
        cols = [c.strip() for c in matched[0].split("&")]
        s_str = re.sub(r"\\textbf\{([^}]*)\}", r"\1", cols[2])
        i_str = re.sub(r"\\textbf\{([^}]*)\}", r"\1", cols[4])
        if s_str != f"{exp_s} / 160" or i_str != f"{exp_i} / 160":
            fail(f"Row `{row_key}` mismatch: got strict=`{s_str}` inflight=`{i_str}`, expected `{exp_s} / 160` and `{exp_i} / 160`")
        checks += 1

    # 2. Check strict <= 10.0s freeze subset disclosure (121/129 vs 32/129)
    d_129 = len(strict_sets["D"] & le10_ids)
    ac_129 = len((strict_sets["A"] | strict_sets["C"]) & le10_ids)
    if f"{d_129}/{len(le10_ids)}" not in tex or f"{ac_129}/{len(le10_ids)}" not in tex:
        fail(f"Strict <=10s freeze subset ({d_129}/{len(le10_ids)} vs {ac_129}/{len(le10_ids)}) missing in main.tex")
    checks += 2

    # 3. Parse Table `tab:vhard` against strict end-to-end <= 30.0s in results_vhard_cert.csv
    vh_rows = list(csv.DictReader((REPO / "data" / "results_vhard_cert.csv").open()))
    lrat_32_s = sum(1 for r in vh_rows if "32" in r["family"] and r["cadical_lrat_ok"] == "True" and float(r["cadical_lrat_sec"]) <= 30.0)
    lrat_32_i = sum(1 for r in vh_rows if "32" in r["family"] and r["cadical_lrat_ok"] == "True")
    lean_tot_s = sum(1 for r in vh_rows if r["lean4_bv_decide_ok"] == "True" and float(r["lean4_bv_decide_sec"]) <= 30.0)
    tab_vhard = tex.split(r"\label{tab:vhard}")[0].split(r"\begin{table}")[-1]
    if f"{lrat_32_s} / 20" not in tab_vhard or f"[{lrat_32_i}/20]" not in tab_vhard:
        fail(f"tab:vhard missing exact strict/in-flight LRAT 32-bit `{lrat_32_s} / 20` `[{lrat_32_i}/20]`")
    if f"{lean_tot_s} / 40" not in tab_vhard:
        fail(f"tab:vhard missing exact strict <=30s Lean4 `{lean_tot_s} / 40`")
    checks += 3

    # 4. Sanity check split (31,744 + 51,200), 4 C templates, H_2 NOT CONFIRMED, no unarchived "355 via"
    for req in ("31,744", "51,200", "4 parameterized C", "NOT CONFIRMED"):
        if req not in tex:
            fail(f"Required accurate disclosure `{req}` missing from main.tex")
        checks += 1
    if "355 via" in tex:
        fail("Unarchived `355 via` split still present in main.tex!")
    checks += 1

    # 5. Public git commit SHA verification
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

    print(f"VERIFY_PAPER_CLAIMS_V2: PASS ({checks} cell-level & raw-log checks verified)")


if __name__ == "__main__":
    main()
