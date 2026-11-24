#!/usr/bin/env python3
"""
Deterministic Zero-LLM Pre-Publication Gate for CRISOL-MBA-x64 (`verify_paper_claims.py` v6).

Portable (zero hardcoded author paths) and checks EXACT string equality (`==`) on EVERY
count, percentage, in-flight bracket, mean/max time, and LLM-call cell of Tables
`tab:vtest`, `tab:vhard`, and `tab:vreal`, plus subset p-values, bibliography, README
consistency, and git commit existence.
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
README_PATH = REPO / "README.md"


def _resolve_git_root() -> Path:
    r = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        return Path(r.stdout.strip())
    return REPO


def fail(msg: str) -> None:
    print(f"[PAPER_GATE: FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def strip_tex(s: str) -> str:
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\texttt\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    return s.replace("\\\\", "").replace(r"\,", " ").replace(r"\%", "%").strip()


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

    def mean_max_str(rs: list[dict], star: str = "") -> str:
        mn = sum(r["elapsed_sec"] for r in rs) / len(rs)
        mx = max(r["elapsed_sec"] for r in rs)
        return f"{mn:.2f} / {mx:.2f}{star}"

    expected_vtest_rows = {
        "$A$": (len(strict_sets["A"]), len(inflight_sets["A"]), 160, mean_max_str(list(by_cfg["A"].values())), "0.00"),
        "GAMBA": (len(gamba_ids), len(gamba_ids), 160, "---", "0.00"),
        "$C$": (len(strict_sets["C"]), len(inflight_sets["C"]), 160, mean_max_str(list(by_cfg["C"].values())), "0.00"),
        "$A \\cup C$": (len(strict_sets["A"] | strict_sets["C"]), len(inflight_sets["A"] | inflight_sets["C"]), 160, "---", "0.00"),
        "$A \\cup C \\cup \\text{GAMBA}$": (
            len(strict_sets["A"] | strict_sets["C"] | gamba_ids),
            len(inflight_sets["A"] | inflight_sets["C"] | gamba_ids),
            160, "---", "0.00",
        ),
        "$B$": (len(strict_sets["B"]), len(inflight_sets["B"]), 160, mean_max_str(list(by_cfg["B"].values()), "*"), "1.00"),
        "$D$": (
            len(strict_sets["D"]), len(inflight_sets["D"]), 160,
            mean_max_str(list(by_cfg["D"].values())),
            f"{sum(r['llm_calls'] for r in by_cfg['D'].values())/160:.2f}",
        ),
        "$H$ (Hydrogen)": (
            len(strict_sets["H"]), len(inflight_sets["H"]), 160,
            mean_max_str(list(by_cfg["H"].values())),
            f"{sum(r['llm_calls'] for r in by_cfg['H'].values())/160:.2f}",
        ),
        "$H$ (GPT-6.2-Sol)": (
            sum(1 for r in rows_hs if r["passed"] and r["elapsed_sec"] <= 60.0),
            sum(1 for r in rows_hs if r["passed"]),
            40,
            mean_max_str(rows_hs),
            f"{sum(r['llm_calls'] for r in rows_hs)/len(rows_hs):.2f}",
        ),
    }

    tab_vtest = tex.split(r"\label{tab:vtest}")[0].split(r"\begin{table}")[-1]
    for row_key, (exp_s, exp_i, denom, exp_tm, exp_llm) in expected_vtest_rows.items():
        matched = [ln for ln in tab_vtest.splitlines() if ln.strip().startswith(row_key + " &")]
        if len(matched) != 1:
            fail(f"Could not uniquely locate row `{row_key}` in tab:vtest")
        cols = [strip_tex(c) for c in matched[0].split("&")]
        exp_sp = f"{100.0 * exp_s / denom:.2f}"
        exp_ip = f"{100.0 * exp_i / denom:.2f}"
        if cols[2] != f"{exp_s} / {denom}" or cols[3] != exp_sp or cols[4] != f"{exp_i} / {denom}" or cols[5] != exp_ip:
            fail(f"tab:vtest `{row_key}` count/pct mismatch: {cols[2:6]}")
        if cols[6] != exp_tm or cols[7] != exp_llm:
            fail(f"tab:vtest `{row_key}` time/llm mismatch: got ({cols[6]}, {cols[7]}) vs ({exp_tm}, {exp_llm})")
        checks += 3

    # 2. Subsets & exact rounding 2.58e-26
    d_129 = len(strict_sets["D"] & le10_ids)
    ac_129 = len((strict_sets["A"] | strict_sets["C"]) & le10_ids)
    if f"{d_129}/{len(le10_ids)}" not in tex or f"{ac_129}/{len(le10_ids)}" not in tex:
        fail("Missing N=129 subset counts")
    if r"2.58 \times 10^{-26}" not in tex or r"2.59 \times 10^{-26}" in tex:
        fail("N=120 McNemar p-value rounding must be 2.58 x 10^-26 (2^-85)!")
    checks += 3

    # 3. Table tab:vhard EXACT CELL EQUALITY (`==`) including ALL 12 percentages & denominators!
    vh_rows = list(csv.DictReader((REPO / "data" / "results_vhard_cert.csv").open()))
    tab_vhard = tex.split(r"\label{tab:vhard}")[0].split(r"\begin{table}")[-1]
    for prefix, sub, denom, pct_fmt in [
        (r"\texttt{test\_mba\_poly\_mul\_32}", [r for r in vh_rows if "32" in r["family"]], 20, ".0f"),
        (r"\texttt{test\_mba\_poly\_mul\_64}", [r for r in vh_rows if "64" in r["family"]], 20, ".0f"),
        (r"\textbf{Total $V_{\mathrm{hard}}$ ($N=40$)}", vh_rows, 40, "total"),
    ]:
        matched = [ln for ln in tab_vhard.splitlines() if ln.strip().startswith(prefix)]
        if len(matched) != 1:
            fail(f"Could not locate `{prefix}` in tab:vhard")
        cols = [strip_tex(c) for c in matched[0].split("&")]
        z3_s = sum(1 for r in sub if r["z3_unsat"] == "True" and float(r["z3_sec"]) <= 30.0)
        lr_s = sum(1 for r in sub if r["cadical_lrat_ok"] == "True" and float(r["cadical_lrat_sec"]) <= 30.0)
        lr_i = sum(1 for r in sub if r["cadical_lrat_ok"] == "True")
        bz_s = sum(1 for r in sub if r["bitwuzla_unsat"] == "True" and float(r["bitwuzla_sec"]) <= 30.0)
        ln_s = sum(1 for r in sub if r["lean4_bv_decide_ok"] == "True" and float(r["lean4_bv_decide_sec"]) <= 30.0)

        def fmt_pct(cnt: int) -> str:
            v = 100.0 * cnt / denom
            if pct_fmt == ".0f" or v in (0.0, 100.0):
                return f"{v:.0f}%"
            return f"{v:.1f}%"

        exp_z3 = f"{z3_s} / {denom} ({fmt_pct(z3_s)})"
        exp_lr = f"{lr_s} / {denom} ({fmt_pct(lr_s)}) [{lr_i}/{denom}]"
        exp_bz = f"{bz_s} / {denom} ({fmt_pct(bz_s)})"
        exp_ln = f"{ln_s} / {denom} ({fmt_pct(ln_s)})"

        m_all = sum(float(r["lean4_bv_decide_sec"]) for r in sub) / len(sub)
        ok_t = [float(r["lean4_bv_decide_sec"]) for r in sub if r["lean4_bv_decide_ok"] == "True" and float(r["lean4_bv_decide_sec"]) <= 30.0]
        m_ok = sum(ok_t) / len(ok_t)
        exp_tcol = f"{m_all:.2f} s / {m_ok:.2f} s"

        for cname, got, exp in [("Z3", cols[1], exp_z3), ("LRAT", cols[2], exp_lr), ("Bitwuzla", cols[3], exp_bz), ("Lean4", cols[4], exp_ln), ("Time", cols[5], exp_tcol)]:
            if got != exp:
                fail(f"tab:vhard `{prefix}` {cname} exact mismatch: got `{got}` vs `{exp}`")
        checks += 5

    # 4. Table tab:vreal exact equality
    vr_rows = [json.loads(l) for l in (REPO / "data" / "results_real_o2.jsonl").open() if l.strip()]
    tab_vreal = tex.split(r"\label{tab:vreal}")[0].split(r"\begin{table}")[-1]
    for prefix, cfg_name, star in [("$A$", "A", ""), ("$C$", "C", "*"), (r"\texttt{H-sol}", "H_sol", ""), (r"\textbf{\texttt{H-hydrogen}}", "H_hydrogen", "")]:
        matched = [ln for ln in tab_vreal.splitlines() if ln.strip().startswith(prefix)]
        if len(matched) != 1:
            fail(f"Could not locate `{prefix}` in tab:vreal")
        cols = [strip_tex(c) for c in matched[0].split("&")]
        sub = [r for r in vr_rows if r["config"] == cfg_name]
        exp_p = sum(1 for r in sub if r["passed"] and r["elapsed_sec"] <= 60.0)
        exp_pct = f"{100.0 * exp_p / 22:.2f}"
        exp_mean = f"{sum(r['elapsed_sec'] for r in sub)/len(sub):.2f}{star}"
        if cols[2] != f"{exp_p} / 22" or cols[3] != exp_pct or cols[4] != exp_mean:
            fail(f"tab:vreal `{prefix}` mismatch: got {cols[2:5]} vs ({exp_p} / 22, {exp_pct}, {exp_mean})")
        checks += 3

    # 5. Bibliography, README (228 passes), & no stale files in REPO / paper
    bib = BIB_PATH.read_text(encoding="utf-8")
    if "Roh, Youjeong" not in bib or "Noh, Youjeong" in bib:
        fail("Bibliography gmba2025 must list `Roh, Youjeong`!")
    if README_PATH.exists():
        rd = README_PATH.read_text(encoding="utf-8")
        if "228 archived" not in rd:
            fail("README.md must state `228 archived` passes for `--mode full`!")
    for stale in ("paper-en.md", "paper-es.md", "paper-es.pdf", "references.bib", "style.css"):
        if (REPO / "paper" / stale).exists():
            fail(f"Stale duplicate file `{stale}` exists in `{REPO / 'paper'}`!")
    checks += 6

    # 6. Portable git commit SHA verification
    git_root = _resolve_git_root()
    shas = re.findall(r"commit\s+\\texttt\{([0-9a-f]{7,40})\}", tex)
    if not shas:
        fail("No public commit SHA cited in main.tex!")
    for sha in shas:
        rc = subprocess.run(["git", "-C", str(git_root), "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True).returncode
        if rc != 0:
            fail(f"Cited commit SHA {sha} does NOT exist in git repository `{git_root}`!")
        checks += 1

    return checks


def main() -> None:
    tex = TEX_PATH.read_text(encoding="utf-8")
    checks = check_tex_text(tex)
    print(f"VERIFY_PAPER_CLAIMS_V6: PASS ({checks} exact-cell, pct, time, README, bib & portable-git checks verified)")


if __name__ == "__main__":
    main()
