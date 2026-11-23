# Síntesis Final · Fase 0: CRISOL-MBA·x64

*CrisoLabs Research Lab · Mesa Pentamodal · 23/11/2026 · Es una propuesta: no se implementa nada hasta que Luis decida.*

## 1. Veredicto unificado

**Proyecto:** **CRISOL-MBA·x64**, un desofuscador neuro-simbólico con certificado para slices x86-64. El uso es defensivo: análisis y auditoría de binarios.

**Problema abierto exacto.** Partimos de un slice x86-64 con estas condiciones:
- Rectilíneo y de solo registros: sin memoria, saltos ni syscalls.
- Hasta 24 instrucciones de una lista cerrada: `MOV ADD ADC SUB SBB NEG AND OR XOR NOT LEA`, desplazamientos por inmediato e `IMUL` sin anidar.
- Calcula una MBA lineal o polinómica de grado ≤ 2, en 32 o 64 bits.

La pregunta: un modelo que propone candidatos y recibe contraejemplos, ¿recupera **con prueba comprobable** una expresión de costo ≤ (1+ε) de la original antes de ofuscar más veces que la mejor combinación determinista con el mismo presupuesto?

**Vacío.** Cada línea cubre una parte:
- SiMBA y GAMBA simplifican expresiones, pero no trabajan sobre bytes con acarreo y extensión a cero.
- Xyntia y STOKE buscan y validan, pero sin conocimiento previo aprendido.
- LLM4Decompile mide si el código se puede volver a ejecutar, no si es equivalente.

Ningún director conoce un trabajo que junte las tres cosas con certificado. **Eso no prueba que no exista.**

**Revisión 2024–2026 a cerrar antes del pre-registro (es un gate):**
- LLM para simplificar MBA.
- Superoptimización o desofuscación con LLM más SMT/CEGIS.
- Solvers de MBA posteriores a GAMBA y sus benchmarks.
- Certificación de bit-vectors (LRAT, `bv_decide` de Lean).

Toda cita se verifica antes de usarla. Si el vacío ya está cubierto, el proyecto se replantea como replicación más benchmark.

## 2. Coincidencias y choques resueltos

Los cuatro coincidían en tres cosas: el modelo nunca decide, un timeout cuenta como FAIL y todo se contrasta con ejecución real.

| Director | Se conserva | Se poda (quién lo detectó) |
|---|---|---|
| Astra | Certificado SAT/LRAT, con la traducción dentro de la base de confianza. Negativos que coinciden en todos los puntos de prueba. Interpolación sobre F₂ como baseline. Lemas locales para la Fase 2 | RV32I + Keccak: RV32I no tiene multiplicación, χ ya es cuadrática y un SAT con *AIG sweeping* cierra el miter sin ayuda (Opus, Argon) |
| Sol | Contrato x86-64 (`CF` y extensión a cero), runner nativo, presupuestos iguales, particiones por familia | GMP como corpus real obligatorio, porque ya es mínimo. Nodos contados sobre el árbol del propio traductor, que permite inflar la métrica (Opus, Argon) |
| Argon | CEGIS, ablación A/B/C/D, benchmark procedural, pre-filtro concreto, Bitwuzla, denominadores completos | *Bit-width scaling* como prueba: `x≫16` vale 0 en 8 y 16 bits pero 1 en 64 bits para x=2¹⁶. También predicados opacos contextuales, Tigress+OLLVM con 4 baselines en 14 días, la semilla de Bitcoin, umbrales sin unidad y la dependencia de la 3090 (Astra, Opus) |
| Opus | Mutantes con inequivalencia demostrada, re-ejecución nativa de todo SAT, categoría `LIFTER_BUG`, McNemar, diseño en CPU/API | Decompilación a C (B→C→B′) en `QF_ABV`: comportamiento indefinido del C, cota de desenrollado sin probar, aliasing y doble lifter (Astra, Argon) |

## 3. Hipótesis falsable y ablación

**H1.** En el subconjunto reservado V, D resuelve **al menos 15 puntos porcentuales absolutos** más que el *virtual best* de A∪C (lo mejor de ambos, instancia por instancia).
- **Presupuesto:** igual por instancia. Incluye el tiempo de reloj con la latencia del modelo y un tope de llamadas al solver.
- **Éxito:** PASS certificado (§4) y costo ≤ (1+ε)·costo(g). El costo se mide con un contador canónico, después de eliminar subexpresiones comunes y plegar constantes en ambos lados.
- **Refutación:** diferencia menor a 15 pp, McNemar no significativo, o C empata a D. Un solo PASS falso invalida la corrida.

**H2.** D supera a B con el mismo número de muestras.

Las cuatro configuraciones:
- **A:** Bitwuzla/Z3 `simplify`, SiMBA, interpolación sobre F₂ y enumeración acotada.
- **B:** el modelo en una sola pasada, K muestras, sin contraejemplos.
- **C:** CEGIS sin modelo: búsqueda estilo Xyntia/STOKE con la misma gramática y el mismo pre-filtro.
- **D:** CEGIS neuro-simbólico completo.

**Búsqueda y verificación se miden por separado.** El generador conoce la expresión original g. Antes de correr se certifica `obf ≡ g` dentro de un presupuesto T_v:
- Las instancias que pasan forman V. Ahí un fallo es de búsqueda, no del solver.
- Las demás se reportan aparte como «verificación difícil».
- Si V sale chico, el cuello de botella es verificar. Ahí entran los lemas de Astra.

## 4. Oráculo determinista y cadena de confianza

1. **Bytes:** cada slice se fija con SHA-256. Capstone decodifica y rechaza toda instrucción fuera de la lista.
2. **Lifter minimalista propio a `QF_BV`.** Modela:
   - `CF` en `ADC`, `SBB`, `SUB`, `NEG` y desplazamientos.
   - Extensión a cero en escrituras de 32 bits.
   - Parte alta preservada en escrituras de 8 y 16 bits.

   **Gate:** al menos 1.024 vectores por instrucción y por slice, contrastados con ejecución nativa y con Unicorn. Una sola discrepancia bloquea el experimento.
3. **Pre-filtro con numpy.** Usa:
   - Valores de frontera: 0, 1, −1, 2³¹, 2³²−1 y 2⁶³.
   - Vectores one-hot.
   - Aleatorios con semilla fija.
   - `CF` en 0 y en 1.
   - Todos los contraejemplos acumulados.

   El pre-filtro solo rechaza; nunca aprueba.
4. **Miter** `∃x. F_orig(x) ≠ F_cand(x)` en Bitwuzla y en Z3. Si discrepan, se frena.
5. **UNSAT:** se traduce a CNF, CaDiCaL emite la prueba LRAT y la revisa un checker independiente (`cake_lpr`, a confirmar). Sin LRAT verificado no hay PASS.
6. **SAT:** el contraejemplo se reproduce en nativo. Si no se reproduce, es `LIFTER_BUG`: cuenta como FAIL y se investiga. Timeout o unknown también es FAIL.
7. **Mutation testing:**
   - Tienen que dar FAIL los mutantes con inequivalencia demostrada (cambio de constante, `ADD↔ADC`, sin extensión a cero, `CF` invertido) y los negativos que pasan el pre-filtro.
   - Tienen que dar PASS la autoequivalencia y `obf ≡ g`.

**Dónde empieza el teorema.** Lo que se prueba es la equivalencia de la fórmula levantada. El paso de bytes a fórmula es evidencia empírica (paso 2). Enlazarlo con una semántica formal de x86-64 queda para la Fase 2, y así se declara.

## 5. MVP de 10 a 14 días en aranserver

- **Recursos:** 12 procesos de solver con tope de 24 GB por cgroup, sin GPU. El modelo corre por las CLIs que ya existen.
- **Bajada al equipo `pentamodal`:** Codex implementa, y cada gate lo audita un director distinto del que propuso esa parte.
- **Dependencias:** `capstone`, `bitwuzla`, `z3-solver`, `unicorn`, `numpy` y `scipy` en un venv. SiMBA clonado. CaDiCaL y el checker LRAT compilados en `build/`.

| Días | Entrega | Gate |
|---|---|---|
| 1–2 | Revisión bibliográfica y pre-registro con hash commiteado | Vacío confirmado |
| 3–5 | Lifter, harness nativo + Unicorn, generador (asm → `as` → bytes) | 0 discrepancias |
| 6–7 | Pre-filtro, miter doble, LRAT, mutantes; armado de V | 0 PASS falsos |
| 8–9 | A y C congelados; B y D ajustados solo con datos de desarrollo; piloto de costo con 20 instancias | Consumo dentro del tope |
| 10–12 | Corrida reservada A/B/C/D y McNemar | — |
| 13–14 | Repetición desde el manifiesto congelado; informe por familia | Veredictos idénticos |

La meta es tener al menos 150 instancias en V reservado; el número final sale del cálculo de potencia.

**Go:** todos los gates y H1.

**No-Go:**
- Si se cae un gate del oráculo, se frena todo.
- Si se cae H1, se documenta el resultado negativo junto con el benchmark y el oráculo, y no se escala el gasto.

## 6. Implicancias reales

- **Esfuerzo:** Codex implementa y Claude revisa la metodología. A Luis le tocan las decisiones de §7, el pre-registro y el informe de Go/No-Go.
- **Instalación:** todo en un venv aislado dentro del repo. Las compilaciones van de a una con `pesado`. GAMBA, Tigress y Lean solo se instalan según lo que decidas en §7. Antes hay que revisar el espacio en disco, porque ya hubo disco lleno.
- **Cuotas:** no hay cifras inventadas. El tope de tokens por instancia se fija en el pre-registro y el piloto mide el consumo real. Si no alcanza la cuota, se achica el corpus, nunca el presupuesto por instancia. No hay servicios ni gastos nuevos.
- **Cómo volver atrás:** todo vive en `~/personal/rea-neuro-simbolico-fase0`. No hay cron, servicios ni cambios en otros proyectos. Para revertir alcanza con borrar `.venv/` y `build/`. Commit por avance y push diario al GitHub privado con `ppush`.

## 7. Decisiones de Luis

1. **Alcance y umbrales.** ¿Aprobás el alcance de §1 y H1 con 15 pp, ε = 0,10 y α = 0,05? Argon pedía α = 0,01.
2. **Ofuscador real.** ¿Sumamos unas 40 funciones ofuscadas con Tigress EncodeArithmetic, o el MVP queda 100 % sintético? Tigress se descarga con licencia académica y para eso hace falta tu OK.
3. **Certificado.** ¿LRAT con un bit-blaster propio dentro de la base de confianza, que es lo barato? ¿O `bv_decide` de Lean, que trae el bit-blasting verificado pero suma 1 o 2 días e instalar Lean?
4. **Proponente y cuota.** ¿Qué modelos del equipo pentamodal proponen candidatos en B y D, y con qué tope de tokens por instancia? ¿Confirmás que la 3090 sigue fuera?
