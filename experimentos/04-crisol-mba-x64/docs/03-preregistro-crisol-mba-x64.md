# Pre-Registro Experimental · CRISOL-MBA·x64 (MVP Fase 1)

*Versión: 1.0 (Borrador para congelar antes de correr modelos) · Fecha: 23/11/2026 · CrisoLabs Research Lab*  
*Decisiones aprobadas por Luis: +15 pp, $\varepsilon = 0{,}10$, $\alpha = 0{,}01$, MVP 100% sintético compilado a bytes x86-64 reales, certificado LRAT (`CaDiCaL` + checker independiente), sin RTX 3090.*

---

## 1. Pregunta de Investigación e Hipótesis Falsables

### Pregunta central
Dado un *slice* binario **x86-64** rectilíneo y de solo registros (sin accesos a memoria, saltos ni syscalls) compilado a bytes reales que implementa una expresión MBA lineal o polinómica de grado $\le 2$ (en 32 o 64 bits, con propagación de `CF` y extensión a cero de escrituras de 32 bits), ¿un bucle **CEGIS neuro-simbólico** (`D`) recupera una expresión simplificada **con certificado LRAT comprobable** y costo canónico $\le (1 + \varepsilon)\cdot \text{costo}(g)$ en una fracción significativamente mayor de instancias que el *virtual best* de los métodos deterministas (`A ∪ C`) bajo **idéntico presupuesto total de reloj y llamadas al solver**?

### Hipótesis primaria ($H_1$)
Sobre el conjunto reservado y congelado de test $V_{\text{test}}$ ($N \ge 150$ instancias verificables, separadas por familia de identidad antes de compilar):
- **Efecto mínimo requerido**: $\text{Tasa}(D) - \text{Tasa}(A \cup C) \ge +15\text{ puntos porcentuales absolutos}$, donde $A \cup C$ es el *virtual best* instancia por instancia entre `A` (determinista algebraico/enumerativo) y `C` (CEGIS sin prior neuronal).
- **Test estadístico**: prueba exacta de **McNemar pareada** (bilateral) con nivel de significancia **$\alpha = 0{,}01$**.
- **Margen de costo**: $\varepsilon = 0{,}10$ sobre el costo canónico de la expresión original $g$ antes de ofuscar (medido tras *Common Subexpression Elimination* y plegado de constantes en ambos lados).

### Hipótesis secundaria ($H_2$ — Ablación de contraejemplos)
Bajo el mismo presupuesto de muestras y reloj, `D` (CEGIS con contraejemplos concretos de SMT) supera significativamente a `B` (modelo en una sola pasada, $K$ muestras, sin retroalimentación de contraejemplos) con McNemar pareado ($\alpha = 0{,}01$).

### Reglas de refutación (sin excepciones)
$H_1$ queda **refutada** si ocurre cualquiera de las siguientes condiciones:
1. $\text{Tasa}(D) - \text{Tasa}(A \cup C) < 15\text{ pp}$ o $p \ge 0{,}01$ en McNemar.
2. `C` (búsqueda sin prior neuronal con igual pre-filtro y presupuesto) empata o supera a `D`.
3. Se detecta **un solo PASS falso** en la suite de *mutation testing* o una discrepancia no resuelta con ejecución nativa (en cuyo caso la corrida entera se invalida).

---

## 2. Alcance Exacto y Lista Cerrada de Instrucciones x86-64

### Contrato de admisión de slices
- **Arquitectura**: x86-64 (System V).
- **Longitud**: hasta **24 instrucciones** rectilíneas (sin `JMP`, `Jcc`, `CALL`, `RET`, `SYSCALL` ni operandos de memoria).
- **Registros**: entradas explícitas (hasta 4 registros de 32/64 bits + flag `CF` inicial); salidas explícitas (registro destino completo de 64 bits + `CF` final cuando forma parte del contrato).
- **Lista cerrada de mnemónicos admitidos** (decodificados desde bytes con `capstone`; cualquier otra instrucción es rechazada determinísticamente):
  - Transferencia y cálculo de dirección sin memoria: `MOV`, `LEA` (solo aritmética de registros/inmediatos).
  - Aritmética con y sin acarreo: `ADD`, `ADC`, `SUB`, `SBB`, `NEG`, `IMUL` (sin anidar multiplicaciones de 64 bits en el MVP).
  - Lógica bit a bit: `AND`, `OR`, `XOR`, `NOT`.
  - Desplazamientos/rotaciones por inmediato: `SHL`, `SHR`, `SAR`, `ROL`, `ROR`.

### Semántica obligatoria del lifter minimalista (`QF_BV`)
- **Flag `CF`**: modelado explícitamente en `ADD`, `ADC`, `SUB`, `SBB`, `NEG` y desplazamientos por inmediato.
- **Escrituras parciales**: extensión a cero automática de la parte alta `[63:32]` en toda escritura a registros de 32 bits (`EAX`, `EBX`, etc.); preservación de la parte alta en escrituras de 8 y 16 bits si aparecen.
- **Compilación a bytes reales**: el generador emite ensamblador x86-64 (o C mínimo compilado con `gcc`/`clang` a flags fijos y versión congelada), se ensambla con `as`, se extraen los bytes exactos de la sección `.text` y se congela el manifiesto con **SHA-256**.

---

## 3. Separación entre Búsqueda y Verificación (Subconjunto $V$)

Para evitar que un timeout del solver SMT se confunda con un fallo de búsqueda:
1. El generador conoce la forma simple original $g$ de cada instancia ofuscada $\text{obf}$.
2. Antes de evaluar `A/B/C/D`, se corre el oráculo sobre el par $(\text{obf}, g)$ con un presupuesto de verificación fijo $T_v = 10\text{ s}$ en **Bitwuzla y Z3** + certificación **LRAT**.
3. **Subconjunto $V$ (experimento principal)**: todas las instancias donde $\text{obf} \equiv g$ se certifica dentro de $T_v$. Sobre $V$, cualquier fallo de `A/B/C/D` es inequívocamente un **fallo de búsqueda**, no de verificación.
4. **Subconjunto $V_{\text{hard}}$**: las instancias donde el oráculo agota $T_v$ o devuelve `UNKNOWN` se reportan en una tabla separada como «verificación difícil» (y alimentan una eventual Fase 2 con lemas locales de Astra).

### Partición Anti-Leakage y Tamaño Muestral
- **Separación por familia de identidad**: las familias de transformaciones MBA (lineales, polinómicas grado 2, con acarreos `ADC`/`SBB`, con desplazamientos) se particionan en **Desarrollo (`dev`, 40 instancias)** y **Reservado (`test`, $N \ge 150$ instancias en $V_{\text{test}}$)** *antes* de ajustar prompts o heurísticas.
- **Deduplicación**: se deduplican slices tras normalización de registros y constantes.
- **Congelado criptográfico**: el script generador, la semilla, las fuentes, los bytes compilados y el manifiesto JSON se congelan con **SHA-256** antes de tocar `test`.
- **Justificación de potencia**: para detectar una diferencia pareada de $+15\text{ pp}$ con $\alpha = 0{,}01$ y potencia $\ge 0{,}85$ bajo McNemar (asumiendo $\le 25\%$ de pares discordantes totales), $N \ge 150$ instancias en $V_{\text{test}}$ es el mínimo operativo; el piloto de 20 instancias en `dev` validará la tasa de discordancia antes de congelar el tamaño final.

---

## 4. Las Cuatro Configuraciones de Ablación (`A / B / C / D`)

Todas compiten sobre la **misma gramática de salida**, el **mismo contador canónico de costo** y el **mismo presupuesto total por instancia** (tiempo de reloj incluyendo latencia de API/CLI + tope fijo de llamadas al solver SMT):

- **`A` (Baseline Determinista)**: `Bitwuzla/Z3 simplify` + `SiMBA` (para el subconjunto lineal) + interpolación exacta sobre $\mathbb{F}_2$ (grado $\le 2$) + enumeración acotada por costo.
- **`B` (LLM One-Shot sin CEGIS)**: el modelo proponente genera $K$ candidatos independientes sin recibir contraejemplos del solver; se evalúan con el mismo pre-filtro y oráculo.
- **`C` (CEGIS sin prior neuronal)**: búsqueda estocástica/local estilo **Xyntia / STOKE** sobre la misma gramática, guiada por el mismo pre-filtro concreto y los contraejemplos de `QF_BV`.
- **`D` (CRISOL-MBA·x64 — CEGIS Neuro-Simbólico)**: bucle cerrado donde el modelo proponente recibe el slice desensamblado normalizado, el resumen de puntos frontera y el contraejemplo concreto $(\vec{x}_{\text{ce}}, \text{out}_{\text{orig}}, \text{out}_{\text{cand}})$ del intento fallido, refinando hasta PASS certificado o agotar el presupuesto.

**Modelo proponente y tope de tokens**: se utilizarán modelos de producción del equipo `pentamodal` común por CLI/API (sin RTX 3090). El modelo exacto y el tope de tokens por instancia se congelarán tras el **piloto de 20 instancias en `dev`** (Día 8–9), registrando costo real y latencia.

---

## 5. Oráculo Determinista y Cadena de Confianza (0 Opinión de LLM)

1. **Sanity Gate del Lifter (Día 3–5)**: cada instrucción admitida y cada slice levantado a `QF_BV` se evalúa sobre **$\ge 1.024$ vectores concretos** (frontera + aleatorios + `CF` $\in \{0,1\}$) contra **ejecución nativa x86-64** y contra **Unicorn**. **Criterio: 0 discrepancias.** Una sola discrepancia detiene el experimento.
2. **Pre-filtro rápido (`numpy`)**: evalúa candidatos sobre fronteras $\{0, 1, -1, 2^{31}, 2^{32}-1, 2^{63}, 2^{64}-1\}$, vectores *one-hot*, aleatorios de semilla fija, `CF` $\in \{0,1\}$ y todos los contraejemplos previos. **Solo rechaza; nunca aprueba.**
3. **Miter doble (`QF_BV`)**: consulta $\exists \vec{x}.\ F_{\text{orig}}(\vec{x}) \neq F_{\text{cand}}(\vec{x})$ en **Bitwuzla** y en **Z3**. Si discrepan entre sí, se frena y audita.
4. **Certificado LRAT obligatorio para PASS**: ante `UNSAT`, el miter se traduce a CNF (*bit-blasting* determinista incluido explícitamente en la TCB), **CaDiCaL** genera la prueba **LRAT** y un **checker independiente** (p. ej. `cake_lpr` o `lrat-check`) la valida. Sin LRAT válido, **no hay PASS**.
5. **Re-ejecución nativa de todo `SAT`**: todo contraejemplo `SAT` se ejecuta sobre los bytes reales del slice. Si no reproduce la diferencia, se clasifica como **`LIFTER_BUG`**, cuenta como **FAIL** en el denominador y dispara auditoría.
6. **Contabilidad estricta de denominadores**: `TIMEOUT`, `UNKNOWN`, sintaxis inválida, costo $> (1+\varepsilon)\cdot\text{costo}(g)$ y `LIFTER_BUG` cuentan todos como **FAIL**. Nada se excluye silenciosamente.
7. **Mutation Testing del Oráculo (Día 6–7)**:
   - Mutantes con inequivalencia demostrada (constante perturbada, `ADD ↔ ADC`, omisión de extensión a cero, `CF` invertido) y negativos que coinciden en todos los puntos del pre-filtro: **100% deben dar FAIL (0 PASS falsos)**.
   - Autoequivalencia ($F \equiv F$) y equivalencia conocida ($\text{obf} \equiv g$): **PASS certificado con LRAT**.

---

## 6. Recursos, Dependencias y Criterio Go / No-Go

### Entorno en `aranserver` (aislado y 100% reversible)
- **Directorio de trabajo**: `~/personal/rea-neuro-simbolico-fase0/` (entorno virtual `.venv/` + `build/` local; sin tocar otros proyectos, sin servicios/cron, sin RTX 3090).
- **Concurrencia**: máximo **12 procesos solver** con límite agregado de **24 GB RAM** (de 56 GB libres). Compilaciones pesadas de a una con `~/bin/pesado`.
- **Dependencias a instalar en Fase 1 (solo tras OK de Luis)**:
  - Python (`.venv/`): `capstone`, `bitwuzla`, `z3-solver`, `unicorn`, `numpy`, `scipy`.
  - Binarios locales (`build/`): `CaDiCaL`, checker LRAT (`lrat-check` / `cake_lpr`) y clon local de `SiMBA`.

### Cronograma restante del MVP (Días 3–14)
| Ventana | Entregable | Gate obligatorio |
|---|---|---|
| **Días 3–5** | Setup `.venv/` + `build/`, lifter minimalista x86-64, harness nativo + Unicorn, generador de slices compilados con SHA-256 | **0 discrepancias** en $\ge 1.024$ vectores/slice |
| **Días 6–7** | Pre-filtro `numpy`, miter doble Bitwuzla/Z3, pipeline CaDiCaL+LRAT, mutation testing, armado y congelado de $V_{\text{dev}}$ y $V_{\text{test}}$ | **0 PASS falsos** en mutantes y negativos |
| **Días 8–9** | Baselines `A` y `C` congelados; ajuste de `B` y `D` solo sobre $V_{\text{dev}}$; piloto de 20 instancias para fijar modelo y tope de tokens | Consumo y latencia dentro de cuota |
| **Días 10–12** | Corrida ciega sobre $V_{\text{test}}$ (`A/B/C/D`), test de McNemar ($\alpha = 0{,}01$) | Sin tocar código ni prompts |
| **Días 13–14** | Repetición desde manifiesto congelado, auditoría fría por otra familia de modelos, informe por familia y archivo final | **Veredictos 100% reproducibles** |

### Criterio Go / No-Go al cierre del MVP
- **GO a Fase 2** (sumar Tigress `EncodeArithmetic` real + `bv_decide` de Lean 4 + redacción de paper): pasan todos los gates del oráculo, 0 PASS falsos, reproducibilidad exacta y se cumple $H_1$ ($\ge +15\text{ pp}$, $p < 0{,}01$).
- **NO-GO**: si falla cualquier gate del oráculo se frena de inmediato; si el oráculo es sólido pero cae $H_1$, se documenta y publica internamente el **resultado negativo + benchmark + oráculo certificado** sin escalar gasto.
