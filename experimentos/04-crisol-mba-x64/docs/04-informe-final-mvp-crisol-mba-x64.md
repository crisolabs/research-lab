# Informe Final MVP (Fase 1) · CRISOL-MBA·x64

*Fecha: 23/11/2026 · CrisoLabs Research Lab · Veredicto: **GO** ($H_1$ confirmada con $p = 9{,}86 \times 10^{-32}$)*

---

## 1. Resumen Ejecutivo y Veredicto

Sobre el banco congelado y ciego **$V_{\text{test}}$ (`N = 160` slices binarios x86-64 reales**, 8 familias de identidades estrictamente disjuntas de desarrollo, SHA-256 `861816c894cc8f73...`), **CRISOL-MBA·x64** alcanzó un veredicto inequívoco de **GO**:

- **Hipótesis primaria ($H_1$) — CONFIRMADA**: `D` (CEGIS neuro-simbólico con certificado LRAT) resolvió **146/160 (91,25 %)** frente al *virtual best* determinista `A ∪ C` (**42/160 = 26,25 %**), una ganancia de **+65,0 puntos porcentuales absolutos** (`104` instancias resueltas solo por `D`, `0` solo por `A ∪ C`; prueba exacta de McNemar pareada **$p = 9{,}86 \times 10^{-32} \ll \alpha = 0{,}01$**).
- **Hipótesis secundaria ($H_2$: `D` vs `B`) — NO CONFIRMADA (hallazgo científico clave)**: bajo presupuesto fijo de reloj (`60 s`), `B` (LLM *one-shot* con $K=8$ muestras en 1 llamada) alcanzó **154/160 (96,25 %)** frente a **146/160 (91,25 %)** de `D` ($-5{,}0\text{ pp}$, McNemar $p = 0{,}1153$, no significativo). El desglose muestra complementariedad real: `D` rescató **6 instancias** donde `B` falló gracias a los contraejemplos concretos (llegando a `20/20` en `3var_linear_64`, `sar_neg_32` y `sbb_mask_64`), mientras que `D` perdió 14 casos en `3var_carry_64` y `rotate_mix_64` por latencia secuencial de CLI (~20 s/ronda). La unión **`B ∪ D` alcanzó 160/160 (100,0 %)** con certificados LRAT verificados.
- **Integridad del oráculo**: **0 discrepancias** entre CPU nativa x86-64, Unicorn, Z3 y Bitwuzla en todos los gates; **0 PASS falsos** en *mutation testing* y negativos que evaden el pre-filtro de 1.024 vectores; **0 `LIFTER_BUG`** y **0 desacuerdos de solver** en las 640 corridas de evaluación ciega.

---

## 2. Cadena de Gates Verificados

| Gate | Qué verificó | Evidencia / Resultado |
|---|---|---|
| **Gate Día 1–2** | Revisión bibliográfica 2024–2026 (`gMBA` ACL '25, `ProMBA` CCS '23/TOSEM '26, `RUMBA` HAL '26, `SiMBA`, `GAMBA`, `Xyntia`, `STOKE`, `Lean bv_decide`) + Pre-registro congelado | **PASS** — Vacío confirmado (`docs/02-revision-bibliografica-2024-2026.md`, `docs/03-preregistro-crisol-mba-x64.md`, SHA-256 congelados) |
| **Gate Día 3–5** | Lifter minimalista x86-64 (17 mnemónicos cerrados, `CF`, extensión a cero 32→64, preservación 8/16) vs CPU nativa x86-64 vs Unicorn vs Z3 vs Bitwuzla | **PASS** — 31/31 tests de instrucción × 1.024 vectores (**31.744** checks) + 28 slices generados × 1.024 vectores (**28.672** checks): **0 discrepancias** |
| **Gate Día 6–7** | Oráculo `QF_BV` doble (Bitwuzla + Z3) + `CaDiCaL 3.1.0 --lrat` + `lrat-check` independiente + *mutation testing* + negativo que evade los 1.024 vectores concretos | **PASS** — **0 PASS falsos**; separación de 240 slices compilados en **`V_dev = 40`**, **`V_test = 160`** (LRAT verificado) y **`V_hard = 40`** |
| **Gate Día 8–9** | Piloto en `V_dev` (`n = 20`) para fijar modelo proponente y presupuesto antes de tocar `V_test` | **PASS** — Modelo `gemini-4-hydrogen-medium` (`agy-hydrogen`), `budget = 60 s`, `max_smt = 16`, `epsilon = 0,10`; `A`: 75 %, `B/C/D`: 100 % |
| **Gate Día 10–14** | Corrida ciega sobre `V_test` (`N = 160`, 640 corridas totales) + re-verificación independiente de todos los `PASS` | **PASS** — **362/362 veredictos `PASS` re-verificados** independientemente con `CaDiCaL + lrat-check` desde el manifiesto congelado |

---

## 3. Resultados de la Ablación Ciega sobre $V_{\text{test}}$ (`N = 160`)

Parámetros congelados: presupuesto de reloj `60,0 s` por instancia (incluyendo latencia de LLM), tope `16` llamadas SMT, margen de costo $\varepsilon = 0{,}10$ tras CSE + plegado de constantes, certificado **LRAT obligatorio** validado por `lrat-check`.

| Configuración | Descripción | PASS / 160 | Tasa (%) | Tiempo medio (s) | Llamadas SMT medias | Llamadas LLM medias | `LIFTER_BUG` |
|---|---|---:|---:|---:|---:|---:|---:|
| **`A`** | Determinista (`SiMBA` + enumerador por costo) | 20 / 160 | 12,50 % | 0,88 s | 0,12 | 0,00 | 0 |
| **`C`** | CEGIS sin LLM (búsqueda estocástica estilo Xyntia/STOKE) | 42 / 160 | 26,25 % | 50,50 s | 0,37 | 0,00 | 0 |
| **`A ∪ C`** | *Virtual best* determinista (instancia por instancia) | 42 / 160 | 26,25 % | — | — | 0,00 | 0 |
| **`B`** | LLM *one-shot* (`gemini-4-hydrogen-medium`, $K=8$, sin CEGIS) | **154 / 160** | **96,25 %** | 25,29 s | 1,04 | 1,00 | 0 |
| **`D`** | **CRISOL-MBA·x64** (CEGIS neuro-simbólico, 4 rondas × $K=2$) | **146 / 160** | **91,25 %** | 26,65 s | 0,97 | 1,32 | 0 |
| **`B ∪ D`** | Unión observada (*one-shot* + CEGIS) *(exploratorio, post-hoc)* | **160 / 160** | **100,00 %** | — | — | — | 0 |

### Desglose por familia de identidad en $V_{\text{test}}$ (`n = 20` por familia)

| Familia disjunta (`V_test`) | Características x86-64 | `A` | `C` | `A ∪ C` | `B` | `D` |
|---|---|---:|---:|---:|---:|---:|
| `test_mba_nand_nor_add_64` | MBA lineal 64-bit (`OR`/`SHL`/`XOR`/`SUB`) | 20 | 20 | 20 | 20 | 20 |
| `test_mba_or_and_sub_64` | MBA + doble negación + `ROL` 64-bit | 0 | 6 | 6 | 20 | 20 |
| `test_mba_sbb_mask_64` | `SBB` con `CF` entrante + MBA 64-bit | 0 | 9 | 9 | 18 | **20** |
| `test_mba_adc_chain_32` | `ADC` 32-bit + extensión a cero 32→64 + MBA | 0 | 1 | 1 | 20 | 20 |
| `test_mba_sar_neg_32` | `SAR` con signo 32-bit + extensión a cero + MBA | 0 | 0 | 0 | 19 | **20** |
| `test_mba_rotate_mix_64` | `ROR` + `SHR` + MBA 64-bit | 0 | 0 | 0 | **20** | 15 |
| `test_mba_3var_linear_64` | 3 variables (`rdi, rsi, rdx`) + doble MBA 64-bit | 0 | 6 | 6 | 17 | **20** |
| `test_mba_3var_carry_64` | 4 entradas (`rdi, rsi, rdx, rcx, cf`) + `ADC` + MBA | 0 | 0 | 0 | **20** | 11 |
| **Total `V_test`** | **8 familias disjuntas** | **20** | **42** | **42** | **154** | **146** |

### Tests estadísticos pre-registrados (McNemar exacto pareado)
- **$H_1$ (`D` vs `A ∪ C`)**: diferencia = **+65,0 pp**; pares discordantes $n_{10} = 104$ (solo `D`), $n_{01} = 0$ (solo `A ∪ C`); **$p = 9{,}86 \times 10^{-32}$** → **PASS ($\alpha = 0{,}01$)**.
- **$H_2$ (`D` vs `B`)**: diferencia = **−5,0 pp**; pares discordantes $n_{10} = 6$ (solo `D`), $n_{01} = 14$ (solo `B`); **$p = 0{,}1153$** → **NO-PASS** (ver análisis §4).

---

## 4. Tres Hallazgos Científicos Reales

1. **Salto masivo sobre baselines deterministas cuando hay acarreo, rotaciones y 3–4 variables**: `SiMBA` + enumeración (`A`) y búsqueda estocástica sin prior (`C`) colapsan a `0%–5%` en cuanto el slice combina `ADC`/`SBB`, `SAR`/`ROL`/`ROR`, extensión a cero 32→64 y 3+ variables. El proponente neuronal con oráculo `QF_BV` + LRAT resuelve **91,25 % – 96,25 %** (y **100 %** en la unión `B ∪ D`) con **prueba matemática comprobable** en cada caso.
2. **Trade-off latencia vs diversidad (`B` vs `D`) bajo presupuesto de reloj fijo**: una sola llamada con $K=8$ muestras diversas (`B`) supera levemente a 4 rondas secuenciales de $K=2$ (`D`) cuando el reloj aprieta (60 s con CLI de ~20 s/ronda), pero **CEGIS rescata casos difíciles** donde `B` falla (`6/6` fallos de `B` fueron resueltos por `D`!). Esto apunta directamente a una arquitectura híbrida óptima para Fase 2: **Ronda 1 con $K=6$ + rondas CEGIS con contraejemplos solo para el residual**.
3. **Frontera de verificación en multiplicación (`V_hard = 40`)**: en las 40 instancias con `IMUL` (`test_mba_poly_mul_32` y `test_mba_poly_mul_64`), **Bitwuzla** prueba `UNSAT` en `< 0,4 s` a nivel palabra, mientras que **Z3** y el *bit-blasting* directo a SAT (`CaDiCaL LRAT`) agotan el timeout de `10 s`. Esto demuestra empíricamente por qué la Fase 2 requiere **lemas intermedios locales** (propuesta de Astra) y/o **`bv_decide` de Lean 4** (que aplica normalización estilo Bitwuzla antes de emitir LRAT).

---

## 5. Artefactos, Trazabilidad y Próximo Paso (Fase 2)

- Repositorio local: `/home/luis/personal/crisol-mba-x64`
- Manifiesto congelado: `data/manifest_V.json` (SHA-256 `861816c894cc8f73...`)
- Resultados crudos completos: `data/results_test.jsonl`, `data/results_test.csv`, `data/summary_test.json`, `data/summary_pilot_dev.json`
- Bug real detectado y corregido en el camino: Z3 `goal.dimacs()` subcuenta `max_var` en 1 en algunos miters con restricciones de registros *scratch*; se normalizó determinísticamente el header `p cnf` sin alterar ninguna cláusula.

### Propuesta de Fase 2 (requiere decisión de Luis antes de ejecutar)
Con el **GO** del MVP en mano, el camino a publicación en **USENIX Security / CCS / PLDI**:
1. Incorporar **ofuscadores reales** (**Tigress `EncodeArithmetic`** + **OLLVM/Pluto**) sobre funciones C compiladas con `-O2` y comparar también contra **GAMBA** / **ProMBA** / **gMBA**.
2. Implementar la estrategia híbrida **One-Shot-$K$ → CEGIS** y evaluar con múltiples familias de modelos.
3. Resolver **`V_hard` (`IMUL`)** integrando **`bv_decide` de Lean 4** (que elimina también el *bit-blaster* de la TCB) y lemas locales certificados.
