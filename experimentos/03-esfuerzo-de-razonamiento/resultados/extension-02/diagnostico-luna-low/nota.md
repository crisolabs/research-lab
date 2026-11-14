# Diagnóstico de Luna low: seis corridas separadas de la matriz.
El agente resolvió 2/6: lotes/1 y caché/2; las otras cuatro terminaron con cero líneas cambiadas.
Los cuatro fallos intentaron leer TAREA.md mediante comandos que devolvieron 127; los recibos conservan comando, estado y retorno.
En caché/1, el agente reconoce que no leyó la tarea ni modificó archivos y pide que le compartan el contenido.
En espera/1 y espera/2, el agente reconoce el bloqueo y pide herramientas de lectura o el contenido; lotes/2 sólo informa que no avanzó.
Los cuatro mensajes no anuncian una implementación terminada ni presentan un parche en texto; no registran intentos de aplicar cambios.
Esos cuatro fallos usaron entre 358 y 536 tokens de salida informados por el CLI, sin que eso mida sólo el mensaje final.
Las dos corridas resueltas también encontraron comandos con retorno 127, pero continuaron leyendo con comandos internos de Bash o con rg y sí editaron.
El patrón muestra abandono ante fallos de herramientas y capacidad de usar otras vías; no establece la causa técnica exacta de esos fallos.
Este diagnóstico es exploratorio: no atribuye retrospectivamente los once fallos originales a este mecanismo, no reclasifica corridas ni entra en la matriz.
