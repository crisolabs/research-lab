## 1. Veredicto: `FIX_REQUIRED`

Ningún número del paper contradice los 5 JSON. Lo que falla es la coherencia interna, la base de algunas afirmaciones y el encuadre metodológico.

## 2. Discrepancias numéricas

**Contra los JSON: 0.** Coinciden todas las cifras que se pueden recalcular, incluidos los McNemar exactos (2^-103 = 9.86e-32, 2^-117 = 6.02e-36, 2^-21 = 4.77e-7 y 2^-5 = 0.03125), A∪C∪GAMBA = 56/160, n10 = 118, los 362 PASS (20+154+42+146) y los 6 fallos de B que D rescata contra los 14 que pierde.

**Incoherencias internas:**
- **60,416 chequeos:** son 59 × 1,024. El texto dice "toda instrucción y todo slice ≥1,024 vectores". Eso serían 17 + 262 slices, o sea al menos 285,696 chequeos. Hay que corregir la cifra o el alcance de la frase.
- **"Total V_hard 11.57 s":** sale de un promedio simple (8.22 + 14.92)/2. Si 14.92 promedia sólo los 12 éxitos, el promedio ponderado es 10.73 s. Hay que aclarar si incluye los timeouts.
- **Datos que no están en los JSON:** tiempos y llamadas de A, B, C y D (0.88, 25.29, 50.50, 26.65 s; 1.32 llamadas), las columnas LIFTER_BUG, el 355 + 7 de la re-verificación y la latencia de "~20 s por ronda". Hay que contrastarlos con los CSV/JSONL.

## 3. Sobre-afirmaciones y ajustes metodológicos

1. **`H` es post-hoc.** Se diseñó después de ver B contra D en V_test, así que su 160/160 no es "blind out-of-sample". Hay que marcarlo como exploratorio. Lo único confirmatorio preregistrado es H1 (D contra A∪C).
2. **H contra B** (154 contra 160, n01 = 0) da p = 0.031, que no es significativo con α = 0.01. "Resolves completely" no se sostiene. Lo mismo pasa con `H-sol` en V_real (p = 0.031): hay que decir que no es significativo.
3. **GAMBA aparece como "Certified PASS".** El JSON sólo dice `simplified`, sin certificado ni criterio de costo. Además, el "UNSUPPORTED" sale del adaptador x86 → expresión de los autores, no de GAMBA: los slices de 32 bits podrían correrse con bitwidth 32. Hay que reformular "cannot even represent".
4. **TCB de Lean.** `bv_decide` usa `Lean.ofReduceBool`, así que el compilador y el runtime de Lean entran al TCB. También entra el generador Python de teoremas (`oracle_lean.py`). "Only the Lean kernel and the lifter" es falso.
5. **V_hard certifica la verdad de referencia (F_B ≡ g), no candidatos sintetizados.** Hay que decirlo así. En el abstract y la conclusión falta que Bitwuzla sin certificar cierra 40/40; "0% → 80%" vale sólo para pruebas con certificado.
6. **Oráculo distinto en V_real.** A y C se certifican con LRAT y H con Lean, justo donde aparece `IMUL` de 64 bits. Es un confound. Además, el promedio de C (60.02 s) supera el tope de 60 s.
7. **Allowlist en V_real.** El `-O2` real suele emitir `movsxd`, `movzx` y `movabs`, que no están en las 17 mnemónicas. Hay que verificar o declarar si se amplió la lista.
8. **"0 false positives" cubre sólo los 362 PASS de la Fase 1.** No cubre los 160 de H ni V_real.
9. **"Solves ... at 100% accuracy" es demasiado general.** Hay que dar intervalos Clopper-Pearson al 95%: 160/160 da una cota inferior de ≈97.7% y 22/22 de ≈84.6%. Además, los benchmarks son familias sintéticas y n = 22.
10. **Tono.** Bajar "Cracking the Multiplication Frontier".

No audité las referencias bibliográficas ni los nombres o versiones de modelos y herramientas.
