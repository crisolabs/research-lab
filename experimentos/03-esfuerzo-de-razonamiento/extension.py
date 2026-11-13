#!/usr/bin/env python3
"""Extensión 01: conserva medir.py y separa las nuevas observaciones."""
import argparse
import collections
import csv
import datetime
import hashlib
import itertools
import json
from pathlib import Path
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import medir

ROOT = Path(__file__).resolve().parent
RESULTADOS = ROOT / 'resultados'
ARTEFACTOS = RESULTADOS / 'extension-01'
SEED = 2026111301
LEVELS = ('xhigh', 'max')
FASES = ('piloto-extension', 'extension')
MARCA = '\n## Extensión: xhigh y max\n'


def schedule(phase):
    if phase not in FASES:
        raise ValueError('Fase de extensión desconocida')
    result = []
    bank = medir.tasks()[:1] if phase == FASES[0] else medir.tasks()
    repetitions = range(1, 2 if phase == FASES[0] else 4)
    for task, level, repetition in itertools.product(bank, LEVELS, repetitions):
        result.append(dict(fase=phase, tarea=task['id'], tipo=task['tipo'],
                           nivel=level, repeticion=repetition,
                           id=f'{phase}-{task["id"]}-{level}-{repetition}'))
    if phase == FASES[1]:
        for task in bank:
            result.append(dict(fase=phase, tarea=task['id'], tipo=task['tipo'],
                               nivel='high', repeticion=1,
                               id=f'{phase}-{task["id"]}-high-control-1'))
    random.Random(SEED).shuffle(result)
    for order, row in enumerate(result, 1):
        row['orden'] = order
    return result


def export_csv(phase):
    rows = []
    for item in schedule(phase):
        path = ARTEFACTOS / 'corridas' / (item['id'] + '.json')
        if path.exists():
            rows.append(json.loads(path.read_text()))
    RESULTADOS.mkdir(exist_ok=True)
    path = RESULTADOS / ('piloto-extension.csv' if phase == FASES[0] else 'crudo-extension.csv')
    temporary = path.with_suffix('.tmp')
    with temporary.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=medir.FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)
    return rows


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configure():
    # Sólo cambia el destino y el exportador; run_one, command y evaluate son originales.
    medir.RESULTADOS = ARTEFACTOS
    medir.export_csv = export_csv


def preflight():
    configure()
    medir.preflight()
    evidence = {
        'verificado_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'coinciden': True,
        'cantidad_archivos': len(medir.bank_hashes()),
        'hashes': medir.bank_hashes(),
        'manifiesto_sha256': sha(ROOT / 'banco-congelado.json'),
        'crudo_original_sha256': sha(RESULTADOS / 'crudo.csv'),
        'extension_codigo_sha256': sha(ROOT / 'extension.py'),
        'prerregistro_sha256': sha(ROOT / 'EXTENSION-01.md'),
    }
    # La primera evidencia fija también el arnés suplementario antes del primer modelo.
    path = ARTEFACTOS / 'verificacion-congelado.json'
    if path.exists():
        previous = json.loads(path.read_text())
        for field in ('hashes', 'manifiesto_sha256', 'crudo_original_sha256',
                      'extension_codigo_sha256', 'prerregistro_sha256'):
            if previous[field] != evidence[field]:
                raise SystemExit('Cambió un archivo fijado antes de la extensión; no se ejecuta.')
    else:
        medir.write_json(path, evidence)
    env_path = ARTEFACTOS / 'entorno.json'
    environment = json.loads(env_path.read_text())
    environment.update(semilla=SEED,
                       orden_aleatorio='random.Random(2026111301).shuffle; piloto separado; 48 principales + 8 controles en una lista',
                       niveles_nuevos=list(LEVELS), nivel_control='high',
                       recibos_separados=True)
    medir.write_json(env_path, environment)


def run_matrix(phase):
    preflight()
    existing = [json.loads(path.read_text()).get('orden_real_inicio', 0)
                for path in (ARTEFACTOS / 'iniciadas').glob('*.json')]
    medir.START_SEQ = max(existing, default=0)
    queue = schedule(phase)
    order_path = RESULTADOS / f'orden-{phase}.json'
    if order_path.exists() and json.loads(order_path.read_text()) != queue:
        raise SystemExit('El orden guardado no coincide; no se modifica.')
    medir.write_json(order_path, queue)
    if phase == FASES[1]:
        pilot = export_csv(FASES[0])
        if len(pilot) != 2 or any(row['estado'] != 'completa' or row['tokens_totales'] == '' for row in pilot):
            raise SystemExit('Piloto incompleto o infraestructura/uso inválido: no lanzar matriz.')
    pending = []
    for row in queue:
        done = ARTEFACTOS / 'corridas' / (row['id'] + '.json')
        start = ARTEFACTOS / 'iniciadas' / (row['id'] + '.json')
        if start.exists() and not done.exists():
            raise SystemExit('Corrida iniciada sin cierre: requiere auditoría, no se repite.')
        if not done.exists():
            pending.append(row)
    for position in range(0, len(pending), 2):
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = []
            for row in pending[position:position + 2]:
                futures.append(pool.submit(medir.run_one, row))
                time.sleep(.05)
            results = [future.result() for future in futures]
        if any(row['estado'] == 'cli_falla' for row in results):
            raise SystemExit('Se pausa por error CLI; no se consumen las corridas pendientes.')
    export_csv(phase)


def read_csv(path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


def median(rows, key):
    return medir.median(rows, key)


def solved(rows):
    return sum(int(row['resuelta']) for row in rows)


def summarize():
    original = read_csv(RESULTADOS / 'crudo.csv')
    new = export_csv(FASES[1])
    main = original + [row for row in new if row['nivel'] in LEVELS]
    control = [row for row in new if row['nivel'] == 'high']
    out = ['## Extensión: xhigh y max', '',
           f'Cobertura nueva: **{len(new)}/56 corridas**: {sum(row["nivel"] in LEVELS for row in new)}/48 principales y {len(control)}/8 controles high. Piloto de dos corridas excluido. Semilla 2026111301; mismo banco, arnés y límites que la tanda original. El pre-registro de esta extensión se encuentra en [EXTENSION-01.md](../EXTENSION-01.md).', '',
           'La tabla conserva low, medium y high de la tanda 1 (24 corridas por nivel) y agrega xhigh y max de la tanda 2 (24 por nivel si la cobertura está completa). Los controles high nuevos se analizan por separado. Las medianas incluyen corridas exitosas y fallidas con datos disponibles; un uso ausente no equivale a cero.', '',
           '| Tipo | Nivel | n | Resueltas | Tokens mediana (n) | Segundos mediana | Fuera de alcance | Líneas mediana |',
           '|---|---|---:|---:|---:|---:|---:|---:|']
    for kind, level in itertools.product(('acotada', 'diseño'), ('low', 'medium', 'high', *LEVELS)):
        group = [row for row in main if row['tipo'] == kind and row['nivel'] == level]
        count = len(group)
        extra = sum(int(row['fuera_alcance']) for row in group)
        nt = sum(row['tokens_totales'] != '' for row in group)
        if count:
            out.append(f'| {kind} | {level} | {count} | {solved(group)}/{count} ({100 * solved(group) / count:.1f} %) | {median(group,"tokens_totales")} ({nt}) | {median(group,"segundos")} | {extra}/{count} ({100 * extra / count:.1f} %) | {median(group,"lineas_tocadas")} |')
        else:
            out.append(f'| {kind} | {level} | 0 | — | — | — | — | — |')
    out += ['', '### Control de high: tanda 1 frente a tanda 2', '',
            'La tanda 1 aporta tres repeticiones por tarea; la tanda 2 aporta una por tarea, intercalada con xhigh y max. Los cocientes son descriptivos y no corrigen los tiempos de otros niveles.', '',
            '| Tarea | n tanda 1 / tanda 2 | Resueltas tanda 1 / tanda 2 | Segundos tanda 1 | Segundos tanda 2 | Cociente 2/1 | Tokens tanda 1 | Tokens tanda 2 |',
            '|---|---:|---:|---:|---:|---:|---:|---:|']
    for task in medir.tasks():
        first = [row for row in original if row['nivel'] == 'high' and row['tarea'] == task['id']]
        second = [row for row in control if row['tarea'] == task['id']]
        ratio = statistics.median(float(row['segundos']) for row in second) / statistics.median(float(row['segundos']) for row in first) if second else None
        out.append(f'| {task["id"]} | {len(first)} / {len(second)} | {solved(first)}/{len(first)} / {solved(second)}/{len(second)} | {median(first,"segundos")} | {median(second,"segundos")} | {ratio:.2f} | {median(first,"tokens_totales")} | {median(second,"tokens_totales")} |' if ratio is not None else f'| {task["id"]} | {len(first)} / 0 | {solved(first)}/{len(first)} / — | {median(first,"segundos")} | — | — | {median(first,"tokens_totales")} | — |')
    out += ['', '| Tipo | n tanda 1 / tanda 2 | Resueltas tanda 1 / tanda 2 | Tokens tanda 1 (n) | Tokens tanda 2 (n) | Segundos tanda 1 | Segundos tanda 2 | Fuera de alcance tanda 1 / tanda 2 | Líneas tanda 1 / tanda 2 |',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for kind in ('acotada', 'diseño'):
        a = [row for row in original if row['nivel'] == 'high' and row['tipo'] == kind]
        b = [row for row in control if row['tipo'] == kind]
        out.append(f'| {kind} | {len(a)} / {len(b)} | {solved(a)}/{len(a)} / {solved(b)}/{len(b)} | {median(a,"tokens_totales")} ({sum(r["tokens_totales"] != "" for r in a)}) | {median(b,"tokens_totales")} ({sum(r["tokens_totales"] != "" for r in b)}) | {median(a,"segundos")} | {median(b,"segundos")} | {sum(int(r["fuera_alcance"]) for r in a)}/{len(a)} / {sum(int(r["fuera_alcance"]) for r in b)}/{len(b)} | {median(a,"lineas_tocadas")} / {median(b,"lineas_tocadas")} |')
    out += ['', '### Sólo corridas resueltas: cinco niveles', '',
            '| Tipo | Nivel | n | Tokens mediana | Segundos mediana | Líneas mediana |',
            '|---|---|---:|---:|---:|---:|']
    for kind, level in itertools.product(('acotada', 'diseño'), ('low', 'medium', 'high', *LEVELS)):
        group = [row for row in main if row['tipo'] == kind and row['nivel'] == level and int(row['resuelta'])]
        out.append(f'| {kind} | {level} | {len(group)} | {median(group,"tokens_totales")} | {median(group,"segundos")} | {median(group,"lineas_tocadas")} |')
    out += ['', '### Por tarea: nuevos niveles', '',
            '| Tarea | Nivel | Resueltas | Tokens mediana (n) | Segundos mediana | Fuera de alcance | Líneas mediana |',
            '|---|---|---:|---:|---:|---:|---:|']
    for task, level in itertools.product(medir.tasks(), LEVELS):
        group = [row for row in new if row['tarea'] == task['id'] and row['nivel'] == level]
        out.append(f'| {task["id"]} | {level} | {solved(group)}/{len(group)} | {median(group,"tokens_totales")} ({sum(r["tokens_totales"] != "" for r in group)}) | {median(group,"segundos")} | {sum(int(r["fuera_alcance"]) for r in group)}/{len(group)} | {median(group,"lineas_tocadas")} |')
    out += ['', '### Errores, timeouts y uso ausente', '',
            f'Corridas nuevas: {sum(int(r["timeout"]) for r in new)} timeouts de agente, {sum(r["estado"] == "cli_falla" for r in new)} errores del CLI, {sum(r["error"] == "timeout_tests" for r in new)} timeouts de tests, {sum(r["tokens_totales"] == "" for r in new)} recibos sin tokens totales y {sum(not int(r["resuelta"]) for r in new)} corridas no resueltas. No se reintentaron observaciones.']
    errors = [row for row in new if row['error']]
    for row in errors:
        out.append(f'- `{row["id"]}`: `{row["error"]}`, estado `{row["estado"]}`, {row["tests_aprobados"]}/{row["tests_total"]} tests, {row["segundos"]} segundos.')
    numeric = '\n'.join(out) + '\n'
    (ARTEFACTOS / 'tablas.md').write_text(numeric)
    # La lectura editorial se conserva aparte: recalcular no la sustituye.
    reading_path = ARTEFACTOS / 'lectura.md'
    reading = reading_path.read_text() if reading_path.exists() else '\n### Lectura\n\nPendiente de interpretar los datos completos.\n'
    summary = RESULTADOS / 'resumen.md'
    original_text = summary.read_text().split(MARCA, 1)[0]
    summary.write_text(original_text + '\n' + numeric + reading)
    print(json.dumps({'corridas_extension': len(new), 'controles': len(control), 'piloto': len(export_csv(FASES[0]))}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('accion', choices=('verificar', 'piloto', 'principal', 'resumir'))
    action = parser.parse_args().accion
    if action == 'verificar':
        preflight()
        print(json.dumps({'hashes_coinciden': True, 'archivos': len(medir.bank_hashes()), 'semilla': SEED}))
    elif action == 'resumir':
        summarize()
    else:
        run_matrix(FASES[0] if action == 'piloto' else FASES[1])


if __name__ == '__main__':
    main()
