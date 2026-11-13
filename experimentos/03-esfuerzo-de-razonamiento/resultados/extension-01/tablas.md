## Extensión: xhigh y max

Cobertura nueva: **56/56 corridas**: 48/48 principales y 8/8 controles high. Piloto de dos corridas excluido. Semilla 2026111301; mismo banco, arnés y límites que la tanda original. El pre-registro de esta extensión se encuentra en [EXTENSION-01.md](../EXTENSION-01.md).

La tabla conserva low, medium y high de la tanda 1 (24 corridas por nivel) y agrega xhigh y max de la tanda 2 (24 por nivel si la cobertura está completa). Los controles high nuevos se analizan por separado. Las medianas incluyen corridas exitosas y fallidas con datos disponibles; un uso ausente no equivale a cero.

| Tipo | Nivel | n | Resueltas | Tokens mediana (n) | Segundos mediana | Fuera de alcance | Líneas mediana |
|---|---|---:|---:|---:|---:|---:|---:|
| acotada | low | 15 | 15/15 (100.0 %) | 92815.0 (15) | 33.8 | 0/15 (0.0 %) | 22.0 |
| acotada | medium | 15 | 15/15 (100.0 %) | 93205.0 (15) | 40.1 | 0/15 (0.0 %) | 18.0 |
| acotada | high | 15 | 15/15 (100.0 %) | 113517.0 (15) | 55.2 | 0/15 (0.0 %) | 18.0 |
| acotada | xhigh | 15 | 15/15 (100.0 %) | 130263.0 (15) | 75.8 | 0/15 (0.0 %) | 20.0 |
| acotada | max | 15 | 15/15 (100.0 %) | 130388.0 (15) | 91.4 | 0/15 (0.0 %) | 18.0 |
| diseño | low | 9 | 9/9 (100.0 %) | 101008.0 (9) | 49.0 | 0/9 (0.0 %) | 88.0 |
| diseño | medium | 9 | 9/9 (100.0 %) | 102288.0 (9) | 56.4 | 0/9 (0.0 %) | 93.0 |
| diseño | high | 9 | 9/9 (100.0 %) | 133571.0 (9) | 79.2 | 0/9 (0.0 %) | 97.0 |
| diseño | xhigh | 9 | 9/9 (100.0 %) | 140699.0 (9) | 131.6 | 0/9 (0.0 %) | 106.0 |
| diseño | max | 9 | 9/9 (100.0 %) | 149146.0 (9) | 161.4 | 0/9 (0.0 %) | 100.0 |

### Control de high: tanda 1 frente a tanda 2

La tanda 1 aporta tres repeticiones por tarea; la tanda 2 aporta una por tarea, intercalada con xhigh y max. Los cocientes son descriptivos y no corrigen los tiempos de otros niveles.

| Tarea | n tanda 1 / tanda 2 | Resueltas tanda 1 / tanda 2 | Segundos tanda 1 | Segundos tanda 2 | Cociente 2/1 | Tokens tanda 1 | Tokens tanda 2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01-lotes | 3 / 1 | 3/3 / 1/1 | 32.2 | 43.0 | 1.33 | 83958.0 | 99003.0 |
| 02-intervalos | 3 / 1 | 3/3 / 1/1 | 55.2 | 42.9 | 0.78 | 116020.0 | 100064.0 |
| 03-importes | 3 / 1 | 3/3 / 1/1 | 57.8 | 61.2 | 1.06 | 115321.0 | 115078.0 |
| 04-espera | 3 / 1 | 3/3 / 1/1 | 92.6 | 113.9 | 1.23 | 140343.0 | 139620.0 |
| 05-consulta | 3 / 1 | 3/3 / 1/1 | 41.3 | 40.0 | 0.97 | 113517.0 | 99458.0 |
| 06-inventario | 3 / 1 | 3/3 / 1/1 | 86.9 | 109.9 | 1.27 | 140405.0 | 122603.0 |
| 07-planificador | 3 / 1 | 3/3 / 1/1 | 87.9 | 87.2 | 0.99 | 133571.0 | 119912.0 |
| 08-cache | 3 / 1 | 3/3 / 1/1 | 78.1 | 67.3 | 0.86 | 120182.0 | 132237.0 |

| Tipo | n tanda 1 / tanda 2 | Resueltas tanda 1 / tanda 2 | Tokens tanda 1 (n) | Tokens tanda 2 (n) | Segundos tanda 1 | Segundos tanda 2 | Fuera de alcance tanda 1 / tanda 2 | Líneas tanda 1 / tanda 2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| acotada | 15 / 5 | 15/15 / 5/5 | 113517.0 (15) | 100064.0 (5) | 55.2 | 43.0 | 0/15 / 0/5 | 18.0 / 17.0 |
| diseño | 9 / 3 | 9/9 / 3/3 | 133571.0 (9) | 122603.0 (3) | 79.2 | 87.2 | 0/9 / 0/3 | 97.0 / 92.0 |

### Sólo corridas resueltas: cinco niveles

| Tipo | Nivel | n | Tokens mediana | Segundos mediana | Líneas mediana |
|---|---|---:|---:|---:|---:|
| acotada | low | 15 | 92815.0 | 33.8 | 22.0 |
| acotada | medium | 15 | 93205.0 | 40.1 | 18.0 |
| acotada | high | 15 | 113517.0 | 55.2 | 18.0 |
| acotada | xhigh | 15 | 130263.0 | 75.8 | 20.0 |
| acotada | max | 15 | 130388.0 | 91.4 | 18.0 |
| diseño | low | 9 | 101008.0 | 49.0 | 88.0 |
| diseño | medium | 9 | 102288.0 | 56.4 | 93.0 |
| diseño | high | 9 | 133571.0 | 79.2 | 97.0 |
| diseño | xhigh | 9 | 140699.0 | 131.6 | 106.0 |
| diseño | max | 9 | 149146.0 | 161.4 | 100.0 |

### Por tarea: nuevos niveles

| Tarea | Nivel | Resueltas | Tokens mediana (n) | Segundos mediana | Fuera de alcance | Líneas mediana |
|---|---|---:|---:|---:|---:|---:|
| 01-lotes | xhigh | 3/3 | 129784.0 (3) | 54.7 | 0/3 | 15.0 |
| 01-lotes | max | 3/3 | 115713.0 (3) | 55.8 | 0/3 | 15.0 |
| 02-intervalos | xhigh | 3/3 | 119010.0 (3) | 75.8 | 0/3 | 35.0 |
| 02-intervalos | max | 3/3 | 133831.0 (3) | 95.0 | 0/3 | 34.0 |
| 03-importes | xhigh | 3/3 | 132461.0 (3) | 95.2 | 0/3 | 20.0 |
| 03-importes | max | 3/3 | 134002.0 (3) | 94.0 | 0/3 | 18.0 |
| 04-espera | xhigh | 3/3 | 184496.0 (3) | 205.1 | 0/3 | 35.0 |
| 04-espera | max | 3/3 | 155096.0 (3) | 180.9 | 0/3 | 32.0 |
| 05-consulta | xhigh | 3/3 | 100896.0 (3) | 60.8 | 0/3 | 10.0 |
| 05-consulta | max | 3/3 | 119135.0 (3) | 70.7 | 0/3 | 10.0 |
| 06-inventario | xhigh | 3/3 | 147069.0 (3) | 138.0 | 0/3 | 116.0 |
| 06-inventario | max | 3/3 | 157093.0 (3) | 191.4 | 0/3 | 100.0 |
| 07-planificador | xhigh | 3/3 | 171684.0 (3) | 149.7 | 0/3 | 108.0 |
| 07-planificador | max | 3/3 | 149146.0 (3) | 161.4 | 0/3 | 107.0 |
| 08-cache | xhigh | 3/3 | 108774.0 (3) | 97.2 | 0/3 | 79.0 |
| 08-cache | max | 3/3 | 111066.0 (3) | 106.7 | 0/3 | 83.0 |

### Errores, timeouts y uso ausente

Corridas nuevas: 0 timeouts de agente, 0 errores del CLI, 0 timeouts de tests, 0 recibos sin tokens totales y 0 corridas no resueltas. No se reintentaron observaciones.
