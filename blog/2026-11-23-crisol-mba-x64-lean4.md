---
titulo: "CRISOL-MBA·x64: Certified x86-64 Deobfuscation with Lean 4 bv_decide"
subtitulo: "Pairing zero-trust formal verification with neural synthesis to certify real gcc/clang -O2 x86-64 machine-code slices"
fecha: "2026-11-23"
autor: "Luis Alejandro Arancibia"
categoria: "Formal Verification"
slug_par: "2026-11-23-crisol-mba-x64-lean4"
---

*By **Luis Alejandro Arancibia** (CrisoLabs Research Lab · ORCID: [0009-0003-6453-575X](https://orcid.org/0009-0003-6453-575X)) — Publication #7 · November 2026*

In binary reverse engineering, malware analysis, and security auditing, there is a persistent gap between deobfuscation theory and compiled machine code. Mixed Boolean-Arithmetic (MBA) obfuscation replaces simple operations with algebraically equivalent yet structurally opaque combinations of `+`, `-`, `*`, `&`, `|`, `^`, and `~`. On pure expression trees over $\mathbb{Z}_{2^n}$, algebraic simplifiers such as SiMBA, GAMBA, ProMBA, and RUMBA are fast. Once those identities are lowered by optimizing compilers (`gcc -O2`, `clang -O2`) or assembly-level obfuscators into x86-64 machine code, however, the resulting basic blocks entangle arithmetic with architecture-specific semantics: explicit Carry Flag (`CF`) chains via `ADC`/`SBB`, implicit 32-to-64-bit zero-extension, arithmetic right shifts (`SAR`), and bit rotations (`ROL`/`ROR`).

Existing approaches hit a three-way impasse:

1. **Algebraic simplifiers** cannot represent most compiled x86-64 slices. In our evaluation, official **GAMBA** (uncertified algebraic simplification) covers only **25.00% (40/160)** of test slices because its algebraic adapter cannot encode `ADC`, `SBB`, `ROL`, `ROR`, or 32-to-64-bit zero-extension inside a single 64-bit expression.
2. **Black-box search and superoptimization** (STOKE, Xyntia) handle machine semantics via I/O traces, but suffer severe combinatorial explosion once expressions combine 3–4 inputs, carry propagation, shifts, and rotations.
3. **Purely neural approaches** (LLM4Decompile, gMBA) recover readable approximations, yet operate on expression strings or evaluate only finite test-case re-executability. For a security analyst, a simplification that silently diverges on a single corner case out of $2^{64}$ inputs is worse than no simplification at all.

**CRISOL-MBA·x64** is built on a principle borrowed from formal mathematics: finding a simplified form is hard, but verifying universal equivalence against the original binary is completely objective and machine-checkable. Accordingly, **the LLM is never part of the Trusted Computing Base (TCB)**. Its sole role is candidate synthesis; final acceptance rests exclusively with SMT solvers, **LRAT** proof certificates, and **Lean 4 `bv_decide`**.

---

## Architecture: Zero Trust in the Model

CRISOL-MBA·x64 runs a five-stage pipeline over straight-line, register-only x86-64 slices of at most 24 instructions drawn from a closed 17-mnemonic allowlist (`MOV`, `LEA_reg`, `ADD`, `ADC`, `SUB`, `SBB`, `NEG`, non-nested `IMUL`, `AND`, `OR`, `XOR`, `NOT`, `SHL`/`SAL`, `SHR`, `SAR`, `ROL`, `ROR`) with no memory accesses, branches, or system calls:

1. **Deterministic Extraction (0 tokens):** `capstone` decodes raw bytes, enforces the 17-mnemonic allowlist and 24-instruction bound, and extracts active input registers, carry usage, output width hints, and immediate constants.
2. **Candidate Synthesis:** We evaluate deterministic baselines (`A`: SiMBA + cost-bounded enumerator; `C`: Xyntia/STOKE-style no-LLM MCMC-CEGIS) alongside neural synthesis (`B`: One-Shot with $K=8$ candidates; `D`: sequential CEGIS $4 \times 2$ with counterexample feedback; and `H`: a Hybrid architecture running Wide One-Shot $K=6 \to$ CEGIS fallback $2 \times 2$).
3. **Vectorized Concrete Pre-Filter:** `numpy` evaluates each candidate on $\ge 1{,}024$ concrete vectors (boundaries $\{0, 1, -1, 2^{31}, 2^{32}-1, 2^{63}, 2^{64}-1\}$, all 64 one-hot bit positions, and seeded pseudo-random vectors with $\texttt{cf} \in \{0,1\}$) in under 1 ms. The pre-filter *only rejects*; it never approves.
4. **Dual `QF_BV` Oracle & Native Replay:** Bitwuzla and Z3 check $\exists \vec{x}.\ F_B(\vec{x}) \neq \llbracket e \rrbracket(\vec{x})$. Any `SAT` vs. `UNSAT` disagreement raises `OracleDisagreementError`. Every `SAT` counterexample is re-executed on native x86-64 CPU; failure to reproduce triggers `LIFTER_BUG` and counts as `FAIL`.
5. **Independent Proof Certification:** Every `UNSAT` verdict must be backed either by `CaDiCaL 3.1.0` + `lrat-check` (with deterministic DIMACS header normalization fixing Z3's `goal.dimacs()` off-by-one `max_var` bug) or by **Lean 4.36.0 `bv_decide`**. Timeouts and unknowns strictly count as `FAIL`.

### Explicit TCB Boundary and Lifter Validation

We state precisely where the formal guarantee begins. Under `CaDiCaL + lrat-check`, the SAT solver is *outside* the TCB, while Z3's bit-blaster remains inside. Under **Lean 4 `bv_decide`**, the bit-blaster itself is formally verified inside Lean, leaving Lean's kernel and runtime (`Lean.ofReduceBool`), our Python theorem emitter (`oracle_lean.py`), and the minimalist x86-64 lifter in the TCB.

To empirically anchor lifter fidelity ($B \to F_B$), a mandatory Sanity Gate executes every slice across three independent engines—native x86-64 CPU (`mmap RX` trampoline), Unicorn CPU emulator, and our `QF_BV` lifter—on 1,024 concrete vectors: **82,944 three-way checks with 0 discrepancies**, covering all 31 instruction unit tests, 28 dataset-sanity slices, and all 22 `V_real` slices.

---

## Anti-Leakage Protocol and Hardness Separation

Before running any model on test data, hypotheses, thresholds ($+15\text{ pp}$, cost margin $\varepsilon = 0.10$, exact McNemar $\alpha = 0.01$), and instruction allowlists were pre-registered and SHA-256 frozen (`docs/03-preregistro-crisol-mba-x64.md`). Identity families were partitioned strictly prior to assembly with GNU `as` + `objcopy` (4 development families disjoint from 10 test families), and search hardness was separated from verification hardness: certifying ground-truth equivalence $F_B \equiv g$ under a 10 s LRAT budget split the 200 test slices into **$V_{\text{test}}$ ($N = 160$)** and **$V_{\text{hard}}$ ($N = 40$)**, the latter consisting of 32-bit and 64-bit `IMUL` polynomial slices where raw Z3 bit-blasting timed out.

Semantic mutation testing (constant $+1$, `ADD`$\leftrightarrow$`ADC`, inverted `CF`, omitted 32-bit zero-extension, cost exceeded) and pre-filter-evading negatives yielded **0 false positives**.

---

## Experimental Results

### 1. Blind Out-of-Sample Evaluation on $V_{\text{test}}$ ($N = 160$, 60 s Wall-Clock Budget)

| Configuration | Description | PASS / 160 | Rate | Mean Time | Mean LLM Calls |
|---|---|---:|---:|---:|---:|
| `A` | SiMBA + cost-bounded enumerator (LRAT) | 20 / 160 | 12.50% | 0.88 s | 0.00 |
| `GAMBA` | Official Denuvo GAMBA *(uncertified)* | 40 / 160 | 25.00% | — | 0.00 |
| `C` | Xyntia/STOKE-style MCMC-CEGIS (LRAT) | 42 / 160 | 26.25% | 50.50 s | 0.00 |
| `A ∪ C` | Virtual best deterministic | 42 / 160 | 26.25% | — | 0.00 |
| **`D` (Confirmatory)** | **CRISOL CEGIS (`gemini-4-hydrogen-medium`, $4\times 2$, LRAT)** | **146 / 160** | **91.25%** | **26.65 s** | **1.32** |
| `B` | LLM One-Shot ($K=8$, LRAT) | 154 / 160 | 96.25% | 25.29 s | 1.00 |
| **`H` (Exploratory)** | **CRISOL Hybrid ($K=6 \to 2\times 2$, LRAT)** | **160 / 160** | **100.00%** | **29.60 s** | **1.01** |
| `H` (`gpt-6.2-sol`, subset) | Stratified cross-family subset ($N = 40$, LRAT) | 40 / 40 | 100.00% | 28.51 s | — |

The pre-registered confirmatory hypothesis (`D` vs. `A ∪ C`) was confirmed with a **$+65.0\text{ pp}$** gain (**91.25%** vs. 26.25%, exact McNemar $p = 9.86 \times 10^{-32}$).

Comparing `D` (91.25%) with `B` (96.25%) exposed a clear latency–diversity trade-off: under a strict 60 s wall-clock cap, `D` rescued all 6 failures of `B` via counterexample feedback, yet lost 14 instances on `3var_carry_64` and `rotate_mix_64` because sequential CLI rounds exhausted the budget before reaching 8 samples. This observation motivated our **Hybrid `H`** architecture (explicitly reported as **exploratory post-hoc**), which samples 6 diverse candidates in Round 1 and invokes CEGIS only if all fail—reaching **160/160 (100.0%; 95% Clopper-Pearson CI $[97.7\%, 100\%]$; $p = 6.02 \times 10^{-36}$ vs. `A ∪ C`)**. All **362** Phase 1 `PASS` verdicts (`A+B+C+D`) were independently re-verified (355 via `CaDiCaL + lrat-check` and 7 via Lean 4 `bv_decide`), with 0 `FAIL_SAT` and 0 `LIFTER_BUG`.

---

### 2. The Multiplication Certification Frontier: $V_{\text{hard}}$ ($N = 40$)

On $V_{\text{hard}}$, we evaluate ground-truth equivalence certification ($F_B \equiv g$) across 40 `IMUL`-entangled slices (20 at 32-bit, 20 at 64-bit):

| Family ($n = 20$ each) | Z3 `QF_BV` (unverified) | Z3 bit-blast + CaDiCaL LRAT | Bitwuzla `QF_BV` (unverified) | **Lean 4 `bv_decide` (Certified)** | Mean Lean 4 Time |
|---|---:|---:|---:|---:|---:|
| `test_mba_poly_mul_32` | 0 / 20 (0%) | 0 / 20 (0%) | 20 / 20 (100%) | **20 / 20 (100%)** | 8.22 s |
| `test_mba_poly_mul_64` | 0 / 20 (0%) | 0 / 20 (0%) | 20 / 20 (100%) | **12 / 20 (60%)** | 14.92 s |
| **Total `V_hard`** | **0 / 40 (0%)** | **0 / 40 (0%)** | **40 / 40 (100%)** | **32 / 40 (80%)** | **11.57 s** |

While uncertified Bitwuzla closes 40/40, raw Z3 bit-blasting + CaDiCaL LRAT times out on **0/40**. **Lean 4 `bv_decide`** performs Bitwuzla-inspired word-level normalization prior to verified bit-blasting and LRAT checking, raising certified proofs from **0/40 to 32/40 (80.0%)**—including **20/20 (100%)** on 32-bit `IMUL` in 8.22 s mean time—while removing the bit-blaster from the TCB. The remaining 8/20 64-bit `IMUL` slices mark the open frontier for intermediate-lemma decomposition.

---

### 3. Real `gcc -O2` and `clang -O2` Compiled C Corpus: $V_{\text{real}}$ ($N = 22$)

To test generalization beyond synthetic families, we compiled 22 real C functions (hash mixers, ARX rounds, signed 32-bit shifts, and 64-bit affine multipliers) with `gcc -O2` and `clang -O2` under the exact same 17-mnemonic allowlist:

| Configuration | Certification Oracle | PASS / 22 | Rate | Mean Time | McNemar vs. `A ∪ C` |
|---|---|---:|---:|---:|---:|
| `A` (SiMBA + Enum) | LRAT | 0 / 22 | 0.00% | 2.28 s | — |
| `C` (MCMC-CEGIS) | LRAT | 0 / 22 | 0.00% | 60.02 s | — |
| `H-sol` (`gpt-6.2-sol`) | Lean 4 `bv_decide` | 6 / 22 | 27.27% | 55.12 s | $p = 0.0313$ *(n.s. at $\alpha = 0.01$)* |
| **`H-hydrogen` (`gemini-4-hydrogen-medium`)** | **Lean 4 `bv_decide`** | **22 / 22** | **100.00%** | **23.44 s** | **$p = 4.77 \times 10^{-7}$** |

Once `gcc -O2` and `clang -O2` fuse instructions, select `LEA` scaling, and emit 64-bit `IMUL` alongside 32-bit zero-extension, both deterministic baselines `A` and `C` collapse to **0%**. **CRISOL-MBA·x64 Hybrid `H` + Lean 4 `bv_decide`** certifies **22/22 (100.0%; 95% CI $[84.6\%, 100\%]$)** in 23.44 s mean time. The contrast with `H-sol` (27.27%, penalized by 55.12 s mean CLI latency under the 60 s cap) highlights that inference latency is a first-order determinant of CEGIS effectiveness under tight wall-clock budgets.

---

## Scope and Limitations

CRISOL-MBA·x64 intentionally restricts slices to $\le 24$ straight-line, register-only instructions without memory aliasing or unbounded loops; extending certified lifting to memory-bearing CFG regions or commercial virtualizers (such as Tigress or VMProtect) requires an upstream devirtualization and slicing stage. Within that boundary, the evidence is clear and reproducible: neural synthesis can deobfuscate real `-O2` x86-64 machine code without ever asking the analyst to trust the model.
