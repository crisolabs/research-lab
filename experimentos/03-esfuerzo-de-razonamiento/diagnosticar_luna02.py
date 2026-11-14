#!/usr/bin/env python3
"""Seis diagnósticos separados: captura final y comandos, nunca matriz."""
import csv
import datetime
import fcntl
import hashlib
import json
from pathlib import Path
import random
import re
import extension0202 as e

DIAG = e.RESULTADOS / 'extension-02' / 'diagnostico-luna-low'
SEED = 2026111304
ORIGINAL_PARSE = e.parse


def sanitize_full(value):
    # Same privacy rules as the adapter, without truncating the final message.
    value = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', str(value))
    value = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[correo omitido]', value)
    value = re.sub(r'(?:/home/|/Users/|/tmp/)[^\s"\'<>]*', '[ruta omitida]', value)
    value = re.sub(r'https?://[^\s"\'<>]+', '[URL omitida]', value)
    value = re.sub(r'(?i)(?:sk-|sess-|eyJ)[a-zA-Z0-9_.-]{12,}', '[secreto omitido]', value)
    return re.sub(r'(?i)(?:Bearer\s+)[^\s]+', '[credencial omitida]', value)


def parse_diagnostic(cli, out, err=b''):
    fields, receipt, effective, error = ORIGINAL_PARSE(cli, out, err)
    messages, commands, changes = [], [], []
    for line in out.decode(errors='replace').splitlines():
        try: event = json.loads(line)
        except ValueError: continue
        if event.get('type') != 'item.completed': continue
        item = event.get('item') or {}
        kind = item.get('type')
        if kind == 'agent_message': messages.append(sanitize_full(item.get('text', '')))
        elif kind == 'command_execution':
            commands.append({'comando': sanitize_full(item.get('command', '')),
                             'estado': item.get('status', ''), 'retorno': item.get('exit_code')})
        elif kind == 'file_change':
            changes.append({'estado': item.get('status', ''), 'archivos': [sanitize_full(c.get('path', '')) for c in item.get('changes', [])]})
    receipt['diagnostico'] = {'mensaje_final': messages[-1] if messages else '', 'comandos': commands, 'aplicaciones_cambio': changes}
    return fields, receipt, effective, error


def schedule():
    items = []
    for task in ('04-espera', '01-lotes', '08-cache'):
        info = next(t for t in e.medir.tasks() if t['id'] == task)
        for rep in (1, 2):
            items.append({'id': f'diagnostico-{task}-low-{rep}', 'fase': 'diagnostico', 'tarea': task,
                          'tipo': info['tipo'], 'repeticion': rep, 'nivel': 'low'})
    random.Random(SEED).shuffle(items)
    for i, item in enumerate(items, 1): item['orden'] = i
    return items


def main():
    e.verify()
    DIAG.mkdir(parents=True, exist_ok=True)
    with (e.ART / '.ejecucion.lock').open('w') as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise SystemExit('Otro runner está activo.')
        items = schedule()
        path = DIAG / 'orden.json'
        previous = e.read(path)
        if previous and previous != items: raise RuntimeError('Cambió el orden diagnóstico.')
        e.write(path, items)
        e.write(DIAG / 'protocolo.json', {'semilla': SEED, 'modelo': 'gpt-6-luna', 'nivel': 'low',
                    'timeout_segundos': 600, 'max_paralelo': 1, 'incluido_matriz': False,
                    'codigo_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
        e.ART = DIAG
        e.parse = parse_diagnostic
        model = 'gpt-6-luna'
        rows = []
        for item in items:
            start = DIAG / model / 'iniciadas' / (item['id'] + '.json')
            done = DIAG / model / 'corridas' / (item['id'] + '.json')
            if start.exists() and not done.exists(): raise RuntimeError('Diagnóstico iniciado sin cierre; no se repite.')
            row = e.read(done) if done.exists() else e.run_one(model, item)
            rows.append(row)
            with (DIAG / 'crudo.csv').open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=e.FIELDS); writer.writeheader(); writer.writerows(rows)
            if row['cuota'] or row['estado'] == 'infraestructura':
                e.write(DIAG / 'estado.json', {'estado': 'incompleto', 'observadas': len(rows), 'pendientes': len(items)-len(rows), 'motivo': row['error']})
                return
        e.write(DIAG / 'estado.json', {'estado': 'completo', 'observadas': len(rows), 'pendientes': 0})


if __name__ == '__main__': main()
