# Enmienda 02-03 · completar Fable por API key

Este documento se guarda solo en un commit antes de los sondeos, piloto y corridas de esta continuación. No modifica `ENMIENDA-02-02.md`, `extension0202.py`, `medir.py`, el banco congelado ni ningún artefacto de `resultados/extension-02/protocolo-02-02/`. No se hace push.

## 1. Alcance y relación con `protocolo-02-02`

El bloque `claude-fable-5-2` de `protocolo-02-02` cerró incompleto por límite de cuota de suscripción con 28 corridas observadas: 27 evaluables, 1 interrupción por cuota (`principal-07-planificador-xhigh-2`, sin evaluación funcional) y 92 corridas nunca iniciadas.

Esta enmienda completa las **93 celdas sin evaluación funcional** de `claude-fable-5-2` (`principal-07-planificador-xhigh-2` más las 92 nunca iniciadas), conservando intacto el orden fijado en `resultados/extension-02/protocolo-02-02/fable/orden-principal.json` (órdenes 28 a 120). Las 27 observaciones evaluables y la observación original de cuota permanecen sin cambios en `protocolo-02-02/`.

## 2. Canal de autenticación, aislamiento y flags

Se invoca exactamente `--model claude-fable-5-2` mediante el binario oficial de Claude Code (`2.1.317 (Claude Code)`), con los mismos flags públicos, prompt, herramientas (`Read`, `Edit`, `Write`, `Glob`, `Grep`, `Bash`), autorización de Bash en `/work`, timeout de 600 segundos, máximo de dos agentes simultáneos y pruebas ocultas de `ENMIENDA-02-02.md`.

Único cambio de ejecución respecto de `ENMIENDA-02-02.md`:
- No se monta `~/.claude/.credentials.json` (OAuth de suscripción).
- Se pasa `ANTHROPIC_API_KEY` al entorno de `bwrap` en memoria (sin `--clearenv`, construyendo explícitamente un diccionario de entorno mínimo de seis variables) sin escribir credenciales en archivos, recibos ni argumentos de línea de comando.

## 3. Fases, corte y reporte

1. **Verificación previa:** se comprueban el banco congelado (34 hashes), la integridad de `protocolo-02-02` y el inventario de históricos antes de cualquier llamada.
2. **Sondeos y piloto:** se ejecutan los cinco sondeos triviales (`low`, `medium`, `high`, `xhigh`, `max`) y un piloto (`01-lotes`, nivel más bajo aceptado) excluidos de la matriz.
3. **Corridas principales:** se ejecutan de a dos por tanda las 93 celdas pendientes, guardando los artefactos en `resultados/extension-02/protocolo-02-03/fable/` y el CSV en `resultados/crudo-fable-02-03.csv` (piloto en `resultados/piloto-fable-02-03.csv`). Si aparece un error de cuota, saldo o autenticación de API, el lanzamiento se detiene al cerrar la tanda y registra estado `incompleto`.
4. **Resumen:** `resumir0203.py` conserva intacto todo el texto anterior a `## Extensión 02: matriz por modelo` y documenta por separado las 27 evaluables por suscripción (`protocolo-02-02`), las corridas por API (`protocolo-02-03`) y la vista combinada de `claude-fable-5-2` aclarando explícitamente el cambio de canal de autenticación/facturación entre ambas tandas.
