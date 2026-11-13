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
ART = OUT / 'extension-02'
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


def summary():
    files = [OUT / 'crudo.csv', OUT / 'crudo-extension.csv'] + [OUT / f'crudo-{m}.csv' for m in MODELS[1:]]
    original = read_csv(files[0])
    extension = read_csv(files[1])
    rows_by_model = {'gpt-6.1-sol': original + [r for r in extension if r['nivel'] in ('xhigh', 'max')]}
    rows_by_model.update({m: read_csv(OUT / f'crudo-{m}.csv') for m in MODELS[1:]})
    states = {m: json.loads((ART / m / 'estado.json').read_text()) for m in MODELS[1:]}
    for model, rows in rows_by_model.items():
        assert len({r['id'] for r in rows}) == len(rows), f'IDs duplicados: {model}'
        assert all(r['resuelta'] in ('0', '1', '') for r in rows)
        assert all(r['nivel'] in LEVELS or r['nivel'] == 'sin-nivel' for r in rows)
    new = [r for model in MODELS[1:] for r in rows_by_model[model]]
    functional = evaluable(new)
    pilots = {m: read_csv(OUT / f'piloto-{m}.csv') if (OUT / f'piloto-{m}.csv').exists() else [] for m in MODELS[1:]}
    probes = {m: len(list((ART / m / 'sondeos').glob('*.json'))) for m in MODELS[1:]}
    totals = {'observadas_principales': len(new), 'evaluables': len(functional), 'resueltas_evaluables': solved(functional),
              'fallos_funcionales': len(functional) - solved(functional), 'infraestructura': sum(r['estado'] == 'infraestructura' for r in new),
              'cuota': sum(r.get('cuota') == '1' for r in new), 'timeouts': sum(r['timeout'] == '1' for r in new),
              'pilotos_excluidos': sum(len(r) for r in pilots.values()), 'sondeos_excluidos': sum(probes.values())}
    out = ['## Extensión 02: matriz por modelo', '',
           f'La extensión registró **{totals["observadas_principales"]} observaciones principales**: {totals["evaluables"]} evaluables, con {totals["resueltas_evaluables"]} resueltas y {totals["fallos_funcionales"]} fallos funcionales; {totals["infraestructura"]} bloqueo del adaptador queda fuera del denominador funcional. Los {totals["pilotos_excluidos"]} pilotos y {totals["sondeos_excluidos"]} sondeos están excluidos. Hubo {totals["cuota"]} interrupciones por cuota y {totals["timeouts"]} timeouts principales.', '',
           'La referencia de gpt-6.1-sol usa 72 corridas originales y 48 de xhigh/max; excluye los ocho controles high de la extensión 01. No se fusionan sus tandas con la extensión 02. Los CSV anteriores siguen intactos.', '',
           '«Evaluables» excluye cuota e infraestructura. Las medianas incluyen resueltas y fallos funcionales con datos disponibles; los denominadores de segundos y tokens se indican entre paréntesis. Una celda sin muestra no significa cero aciertos. «Pendientes» cuenta las corridas principales que nunca se iniciaron, no el bloqueo ya observado.', '',
           '| Modelo | Nivel | Observadas / previstas | Resueltas / evaluables | Segundos mediana (n) | Tokens mediana (n) | Fuera de alcance / evaluables | Pendientes |',
           '|---|---|---:|---:|---:|---:|---:|---:|']
    for model in MODELS:
        levels = LEVELS if model == MODELS[0] else states[model]['niveles']
        if not levels:
            out.append(f'| {model} | — | 0 / sin definir | Sin muestra atribuible | — (0) | — (0) | — | Sin definir: identidad |')
        for level in levels:
            observed = [r for r in rows_by_model[model] if r['nivel'] == level]
            group = evaluable(observed)
            resolution = f'{solved(group)}/{len(group)}' if group else 'Sin muestra evaluable'
            outside = f'{sum(r["fuera_alcance"] == "1" for r in group)}/{len(group)}' if group else '—'
            ns = sum(r['segundos'] != '' for r in group); nt = sum(r['tokens_totales'] != '' for r in group)
            out.append(f'| {model} | {level} | {len(observed)}/24 | {resolution} | {fmt(median(group,"segundos"))} ({ns}) | {fmt(median(group,"tokens_totales"),1)} ({nt}) | {outside} | {24-len(observed)} |')
    out += ['', '### Cobertura y cierres de los bloques nuevos', '', '| Modelo solicitado | Estado | Principales observadas | Evaluables | Pendientes | Pilotos excluidos | Sondeos excluidos | Motivo |', '|---|---|---:|---:|---:|---:|---:|---|']
    for model in MODELS[1:]:
        state = states[model]; rows = rows_by_model[model]
        pending = state.get('pendientes')
        out.append(f'| {model} | {state["estado"]} | {len(rows)} | {len(evaluable(rows))} | {pending if pending is not None else "Sin definir"} | {len(pilots[model])} | {probes[model]} | {state.get("motivo", "")} |')
    out += ['', '### Razón nivel más alto / nivel más bajo', '',
            'Los cocientes se calculan sobre las medianas de los valores crudos, antes de redondear la presentación. Sólo se informa una razón comparable cuando ambos niveles extremos tienen las 24 observaciones evaluables. Los niveles con el mismo nombre no implican igual procesamiento interno entre modelos.', '',
            '| Modelo | Niveles | Segundos nivel bajo | Segundos nivel alto | Razón tiempo | Tokens nivel bajo | Tokens nivel alto | Razón tokens |', '|---|---|---:|---:|---:|---:|---:|---:|']
    ratios = {}
    for model in MODELS:
        levels = LEVELS if model == MODELS[0] else states[model]['niveles']
        if len(levels) < 2:
            out.append(f'| {model} | — | — | — | No comparable | — | — | No comparable |'); continue
        low, high = levels[0], levels[-1]
        a = evaluable([r for r in rows_by_model[model] if r['nivel'] == low]); b = evaluable([r for r in rows_by_model[model] if r['nivel'] == high])
        if len(a) != 24 or len(b) != 24:
            out.append(f'| {model} | {high}/{low} | — | — | No comparable: cobertura incompleta | — | — | No comparable |'); continue
        av, bv = median(a,'segundos'), median(b,'segundos'); at, bt = median(a,'tokens_totales'), median(b,'tokens_totales')
        tr, nr = bv/av, bt/at
        ratios[model] = {k:str(v) for k,v in {'segundos_bajo':av,'segundos_alto':bv,'razon_tiempo':tr,'tokens_bajo':at,'tokens_alto':bt,'razon_tokens':nr}.items()}
        out.append(f'| {model} | {high}/{low} | {fmt(av)} | {fmt(bv)} | {fmt(tr)} | {fmt(at,1)} | {fmt(bt,1)} | {fmt(nr)} |')
    out += ['', '### Luna por tarea: resueltas sobre tres repeticiones', '', '| Tarea | low | medium | high | xhigh | max |', '|---|---:|---:|---:|---:|---:|']
    tasks = json.loads((ROOT / 'banco.json').read_text())
    for task in tasks:
        cells = []
        for level in LEVELS:
            group = evaluable([r for r in rows_by_model['gpt-6-luna'] if r['tarea'] == task['id'] and r['nivel'] == level])
            cells.append(f'{solved(group)}/{len(group)}' if group else 'Sin muestra')
        out.append('| '+task['id']+' | '+' | '.join(cells)+' |')
    out += ['', '### Todos los fallos funcionales de Luna', '', '| ID | Tests aprobados / total | Segundos | Tokens totales |', '|---|---:|---:|---:|']
    for row in rows_by_model['gpt-6-luna']:
        if row['resuelta'] == '0': out.append(f'| {row["id"]} | {row["tests_aprobados"]}/{row["tests_total"]} | {row["segundos"]} | {row["tokens_totales"]} |')
    out += ['', '### Sólo corridas resueltas', '', '| Modelo | Nivel | n | Segundos mediana (n) | Tokens mediana (n) | Líneas tocadas mediana |', '|---|---|---:|---:|---:|---:|']
    for model in MODELS:
        levels = LEVELS if model == MODELS[0] else states[model]['niveles']
        for level in levels:
            group = [r for r in rows_by_model[model] if r['nivel'] == level and r['resuelta'] == '1']
            out.append(f'| {model} | {level} | {len(group)} | {fmt(median(group,"segundos"))} ({sum(r["segundos"] != "" for r in group)}) | {fmt(median(group,"tokens_totales"),1)} ({sum(r["tokens_totales"] != "" for r in group)}) | {fmt(median(group,"lineas_tocadas"),1)} |')
    out += ['', '### Uso e interpretación de los recibos', '',
            'Codex: total = input_tokens + output_tokens; su caché y razonamiento no se suman otra vez. Claude: total = input_tokens + cache_creation_input_tokens + cache_read_input_tokens + output_tokens; no se suman los desgloses de thinking ni modelUsage encima de usage. Los recibos numéricos crudos conservan ambas contabilidades, duración y turnos cuando el CLI los entrega. La comparación de tokens válida es entre niveles de un mismo modelo y CLI; los totales entre CLI no son homogéneos ni representan precios de suscripción.', '',
            'Los comandos exactos, versiones, montajes y límites están en [OPERACION-02.md](../OPERACION-02.md) y [aislamiento.json](extension-02/aislamiento.json). La reconexión recuperada de una observación de Luna se documenta en [ENMIENDA-02-01.md](../ENMIENDA-02-01.md), con original, hashes y reclasificación auditables; no se repitió la observación ni se alteraron sus tiempos, tokens o tests.']
    numeric = '\n'.join(out)+'\n'
    (ART/'tablas.md').write_text(numeric)
    reading = (ART/'lectura.md').read_text()
    path = OUT/'resumen.md'; original_text = path.read_text().split(MARK,1)[0]
    path.write_text(original_text.rstrip()+'\n\n'+numeric+'\n'+reading)
    provenance = {'generador':'resumir02.py','generador_sha256':sha(Path(__file__)), 'motivo':'Resumen separado; no modifica el arnés de medición ni sus hashes registrados.',
                  'codigo_medicion_sha256':sha(ROOT/'extension02.py'), 'csv_entrada_sha256':{p.name:sha(p) for p in files}, 'conteos':totals,'razones_sobre_medianas_crudas':ratios,
                  'controles_sol_excluidos':sum(r['nivel']=='high' for r in extension)}
    (ART/'resumen-trazabilidad.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'conteos':totals,'razones':ratios},ensure_ascii=False))


if __name__ == '__main__':
    summary()
