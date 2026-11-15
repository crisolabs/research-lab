#!/usr/bin/env python3
"""Recalcula tablas y trazabilidad integrando protocolo-02-02 y protocolo-02-03 (Fable por API)."""
import json
from pathlib import Path

import resumir0202 as r02

ROOT = r02.ROOT
OUT = r02.OUT
HIST = r02.HIST
ART02 = r02.ART
ART03 = HIST / 'protocolo-02-03'
LEVELS = r02.LEVELS
MODELS = r02.MODELS


def fable_effective_label():
    """Verify and format observed effective model ID across 02-02 and 02-03 receipts."""
    ids = set()
    for base in (ART02 / 'fable' / 'recibos', ART03 / 'fable' / 'recibos'):
        for path in base.glob('principal-*.json'):
            receipt = json.loads(path.read_text())
            uses = receipt.get('uso_por_modelo', {})
            pairs = sorted([(v.get('outputTokens', -1), k) for k, v in uses.items()], reverse=True)
            if pairs and (len(pairs) == 1 or pairs[0][0] > pairs[1][0]):
                ids.add(pairs[0][1])
    return ', '.join(sorted(ids)) if ids else 'claude-fable-5-2'


def summary():
    """Rebuild Extension 02 section of resumen.md without modifying CSVs or historical data."""
    f02_files = [OUT / 'crudo.csv', OUT / 'crudo-extension.csv'] + [r02.csv_path(m) for m in MODELS[1:]]
    f03_main = OUT / 'crudo-fable-02-03.csv'
    f03_pilot = OUT / 'piloto-fable-02-03.csv'
    all_files = f02_files + [f03_main]

    original = r02.read_csv(f02_files[0])
    extension = r02.read_csv(f02_files[1])
    rows_by_model = {'gpt-6.1-sol': original + [row for row in extension if row['nivel'] in ('xhigh', 'max')]}
    for model in MODELS[1:-1]:
        rows_by_model[model] = r02.read_csv(r02.csv_path(model))

    fable_02_raw = r02.read_csv(r02.csv_path('fable'))
    fable_02_eval = r02.evaluable(fable_02_raw)
    fable_03_raw = r02.read_csv(f03_main)
    fable_combined = fable_02_eval + fable_03_raw
    rows_by_model['fable'] = fable_combined

    for model, rows in rows_by_model.items():
        assert len({row['id'] for row in rows}) == len(rows), f'IDs duplicados: {model}'
        assert all(row['resuelta'] in ('0', '1', '') for row in rows)
        assert all(row['nivel'] in LEVELS for row in rows)

    states = {m: json.loads((r02.model_art(m) / 'estado.json').read_text()) for m in MODELS[1:-1]}
    state_f02 = json.loads((ART02 / 'fable' / 'estado.json').read_text())
    state_f03 = json.loads((ART03 / 'fable' / 'estado.json').read_text())

    # Combined extension rows (Sol baseline excluded; Fable combines 27 eval 02-02 + 93 02-03 + 1 quota 02-02).
    new_evaluable = [row for m in MODELS[1:] for row in r02.evaluable(rows_by_model[m])]
    all_observed = [row for m in MODELS[1:-1] for row in rows_by_model[m]] + fable_02_raw + fable_03_raw
    pilots_02 = {m: r02.read_csv(r02.csv_path(m, 'piloto')) for m in MODELS[1:]}
    pilot_03 = r02.read_csv(f03_pilot) if f03_pilot.exists() else []
    probes_02 = {m: len(list((r02.model_art(m) / 'sondeos').glob('*.json'))) for m in MODELS[1:]}
    probes_03 = len(list((ART03 / 'fable' / 'sondeos').glob('*.json')))

    totals = {
        'observadas_principales': len(all_observed),
        'evaluables': len(new_evaluable),
        'resueltas_evaluables': r02.solved(new_evaluable),
        'fallos_funcionales': len(new_evaluable) - r02.solved(new_evaluable),
        'infraestructura': sum(row['estado'] == 'infraestructura' for row in all_observed),
        'cuota': sum(row.get('cuota') == '1' for row in all_observed),
        'timeouts': sum(row['timeout'] == '1' for row in all_observed),
        'pilotos_excluidos': sum(len(v) for v in pilots_02.values()) + len(pilot_03),
        'sondeos_excluidos': sum(probes_02.values()) + probes_03,
    }

    fable_label = fable_effective_label()
    label = lambda m: fable_label if m == 'fable' else m

    out = [
        '## Extensión 02: matriz por modelo',
        '',
        (
            f'La extensión registró **{totals["observadas_principales"]} observaciones principales** '
            f'(388 de `protocolo-02-02` + {len(fable_03_raw)} de `protocolo-02-03`): '
            f'{totals["evaluables"]} evaluables, con {totals["resueltas_evaluables"]} resueltas y '
            f'{totals["fallos_funcionales"]} fallos funcionales; {totals["infraestructura"]} errores de '
            f'infraestructura quedan fuera del denominador funcional. Los {totals["pilotos_excluidos"]} pilotos '
            f'y {totals["sondeos_excluidos"]} sondeos están excluidos. Hubo {totals["cuota"]} interrupción '
            f'por cuota (en `02-02`, re-ejecutada por API en `02-03`) y {totals["timeouts"]} timeouts principales.'
        ),
        '',
        'La referencia de gpt-6.1-sol usa 72 corridas originales y 48 de xhigh/max; excluye los ocho controles high de la extensión 01. En `claude-fable-5-2`, la fila combinada reúne las 27 corridas evaluables por suscripción (`protocolo-02-02`) y las 93 corridas por API key (`protocolo-02-03`).',
        '',
        '«Evaluables» excluye cuota e infraestructura. Las medianas incluyen resueltas y fallos funcionales con datos disponibles; los denominadores de segundos y tokens se indican entre paréntesis.',
        '',
        '| Modelo | Nivel | Observadas / previstas | Resueltas / evaluables | Segundos mediana (n) | Tokens mediana (n) | Fuera de alcance / evaluables | Pendientes |',
        '|---|---|---:|---:|---:|---:|---:|---:|',
    ]

    for model in MODELS:
        for level in LEVELS:
            group = r02.evaluable([row for row in rows_by_model[model] if row['nivel'] == level])
            observed_count = len(group)
            resolution = f'{r02.solved(group)}/{len(group)}' if group else 'Sin muestra evaluable'
            outside = f'{sum(row["fuera_alcance"] == "1" for row in group)}/{len(group)}' if group else '—'
            ns = sum(row['segundos'] != '' for row in group)
            nt = sum(row['tokens_totales'] != '' for row in group)
            out.append(
                f'| {label(model)} | {level} | {observed_count}/24 | {resolution} | '
                f'{r02.fmt(r02.median(group, "segundos"))} ({ns}) | {r02.fmt(r02.median(group, "tokens_totales"), 1)} ({nt}) | '
                f'{outside} | {24 - observed_count} |'
            )

    out += [
        '',
        '### Cobertura y cierres por bloque y canal',
        '',
        '| Bloque | Canal | Estado | Principales observadas | Evaluables | Pendientes | Pilotos excluidos | Sondeos excluidos | Motivo |',
        '|---|---|---|---:|---:|---:|---:|---:|---|',
        f'| gpt-6-luna | OAuth Codex | {states["gpt-6-luna"]["estado"]} | {len(rows_by_model["gpt-6-luna"])} | {len(r02.evaluable(rows_by_model["gpt-6-luna"]))} | 0 | {len(pilots_02["gpt-6-luna"])} | {probes_02["gpt-6-luna"]} | {states["gpt-6-luna"].get("motivo", "")} |',
        f'| claude-haiku-5-5 | OAuth Claude | {states["claude-haiku-5-5"]["estado"]} | {len(rows_by_model["claude-haiku-5-5"])} | {len(r02.evaluable(rows_by_model["claude-haiku-5-5"]))} | 0 | {len(pilots_02["claude-haiku-5-5"])} | {probes_02["claude-haiku-5-5"]} | |',
        f'| claude-opus-5-5 | OAuth Claude | {states["claude-opus-5-5"]["estado"]} | {len(rows_by_model["claude-opus-5-5"])} | {len(r02.evaluable(rows_by_model["claude-opus-5-5"]))} | 0 | {len(pilots_02["claude-opus-5-5"])} | {probes_02["claude-opus-5-5"]} | |',
        f'| claude-fable-5-2 (02-02) | OAuth Claude | {state_f02["estado"]} | {len(fable_02_raw)} | {len(fable_02_eval)} | {state_f02["pendientes"]} | {len(pilots_02["fable"])} | {probes_02["fable"]} | cuota (1 corrida sin evaluar) |',
        f'| claude-fable-5-2 (02-03) | API key | {state_f03["estado"]} | {len(fable_03_raw)} | {len(r02.evaluable(fable_03_raw))} | {state_f03["pendientes"]} | {len(pilot_03)} | {probes_03} | completa las 93 celdas pendientes |',
    ]

    out += [
        '',
        '### Razón nivel más alto / nivel más bajo',
        '',
        'Los cocientes se calculan sobre las medianas de los valores crudos, antes de redondear la presentación. Sólo se informa una razón comparable cuando ambos niveles extremos tienen las 24 observaciones evaluables. Los niveles con el mismo nombre no implican igual procesamiento interno entre modelos.',
        '',
        'Los tiempos incluyen los timeouts funcionales. Si falta el recibo final, los tokens quedan ausentes. El cociente de sus medianas usa sólo los datos disponibles, con n explícitos: no representa el consumo de las corridas sin recibo.',
        '',
        '| Modelo | Niveles | Segundos nivel bajo (n) | Segundos nivel alto (n) | Razón tiempo | Tokens nivel bajo (n) | Tokens nivel alto (n) | Razón tokens |',
        '|---|---|---:|---:|---:|---:|---:|---:|',
    ]

    ratios = {}
    for model in MODELS:
        low, high = LEVELS[0], LEVELS[-1]
        a = r02.evaluable([row for row in rows_by_model[model] if row['nivel'] == low])
        b = r02.evaluable([row for row in rows_by_model[model] if row['nivel'] == high])
        assert len(a) == 24 and len(b) == 24, f'Cobertura incompleta en {model}'
        av, bv = r02.median(a, 'segundos'), r02.median(b, 'segundos')
        at, bt = r02.median(a, 'tokens_totales'), r02.median(b, 'tokens_totales')
        tr = bv / av
        nr = bt / at
        na = sum(row['tokens_totales'] != '' for row in a)
        nb = sum(row['tokens_totales'] != '' for row in b)
        ratios[model] = {k: str(v) for k, v in {'segundos_bajo': av, 'segundos_alto': bv, 'razon_tiempo': tr, 'tokens_bajo': at, 'tokens_alto': bt, 'razon_tokens': nr}.items()}
        ratios[model].update(n_segundos_bajo=len(a), n_segundos_alto=len(b), n_tokens_bajo=na, n_tokens_alto=nb)
        partial = ' (datos parciales)' if na != 24 or nb != 24 else ''
        out.append(f'| {label(model)} | {high}/{low} | {r02.fmt(av)} ({len(a)}) | {r02.fmt(bv)} ({len(b)}) | {r02.fmt(tr)} | {r02.fmt(at, 1)} ({na}) | {r02.fmt(bt, 1)} ({nb}) | {r02.fmt(nr)}{partial} |')

    tasks = json.loads((ROOT / 'banco.json').read_text())
    out += ['', '### Luna por tarea: resueltas sobre tres repeticiones', '', '| Tarea | low | medium | high | xhigh | max |', '|---|---:|---:|---:|---:|---:|']
    for task in tasks:
        cells = [f'{r02.solved(r02.evaluable([r for r in rows_by_model["gpt-6-luna"] if r["tarea"] == task["id"] and r["nivel"] == lvl]))}/3' for lvl in LEVELS]
        out.append('| ' + task['id'] + ' | ' + ' | '.join(cells) + ' |')

    out += ['', '### Tareas con fallos: resueltas / evaluables por nivel', '', '| Modelo | Tarea | low | medium | high | xhigh | max |', '|---|---|---:|---:|---:|---:|---:|']
    for model in MODELS:
        for task in tasks:
            task_rows = [row for row in rows_by_model[model] if row['tarea'] == task['id']]
            if not any(row['resuelta'] == '0' for row in task_rows):
                continue
            cells = []
            for lvl in LEVELS:
                group = r02.evaluable([row for row in task_rows if row['nivel'] == lvl])
                cells.append(f'{r02.solved(group)}/{len(group)}' if group else 'Sin muestra')
            out.append('| ' + label(model) + ' | ' + task['id'] + ' | ' + ' | '.join(cells) + ' |')

    out += ['', '### Todos los fallos funcionales de la matriz', '', '| Modelo | ID | Tests aprobados / total | Segundos | Tokens totales | Motivo |', '|---|---|---:|---:|---:|---|']
    for model in MODELS:
        for row in rows_by_model[model]:
            if row['resuelta'] == '0':
                out.append(f'| {label(model)} | {row["id"]} | {row["tests_aprobados"]}/{row["tests_total"]} | {row["segundos"]} | {row["tokens_totales"] or "—"} | {row["error"]} |')

    out += ['', '### Sólo corridas resueltas', '', '| Modelo | Nivel | n | Segundos mediana (n) | Tokens mediana (n) | Líneas tocadas mediana |', '|---|---|---:|---:|---:|---:|']
    for model in MODELS:
        for level in LEVELS:
            group = [row for row in rows_by_model[model] if row['nivel'] == level and row['resuelta'] == '1']
            out.append(
                f'| {label(model)} | {level} | {len(group)} | '
                f'{r02.fmt(r02.median(group, "segundos"))} ({sum(r["segundos"] != "" for r in group)}) | '
                f'{r02.fmt(r02.median(group, "tokens_totales"), 1)} ({sum(r["tokens_totales"] != "" for r in group)}) | '
                f'{r02.fmt(r02.median(group, "lineas_tocadas"), 1)} |'
            )

    out += [
        '',
        '### Uso e interpretación de los recibos',
        '',
        'Codex: total = input_tokens + output_tokens; su caché y razonamiento no se suman otra vez. Claude: total = input_tokens + cache_creation_input_tokens + cache_read_input_tokens + output_tokens; no se suman los desgloses de thinking ni modelUsage encima de usage. Los recibos numéricos crudos conservan ambas contabilidades, duración y turnos cuando el CLI los entrega. La comparación de tokens válida es entre niveles de un mismo modelo y CLI; los totales entre CLI no son homogéneos ni representan precios de suscripción.',
        '',
        'La continuación inicial sigue [ENMIENDA-02-02.md](../ENMIENDA-02-02.md) (`protocolo-02-02`); el completado de Fable por API key sigue [ENMIENDA-02-03.md](../ENMIENDA-02-03.md) (`protocolo-02-03`), preservando intactos los datos históricos y de `protocolo-02-02`.',
        '',
        '### Denegaciones e identidad informada por Claude',
        '',
        'Una denegación se cuenta sin invalidar la corrida. El efectivo es el ID con más tokens de salida de modelUsage; los otros IDs con menos salida se registran como auxiliares.',
        '',
        '| Modelo solicitado | Denegaciones principales | Corridas con denegación | Modelos efectivos principales | Efectivo ausente | Auxiliares (tokens de salida) |',
        '|---|---:|---:|---|---:|---|',
    ]

    for model in MODELS[2:]:
        records = rows_by_model[model]
        effective = sorted({row['modelo_efectivo'] for row in records if row['modelo_efectivo']})
        auxiliary = {}
        receipt_dirs = [ART02 / model / 'recibos'] + ([ART03 / model / 'recibos'] if model == 'fable' else [])
        for rdir in receipt_dirs:
            for path in rdir.glob('principal-*.json'):
                receipt = json.loads(path.read_text())
                for aux in receipt.get('modelos_auxiliares', []):
                    auxiliary[aux] = auxiliary.get(aux, 0) + receipt['uso_por_modelo'][aux].get('outputTokens', 0)
        denied = sum(int(row.get('denegaciones') or 0) for row in records)
        count = sum(int(row.get('denegaciones') or 0) > 0 for row in records)
        absent = sum(not row['modelo_efectivo'] for row in records)
        out.append('| ' + ('claude-fable-5-2' if model == 'fable' else model) + f' | {denied} | {count} | ' + (', '.join(effective) or 'Sin principales') + f' | {absent} | ' + (', '.join(f'{k}: {v}' for k, v in sorted(auxiliary.items())) or 'Ninguno informado') + ' |')

    out += [
        '',
        '### Protocolo anterior, fuera de esta matriz',
        '',
        'Los archivos originales se conservan con sus hashes. Opus: dos principales (una evaluable resuelta y una anulada por la regla anterior del adaptador); Haiku: un piloto anulado por esa misma regla. Estos tres casos no se reevalúan ni se suman a la matriz nueva. El diagnóstico nuevo de Luna está separado de todas las tablas anteriores y de sus razones.',
    ]

    numeric = '\n'.join(out) + '\n'
    (ART03 / 'tablas.md').write_text(numeric)
    reading = (ART03 / 'lectura.md').read_text()
    path = OUT / 'resumen.md'
    original_text = path.read_text().split(r02.MARK, 1)[0]
    path.write_text(original_text.rstrip() + '\n\n' + numeric + '\n' + reading)

    provenance = {
        'generador': 'resumir0203.py',
        'generador_sha256': r02.sha(Path(__file__)),
        'motivo': 'Integra protocolo-02-02 (suscripción) y protocolo-02-03 (Fable por API key) sin modificar CSVs ni datos históricos.',
        'codigo_medicion_02_02_sha256': r02.sha(ROOT / 'extension0202.py'),
        'codigo_medicion_02_03_sha256': r02.sha(ROOT / 'extension0203.py'),
        'csv_entrada_sha256': {p.name: r02.sha(p) for p in all_files},
        'conteos': totals,
        'razones_sobre_medianas_crudas': ratios,
        'controles_sol_excluidos': sum(row['nivel'] == 'high' for row in extension),
    }
    (ART03 / 'resumen-trazabilidad.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'conteos': totals, 'razones': ratios}, ensure_ascii=False))


if __name__ == '__main__':
    summary()
