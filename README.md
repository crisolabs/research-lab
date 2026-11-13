# CrisoLabs Research Lab

Laboratorio público y reproducible detrás de los experimentos técnicos, artículos y reels de **CrisoLabs**.
Regla de la casa: **ninguna cifra sin su experimento reproducible o su fuente primaria verificada.**

> **Estructura dual:** los experimentos en curso permanecen en el repositorio privado de trabajo hasta completar su protocolo y auditoría. A este repositorio público pasan únicamente los estudios terminados, verificados y auditados.

---

## Cómo leer y aprender de este repositorio (paso a paso)

Este repositorio está pensado tanto como evidencia científica auditable como **guía didáctica de cómo diseñar y ejecutar experimentos empíricos con agentes de IA** sin caer en sesgos ni *cherry-picking*:

1. **Experimento y protocolo (`experimentos/03-esfuerzo-de-razonamiento/`):**
   - Pre-registro previo a correr modelos (`README.md`, `EXTENSION-01.md`, `EXTENSION-02.md`) y enmiendas auditables (`ENMIENDA-02-01.md` a `02-03.md`).
   - Banco de 8 tareas en Python congelado criptográficamente (`banco-congelado.json`, `34` hashes SHA-256) y suites de tests ocultos (`tareas/*/ocultos/`).
   - Arnés aislado (`medir.py`, `extension*.py`) con límites estrictos (timeout `600 s`, concurrencia `<= 2`) y datos crudos completos (`resultados/*.csv`, recibos y código generado).
2. **Papers científicos (EN y ES):**
   - [Paper en inglés (Markdown)](experimentos/03-esfuerzo-de-razonamiento/paper/paper-en.md) · [Paper en inglés (PDF)](experimentos/03-esfuerzo-de-razonamiento/paper/paper-en.pdf)
   - [Paper en español (Markdown)](experimentos/03-esfuerzo-de-razonamiento/paper/paper-es.md) · [Paper en español (PDF)](experimentos/03-esfuerzo-de-razonamiento/paper/paper-es.pdf)
   - Script de gráficos reproducibles desde los CSV (`experimentos/03-esfuerzo-de-razonamiento/generar_figuras_paper.py`).
3. **Versión para público general (PDF y Blog):**
   - [PDF de divulgación (español)](blog/2026-11-esfuerzo-de-razonamiento.pdf)
   - [Nota completa del blog (Markdown)](blog/2026-11-esfuerzo-de-razonamiento.md)
4. **Referencias verificadas:**
   - [Índice comentado](referencias/README.md) y [BibTeX](referencias/referencias.bib).

---

## Historia didáctica en `git log`

Podés recorrer `git log --reverse` para ver la secuencia real en 11 pasos:

1. Setup del laboratorio y referencias iniciales
2. Pre-registro del Experimento 03 y banco de 8 tareas antes de invocar modelos
3. Congelado SHA-256 del banco y validación unitaria del arnés
4. Tanda base (`gpt-6.1-sol`, `72` corridas en `low`/`medium`/`high` → techo `24/24`)
5. Extensión 01 (`xhigh` y `max` + controles `high` en `gpt-6.1-sol`, `56` corridas)
6. Extensión 02 (diseño aislado con `bwrap` para 4 modelos adicionales y sondeos iniciales)
7. Enmienda `02-01` y cierre de `gpt-6-luna` (`120` corridas: caída a `13/24` en `low`, `24/24` desde `medium`)
8. Enmienda `02-02`: matrices de Haiku (`119/120`) y Opus (`117/120`), diagnóstico separado de Luna `low` (`6` corridas) y corte de Fable por cuota (`27` evaluables)
9. Enmienda `02-03`: cierre de las `93` celdas pendientes de Fable 5.2 por API key (`4/24` en `max`, `20` timeouts) e integración de las `600` corridas
10. Papers científicos en inglés y español (MD, figuras desde CSV y PDFs)
11. Divulgación para público general (PDF accesible y artículo del blog)

---

## Experimentos publicados

| # | Pregunta | Papers | Divulgación | Datos y código |
|---|---|---|---|---|
| 03 | ¿Más esfuerzo de razonamiento hace que un agente programe mejor? (`600` corridas en `5` modelos) | [EN PDF](experimentos/03-esfuerzo-de-razonamiento/paper/paper-en.pdf) · [ES PDF](experimentos/03-esfuerzo-de-razonamiento/paper/paper-es.pdf) | [PDF público](blog/2026-11-esfuerzo-de-razonamiento.pdf) · [Blog MD](blog/2026-11-esfuerzo-de-razonamiento.md) | [Experimento 03](experimentos/03-esfuerzo-de-razonamiento/) |

---

## Verificación y reproducción rápida

No necesitás dependencias externas para verificar la integridad del banco congelado, correr los `54` tests unitarios del arnés ni recalcular las tablas desde los CSV crudos (Python `3.12+` estándar):

```bash
cd experimentos/03-esfuerzo-de-razonamiento

# 1. Verificar los 34 hashes SHA-256 del banco congelado
python3 - <<'EOF'
import medir
medir.check_frozen()
print("Banco congelado: 34/34 hashes verificados")
EOF

# 2. Ejecutar la suite completa de 54 tests unitarios
python3 -m unittest \
  test_arnes.py test_extension.py test_extension02.py \
  test_extension0202.py test_diagnosticar_luna02.py test_extension0203.py

# 3. Opcional: regenerar figuras (requiere matplotlib)
python3 generar_figuras_paper.py
```
