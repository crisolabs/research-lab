# Diagnóstico separado de Luna low

Seis observaciones de la enmienda 02-02; no se suman a la matriz, sus medianas ni sus razones. [Nota de diez líneas](nota.md).

| ID | Resuelta | Tests | Líneas tocadas | Segundos | Tokens de salida | Comandos completados / fallidos |
|---|---:|---:|---:|---:|---:|---:|
| diagnostico-01-lotes-low-1 | 1 | 3/3 | 16 | 30.832 | 800 | 4/3 |
| diagnostico-08-cache-low-2 | 1 | 6/6 | 81 | 49.787 | 1802 | 3/6 |
| diagnostico-08-cache-low-1 | 0 | 0/1 | 0 | 17.592 | 520 | 1/4 |
| diagnostico-04-espera-low-1 | 0 | 0/2 | 0 | 15.707 | 536 | 0/3 |
| diagnostico-01-lotes-low-2 | 0 | 0/3 | 0 | 15.637 | 358 | 0/4 |
| diagnostico-04-espera-low-2 | 0 | 0/2 | 0 | 13.993 | 442 | 0/3 |

Los recibos individuales incluyen el mensaje final completo, los comandos con estado y retorno y los eventos de aplicación de cambios. Las salidas arbitrarias de los comandos y el transcript no se conservaron; no se inventa su texto. Retorno 127 es la evidencia técnica capturada: que el agente diga que un comando no está instalado es su interpretación, no una auditoría de instalación.

En los cuatro casos sin cambios el agente reconoce que no pudo leer la tarea y no anuncia éxito. Las dos corridas resueltas también toparon con comandos fallidos: lotes/1 leyó mediante comandos internos de Bash; caché/2 usó rg y aplicó cambios. Esto señala una interacción entre la persistencia del agente y el entorno de herramientas, no un efecto puro del modelo ni una explicación individual comprobada de los once fallos originales.

## Lo que este diagnóstico no demuestra

No reconstruye los mensajes originales, no identifica la causa exacta de la disponibilidad de comandos, no estima frecuencias generales y no justifica reclasificar las observaciones históricas. Se mantuvieron el entorno y el protocolo; no hubo corridas adicionales ni reparación durante el diagnóstico.
