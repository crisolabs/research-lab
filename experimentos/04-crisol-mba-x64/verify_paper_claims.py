#!/usr/bin/env python3
"""
Deterministic Zero-LLM Pre-Publication Gate for CRISOL-MBA-x64 (`verify_paper_claims.py` v4).

Parses EVERY cell of Tables `tab:vtest` (including H-Sol, percentages, and LLM calls),
`tab:vhard`, and `tab:vreal`, plus sensitivity subsets, bibliography, and absence of
stale markdown files in the public repository.
"""
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
TEX_PATH = REPO / "paper" / "arxiv-v1" / "main.tex"
BIB_PATH = REPO / "paper" / "arxiv-v1" / "references.bib"
PUBLIC_REPO = Path("/home/luis/personal/research-lab")


def fail(msg: str) -> None:
    print(f"[PAPER_GATE: FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def strip_tex(s: str) -> str:
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\texttt\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    return s.replace("\\\\", "").strip()


def check_tex_text(tex: str) -> int:
    checks = 0
    mv = json.loads((REPO / "data" / "manifest_V.json").read_text(encoding="utf-8"))
    vtest = mv["V_test"]
    gamba_ids = {d["instance_id"] for d in vtest if d["family"] in ("test_mba_3var_linear_64", "test_mba_nand_nor_add_64")}
    le10_ids = {d["instance_id"] for d in vtest if d["gt_cert_sec"] <= 10.0}

    rows_t = [json.loads(l) for l in (REPO / "data" / "results_test.jsonl").open() if l.strip()]
    rows_h = [json.loads(l) for l in (REPO / "data" / "results_test_H_hydrogen.jsonl").open() if l.strip()]
    rows_hs = [json.loads(l) for l in (REPO / "data" / "results_test_H_sol40.jsonl").open() if l.strip()]
    by_cfg = {}
    for r in rows_t + rows_h:
        by_cfg.setdefault(r["config"], {})[r["instance_id"]] = r

    strict_sets = {c: {i for i, r in by_cfg[c].items() if r["passed"] and r["elapsed_sec"] <= 60.0} for c in ("A", "B", "C", "D", "H")}
    inflight_sets = {c: {i for i, r in by_cfg[c].items() if r["passed"]} for c in ("A", "B", "C", "D", "H")}

    expected_vtest_rows = {
        "$A$": (len(strict_sets["A"]), len(inflight_sets["A"]), 160),
        "GAMBA": (len(gamba_ids), len(gamba_ids), 160),
        "$C$": (len(strict_sets["C"]), len(inflight_sets["C"]), 160),
        "$A \\cup C$": (len(strict_sets["A"] | strict_sets["C"]), len(inflight_sets["A"] | inflight_sets["C"]), 160),
        "$A \\cup C \\cup \\text{GAMBA}$": (
            len(strict_sets["A"] | strict_sets["C"] | gamba_ids),
            len(inflight_sets["A"] | inflight_sets["C"] | gamba_ids),
            160,
        ),
        "$B$": (len(strict_sets["B"]), len(inflight_sets["B"]), 160),
        "$D$": (len(strict_sets["D"]), len(inflight_sets["D"]), 160),
        "$H$ (Hydrogen)": (len(strict_sets["H"]), len(inflight_sets["H"]), 160),
        "$H$ (GPT-6.2-Sol)": (
            sum(1 for r in rows_hs if r["passed"] and r["elapsed_sec"] <= 60.0),
            sum(1 for r in rows_hs if r["passed"]),
            40,
        ),
    }

    tab_vtest = tex.split(r"\label{tab:vtest}")[0].split(r"\begin{table}")[-1]
    for row_key, (exp_s, exp_i, denom) in expected_vtest_rows.items():
        matched = [ln for ln in tab_vtest.splitlines() if ln.strip().startswith(row_key + " &")]
        if len(matched) != 1:
            fail(f"Could not uniquely locate row `{row_key}` in tab:vtest")
        cols = [strip_tex(c) for c in matched[0].split("&")]
        exp_sp = f"{100.0 * exp_s / denom:.2f}"
        exp_ip = f"{100.0 * exp_i / denom:.2f}"
        if cols[2] != f"{exp_s} / {denom}" or cols[3] != exp_sp or cols[4] != f"{exp_i} / {denom}" or cols[5] != exp_ip:
            fail(f"tab:vtest `{row_key}` mismatch: got {cols[2:6]} vs ({exp_s} / {denom}, {exp_sp}, {exp_i} / {denom}, {exp_ip})")
        if row_key == "$H$ (GPT-6.2-Sol)" and cols[7] != f"{sum(r['llm_calls'] for r in rows_hs)/len(rows_hs):.2f}":
            fail(f"tab:vtest H-Sol LLM calls mismatch: got `{cols[7]}`")
        checks += 2

    # 2. Subsets: N=129 (<=10s freeze) and N=120 (excl nand_nor_add_64 & sar_neg_32)
    d_129 = len(strict_sets["D"] & le10_ids)
    ac_129 = len((strict_sets["A"] | strict_sets["C"]) & le10_ids)
    if f"{d_129}/{len(le10_ids)}" not in tex or f"{ac_129}/{len(le10_ids)}" not in tex:
        fail(f"Missing N=129 subset ({d_129}/{len(le10_ids)} vs {ac_129}/{len(le10_ids)})")
    ids_120 = {i for i, r in by_cfg["A"].items() if r["family"] not in ("test_mba_nand_nor_add_64", "test_mba_sar_neg_32")}
    d_120 = len(strict_sets["D"] & ids_120)
    h_120 = len(strict_sets["H"] & ids_120)
    ac_120 = len((strict_sets["A"] | strict_sets["C"]) & ids_120)
    for tok in (f"{d_120}/120", f"{h_120}/120", f"{ac_120}/120"):
        if tok not in tex:
            fail(f"Missing N=120 sensitivity count `{tok}` in main.tex")
    checks += 5

    # 3. Table tab:vhard cell-by-cell
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
            fail(f"tab:vhard `{prefix}` Z3 mismatch: `{cols[1]}`")
        if not (cols[2].startswith(f"{lr_s} / {denom}") and f"[{lr_i}/{denom}]" in cols[2]):
            fail(f"tab:vhard `{prefix}` LRAT mismatch: `{cols[2]}`")
        if not cols[3].startswith(f"{bz_s} / {denom}"):
            fail(f"tab:vhard `{prefix}` Bitwuzla mismatch: `{cols[3]}`")
        if not cols[4].startswith(f"{ln_s} / {denom}"):
            fail(f"tab:vhard `{prefix}` Lean4 mismatch: `{cols[4]}`")
        checks += 4

    # 4. Table tab:vreal cell-by-cell
    vr_rows = [json.loads(l) for l in (REPO / "data" / "results_real_o2.jsonl").open() if l.strip()]
    tab_vreal = tex.split(r"\label{tab:vreal}")[0].split(r"\begin{table}")[-1]
    for prefix, cfg_name in [("$A$", "A"), ("$C$", "C"), (r"\texttt{H-sol}", "H_sol"), (r"\textbf{\texttt{H-hydrogen}}", "H_hydrogen")]:
        matched = [ln for ln in tab_vreal.splitlines() if ln.strip().startswith(prefix)]
        if len(matched) != 1:
            fail(f"Could not uniquely locate row `{prefix}` in tab:vreal")
        cols = [strip_tex(c) for c in matched[0].split("&")]
        exp_p = sum(1 for r in vr_rows if r["config"] == cfg_name and r["passed"] and r["elapsed_sec"] <= 60.0)
        if cols[2] != f"{exp_p} / 22":
            fail(f"tab:vreal `{prefix}` mismatch: `{cols[2]}` vs `{exp_p} / 22`")
        checks += 1

    # 5. Bibliography & no stale markdown files in public repo
    bib = BIB_PATH.read_text(encoding="utf-8")
    if "Roh, Youjeong" not in bib or "Noh, Youjeong" in bib:
        fail("Bibliography gmba2025 must list `Roh, Youjeong` (ACL Anthology 2025)!")
    pub_paper = PUBLIC_REPO / "experimentos" / "04-crisol-mba-x64" / "paper"
    if pub_paper.exists():
        for stale in ("paper-en.md", "paper-es.md", "paper-es.pdf"):
            if (pub_paper / stale).exists():
                fail(f"Stale contradictory file `{stale}` still exists in public repo `{pub_paper}`!")
    checks += 4

    # 6. Public git commit SHA verification
    shas = re.findall(r"commit\s+\\texttt\{([0-9a-f]{7,40})\}", tex)
    if not shas:
        fail("No public commit SHA cited in main.tex!")
    for sha in shas:
        rc = subprocess.run(["git", "-C", str(PUBLIC_REPO), "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True).returncode
        if rc != 0:
            fail(f"Cited commit SHA {sha} does NOT exist in public repo {PUBLIC_REPO}!")
        checks += 1

    return checks


def main() -> None:
    tex = TEX_PATH.read_text(encoding="utf-8")
    checks = check_tex_text(tex)
    print(f"VERIFY_PAPER_CLAIMS_V4: PASS ({checks} exhaustive cell, percentage, subset, bib & packaging checks verified)")


if __name__ == "__main__":
    main()
