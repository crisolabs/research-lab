"""Gate Día 6-7: Sound Oracle Verification (Bitwuzla+Z3, CaDiCaL LRAT, Mutation Testing, 0 False PASS)."""

from __future__ import annotations

import pytest

from crisol_mba.expr import Binary, Const, Ternary, Unary, Var, canonical_cost
from crisol_mba.generator import assemble_x64, expr_from_dict, generate_dataset
from crisol_mba.oracle_smt import SlicePreFilter, verify_candidate


def test_lrat_verified_pass_on_all_generated_families() -> None:
    """All V-eligible families must PASS with verified LRAT proof; V_hard (mul) may timeout on SAT bit-blasting."""
    instances = generate_dataset(seed=20261123, n_dev_per_family=1, n_test_per_family=1)
    assert len(instances) == 14
    lrat_passed = 0
    for inst in instances:
        code = bytes.fromhex(inst.bytes_hex)
        gt = expr_from_dict(inst.ground_truth_expr)
        pf = SlicePreFilter(code, seed=20261123, n_vectors=1024)
        verdict = verify_candidate(
            code,
            gt,
            max_cost=canonical_cost(gt) * 1.10,
            prefilter=pf,
            timeout_sec=10.0,
            require_lrat=True,
        )
        if inst.family in {"test_mba_poly_mul_32", "test_mba_poly_mul_64"}:
            # Known V_hard candidates: either PASS with LRAT or FAIL_LRAT (timeout), NEVER LIFTER_BUG or SAT
            assert verdict.status in {"PASS", "FAIL_LRAT"}, f"Unexpected status on V_hard: {verdict}"
        else:
            assert verdict.status == "PASS", f"Expected PASS on {inst.instance_id}, got {verdict}"
            assert verdict.lrat_sha256 is not None and len(verdict.lrat_sha256) == 64
            lrat_passed += 1
    assert lrat_passed == 12


def test_mutation_testing_zero_false_pass() -> None:
    """All semantic mutants MUST fail (0 false PASS allowed):
    - Constant perturbed by 1
    - ADD <-> ADC swap
    - Omitted 32-bit zero-extension
    - Inverted CF
    - Cost exceeded
    """
    # 1. Constant perturbed by +1 on (rdi + rsi) + 17
    code1 = assemble_x64("mov rax, rdi\nxor rax, rsi\nmov r8, rdi\nand r8, rsi\nlea rax, [rax + r8*2 + 17]")
    pf1 = SlicePreFilter(code1)
    mut_const = Binary(64, "add", Binary(64, "add", Var(64, "rdi"), Var(64, "rsi")), Const(64, 18))
    v1 = verify_candidate(code1, mut_const, max_cost=10, prefilter=pf1)
    assert v1.status != "PASS" and v1.status != "LIFTER_BUG"

    # 2. ADD instead of ADC (ignores incoming CF)
    code2 = assemble_x64("mov rax, rdi\nadc rax, rsi")
    pf2 = SlicePreFilter(code2)
    mut_add = Binary(64, "add", Var(64, "rdi"), Var(64, "rsi"))
    v2 = verify_candidate(code2, mut_add, max_cost=10, prefilter=pf2)
    assert v2.status in {"FAIL_PREFILTER", "FAIL_SAT"}

    # 3. Inverted CF on ADC
    mut_inv_cf = Ternary(64, "adc", Var(64, "rdi"), Var(64, "rsi"), Unary(1, "not", Var(1, "cf")))
    v3 = verify_candidate(code2, mut_inv_cf, max_cost=10, prefilter=None)  # force SMT SAT + native replay
    assert v3.status == "FAIL_SAT", f"Expected native-reproduced FAIL_SAT, got {v3}"

    # 4. Omitted 32-bit zero-extension: `mov eax, edi; add eax, esi` clears upper 32 bits of rax
    code4 = assemble_x64("mov eax, edi\nadd eax, esi")
    pf4 = SlicePreFilter(code4)
    mut_no_zext = Binary(64, "add", Var(64, "rdi"), Var(64, "rsi"))
    v4 = verify_candidate(code4, mut_no_zext, max_cost=10, prefilter=pf4)
    assert v4.status in {"FAIL_PREFILTER", "FAIL_SAT"}

    # 5. Cost bound enforcement (valid equivalence but too expensive)
    gt_ok = Binary(64, "add", Binary(64, "add", Var(64, "rdi"), Var(64, "rsi")), Const(64, 17))
    v5 = verify_candidate(code1, gt_ok, max_cost=1.0, prefilter=pf1)
    assert v5.status == "FAIL_COST"


def test_prefilter_evading_negative_caught_by_smt_and_native() -> None:
    """A candidate that agrees on ALL 1024 pre-filter points but differs on a single rare input
    MUST still be caught by Bitwuzla+Z3 and reproduced natively (0 false PASS)."""
    # Slice computes: rdi + rsi
    code = assemble_x64("mov rax, rdi\nadd rax, rsi")
    pf = SlicePreFilter(code, seed=20261123, n_vectors=1024)

    # Verify that a subtle mutant differing only when (rdi ^ 0x1337CAFE) == 0:
    # Actually we don't have ITE in Expr, so use a 64-bit arithmetic identity that agrees on
    # small values / boundaries? Even better: test WITHOUT prefilter on a mutant that differs
    # only at bit 32 when rdi has bit 32 set: e.g. bypass prefilter with prefilter=None
    # OR construct a mutant that agrees on all 1024 vectors by testing (rdi + rsi) vs
    # (rdi + rsi) + ((rdi & 0x0000123456780000) == ...). With our AST ops, let's test:
    # Slice: `mov rax, rdi; shr rax, 63` (returns 0 or 1).
    # Wait: even simpler! Slice = `mov rax, rdi; and rax, 0x12345678; xor rax, 0x12345678`.
    # Better: use `prefilter=None` to force the dual SMT miter + native replay directly on a
    # 1-bit-off mutant `((rdi + rsi) ^ (rdi & rsi & (rdi >> 1) & (rsi >> 2) & (rdi >> 3) & (rsi >> 4) & (rdi >> 5) & (rsi >> 6)))`
    # Wait: on 1024 vectors, `a & (a>>1) & ...` is almost always 0, let's check if it passes prefilter!
    x = Var(64, "rdi")
    y = Var(64, "rsi")
    # Product of 20 shifted copies of (x ^ 0x5A5A5A5A5A5A5A5A) & (y ^ 0xA5A5A5A5A5A5A5A5)
    # is 0 on all 1024 test vectors (prob 2^-20 per bit) yet non-zero when x==~0x5A.. and y==~0xA5..!
    t = Binary(64, "and", Binary(64, "xor", x, Const(64, 0x5A5A5A5A5A5A5A5A)), Binary(64, "xor", y, Const(64, 0xA5A5A5A5A5A5A5A5)))
    rare = t
    for sh in (1, 2, 4, 8, 16, 32):
        rare = Binary(64, "and", rare, Binary(64, "ror", rare, Const(64, sh)))
    # `rare` is 0 unless EVERY bit of t is 1 (i.e. x == 0xA5A5... AND y == 0x5A5A..., which is NOT in the 1024 vectors!)
    sneaky_cand = Binary(64, "xor", Binary(64, "add", x, y), rare)

    ok_pf, _, _, _ = pf.check(sneaky_cand)
    assert ok_pf is True, "Sneaky negative should evade the 1024-vector concrete pre-filter!"

    verdict = verify_candidate(code, sneaky_cand, max_cost=50, prefilter=pf, timeout_sec=10.0)
    assert verdict.status == "FAIL_SAT", f"SMT+native MUST catch prefilter-evading negative! Got {verdict}"
    assert verdict.counterexample is not None
    assert verdict.orig_out != verdict.cand_out
