# Revisión Bibliográfica Sistemática (2024–2026) · CRISOL-MBA·x64

*Fecha de verificación: 23/11/2026 · Gate Día 1–2 previo al pre-registro · CrisoLabs Research Lab*

## 1. Veredicto del Gate Día 1–2

**VACÍO CONFIRMADO (PASS).**  
Ningún trabajo publicado entre 2021 y 2026 encontrado en esta revisión combina simultáneamente las cuatro propiedades centrales de **CRISOL-MBA·x64**:

1. **Entrada binaria x86-64 real** (bytes compilados con `ADC`/`SBB`, flag `CF` y extensión a cero de escrituras de 32 bits en registros de 64 bits), contrastada contra ejecución nativa + Unicorn.
2. **Síntesis CEGIS neuro-simbólica** con contraejemplos concretos devueltos por un solver `QF_BV` (Bitwuzla + Z3) y ablación controlada `A/B/C/D` bajo idéntico presupuesto de reloj y llamadas.
3. **Separación explícita entre dificultad de búsqueda y dificultad de verificación** (subconjunto verificable $V$ pre-certificado contra la expresión original $g$).
4. **Certificado matemático comprobable independiente del solver** (prueba SAT **LRAT** emitida por CaDiCaL y validada por un checker independiente; escalable a `bv_decide` de Lean 4 en Fase 2).

**Hallazgo crítico que refina el posicionamiento:** la aparición de **`gMBA` (Findings of ACL 2025)** y las extensiones recientes **`ProMBA` (ACM TOSEM 2026)** y **`RUMBA` (HAL 2026)** obligan a citar explícitamente estos trabajos y a enmarcar nuestra contribución no como "el primer uso de IA en MBA", sino como **la primera evaluación rigurosa y certificada (LRAT) de CEGIS neuro-simbólico directamente sobre slices binarios x86-64 con acarreo y escrituras parciales, bajo control anti-leakage y ablación contra búsqueda sin prior neuronal**.

---

## 2. Mapa del Estado del Arte Verificado

### A. Solvers algebraicos y de síntesis para MBA (2021–2026)

| Trabajo | Autores | Año / Venue | Qué hace | Qué deja abierto frente a CRISOL-MBA·x64 |
|---|---|---|---|---|
| **MBA-Blast** | Liu, Shen, Ming, Zheng, Li, Xu | 2021 · USENIX Security '21 | Transforma MBA lineales de espacio $n$-bit a espacio de 1 bit para normalización rápida. | Solo MBA lineales sobre expresiones AST; sin semántica binaria x86-64 (`CF`, 32→64 bits) ni certificado LRAT. |
| **Xyntia** | Menguy, Bardin, Bonichon, de Souza Lima | 2021 · ACM CCS '21 | Desofuscación *black-box* por búsqueda local sobre trazas I/O (extiende Syntia). | Sin prior neuronal ni prueba formal universal (equivalencia probabilística salvo verificación externa). **Baseline obligatorio de la configuración `C`.** |
| **SiMBA** | Reichenwallner, Meerwald-Stadler | 2022 · CheckMATE '22 (ACM CCS) | Simplificación algebraica rápida de MBA **lineales** sin bajar a 1 bit. | Limitado a MBA lineales sobre expresiones simbólicas, no bytes x86-64 con acarreo. **Baseline obligatorio de la configuración `A`.** |
| **GAMBA** | Reichenwallner, Meerwald-Stadler | 2023 · IEEE EuroS&PW / WoRMA '23 | Extiende SiMBA a MBA **generales/no-lineales** aislando subexpresiones no lineales con variables temporales. | Trabaja sobre expresiones algebraicas, no sobre slices compilados con `ADC`/`SBB`/flags ni entrega certificado LRAT. |
| **ProMBA** | Lee, Lee, Cho, Lee | 2023 (CCS) / 2026 (ACM TOSEM) | Combina síntesis de programas y reescritura / *equality saturation* para simplificar MBA. | Opera sobre AST de expresiones MBA sin bucle CEGIS neuronal ni certificación SAT/LRAT sobre bytes x86-64. |
| **RUMBA** | Grupo Thalium (HAL) | 2026 · `hal-05578742` | Marco matemático unificado e implementación de referencia para simplificación de MBA lineales y polinómicas. | Herramienta puramente algebraica sobre expresiones; no evalúa síntesis neuro-simbólica CEGIS sobre binarios x86-64. |

### B. Enfoques neuronales, LLM y *verified lifting* (2024–2026)

| Trabajo | Autores / Identificador | Año / Venue | Qué hace | Qué deja abierto frente a CRISOL-MBA·x64 |
|---|---|---|---|---|
| **gMBA** | Noh, Paik, Kwon, Cho (`arXiv:2506.23634`, `2025.findings-acl.1127`) | 2025 · Findings of ACL 2025 | Transformer encoder-decoder guiado por **tablas de verdad** como representación semántica interna para desofuscar MBA (supera a NeuReduce). | Opera sobre strings de expresiones MBA, **sin bucle CEGIS** con contraejemplos SMT, sin semántica x86-64 de registros/flags y sin certificado LRAT. |
| **LLM4Decompile** | Tan et al. | 2024–2025 · EMNLP 2024 / seguimiento | Modelos open-source (1.3B–33B) para traducir ensamblador a C legible. | Evalúa recompilabilidad y paso de tests (*re-executability*), **no equivalencia formal universal**. |
| **LLMLift / Verified Lifting** | Cheung et al. (línea 2024) | 2024 · arXiv / PL | Usa LLMs para proponer traducciones/invariantes verificadas por SMT. | Parte de código fuente de alto nivel, no de bytes binarios x86-64 ofuscados. |
| **D-LiFT y pipelines SMT** | Literatura 2024–2025 (arXiv) | 2024–2025 | Acopla salidas de decompilación LLM con ejecución simbólica / SMT para medir equivalencia semántica. | Enfocado en evaluación/scoring de decompilación general a C; no resuelve desofuscación certificada con LRAT ni ablación controlada contra Xyntia/SiMBA. |

### C. Superoptimización x86-64 y certificación de bit-vectors

| Trabajo | Autores / Referencia | Año / Venue | Relevancia directa para CRISOL-MBA·x64 |
|---|---|---|---|
| **STOKE** | Schkufza, Sharma, Aiken | 2013 · ASPLOS '13 | Precedente fundacional de superoptimización estocástica + validación formal sobre x86-64 con flags. **Precedente obligatorio a citar y reflejar en el baseline `C`.** |
| **Lean 4 `bv_decide` + CaDiCaL + LRAT** | Ecosistema Lean 4 (2024–2026) | 2024–2026 | Normalización estilo Bitwuzla → *bit-blasting* (AIG/CNF) → CaDiCaL → prueba **LRAT** verificada por un checker probado formalmente. Valida nuestra arquitectura de certificados (LRAT en MVP; `bv_decide` drop-in en Fase 2). |

---

## 3. Consecuencias directas para el Pre-Registro

1. **Citas verificadas obligatorias**: citar `STOKE (2013)`, `MBA-Blast (2021)`, `Xyntia (2021)`, `SiMBA (2022)`, `GAMBA (2023)`, `ProMBA (CCS 2023 / TOSEM 2026)`, `LLM4Decompile (2024)`, `gMBA (ACL 2025)` y `RUMBA (2026)` — y **no citar** ningún paper que no se haya verificado en su fuente primaria.
2. **Posicionamiento blindado**: el diferencial no es "un LLM simplifica strings MBA" (eso ya lo exploraron NeuReduce y gMBA), sino **CEGIS neuro-simbólico con contraejemplos `QF_BV` y certificado LRAT comprobable sobre bytes x86-64 reales con acarreo (`CF`) y extensión a cero de 32→64 bits**, medido con ablación estricta `A/B/C/D` bajo igualdad de presupuesto.
3. **Decisiones de Luis incorporadas**: $\alpha = 0{,}01$, $+15\text{ pp}$, $\varepsilon = 0{,}10$, MVP 100% sintético compilado a bytes x86-64 reales (`as`/gcc/clang), LRAT en MVP (`bv_decide` en Fase 2), sin 3090.
