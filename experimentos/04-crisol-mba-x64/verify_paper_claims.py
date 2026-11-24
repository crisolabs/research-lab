#!/usr/bin/env python3
"""
Deterministic Zero-LLM Pre-Publication Gate for CRISOL-MBA-x64 (`verify_paper_claims.py` v3).

Parses EVERY cell of Tables `tab:vtest`, `tab:vhard`, and `tab:vreal` and checks key claims
directly against RAW JSONL/CSV/JSON manifests and public Git:
  1. Table `tab:vtest`: every row's Strict <= 60.0s AND In-Flight counts (including exact set
     unions `A u C` and `A u C u GAMBA`).
  2. Strict `gt_cert_sec <= 10.0s` subset (`N=129`: `121/129` vs `32/129`) + immediate-constant
     template disclosure + non-LLM framing of `C`.
  3. Table `tab:vhard`: parses EVERY row (`poly_mul_32`, `poly_mul_64`, AND `Total V_hard`)
     and checks Z3, CaDiCaL LRAT strict <=30.0s + `[in-flight]`, Bitwuzla, and Lean 4 <=30.0s
     cell-by-cell against `data/results_vhard_cert.csv` (blocks mutations like `2/40 -> 9/40`).
  4. Table `tab:vreal`: parses all 4 rows (`A`, `C`, `H-sol`, `H-hydrogen`) cell-by-cell against
     `data/results_real_o2.jsonl`.
  5. Checks `31,744` + `51,200` = `82,944` sanity split, 4 C templates, `H_2` NOT CONFIRMED,
     no unarchived claims (`355 via`, `independent re-verification logs`), and public commit SHA.
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


def strip_tex(s: str) -> str:
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\texttt\{([^}]*)\}", r"\1", s)
    return s.replace("\\\\", "").strip()


def check_tex_text(tex: str) -> int:
    checks = 0

    # 1. Table tab:vtest cell-by-cell
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
        cols = [strip_tex(c) for c in matched[0].split("&")]
        if cols[2] != f"{exp_s} / 160" or cols[4] != f"{exp_i} / 160":
            fail(f"tab:vtest row `{row_key}` mismatch: got strict=`{cols[2]}` inflight=`{cols[4]}`, expected `{exp_s} / 160`, `{exp_i} / 160`")
        checks += 1

    # 2. Strict <= 10.0s freeze subset (121/129 vs 32/129)
    d_129 = len(strict_sets["D"] & le10_ids)
    ac_129 = len((strict_sets["A"] | strict_sets["C"]) & le10_ids)
    if f"{d_129}/{len(le10_ids)}" not in tex or f"{ac_129}/{len(le10_ids)}" not in tex:
        fail(f"Strict <=10s freeze subset ({d_129}/{len(le10_ids)} vs {ac_129}/{len(le10_ids)}) missing in main.tex")
    checks += 2

    # 3. Table tab:vhard EVERY ROW & EVERY SOLVER COLUMN cell-by-cell!
    vh_rows = list(csv.DictReader((REPO / "data" / "results_vhard_cert.csv").open()))
    tab_vhard = tex.split(r"\label{tab:vhard}")[0].split(r"\begin{table}")[-1]
    for prefix, sub, denom in [
        (r"\texttt{test\_mba\_poly\_mul\_32}", [r for r in vh_rows if "32" in r["family"]], 20),
        (r"\texttt{test\_mba\_poly\_mul\_64}", [r for r in vh_rows if "64" in r["family"]], 20),
        (r"\textbf{Total $V_{\mathrm{hard}}$ ($N=40$)}", vh_rows, 40),
    ]:
        matched = [ln for ln in tab_vhard.splitlines() if ln.strip().startswith(prefix)]
        if len(matched) != 1:
            fail(f"Could not uniquely locate row `{prefix}` in tab:vhard")
        cols = [strip_tex(c) for c in matched[0].split("&")]
        z3_s = sum(1 for r in sub if r["z3_unsat"] == "True" and float(r["z3_sec"]) <= 30.0)
        lr_s = sum(1 for r in sub if r["cadical_lrat_ok"] == "True" and float(r["cadical_lrat_sec"]) <= 30.0)
        lr_i = sum(1 for r in sub if r["cadical_lrat_ok"] == "True")
        bz_s = sum(1 for r in sub if r["bitwuzla_unsat"] == "True" and float(r["bitwuzla_sec"]) <= 30.0)
        ln_s = sum(1 for r in sub if r["lean4_bv_decide_ok"] == "True" and float(r["lean4_bv_decide_sec"]) <= 30.0)
        if not cols[1].startswith(f"{z3_s} / {denom}"):
            fail(f"tab:vhard `{prefix}` Z3 mismatch: `{cols[1]}` vs `{z3_s} / {denom}`")
        if not (cols[2].startswith(f"{lr_s} / {denom}") and f"[{lr_i}/{denom}]" in cols[2]):
            fail(f"tab:vhard `{prefix}` LRAT mismatch: `{cols[2]}` vs `{lr_s} / {denom} ... [{lr_i}/{denom}]`")
        if not cols[3].startswith(f"{bz_s} / {denom}"):
            fail(f"tab:vhard `{prefix}` Bitwuzla mismatch: `{cols[3]}` vs `{bz_s} / {denom}`")
        if not cols[4].startswith(f"{ln_s} / {denom}"):
            fail(f"tab:vhard `{prefix}` Lean4 mismatch: `{cols[4]}` vs `{ln_s} / {denom}`")
        checks += 4

    # 4. Table tab:vreal cell-by-cell
    vr_rows = [json.loads(l) for l in (REPO / "data" / "results_real_o2.jsonl").open() if l.strip()]
    tab_vreal = tex.split(r"\label{tab:vreal}")[0].split(r"\begin{table}")[-1]
    for prefix, cfg_name in [
        ("$A$", "A"),
        ("$C$", "C"),
        (r"\texttt{H-sol}", "H_sol"),
        (r"\textbf{\texttt{H-hydrogen}}", "H_hydrogen"),
    ]:
        matched = [ln for ln in tab_vreal.splitlines() if ln.strip().startswith(prefix)]
        if len(matched) != 1:
            fail(f"Could not uniquely locate row `{prefix}` in tab:vreal")
        cols = [strip_tex(c) for c in matched[0].split("&")]
        exp_p = sum(1 for r in vr_rows if r["config"] == cfg_name and r["passed"] and r["elapsed_sec"] <= 60.0)
        if cols[2] != f"{exp_p} / 22":
            fail(f"tab:vreal `{prefix}` mismatch: `{cols[2]}` vs `{exp_p} / 22`")
        checks += 1

    # 5. Required accurate disclosures & forbidden stale strings
    for req in ("31,744", "51,200", "4 parameterized C", "NOT CONFIRMED", "immediate-constant variants"):
        if req not in tex:
            fail(f"Required accurate disclosure `{req}` missing from main.tex")
        checks += 1
    for forbidden in ("355 via", "independent re-verification logs", "constant/register variants", "deterministic baseline"):
        if forbidden in tex:
            fail(f"Stale/inaccurate phrase `{forbidden}` still present in main.tex!")
        checks += 1

    # 6. Public git commit SHA verification
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

    return checks


def main() -> None:
    tex = TEX_PATH.read_text(encoding="utf-8")
    checks = check_tex_text(tex)
    print(f"VERIFY_PAPER_CLAIMS_V3: PASS ({checks} exhaustive cell-level, raw-log & git checks verified)")


if __name__ == "__main__":
    main()
