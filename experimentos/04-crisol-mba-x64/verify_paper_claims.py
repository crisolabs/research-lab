#!/usr/bin/env python3
"""
Deterministic Zero-LLM Pre-Publication Gate for CRISOL-MBA-x64 (`verify_paper_claims.py` v6).

Portable (zero hardcoded author paths) and checks EXACT string equality (`==`) on EVERY
count, percentage, in-flight bracket, mean/max time, LLM-call, and McNemar p-value cell of
Tables `tab:vtest`, `tab:vhard`, and `tab:vreal`, plus full-document p-values (McNemar +
family sign test) with whitespace/LaTeX-aware operator guards, Abstract/Conclusion fraction
and percentage sequences, all three SHA-256 manifests (`data/manifest_V.sha256`,
`data/manifest_V_real.sha256`, `docs/SHA256SUMS.txt`) pinned to their exact target files,
LRAT digests, bibliography, README consistency, and git commit existence (`--allow-no-git`
supported for `.git`-less Zenodo archive snapshots).
"""
import argparse
import csv
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
TEX_PATH = REPO / "paper" / "arxiv-v1" / "main.tex"
BIB_PATH = REPO / "paper" / "arxiv-v1" / "references.bib"
README_PATH = REPO / "README.md"

# Whitespace- and LaTeX-wrapper-aware arithmetic modifier guards:
# Catches `$-$96.25\%`, `− 96.25\%`, `-\textbf{96.25\%}`, `p = 0.078 / 10`, `$p = 0.078$ / 10`, etc.
_MODIFIER_LEFT_RE = re.compile(
    r"(?:(?<!-)--(?!-)|(?<!-)-(?!-)|[+−/*^]|\\(?:pm|mp|minus|times|cdot|div|frac))\s*"
    r"(?:\\,|~|\$|\{|\}|\\textbf\{|\\emph\{|\\texttt\{|\s)*$"
)
_MODIFIER_RIGHT_RE = re.compile(
    r"^(?:\\,|~|\$|\{|\}|\s)*(?:(?<!-)--(?!-)|(?<!-)-(?!-)|[+−/*^]|\\(?:pm|mp|minus|times|cdot|div)\b|\d)"
)


def _assert_clean_numeric_context(text: str, start: int, end: int, label: str) -> None:
    left = text[max(0, start - 32):start]
    right = text[end:min(len(text), end + 32)]
    if _MODIFIER_LEFT_RE.search(left):
        fail(f"{label} has unexpected arithmetic sign/operator prefix in `{left}{text[start:end]}`")
    if _MODIFIER_RIGHT_RE.search(right):
        fail(f"{label} has unexpected arithmetic operator/digit suffix in `{text[start:end]}{right}`")


def _resolve_git_root() -> Path | None:
    r = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        return Path(r.stdout.strip())
    return None


def fail(msg: str) -> None:
    print(f"[PAPER_GATE: FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def strip_tex(s: str) -> str:
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"\\(?:textbf|texttt|emph)\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", r"\1", s)
    return s.replace("\\\\", "").replace(r"\,", " ").replace(r"\%", "%").strip()


def exact_binom_two_sided(n10: int, n01: int) -> float:
    n = n10 + n01
    if n == 0:
        return 1.0
    k = min(n10, n01)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2.0 * tail)


def mcnemar_sets(a: set[str], b: set[str]) -> float:
    return exact_binom_two_sided(len(a - b), len(b - a))


def fmt_dec_half_up(p: float, places: int) -> str:
    q = Decimal("10") ** (-places)
    return str(Decimal(str(p)).quantize(q, rounding=ROUND_HALF_UP))


def fmt_sci_tex(p: float) -> str:
    mant, exp = f"{p:.2e}".split("e")
    return f"{mant} \\times 10^{{{int(exp)}}}"


def verify_sha256_manifest(manifest_path: Path, base_dir: Path, expected_targets: list[str]) -> int:
    if not manifest_path.exists():
        fail(f"Missing required SHA-256 manifest: {manifest_path}")
    seen_targets: list[str] = []
    for raw in manifest_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            fail(f"Malformed SHA-256 line in {manifest_path}: {line}")
        exp_hash, rel = parts
        seen_targets.append(rel)
        target = (base_dir / rel).resolve()
        try:
            target.relative_to(REPO.resolve())
        except ValueError:
            fail(f"SHA-256 target escapes repository root: {target}")
        if not target.is_file():
            fail(f"SHA-256 target missing: {target}")
        got_hash = hashlib.sha256(target.read_bytes()).hexdigest()
        if got_hash != exp_hash:
            fail(f"SHA-256 mismatch for {target}: got {got_hash} vs {exp_hash}")
    if seen_targets != expected_targets:
        fail(f"SHA-256 manifest target list mismatch in {manifest_path}: got {seen_targets} vs {expected_targets}")
    return len(seen_targets)


def check_tex_text(tex: str, *, allow_no_git: bool = False) -> int:
    checks = 0

    # 0. Unconditionally verify ALL THREE SHA-256 manifests pinned to their exact target files
    expected_manifests = ["data/manifest_V.sha256", "data/manifest_V_real.sha256", "docs/SHA256SUMS.txt"]
    found_manifests = sorted(
        p.relative_to(REPO).as_posix()
        for p in REPO.rglob("*")
        if p.is_file() and ".git" not in p.parts and (p.suffix == ".sha256" or p.name.startswith("SHA256SUMS"))
    )
    if found_manifests != expected_manifests:
        fail(f"SHA-256 manifest inventory mismatch: got {found_manifests} vs {expected_manifests}")
    checks += 1
    checks += verify_sha256_manifest(REPO / "data" / "manifest_V.sha256", REPO / "data", ["manifest_V.json"])
    checks += verify_sha256_manifest(REPO / "data" / "manifest_V_real.sha256", REPO / "data", ["manifest_V_real.json"])
    checks += verify_sha256_manifest(
        REPO / "docs" / "SHA256SUMS.txt",
        REPO,
        [
            "docs/01-sintesis-pentamodal-elite.md",
            "docs/02-revision-bibliografica-2024-2026.md",
            "docs/03-preregistro-crisol-mba-x64.md",
        ],
    )

    mv = json.loads((REPO / "data" / "manifest_V.json").read_text(encoding="utf-8"))
    vtest = mv["V_test"]
    fam_by_id = {d["instance_id"]: d["family"] for d in vtest}
    gamba_ids = {d["instance_id"] for d in vtest if d["family"] in ("test_mba_3var_linear_64", "test_mba_nand_nor_add_64")}
    le10_ids = {d["instance_id"] for d in vtest if d["gt_cert_sec"] <= 10.0}
    n120_ids = {d["instance_id"] for d in vtest if d["family"] not in ("test_mba_nand_nor_add_64", "test_mba_sar_neg_32")}

    rows_t = [json.loads(l) for l in (REPO / "data" / "results_test.jsonl").open() if l.strip()]
    rows_h = [json.loads(l) for l in (REPO / "data" / "results_test_H_hydrogen.jsonl").open() if l.strip()]
    rows_hs = [json.loads(l) for l in (REPO / "data" / "results_test_H_sol40.jsonl").open() if l.strip()]

    # Verify 362 Phase-1 PASS LRAT SHA-256 digests and 0 final LIFTER_BUG verdicts
    p1_passes = [r for r in rows_t if r["passed"]]
    if len(p1_passes) != 362 or any(not re.fullmatch(r"[0-9a-f]{64}", r.get("lrat_sha256") or "") for r in p1_passes):
        fail("Phase 1 results_test.jsonl must have 362 PASS entries all with 64-hex lrat_sha256 digests")
    if any(r.get("status") == "LIFTER_BUG" for r in rows_t + rows_h + rows_hs):
        fail("Unexpected LIFTER_BUG verdict in V_test logs")
    checks += 2

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
    ac_strict = strict_sets["A"] | strict_sets["C"]
    ac_inflight = inflight_sets["A"] | inflight_sets["C"]
    d_129 = len(strict_sets["D"] & le10_ids)
    ac_129 = len(ac_strict & le10_ids)
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

    # 4. Table tab:vreal exact equality (including McNemar p-value column derived from raw JSONL!)
    vr_rows = [json.loads(l) for l in (REPO / "data" / "results_real_o2.jsonl").open() if l.strip()]
    vr_sets = {
        cfg: {r["instance_id"] for r in vr_rows if r["config"] == cfg and r["passed"] and r["elapsed_sec"] <= 60.0}
        for cfg in ("A", "C", "H_sol", "H_hydrogen")
    }
    vr_ac = vr_sets["A"] | vr_sets["C"]
    p_vr_hsol = mcnemar_sets(vr_sets["H_sol"], vr_ac)
    p_vr_hhyd = mcnemar_sets(vr_sets["H_hydrogen"], vr_ac)

    tab_vreal = tex.split(r"\label{tab:vreal}")[0].split(r"\begin{table}")[-1]
    for prefix, cfg_name, star, exp_pcol in [
        ("$A$", "A", "", "---"),
        ("$C$", "C", "*", "---"),
        (r"\texttt{H-sol}", "H_sol", "", f"$p = {fmt_dec_half_up(p_vr_hsol, 4)}$ (n.s.\\ at $\\alpha=0.01$)"),
        (r"\textbf{\texttt{H-hydrogen}}", "H_hydrogen", "", f"$p = {fmt_sci_tex(p_vr_hhyd)}$"),
    ]:
        matched = [ln for ln in tab_vreal.splitlines() if ln.strip().startswith(prefix)]
        if len(matched) != 1:
            fail(f"Could not locate `{prefix}` in tab:vreal")
        cols = [strip_tex(c) for c in matched[0].split("&")]
        sub = [r for r in vr_rows if r["config"] == cfg_name]
        exp_p = len(vr_sets[cfg_name])
        exp_pct = f"{100.0 * exp_p / 22:.2f}"
        exp_mean = f"{sum(r['elapsed_sec'] for r in sub)/len(sub):.2f}{star}"
        if cols[2] != f"{exp_p} / 22" or cols[3] != exp_pct or cols[4] != exp_mean or cols[5] != exp_pcol:
            fail(f"tab:vreal `{prefix}` mismatch: got {cols[2:6]} vs ({exp_p} / 22, {exp_pct}, {exp_mean}, {exp_pcol})")
        checks += 4

    # 4b. Full-document exact p-value verification (17 McNemar + 3 sign-test occurrences)
    # with whitespace/LaTeX-aware suffix guard (blocks `p = 0.078 / 10`, `$p = 0.078$ / 10`, `p = -0.078`, etc.)
    fams = sorted(set(fam_by_id.values()))
    fam_wins = sum(
        1 for f in fams
        if len({i for i in strict_sets["D"] if fam_by_id[i] == f}) > len({i for i in ac_strict if fam_by_id[i] == f})
    )
    fam_losses = sum(
        1 for f in fams
        if len({i for i in strict_sets["D"] if fam_by_id[i] == f}) < len({i for i in ac_strict if fam_by_id[i] == f})
    )
    p_fam_two = exact_binom_two_sided(fam_wins, fam_losses)
    p_fam_one = p_fam_two / 2.0

    exp_all_pvals = [
        fmt_sci_tex(mcnemar_sets(strict_sets["D"], ac_strict)),                  # Abstract: D vs A|C strict
        f"{p_fam_two:.4f}",                                                      # Abstract: family sign test
        fmt_sci_tex(mcnemar_sets(strict_sets["H"], ac_strict)),                  # Abstract: H vs A|C strict
        fmt_sci_tex(p_vr_hhyd),                                                  # Abstract: V_real H-hydrogen
        f"{p_vr_hsol:.3f}",                                                      # Abstract: V_real H-sol (0.031)
        fmt_sci_tex(mcnemar_sets(strict_sets["D"], ac_strict)),                  # Sec 4 H1: D vs A|C strict
        fmt_sci_tex(mcnemar_sets(inflight_sets["D"], ac_inflight)),              # Sec 4 H1: D vs A|C in-flight
        fmt_sci_tex(mcnemar_sets(strict_sets["D"] & le10_ids, ac_strict & le10_ids)),  # Sec 4 H1: N=129
        f"{p_fam_two:.4f}",                                                      # Sec 4 H1: family two-sided
        f"{p_fam_one:.4f}",                                                      # Sec 4 H1: family one-sided
        fmt_sci_tex(mcnemar_sets(strict_sets["D"] & n120_ids, ac_strict & n120_ids)),  # Sec 4 H1: N=120 D
        fmt_sci_tex(mcnemar_sets(strict_sets["H"] & n120_ids, ac_strict & n120_ids)),  # Sec 4 H1: N=120 H
        f"{mcnemar_sets(strict_sets['D'], strict_sets['B']):.3f}",               # Sec 4 H2: D vs B strict
        f"{mcnemar_sets(inflight_sets['D'], inflight_sets['B']):.3f}",           # Sec 4 H2: D vs B in-flight
        fmt_sci_tex(mcnemar_sets(strict_sets["H"], ac_strict)),                  # Sec 4 H: H vs A|C strict
        f"{mcnemar_sets(strict_sets['H'], strict_sets['B']):.3f}",               # Sec 4 H: H vs B strict
        f"{fmt_dec_half_up(p_vr_hsol, 4)}",                                      # Table 4: V_real H-sol (0.0313)
        fmt_sci_tex(p_vr_hhyd),                                                  # Table 4: V_real H-hydrogen
        fmt_sci_tex(mcnemar_sets(strict_sets["D"], ac_strict)),                  # Conclusion: D vs A|C strict
        fmt_sci_tex(mcnemar_sets(strict_sets["D"] & le10_ids, ac_strict & le10_ids)),  # Conclusion: N=129
    ]
    total_peq = len(re.findall(r"\bp\s*=", tex))
    pval_matches = list(re.finditer(r"\bp\s*=\s*(\d+\.\d+\s*\\times\s*10\^\{-?\d+\}|\d+\.\d+)", tex))
    got_all_pvals = [m.group(1) for m in pval_matches]
    if total_peq != len(exp_all_pvals) or got_all_pvals != exp_all_pvals:
        fail(f"Document p-value sequence mismatch (total `p =`={total_peq}):\n  got={got_all_pvals}\n  exp={exp_all_pvals}")
    for m in pval_matches:
        right = tex[m.end():min(len(tex), m.end() + 32)]
        if _MODIFIER_RIGHT_RE.search(right):
            fail(f"Document p-value has unexpected trailing operator/digit in `{m.group(0)}{right}`")
    checks += len(exp_all_pvals)

    # 5. Bibliography, README (228 passes verified against JSONLs), & no stale files in REPO / paper
    h_hyd_passes = len(inflight_sets["H"]) + len(vr_sets["H_hydrogen"])
    h_sol_passes = sum(1 for r in rows_hs if r["passed"]) + len(vr_sets["H_sol"])
    total_h_passes = h_hyd_passes + h_sol_passes
    if (h_hyd_passes, h_sol_passes, total_h_passes) != (182, 46, 228):
        fail(f"Unexpected archived H pass counts: {(h_hyd_passes, h_sol_passes, total_h_passes)}")
    bib = BIB_PATH.read_text(encoding="utf-8")
    if "Roh, Youjeong" not in bib or "Noh, Youjeong" in bib:
        fail("Bibliography gmba2025 must list `Roh, Youjeong`!")
    if README_PATH.exists():
        rd = README_PATH.read_text(encoding="utf-8")
        if f"{total_h_passes} archived" not in rd:
            fail(f"README.md must state `{total_h_passes} archived` passes for `--mode full`!")
    for stale in ("paper-en.md", "paper-es.md", "paper-es.pdf", "references.bib", "style.css"):
        if (REPO / "paper" / stale).exists():
            fail(f"Stale duplicate file `{stale}` exists in `{REPO / 'paper'}`!")
    checks += 7

    # 5b. Exact token-list & whitespace/LaTeX-aware context guards in Abstract & Conclusion!
    abstract = tex.split(r"\begin{abstract}")[1].split(r"\end{abstract}")[0]
    conclusion = tex.split(r"\paragraph{Conclusion.}")[1].split(r"\bibliographystyle")[0]
    exp_abs_fracs = [
        "39/160", "42/160", "40/40", "40/160", "145/160", "146/160", "121/129", "32/129",
        "154/160", "159/160", "160/160", "119/120", "19/120", "40/40",
        "40/40", "0/40", "2/40", "3/40", "35/40", "20/20", "15/20",
        "0/22", "22/22", "6/22",
    ]
    exp_abs_pcts = [
        "24.38%", "26.25%", "100%", "25.00%", "90.62%", "91.25%", "96.25%",
        "99.38%", "95%", "96.6%", "100%", "100.0%", "99.17%", "15.83%", "100.0%",
        "0.0%", "5.0%", "7.5%", "87.5%", "100%", "75%",
        "0.0%", "100.0%", "95%", "84.6%", "100%", "27.27%",
    ]
    exp_conc_fracs = ["159/160", "160/160", "22/22", "2/40", "3/40", "35/40"]
    exp_conc_pcts = ["99.38%", "95%", "96.6%", "100%", "95%", "84.6%", "100%", "5.0%", "87.5%"]

    for sec_name, sec_txt, exp_fr, exp_pc in [
        ("Abstract", abstract, exp_abs_fracs, exp_abs_pcts),
        ("Conclusion", conclusion, exp_conc_fracs, exp_conc_pcts),
    ]:
        raw_slash_pairs = len(re.findall(r"\d\s*/\s*\d", sec_txt))
        fr_matches = list(re.finditer(r"\b\d+/\d+\b", sec_txt))
        got_fr = [m.group(0) for m in fr_matches]
        if raw_slash_pairs != len(exp_fr) or got_fr != exp_fr:
            fail(f"{sec_name} fraction sequence mismatch (pairs={raw_slash_pairs}): got {got_fr} vs {exp_fr}")
        for m in fr_matches:
            _assert_clean_numeric_context(sec_txt, m.start(), m.end(), f"{sec_name} fraction `{m.group(0)}`")

        raw_pct_cnt = sec_txt.count(r"\%")
        pc_matches = list(re.finditer(r"\d+(?:\.\d+)?\\%", sec_txt))
        got_pc = [m.group(0).replace(r"\%", "%") for m in pc_matches]
        if raw_pct_cnt != len(exp_pc) or got_pc != exp_pc:
            fail(f"{sec_name} percentage sequence mismatch (cnt={raw_pct_cnt}): got {got_pc} vs {exp_pc}")
        for m in pc_matches:
            _assert_clean_numeric_context(sec_txt, m.start(), m.end(), f"{sec_name} percentage `{m.group(0)}`")
        checks += 2

    # 6. Portable git commit SHA verification (`--allow-no-git` for `.git`-less Zenodo archive downloads)
    shas = re.findall(r"commit\s+\\texttt\{([0-9a-f]{7,40})\}", tex)
    if not shas:
        fail("No public commit SHA cited in main.tex!")
    git_root = _resolve_git_root()
    if git_root is None:
        if not allow_no_git:
            fail(
                "Not inside a Git repository with commit history; run inside a full clone of "
                "`crisolabs/research-lab` (containing commit 42c3d22) or pass `--allow-no-git` "
                "when verifying an extracted Zenodo snapshot without `.git`."
            )
    else:
        for sha in shas:
            rc = subprocess.run(["git", "-C", str(git_root), "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True).returncode
            if rc != 0:
                fail(
                    f"Cited commit SHA {sha} does NOT exist in git repository `{git_root}` "
                    "(ensure full clone without `--depth 1`, or pass `--allow-no-git` for `.git`-less Zenodo archives)!"
                )
            checks += 1

    return checks


def main() -> None:
    ap = argparse.ArgumentParser(description="Deterministic Zero-LLM Pre-Publication Gate for CRISOL-MBA-x64")
    ap.add_argument(
        "--allow-no-git",
        action="store_true",
        help="Skip `git cat-file -e` check when running inside an extracted Zenodo archive without `.git` history.",
    )
    args = ap.parse_args()
    tex = TEX_PATH.read_text(encoding="utf-8")
    checks = check_tex_text(tex, allow_no_git=args.allow_no_git)
    suffix = " (git history check skipped via --allow-no-git)" if args.allow_no_git and _resolve_git_root() is None else ""
    print(f"VERIFY_PAPER_CLAIMS_V6: PASS ({checks} exact-cell, p-val, 3-sha256-manifests, pct, time, README, bib & git checks verified){suffix}")


if __name__ == "__main__":
    main()
