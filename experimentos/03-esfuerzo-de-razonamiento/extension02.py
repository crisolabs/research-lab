#!/usr/bin/env python3
"""Extensión 02: adaptadores oficiales, banco intacto y observaciones retomables."""
import argparse
import csv
import datetime
import fcntl
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import medir

ROOT = Path(__file__).resolve().parent
RESULTADOS = ROOT / 'resultados'
ART = RESULTADOS / 'extension-02'
SEED = 2026111302
LEVELS = ('low', 'medium', 'high', 'xhigh', 'max')
MODELS = ('gpt-6-luna', 'claude-haiku-5-5', 'claude-opus-5-5', 'fable')
VERSIONS = {'codex': 'codex-cli 0.166.0', 'claude': '2.1.317 (Claude Code)'}
FIELDS = list(medir.FIELDS) + ['modelo', 'modelo_efectivo', 'proveedor', 'cuota', 'error_textual', 'advertencias']
TRIVIAL = 'Respondé solamente OK. No uses herramientas'
LOCK = threading.Lock()
ACTIVE = 0
SEQ = 0


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provider(model):
    return 'openai' if model == MODELS[0] else 'anthropic'


def write(path, obj):
    medir.write_json(path, obj)


def read(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def clean(text):
    text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', str(text))
    text = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[correo omitido]', text)
    text = re.sub(r'(?:/home/|/Users/|/tmp/)[^\s"\'<>]*', '[ruta omitida]', text)
    text = re.sub(r'https?://[^\s"\'<>]+', '[URL omitida]', text)
    text = re.sub(r'(?i)(?:sk-|sess-|eyJ)[a-zA-Z0-9_.-]{12,}', '[secreto omitido]', text)
    text = re.sub(r'(?i)(?:Bearer\s+)[^\s]+', '[credencial omitida]', text)
    return text[:8000]


def numeric(obj):
    """Only numeric usage objects; do not retain arbitrary provider strings."""
    if isinstance(obj, dict):
        return {k: numeric(v) for k, v in obj.items() if isinstance(v, (dict, int, float)) and not isinstance(v, bool)}
    return obj


def parse(cli, out, err=b''):
    objects = []
    try:
        whole = json.loads(out)
        if isinstance(whole, dict): objects.append(whole)
    except ValueError:
        pass
    for line in out.decode(errors='replace').splitlines():
        try:
            obj = json.loads(line)
            if isinstance(obj, dict) and obj not in objects: objects.append(obj)
        except ValueError:
            pass
    receipt = {'tipos_eventos': [o.get('type', 'unknown') for o in objects], 'uso': {}, 'uso_por_modelo': {}}
    messages = []
    if cli == 'codex':
        final_completed = max((i for i, obj in enumerate(objects) if obj.get('type') == 'turn.completed'), default=-1)
        receipt['advertencias'] = []
        for index, obj in enumerate(objects):
            if obj.get('type') == 'turn.completed': receipt['uso'] = numeric(obj.get('usage') or {})
            if obj.get('type') in ('error', 'turn.failed'):
                message = obj.get('message', obj.get('error', ''))
                if isinstance(message, dict): message = message.get('message', '')
                low = str(message).lower()
                recovered_network = (index < final_completed and 'reconnecting' in low and any(k in low for k in ('stream disconnected', 'connection reset', 'io error', 'network')))
                if recovered_network and category(str(message)) == 'infraestructura':
                    receipt['advertencias'].append(clean(message))
                else:
                    messages.append(str(message))
        usage = receipt['uso']
        total = usage['input_tokens'] + usage['output_tokens'] if all(k in usage for k in ('input_tokens', 'output_tokens')) else ''
        fields = {'tokens_entrada': usage.get('input_tokens', ''), 'tokens_cache': usage.get('cached_input_tokens', ''),
                  'tokens_salida': usage.get('output_tokens', ''), 'tokens_razonamiento': usage.get('reasoning_output_tokens', usage.get('reasoning_tokens', ''))}
        effective = ''
    else:
        obj = objects[-1] if objects else {}
        receipt['uso'] = numeric(obj.get('usage') or {})
        receipt['uso_por_modelo'] = {k: numeric(v) for k, v in (obj.get('modelUsage') or {}).items() if re.fullmatch(r'claude-[a-zA-Z0-9_.-]+', k)}
        for key in ('duration_ms', 'duration_api_ms', 'num_turns'):
            if isinstance(obj.get(key), (int, float)): receipt[key] = obj[key]
        receipt['subtipo'] = clean(obj.get('subtype', ''))
        receipt['es_error'] = bool(obj.get('is_error', False))
        denials = obj.get('permission_denials') or []
        receipt['permisos_denegados'] = {'cantidad': len(denials), 'herramientas': sorted({d.get('tool_name') if d.get('tool_name') in ('Read', 'Edit', 'Write', 'Bash') else 'otra' for d in denials if isinstance(d, dict)})}
        declared = obj.get('model', '')
        receipt['modelo_principal_declarado'] = declared if re.fullmatch(r'claude-[a-zA-Z0-9_.-]+', str(declared)) else ''
        usage = receipt['uso']
        total = sum(usage.get(k, 0) for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens')) if all(k in usage for k in ('input_tokens', 'output_tokens')) else ''
        fields = {'tokens_entrada': usage.get('input_tokens', ''), 'tokens_cache': usage.get('cache_read_input_tokens', ''),
                  'tokens_salida': usage.get('output_tokens', ''), 'tokens_razonamiento': usage.get('thinking_tokens', usage.get('reasoning_tokens', ''))}
        effective = receipt['modelo_principal_declarado']
        if not effective and len(receipt['uso_por_modelo']) == 1: effective = next(iter(receipt['uso_por_modelo']))
        if obj.get('is_error'):
            errors = obj.get('errors') or []
            messages.extend(errors if isinstance(errors, list) else [errors])
            if obj.get('result'): messages.append(str(obj['result']))
    fields['tokens_totales'] = total
    # stdout error fields are preferred; stderr is retained only on a failed call by the caller.
    text = '\n'.join(str(m) for m in messages)
    return fields, receipt, effective, text


def category(text):
    low = text.lower()
    if any(k in low for k in ('usage limit', 'rate limit', 'rate_limit', 'too many requests', 'hit your limit', 'out of extra usage', 'limit reached', 'quota exceeded', 'out of usage', 'usage_limit', 'rate_limit_error', 'rate-limit', 'http 429')): return 'cuota'
    if any(k in low for k in ('unauthorized', 'authentication', 'not logged in', 'login required', 'invalid_grant', 'oauth token')): return 'autenticacion'
    if any(k in low for k in ('model not found', 'model does not exist', 'unknown model', 'invalid model', 'no access to model')): return 'modelo_no_disponible'
    if any(k in low for k in ('effort', 'reasoning_effort', 'reasoning effort')) and any(k in low for k in ('unsupported', 'not support', "doesn't support", 'invalid', 'not allowed', 'must be', 'cannot', 'ignored', 'ignoring', 'not available')): return 'nivel_no_admitido'
    if any(k in low for k in ('not found', 'does not exist', 'not available')): return 'modelo_no_disponible'
    return 'infraestructura'


def claude_command(work, model, level, probe=False):
    binary = Path(shutil.which('claude') or '').resolve()
    credentials = Path.home() / '.claude' / '.credentials.json'
    if not binary.is_file() or not credentials.is_file(): raise RuntimeError('Falta runtime oficial o autenticación oficial de Claude Code.')
    args = ['bwrap', '--die-with-parent', '--new-session', '--unshare-all', '--share-net', '--clearenv',
            '--ro-bind', '/usr', '/usr', '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib64', '/lib64',
            '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/sbin', '/sbin', '--proc', '/proc', '--dev', '/dev',
            '--tmpfs', '/tmp', '--dir', '/etc', '--ro-bind', '/etc/resolv.conf', '/etc/resolv.conf',
            '--ro-bind', '/etc/ssl', '/etc/ssl', '--dir', '/opt', '--ro-bind', str(binary), '/opt/claude',
            '--dir', '/user', '--dir', '/user/.claude', '--ro-bind', str(credentials), '/user/.claude/.credentials.json',
            '--bind', str(work), '/work', '--chdir', '/work', '--setenv', 'HOME', '/user',
            '--setenv', 'PATH', '/usr/bin:/bin', '--setenv', 'LANG', 'C.UTF-8',
            '--setenv', 'PYTHONDONTWRITEBYTECODE', '1', '--setenv', 'PYTHONHASHSEED', '0',
            '/opt/claude', '-p', TRIVIAL if probe else medir.PROMPT, '--model', model,
            '--output-format', 'json', '--restricted', '--setting-sources', '',
            '--settings', '{"disableAllHooks":true,"autoMemoryEnabled":false}',
            '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--disable-slash-commands',
            '--no-session-persistence', '--no-chrome', '--permission-mode', 'dontAsk',
            '--tools', '' if probe else 'Read,Edit,Write,Bash']
    if not probe: args += ['--allowedTools', 'Read', 'Edit', 'Write', 'Bash(python3:*)']
    if level != 'sin-nivel': args += ['--effort', level]
    return args


def command(work, model, level, probe=False):
    if provider(model) == 'anthropic': return claude_command(work, model, level, probe)
    args = medir.command(work, level)
    args[args.index(medir.MODEL)] = model
    if level == 'sin-nivel':
        i = args.index('model_reasoning_effort=sin-nivel')
        del args[i-1:i+1]
    if probe: args[-1] = TRIVIAL
    return args


def verify():
    medir.check_frozen()
    if sys.version.split()[0] != medir.PYTHON_VERSION: raise RuntimeError('Versión Python diferente de la fijada.')
    for cli, version in VERSIONS.items():
        found = subprocess.check_output([cli, '--version'], stdin=subprocess.DEVNULL, text=True).strip()
        if found != version: raise RuntimeError('Versión CLI diferente de la fijada: ' + cli)
    if not shutil.which('bwrap'): raise RuntimeError('Falta bubblewrap.')
    evidence = {'hashes': medir.bank_hashes(), 'manifiesto_sha256': sha(ROOT / 'banco-congelado.json'),
                'prerregistro_sha256': sha(ROOT / 'EXTENSION-02.md'), 'suplemento_sha256': sha(Path(__file__)),
                'csv_previos': {p.name: sha(p) for p in RESULTADOS.glob('*.csv') if p.name in ('crudo.csv', 'crudo-extension.csv', 'piloto.csv', 'piloto-extension.csv')},
                'versiones': VERSIONS, 'python': medir.PYTHON_VERSION, 'semilla': SEED, 'timeout_segundos': 600, 'max_paralelo': 2}
    path = ART / 'verificacion-congelado.json'
    previous = read(path)
    if previous and previous != evidence:
        same = {k: v for k, v in previous.items() if k != 'suplemento_sha256'} == {k: v for k, v in evidence.items() if k != 'suplemento_sha256'}
        changes = read(ART / 'cambios-suplemento.json', [])
        authorized = any(c.get('anterior_sha256') == previous['suplemento_sha256'] and c.get('nuevo_sha256') == evidence['suplemento_sha256'] and re.fullmatch(r'[0-9a-f]{40}', c.get('commit_correccion', '')) for c in changes)
        if not same or not authorized: raise RuntimeError('Cambió evidencia congelada de extensión 02; requiere auditoría.')
    if not previous: write(path, evidence)
    isolation = {'claude': {'argv_publico': public_command(claude_command(Path('/work'), 'claude-haiku-5-5', 'low')),
                 'montajes': ['runtime oficial de Claude en /opt/claude (sólo lectura)', 'credenciales oficiales en /user/.claude/.credentials.json (sólo lectura, sin copia)', '/usr y certificados (sólo lectura)', 'copia nueva de tarea en /work (escritura)', 'HOME vacío excepto autenticación'],
                 'limites': ['La red del proveedor está disponible al proceso.', 'Las credenciales oficiales son legibles por el proceso.', 'Permanecen instrucciones incorporadas del proveedor; no se inspecciona su contexto interno.']},
                 'codex': {'instrucciones_globales_usuario': True, 'limite': 'Los flags de aislamiento no demuestran ausencia de instrucciones globales en el contexto efectivo.'}}
    write(ART / 'aislamiento.json', isolation)
    return evidence


def public_command(args):
    # Only executable argv after the final runtime boundary, no host mounts/auth paths.
    return args[len(args) - 1 - list(reversed(args)).index('/opt/claude'):]


def state(model):
    return read(ART / model / 'estado.json', {'modelo': model, 'proveedor': provider(model), 'estado': 'nuevo', 'niveles': []})


def save_state(model, data):
    write(ART / model / 'estado.json', data)


def assert_order(model):
    blocked = read(ART / ('cuota-' + provider(model) + '.json'))
    if blocked: raise RuntimeError('Proveedor cerrado por cuota; no se vuelve a invocar.')
    for earlier in MODELS[:MODELS.index(model)]:
        if state(earlier)['estado'] not in ('completo', 'incompleto', 'no_disponible', 'omitido_cuota'):
            raise RuntimeError('Debe cerrar primero el bloque anterior: ' + earlier)


def record_quota(model, message):
    write(ART / ('cuota-' + provider(model) + '.json'), {'proveedor': provider(model), 'mensaje': clean(message), 'espera': 'No se espera ni reintenta; cierre inmediato dentro del máximo autorizado.', 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()})
    for following in MODELS[MODELS.index(model)+1:]:
        if provider(following) == provider(model):
            save_state(following, {'modelo': following, 'proveedor': provider(model), 'estado': 'omitido_cuota', 'niveles': [], 'motivo': 'Proveedor agotado en bloque anterior.'})
            export(following)


def invoke(work, model, level, probe=False, started=None):
    global ACTIVE, SEQ
    def launch():
        global ACTIVE, SEQ
        with LOCK:
            ACTIVE += 1; SEQ += 1
            if started:
                started.update(inicio_monotonic_ns=time.monotonic_ns(), orden_real_inicio=SEQ, concurrencia_al_inicio=ACTIVE)
                write(ART / model / 'iniciadas' / (started['id'] + '.json'), started)
    def finish():
        global ACTIVE
        with LOCK: ACTIVE -= 1
    rc, timeout, seconds, out, err = medir.run_process(command(work, model, level, probe), 600, env={'PATH': '/usr/bin:/bin'}, on_start=launch, on_finish=finish)
    fields, receipt, effective, message = parse('codex' if provider(model) == 'openai' else 'claude', out, err)
    stderr = err.decode(errors='replace')
    if not message and stderr and category(stderr) in ('nivel_no_admitido', 'cuota', 'autenticacion', 'modelo_no_disponible'): message = stderr
    if rc != 0 and not message: message = stderr or 'CLI terminó sin resultado.'
    error = category(message) if message or receipt.get('es_error') else ''
    if timeout: error = 'timeout_agente'
    if rc != 0 and not error: error = 'infraestructura'
    if not error and fields['tokens_totales'] == '': error = 'uso_no_disponible'
    if not error and receipt.get('permisos_denegados', {}).get('cantidad', 0): error = 'permisos_incompatibles'
    if not error and provider(model) == 'anthropic':
        expected = 'claude-fable-5-2' if model == 'fable' else model
        if not effective: error = 'identificador_no_verificable'
        elif not re.fullmatch(re.escape(expected) + r'(?:-[0-9]{8})?', effective): error = 'modelo_distinto_del_solicitado'
    return {'retorno_cli': rc, 'timeout': int(timeout), 'segundos': round(seconds, 3), 'error': error, 'error_textual': clean(message), 'modelo_efectivo': effective, 'advertencias': json.dumps(receipt.get('advertencias', []), ensure_ascii=False), **fields}, receipt


def probe(model):
    assert_order(model)
    data = state(model)
    if data['estado'] != 'nuevo': raise RuntimeError('El sondeo ya empezó o terminó; no se repite automáticamente.')
    save_state(model, {**data, 'estado': 'sondeando'})
    accepted = []
    for level in (*LEVELS, 'sin-nivel'):
        if level == 'sin-nivel' and accepted: break
        with tempfile.TemporaryDirectory(prefix='ext02-sondeo-') as temp:
            start = {'id': 'sondeo-' + level, 'nivel': level, 'inicio_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
            result, receipt = invoke(Path(temp), model, level, True, start)
        write(ART / model / 'sondeos' / (level + '.json'), result)
        write(ART / model / 'recibos' / ('sondeo-' + level + '.json'), receipt)
        print(json.dumps({'modelo': model, 'sondeo': level, 'error': result['error']}), flush=True)
        if not result['error']: accepted.append(level)
        elif result['error'] == 'nivel_no_admitido': continue
        else:
            if result['error'] == 'cuota': record_quota(model, result['error_textual'])
            save_state(model, {**data, 'estado': 'no_disponible', 'niveles': accepted, 'motivo': result['error'], 'pendientes': 24 * len(accepted)})
            export(model)
            return
    save_state(model, {**data, 'estado': 'sondeado' if accepted else 'no_disponible', 'niveles': accepted, 'motivo': '' if accepted else 'Ninguna llamada completó con esfuerzo o sin nivel.'})
    export(model)


def schedule(model, phase):
    levels = state(model)['niveles']
    if phase == 'piloto':
        return [dict(id='piloto-01-lotes-' + levels[0] + '-1', fase='piloto', orden=1, tarea='01-lotes', tipo='acotada', repeticion=1, nivel=levels[0])]
    rows = [dict(id=f'principal-{task["id"]}-{level}-{rep}', fase='principal', tarea=task['id'], tipo=task['tipo'], repeticion=rep, nivel=level) for task, level, rep in itertools.product(medir.tasks(), levels, range(1, 4))]
    random.Random(SEED).shuffle(rows)
    for i, row in enumerate(rows, 1): row['orden'] = i
    return rows


def export(model, phase='principal'):
    rows = []
    levels = state(model)['niveles']
    if levels:
        for item in schedule(model, phase):
            result = read(ART / model / 'corridas' / (item['id'] + '.json'))
            if result: rows.append(result)
    path = RESULTADOS / (('crudo-' if phase == 'principal' else 'piloto-') + model + '.csv')
    path.parent.mkdir(exist_ok=True)
    temporary = path.with_suffix('.tmp')
    with temporary.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    temporary.replace(path)
    return rows


def run_one(model, item):
    record = {field: '' for field in FIELDS}
    record.update(item, modelo=model, proveedor=provider(model), inicio_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cuota=0)
    task = next(t for t in medir.tasks() if t['id'] == item['tarea'])
    base = ROOT / 'tareas' / task['id']
    write(ART / model / 'iniciadas' / (item['id'] + '.json'), record)
    with tempfile.TemporaryDirectory(prefix='ext02-corrida-') as temp:
        work = Path(temp) / 'work'; shutil.copytree(base / 'inicio', work); shutil.copy(base / 'TAREA.md', work / 'TAREA.md')
        before = medir.files_at(work)
        result, receipt = invoke(work, model, item['nivel'], started=record)
        record.update(result)
        after = medir.files_at(work)
        added, deleted, extra, binaries = medir.measure_diff(before, after, task['permitidos'])
        quota = result['error'] == 'cuota'
        infra = result['error'] not in ('', 'timeout_agente')
        if not quota:
            ok, passed, total, eval_timeout = medir.evaluate(work, base / 'ocultos')
            record.update(tests_aprobados=passed, tests_total=total, resuelta=int(not infra and result['retorno_cli'] == 0 and not result['timeout'] and ok))
            if not result['error'] and eval_timeout: record['error'] = 'timeout_tests'
            elif not result['error'] and not ok: record['error'] = 'tests_fallan'
        record.update(estado='cuota' if quota else ('infraestructura' if infra else ('timeout' if result['timeout'] else 'completa')),
                      cuota=int(quota), lineas_agregadas=added, lineas_borradas=deleted, lineas_tocadas=added + deleted,
                      fuera_alcance=int(bool(extra)), archivos_extra=json.dumps(extra, ensure_ascii=False), binarios=json.dumps(binaries, ensure_ascii=False))
        if infra: record['resuelta'] = ''
        dest = ART / model / 'codigo' / item['id']; dest.mkdir(parents=True, exist_ok=True)
        for name in task['permitidos']:
            candidate = work / name
            if candidate.is_file() and not candidate.is_symlink(): shutil.copy(candidate, dest / name)
        write(ART / model / 'recibos' / (item['id'] + '.json'), receipt)
    write(ART / model / 'corridas' / (item['id'] + '.json'), record)
    print(json.dumps({k: record[k] for k in ('modelo', 'id', 'estado', 'resuelta', 'segundos', 'tokens_totales', 'error')}), flush=True)
    return record


def run_matrix(model, phase):
    global SEQ
    assert_order(model)
    data = state(model)
    allowed = ('sondeado', 'piloto') if phase == 'piloto' else ('piloto', 'principal')
    if data['estado'] not in allowed: raise RuntimeError('Estado inválido para esta fase.')
    rows = schedule(model, phase)
    order_path = ART / model / ('orden-' + phase + '.json')
    if order_path.exists() and read(order_path) != rows: raise RuntimeError('El orden persistido cambió.')
    write(order_path, rows)
    existing = [read(p).get('orden_real_inicio', 0) or 0 for p in (ART / model / 'iniciadas').glob('*.json')]
    SEQ = max(existing, default=0)
    pending = []
    for item in rows:
        start = ART / model / 'iniciadas' / (item['id'] + '.json')
        done = ART / model / 'corridas' / (item['id'] + '.json')
        if start.exists() and not done.exists(): raise RuntimeError('Iniciada sin cierre: auditoría manual, no reintento.')
        if not done.exists(): pending.append(item)
    if phase == 'principal':
        pilots = export(model, 'piloto')
        if len(pilots) != 1 or pilots[0]['estado'] != 'completa' or pilots[0]['tokens_totales'] == '': raise RuntimeError('Piloto inválido por infraestructura/uso.')
    save_state(model, {**data, 'estado': phase})
    for offset in range(0, len(pending), 1 if phase == 'piloto' else 2):
        batch = pending[offset:offset + (1 if phase == 'piloto' else 2)]
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = []
            for item in batch:
                futures.append(pool.submit(run_one, model, item)); time.sleep(.05)
            results = [future.result() for future in futures]
        export(model, phase)
        bad = next((r for r in results if r['cuota']), None) or next((r for r in results if r['estado'] == 'infraestructura'), None)
        if bad:
            if bad['cuota']: record_quota(model, bad['error_textual'])
            save_state(model, {**data, 'estado': 'incompleto', 'motivo': bad['error'], 'pendientes': len(rows) - len(export(model, phase))})
            return
    completed = export(model, phase)
    save_state(model, {**data, 'estado': 'piloto' if phase == 'piloto' else 'completo', 'observadas': len(completed), 'pendientes': 0})


def median(rows, key):
    vals = [float(r[key]) for r in rows if r.get(key, '') != '']
    return statistics.median(vals) if vals else None


def fmt(value):
    return '—' if value is None else f'{value:.2f}'


def summarize():
    out = ['## Extensión 02: matriz por modelo', '', 'Los pilotos y sondeos están excluidos. Las interrupciones por cuota y los errores de infraestructura no son fallos funcionales y se separan del denominador. Tokens de CLI distintos no representan la misma contabilidad; las comparaciones válidas de tokens son dentro de un modelo.', '',
           '| Modelo | Nivel | Observadas / previstas | Resueltas / evaluables | Segundos mediana | Tokens mediana (n) | Fuera de alcance |', '|---|---|---:|---:|---:|---:|---:|']
    collected = {}
    for model in MODELS:
        rows = export(model); collected[model] = rows
        data = state(model)
        for level in data['niveles'] or ['—']:
            observed = [r for r in rows if r['nivel'] == level]
            group = [r for r in observed if r['resuelta'] != '']
            out.append(f'| {model} | {level} | {len(observed)} / {24 if level != "—" else "—"} | {sum(int(r["resuelta"]) for r in group)}/{len(group)} | {fmt(median(group,"segundos"))} | {fmt(median(group,"tokens_totales"))} ({sum(r["tokens_totales"] != "" for r in group)}) | {sum(int(r["fuera_alcance"]) for r in group)}/{len(group)} |')
        out.extend(['', f'`{model}`: estado **{data["estado"]}**; motivo `{data.get("motivo", "")}`; pendientes {data.get("pendientes", "no determinadas sin niveles aceptados")}; cuota {sum(r["cuota"] for r in rows)}, infraestructura {sum(r["estado"] == "infraestructura" for r in rows)}, timeouts {sum(r["timeout"] for r in rows)}.', ''])
    out.extend(['### Razón nivel más alto / nivel más bajo', '', '| Modelo | Niveles | Tiempo | Tokens | Cobertura |', '|---|---|---:|---:|---|'])
    for model, rows in collected.items():
        levels = state(model)['niveles']
        if len(levels) < 2:
            out.append(f'| {model} | — | — | — | Sin comparación de niveles |'); continue
        low, high = levels[0], levels[-1]
        a = [r for r in rows if r['nivel'] == low and r['resuelta'] != '']; b = [r for r in rows if r['nivel'] == high and r['resuelta'] != '']
        ratios = []
        for key in ('segundos', 'tokens_totales'):
            av, bv = median(a, key), median(b, key)
            ratios.append(fmt(bv / av) if av and bv is not None else '—')
        out.append(f'| {model} | {high}/{low} | {ratios[0]} | {ratios[1]} | {len(a)}/24 y {len(b)}/24; descriptiva |')
    out.extend(['', '### Por tarea y nivel', '', '| Modelo | Tarea | Nivel | Resueltas / evaluables | Segundos mediana | Tokens mediana |', '|---|---|---|---:|---:|---:|'])
    for model, rows in collected.items():
        for task, level in itertools.product(medir.tasks(), state(model)['niveles']):
            group = [r for r in rows if r['tarea'] == task['id'] and r['nivel'] == level and r['resuelta'] != '']
            out.append(f'| {model} | {task["id"]} | {level} | {sum(int(r["resuelta"]) for r in group)}/{len(group)} | {fmt(median(group,"segundos"))} | {fmt(median(group,"tokens_totales"))} |')
    out.extend(['', '### Sólo corridas resueltas', '', '| Modelo | Nivel | n | Segundos mediana | Tokens mediana |', '|---|---|---:|---:|---:|'])
    for model, rows in collected.items():
        for level in state(model)['niveles']:
            group = [r for r in rows if r['nivel'] == level and r['resuelta'] == 1]
            out.append(f'| {model} | {level} | {len(group)} | {fmt(median(group,"segundos"))} | {fmt(median(group,"tokens_totales"))} |')
    write(ART / 'cobertura.json', {model: state(model) for model in MODELS})
    (ART / 'tablas.md').write_text('\n'.join(out) + '\n')
    editorial = ART / 'lectura.md'
    reading = editorial.read_text() if editorial.exists() else '\n### Lectura\n\nPendiente de evaluar cobertura y resultados.\n\n### Lo que este experimento no demuestra\n\nUna matriz incompleta no permite una afirmación universal. El banco es artificial y los CLI, momentos y contabilización de tokens difieren.\n\n### Qué se puede decir en un reel\n\nPendiente de interpretar datos; no hay una afirmación general autorizada por la cobertura todavía.\n'
    path = RESULTADOS / 'resumen.md'; old = path.read_text().split('\n## Extensión 02: matriz por modelo\n')[0]
    path.write_text(old.rstrip() + '\n\n' + '\n'.join(out) + '\n' + reading)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('accion', choices=('verificar', 'sondear', 'piloto', 'principal', 'resumir'))
    parser.add_argument('modelo', nargs='?', choices=MODELS)
    args = parser.parse_args()
    ART.mkdir(parents=True, exist_ok=True)
    with (ART / '.ejecucion.lock').open('w') as handle:
        try: fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise SystemExit('Otro runner de extensión 02 está activo.')
        if args.accion == 'verificar':
            evidence = verify(); print(json.dumps({'hashes_coinciden': True, 'archivos': len(evidence['hashes']), 'versiones': VERSIONS})); return
        if args.accion == 'resumir': summarize(); return
        if not args.modelo: parser.error('La acción requiere modelo.')
        verify()
        if args.accion == 'sondear': probe(args.modelo)
        else: run_matrix(args.modelo, args.accion)


if __name__ == '__main__':
    main()
