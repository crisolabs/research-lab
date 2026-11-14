#!/usr/bin/env python3
"""Recalcula sólo tablas y trazabilidad: no invoca modelos ni modifica CSV."""
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'resultados'
HIST = OUT / 'extension-02'
ART = HIST / 'protocolo-02-02'
LEVELS = ('low', 'medium', 'high', 'xhigh', 'max')
MODELS = ('gpt-6.1-sol', 'gpt-6-luna', 'claude-haiku-5-5', 'claude-opus-5-5', 'fable')
MARK = '\n## Extensión 02: matriz por modelo\n'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


def evaluable(rows):
    return [r for r in rows if r['resuelta'] in ('0', '1') and r.get('cuota') != '1']


def median(rows, field):
    values = [Decimal(r[field]) for r in rows if r.get(field, '') != '']
    return statistics.median(values) if values else None


def fmt(number, digits=3):
    if number is None:
        return '—'
    return f'{number:,.{digits}f}'.replace(',', '@').replace('.', ',').replace('@', '.')


def solved(rows):
    return sum(r['resuelta'] == '1' for r in rows)


def csv_path(model, phase='crudo'):
    suffix = '' if model == 'gpt-6-luna' else '-02-02'
    return OUT / f'{phase}-{model}{suffix}.csv'


def model_art(model):
    return (HIST if model == 'gpt-6-luna' else ART) / model


def model_label(model):
    if model != 'fable': return model
    ids = set()
    receipts = ART / model / 'recibos'
    paths = list(receipts.glob('principal-*.json')) or list(receipts.glob('piloto-*.json')) or list(receipts.glob('sondeo-*.json'))
    for path in paths:
        receipt = json.loads(path.read_text())
        uses = receipt.get('uso_por_modelo', {})
        pairs = sorted([(v.get('outputTokens', -1), k) for k, v in uses.items()], reverse=True)
        if pairs and (len(pairs) == 1 or pairs[0][0] > pairs[1][0]): ids.add(pairs[0][1])
    return ', '.join(sorted(ids)) if ids else 'Fable (pedido claude-fable-5-2; sin identidad medida)'


def summary():
    files = [OUT / 'crudo.csv', OUT / 'crudo-extension.csv'] + [csv_path(m) for m in MODELS[1:]]
    original = read_csv(files[0])
    extension = read_csv(files[1])
    rows_by_model = {'gpt-6.1-sol': original + [r for r in extension if r['nivel'] in ('xhigh', 'max')]}
    rows_by_model.update({m: read_csv(csv_path(m)) for m in MODELS[1:]})
    states = {m: json.loads((model_art(m) / 'estado.json').read_text()) for m in MODELS[1:]}
    for model, rows in rows_by_model.items():
        assert len({r['id'] for r in rows}) == len(rows), f'IDs duplicados: {model}'
        assert all(r['resuelta'] in ('0', '1', '') for r in rows)
        assert all(r['nivel'] in LEVELS or r['nivel'] == 'sin-nivel' for r in rows)
    new = [r for model in MODELS[1:] for r in rows_by_model[model]]
    functional = evaluable(new)
    pilots = {m: read_csv(csv_path(m, 'piloto')) if csv_path(m, 'piloto').exists() else [] for m in MODELS[1:]}
    probes = {m: len(list((model_art(m) / 'sondeos').glob('*.json'))) for m in MODELS[1:]}
    totals = {'observadas_principales': len(new), 'evaluables': len(functional), 'resueltas_evaluables': solved(functional),
              'fallos_funcionales': len(functional) - solved(functional), 'infraestructura': sum(r['estado'] == 'infraestructura' for r in new),
              'cuota': sum(r.get('cuota') == '1' for r in new), 'timeouts': sum(r['timeout'] == '1' for r in new),
              'pilotos_excluidos': sum(len(r) for r in pilots.values()), 'sondeos_excluidos': sum(probes.values())}
    out = ['## Extensión 02: matriz por modelo', '',
           f'La extensión registró **{totals["observadas_principales"]} observaciones principales**: {totals["evaluables"]} evaluables, con {totals["resueltas_evaluables"]} resueltas y {totals["fallos_funcionales"]} fallos funcionales; {totals["infraestructura"]} errores de infraestructura quedan fuera del denominador funcional. Los {totals["pilotos_excluidos"]} pilotos y {totals["sondeos_excluidos"]} sondeos están excluidos. Hubo {totals["cuota"]} interrupciones por cuota y {totals["timeouts"]} timeouts principales.', '',
           'La referencia de gpt-6.1-sol usa 72 corridas originales y 48 de xhigh/max; excluye los ocho controles high de la extensión 01. No se fusionan sus tandas con la extensión 02. Los CSV anteriores siguen intactos.', '',
           '«Evaluables» excluye cuota e infraestructura. Las medianas incluyen resueltas y fallos funcionales con datos disponibles; los denominadores de segundos y tokens se indican entre paréntesis. Una celda sin muestra no significa cero aciertos. «Pendientes» cuenta las corridas principales que nunca se iniciaron, no el bloqueo ya observado.', '',
           '| Modelo | Nivel | Observadas / previstas | Resueltas / evaluables | Segundos mediana (n) | Tokens mediana (n) | Fuera de alcance / evaluables | Pendientes |',
           '|---|---|---:|---:|---:|---:|---:|---:|']
    for model in MODELS:
        levels = LEVELS if model == MODELS[0] else states[model]['niveles']
        if not levels:
            out.append(f'| {model_label(model)} | — | 0 / sin definir | Sin muestra atribuible | — (0) | — (0) | — | Sin definir: bloque no medido |')
        for level in levels:
            observed = [r for r in rows_by_model[model] if r['nivel'] == level]
            group = evaluable(observed)
            resolution = f'{solved(group)}/{len(group)}' if group else 'Sin muestra evaluable'
            outside = f'{sum(r["fuera_alcance"] == "1" for r in group)}/{len(group)}' if group else '—'
            ns = sum(r['segundos'] != '' for r in group); nt = sum(r['tokens_totales'] != '' for r in group)
            out.append(f'| {model_label(model)} | {level} | {len(observed)}/24 | {resolution} | {fmt(median(group,"segundos"))} ({ns}) | {fmt(median(group,"tokens_totales"),1)} ({nt}) | {outside} | {24-len(observed)} |')
    out += ['', '### Cobertura y cierres de los bloques nuevos', '', '| Modelo solicitado | Estado | Principales observadas | Evaluables | Pendientes | Pilotos excluidos | Sondeos excluidos | Motivo |', '|---|---|---:|---:|---:|---:|---:|---|']
    for model in MODELS[1:]:
        state = states[model]; rows = rows_by_model[model]
        pending = state.get('pendientes')
        out.append(f'| {model_label(model)} | {state["estado"]} | {len(rows)} | {len(evaluable(rows))} | {pending if pending is not None else "Sin definir"} | {len(pilots[model])} | {probes[model]} | {state.get("motivo", "")} |')
    out += ['', '### Razón nivel más alto / nivel más bajo', '',
            'Los cocientes se calculan sobre las medianas de los valores crudos, antes de redondear la presentación. Sólo se informa una razón comparable cuando ambos niveles extremos tienen las 24 observaciones evaluables. Los niveles con el mismo nombre no implican igual procesamiento interno entre modelos.', '',
            'Los tiempos incluyen los timeouts funcionales. Si falta el recibo final, los tokens quedan ausentes. El cociente de sus medianas usa sólo los datos disponibles, con n explícitos: no representa el consumo de las corridas sin recibo.', '',
            '| Modelo | Niveles | Segundos nivel bajo (n) | Segundos nivel alto (n) | Razón tiempo | Tokens nivel bajo (n) | Tokens nivel alto (n) | Razón tokens |', '|---|---|---:|---:|---:|---:|---:|---:|']
    ratios = {}
    for model in MODELS:
        levels = LEVELS if model == MODELS[0] else states[model]['niveles']
        if len(levels) < 2:
            out.append(f'| {model_label(model)} | — | — | — | No comparable | — | — | No comparable |'); continue
        low, high = levels[0], levels[-1]
        a = evaluable([r for r in rows_by_model[model] if r['nivel'] == low]); b = evaluable([r for r in rows_by_model[model] if r['nivel'] == high])
        if len(a) != 24 or len(b) != 24:
            out.append(f'| {model_label(model)} | {high}/{low} | — | — | No comparable: cobertura incompleta | — | — | No comparable |'); continue
        av, bv = median(a,'segundos'), median(b,'segundos'); at, bt = median(a,'tokens_totales'), median(b,'tokens_totales')
        tr = bv/av
        nr = bt/at if at and bt is not None else None
        na = sum(r['tokens_totales'] != '' for r in a); nb = sum(r['tokens_totales'] != '' for r in b)
        ratios[model] = {k:str(v) for k,v in {'segundos_bajo':av,'segundos_alto':bv,'razon_tiempo':tr,'tokens_bajo':at,'tokens_alto':bt,'razon_tokens':nr}.items()}
        ratios[model].update(n_segundos_bajo=len(a), n_segundos_alto=len(b), n_tokens_bajo=na, n_tokens_alto=nb)
        partial = ' (datos parciales)' if na != 24 or nb != 24 else ''
        out.append(f'| {model_label(model)} | {high}/{low} | {fmt(av)} ({len(a)}) | {fmt(bv)} ({len(b)}) | {fmt(tr)} | {fmt(at,1)} ({na}) | {fmt(bt,1)} ({nb}) | {fmt(nr)}{partial} |')
    out += ['', '### Luna por tarea: resueltas sobre tres repeticiones', '', '| Tarea | low | medium | high | xhigh | max |', '|---|---:|---:|---:|---:|---:|']
    tasks = json.loads((ROOT / 'banco.json').read_text())
    for task in tasks:
        cells = []
        for level in LEVELS:
            group = evaluable([r for r in rows_by_model['gpt-6-luna'] if r['tarea'] == task['id'] and r['nivel'] == level])
            cells.append(f'{solved(group)}/{len(group)}' if group else 'Sin muestra')
        out.append('| '+task['id']+' | '+' | '.join(cells)+' |')
    out += ['', '### Tareas con fallos: resueltas / evaluables por nivel', '', '| Modelo | Tarea | low | medium | high | xhigh | max |', '|---|---|---:|---:|---:|---:|---:|']
    for model in MODELS:
        for task in tasks:
            task_rows = [r for r in rows_by_model[model] if r['tarea'] == task['id']]
            if not any(r['resuelta'] == '0' for r in task_rows): continue
            cells = []
            for level in LEVELS:
                group = evaluable([r for r in task_rows if r['nivel'] == level])
                cells.append(f'{solved(group)}/{len(group)}' if group else 'Sin muestra')
            out.append('| '+model_label(model)+' | '+task['id']+' | '+' | '.join(cells)+' |')
    out += ['', '### Todos los fallos funcionales de la matriz', '', '| Modelo | ID | Tests aprobados / total | Segundos | Tokens totales | Motivo |', '|---|---|---:|---:|---:|---|']
    for model in MODELS:
      for row in rows_by_model[model]:
        if row['resuelta'] == '0': out.append(f'| {model_label(model)} | {row["id"]} | {row["tests_aprobados"]}/{row["tests_total"]} | {row["segundos"]} | {row["tokens_totales"] or "—"} | {row["error"]} |')
    out += ['', '### Sólo corridas resueltas', '', '| Modelo | Nivel | n | Segundos mediana (n) | Tokens mediana (n) | Líneas tocadas mediana |', '|---|---|---:|---:|---:|---:|']
    for model in MODELS:
        levels = LEVELS if model == MODELS[0] else states[model]['niveles']
        for level in levels:
            group = [r for r in rows_by_model[model] if r['nivel'] == level and r['resuelta'] == '1']
            out.append(f'| {model_label(model)} | {level} | {len(group)} | {fmt(median(group,"segundos"))} ({sum(r["segundos"] != "" for r in group)}) | {fmt(median(group,"tokens_totales"),1)} ({sum(r["tokens_totales"] != "" for r in group)}) | {fmt(median(group,"lineas_tocadas"),1)} |')
    out += ['', '### Uso e interpretación de los recibos', '',
            'Codex: total = input_tokens + output_tokens; su caché y razonamiento no se suman otra vez. Claude: total = input_tokens + cache_creation_input_tokens + cache_read_input_tokens + output_tokens; no se suman los desgloses de thinking ni modelUsage encima de usage. Los recibos numéricos crudos conservan ambas contabilidades, duración y turnos cuando el CLI los entrega. La comparación de tokens válida es entre niveles de un mismo modelo y CLI; los totales entre CLI no son homogéneos ni representan precios de suscripción.', '',
            'La continuación sigue [ENMIENDA-02-02.md](../ENMIENDA-02-02.md), con aislamiento y hashes propios en protocolo-02-02. El banco y los históricos permanecen intactos. Las dos observaciones anteriores de Opus y el piloto anterior de Haiku son protocolo anterior y no están en esta matriz. La reclasificación anterior de Luna permanece documentada en ENMIENDA-02-01.md; esta continuación no reclasifica corridas históricas de Luna ni del protocolo anterior.']
    out += ['', '### Denegaciones e identidad informada por Claude', '',
            'Una denegación se cuenta sin invalidar la corrida. El efectivo es el ID con más tokens de salida de modelUsage; los otros IDs con menos salida se registran como auxiliares. Fable se solicitó como claude-fable-5-2: el rótulo de sus tablas sigue al ID informado, incluso si difiere.', '',
            '| Modelo solicitado | Denegaciones principales | Corridas con denegación | Modelos efectivos principales | Efectivo ausente | Auxiliares (tokens de salida) |',
            '|---|---:|---:|---|---:|---|']
    for model in MODELS[2:]:
        records = rows_by_model[model]
        effective = sorted({r['modelo_efectivo'] for r in records if r['modelo_efectivo']})
        auxiliary = {}
        for path in (ART / model / 'recibos').glob('principal-*.json'):
            receipt = json.loads(path.read_text())
            for aux in receipt.get('modelos_auxiliares', []):
                auxiliary[aux] = auxiliary.get(aux, 0) + receipt['uso_por_modelo'][aux].get('outputTokens', 0)
        denied = sum(int(r.get('denegaciones') or 0) for r in records)
        count = sum(int(r.get('denegaciones') or 0) > 0 for r in records)
        absent = sum(not r['modelo_efectivo'] for r in records)
        out.append('| '+('claude-fable-5-2' if model == 'fable' else model)+f' | {denied} | {count} | '+(', '.join(effective) or 'Sin principales')+f' | {absent} | '+(', '.join(f'{k}: {v}' for k,v in sorted(auxiliary.items())) or 'Ninguno informado')+' |')
    out += ['', '### Protocolo anterior, fuera de esta matriz', '',
            'Los archivos originales se conservan con sus hashes. Opus: dos principales (una evaluable resuelta y una anulada por la regla anterior del adaptador); Haiku: un piloto anulado por esa misma regla. Estos tres casos no se reevalúan ni se suman a la matriz nueva. Los sondeos y pilotos anteriores de los demás modelos tampoco se incorporan a los bloques nuevos. El diagnóstico nuevo de Luna está separado de todas las tablas anteriores y de sus razones.']
    numeric = '\n'.join(out)+'\n'
    (ART/'tablas.md').write_text(numeric)
    reading = (ART/'lectura.md').read_text()
    path = OUT/'resumen.md'; original_text = path.read_text().split(MARK,1)[0]
    path.write_text(original_text.rstrip()+'\n\n'+numeric+'\n'+reading)
    provenance = {'generador':'resumir0202.py','generador_sha256':sha(Path(__file__)), 'motivo':'Resumen separado; no modifica el arnés de medición ni sus hashes registrados.',
                  'codigo_medicion_sha256':sha(ROOT/'extension0202.py'), 'csv_entrada_sha256':{p.name:sha(p) for p in files}, 'conteos':totals,'razones_sobre_medianas_crudas':ratios,
                  'controles_sol_excluidos':sum(r['nivel']=='high' for r in extension)}
    (ART/'resumen-trazabilidad.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'conteos':totals,'razones':ratios},ensure_ascii=False))


if __name__ == '__main__':
    summary()
