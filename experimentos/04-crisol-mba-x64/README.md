# CRISOL-MBA-x64 — Artifact Evaluation & Reproduction Package (v1.0.0)

Official artifact repository for **"CRISOL-MBA-x64: Certified Neuro-Symbolic Deobfuscation of x86-64 Machine-Code Slices via Hybrid CEGIS and Lean 4 `bv_decide`"**.

- **Author:** Luis Alejandro Arancibia (Computer Engineer, FIUBA / UBA · CrisoLabs Research Lab)
- **Canonical Paper PDF:** [`paper/paper-en.pdf`](paper/paper-en.pdf) (compiled directly from [`paper/arxiv-v1/main.tex`](paper/arxiv-v1/main.tex))
- **Reserved Zenodo DOI:** `10.5281/zenodo.24476603` (resolves upon Zenodo publication)
- **License:** MIT ([`LICENSE`](LICENSE))

---

## 1. System Requirements & Toolchain Setup (Linux x86-64)

### Python Environment (`>= 3.11`)
```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .
```

### External Formal Verifiers (`build/`)
`replay_offline.py` and `run_phase2.py` expect the following local binaries under `build/` (excluded from Git via `.gitignore`):
1. **`CaDiCaL` (`build/cadical/build/cadical`)** — CaDiCaL `>= 2.0` / `3.1.0` compiled from source (`git clone https://github.com/arminbiere/cadical build/cadical && cd build/cadical && ./configure && make`).
2. **`lrat-check` (`build/drat-trim/lrat-check`)** — Independent LRAT proof checker (`git clone https://github.com/marijnheule/drat-trim build/drat-trim && make -C build/drat-trim lrat-check`).
3. **Lean 4.36.0 (`build/elan` + `build/lean_proj`)** — Install `elan` with `ELAN_HOME="$PWD/build/elan"` and initialize a Lean `v4.36.0` project in `build/lean_proj` (`echo "leanprover/lean4:v4.36.0" > build/lean_proj/lean-toolchain`).

---

## 2. Deterministic Paper & Checksum Verification (Zero External Solvers Needed)

Verify every cell of Tables 2–4, strict wall-clock cutoffs, subset counts, and SHA-256 manifests directly against raw `.jsonl`/`.csv` logs:

```bash
.venv/bin/python verify_paper_claims.py
.venv/bin/pytest -q
```

---

## 3. Offline Certificate Replay & Figure Regeneration (Zero LLM API Keys)

Re-verifies cached `Hybrid H` outputs (`--mode smoke`: 12 slices in ~30 s; `--mode full`: all 182 archived `H` passes across `V_test` and `V_real`, checking canonical cost, LRAT, and Lean 4 `bv_decide`) and regenerates `paper/fig1..fig3`:

```bash
.venv/bin/python replay_offline.py --mode smoke
```
