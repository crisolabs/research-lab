#!/usr/bin/env python3
"""Continuación pre-registrada en ENMIENDA-02-03.md: Fable por API key."""
import argparse
import csv
import datetime
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import extension0202 as e02
import medir

ROOT = Path(__file__).resolve().parent
RESULTADOS = ROOT / 'resultados'
ART02 = e02.ART
ART03 = RESULTADOS / 'extension-02' / 'protocolo-02-03'
MODEL = 'fable'
TARGET_MODEL = 'claude-fable-5-2'
P0202_FABLE = ART02 / MODEL
VERSIONS = {'claude': e02.VERSIONS['claude']}
FIELDS = list(e02.FIELDS) + ['canal_auth']
LOCK = threading.Lock()
ACTIVE = 0
SEQ = 0


def category(text):
    """Classify provider errors including API billing/credit exhaustion."""
    low = text.lower()
    if any(k in low for k in ('credit balance', 'insufficient_quota', 'insufficient quota', 'billing', 'out of credits')):
        return 'cuota'
    if any(k in low for k in ('invalid x-api-key', 'api key', 'invalid_api_key')):
        return 'autenticacion'
    return e02.category(text)


def claude_api_env():
    """Minimal environment passed to bwrap without exposing host variables or CLI argv."""
    key = os.environ.get('ANTHROPIC_API_KEY', '').strip()
    if not key:
        raise RuntimeError('Falta ANTHROPIC_API_KEY en el entorno (cargar vía vault-env).')
    return {
        'PATH': '/usr/bin:/bin',
        'LANG': 'C.UTF-8',
        'HOME': '/user',
        'PYTHONDONTWRITEBYTECODE': '1',
        'PYTHONHASHSEED': '0',
        'ANTHROPIC_API_KEY': key,
    }


def claude_api_command(work, level, probe=False):
    """Build isolated bwrap command without mounting ~/.claude/.credentials.json."""
    binary = Path(shutil.which('claude') or '').resolve()
    if not binary.is_file():
        raise RuntimeError('Falta el binario oficial de Claude Code.')
    args = [
        'bwrap', '--die-with-parent', '--new-session', '--unshare-all', '--share-net',
        '--ro-bind', '/usr', '/usr', '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib64', '/lib64',
        '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/sbin', '/sbin', '--proc', '/proc', '--dev', '/dev',
        '--tmpfs', '/tmp', '--dir', '/etc', '--ro-bind', '/etc/resolv.conf', '/etc/resolv.conf',
        '--ro-bind', '/etc/ssl', '/etc/ssl', '--dir', '/opt', '--ro-bind', str(binary), '/opt/claude',
        '--dir', '/user', '--dir', '/user/.claude',
        '--bind', str(work), '/work', '--chdir', '/work',
        '/opt/claude', '-p', e02.TRIVIAL if probe else medir.PROMPT, '--model', TARGET_MODEL,
        '--output-format', 'json', '--restricted', '--setting-sources', '',
        '--settings', '{"disableAllHooks":true,"autoMemoryEnabled":false}',
        '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--disable-slash-commands',
        '--no-session-persistence', '--no-chrome', '--permission-mode', 'dontAsk',
        '--tools', '' if probe else 'Read,Edit,Write,Glob,Grep,Bash',
    ]
    if not probe:
        args += ['--allowedTools', 'Read', 'Edit', 'Write', 'Glob', 'Grep', 'Bash']
    if level != 'sin-nivel':
        args += ['--effort', level]
    return args


def p0202_hashes():
    """Snapshot sha256 of sealed protocolo-02-02 artifacts relevant to this continuation."""
    paths = [
        ROOT / 'ENMIENDA-02-02.md',
        ROOT / 'extension0202.py',
        ART02 / 'historicos-congelados.json',
        ART02 / 'validacion-cierre.json',
        P0202_FABLE / 'orden-principal.json',
        P0202_FABLE / 'estado.json',
        P0202_FABLE / 'cierre.json',
    ]
    paths += sorted((P0202_FABLE / 'corridas').glob('*.json'))
    return {str(p.relative_to(ROOT)): e02.sha(p) for p in paths}


def verify():
    """Verify frozen bank, historical baseline, Python/CLI versions, and untouched protocolo-02-02."""
    medir.check_frozen()
    if sys.version.split()[0] != medir.PYTHON_VERSION:
        raise RuntimeError('Versión Python diferente de la fijada.')
    found = subprocess.check_output(['claude', '--version'], stdin=subprocess.DEVNULL, text=True).strip()
    if found != VERSIONS['claude']:
        raise RuntimeError('Versión CLI diferente de la fijada: claude')
    if not shutil.which('bwrap'):
        raise RuntimeError('Falta bubblewrap.')
    baseline = e02.read(ART02 / 'historicos-congelados.json')
    if not baseline or any(not (ROOT / p).is_file() or e02.sha(ROOT / p) != h for p, h in baseline.items()):
        raise RuntimeError('Cambió un archivo histórico; no se ejecuta.')
    evidence = {
        'hashes': medir.bank_hashes(),
        'manifiesto_sha256': e02.sha(ROOT / 'banco-congelado.json'),
        'prerregistro_sha256': e02.sha(ROOT / 'ENMIENDA-02-03.md'),
        'suplemento_sha256': e02.sha(Path(__file__)),
        'protocolo_02_02_hashes': p0202_hashes(),
        'versiones': VERSIONS,
        'python': medir.PYTHON_VERSION,
        'timeout_segundos': 600,
        'max_paralelo': 2,
    }
    path = ART03 / 'verificacion-congelado.json'
    previous = e02.read(path)
    if previous and previous != evidence:
        raise RuntimeError('Cambió evidencia de la continuación 02-03; requiere auditoría.')
    if not previous:
        e02.write(path, evidence)
    isolation = {
        'claude': {
            'argv_publico': e02.public_command(claude_api_command(Path('/work'), 'high')),
            'montajes': [
                'Runtime y certificados en lectura',
                'Directorio /user/.claude vacío sin .credentials.json',
                'Copia temporal nueva en /work con escritura',
            ],
            'env': ['PATH', 'LANG', 'HOME', 'PYTHONDONTWRITEBYTECODE', 'PYTHONHASHSEED', 'ANTHROPIC_API_KEY (en memoria, nunca en argv ni archivos)'],
            'limites': ['Red del proveedor disponible', 'Instrucciones incorporadas del proveedor'],
        }
    }
    e02.write(ART03 / 'aislamiento.json', isolation)
    return evidence


def state():
    return e02.read(ART03 / MODEL / 'estado.json', {'modelo': MODEL, 'modelo_solicitado': TARGET_MODEL, 'proveedor': 'anthropic', 'canal_auth': 'api_key', 'estado': 'nuevo', 'niveles': []})


def save_state(data):
    e02.write(ART03 / MODEL / 'estado.json', data)


def schedule(phase):
    """Return remaining non-evaluated items in the exact order of protocolo-02-02/fable."""
    levels = state()['niveles']
    if phase == 'piloto':
        return [{'id': 'piloto-01-lotes-' + levels[0] + '-1', 'fase': 'piloto', 'orden': 1, 'tarea': '01-lotes', 'tipo': 'acotada', 'repeticion': 1, 'nivel': levels[0]}]
    order = e02.read(P0202_FABLE / 'orden-principal.json')
    if not order:
        raise RuntimeError('Falta orden-principal.json de protocolo-02-02/fable.')
    evaluated = set()
    for p in (P0202_FABLE / 'corridas').glob('*.json'):
        rec = e02.read(p)
        if rec and rec.get('fase') == 'principal' and rec.get('resuelta') in (0, 1) and rec.get('cuota') != 1:
            evaluated.add(rec['id'])
    return [row for row in order if row['id'] not in evaluated]


def invoke(work, level, probe=False, started=None):
    global ACTIVE, SEQ
    def launch():
        global ACTIVE, SEQ
        with LOCK:
            ACTIVE += 1
            SEQ += 1
            if started is not None:
                started.update(inicio_monotonic_ns=time.monotonic_ns(), orden_real_inicio=SEQ, concurrencia_al_inicio=ACTIVE)
                e02.write(ART03 / MODEL / 'iniciadas' / (started['id'] + '.json'), started)
    def finish():
        global ACTIVE
        with LOCK:
            ACTIVE -= 1
    rc, timeout, seconds, out, err = medir.run_process(
        claude_api_command(work, level, probe),
        600,
        env=claude_api_env(),
        on_start=launch,
        on_finish=finish,
    )
    fields, receipt, effective, message = e02.parse('claude', out, err)
    stderr = err.decode(errors='replace')
    if not message and stderr and category(stderr) in ('nivel_no_admitido', 'cuota', 'autenticacion', 'modelo_no_disponible'):
        message = stderr
    if rc != 0 and not message:
        message = stderr or 'CLI terminó sin resultado.'
    error = category(message) if message or receipt.get('es_error') else ''
    if timeout:
        error = 'timeout_agente'
    if rc != 0 and not error:
        error = 'infraestructura'
    if not error and fields['tokens_totales'] == '':
        error = 'uso_no_disponible'
    if not error:
        if not effective:
            error = 'identificador_no_verificable'
        receipt['modelo_solicitado'] = TARGET_MODEL
        receipt['modelo_distinto_del_solicitado'] = bool(effective and effective != TARGET_MODEL)
    return {
        'retorno_cli': rc,
        'timeout': int(timeout),
        'segundos': round(seconds, 3),
        'error': error,
        'error_textual': e02.clean(message),
        'modelo_efectivo': effective,
        'advertencias': json.dumps(receipt.get('advertencias', []), ensure_ascii=False),
        'denegaciones': receipt.get('permisos_denegados', {}).get('cantidad', 0),
        'canal_auth': 'api_key',
        **fields,
    }, receipt


def export(phase='principal'):
    rows = []
    if state()['niveles']:
        for item in schedule(phase):
            result = e02.read(ART03 / MODEL / 'corridas' / (item['id'] + '.json'))
            if result:
                rows.append(result)
    path = RESULTADOS / (('crudo-' if phase == 'principal' else 'piloto-') + MODEL + '-02-03.csv')
    path.parent.mkdir(exist_ok=True)
    temporary = path.with_suffix('.tmp')
    with temporary.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)
    return rows


def probe():
    data = state()
    if data['estado'] != 'nuevo':
        raise RuntimeError('El sondeo 02-03 ya empezó o terminó; no se repite automáticamente.')
    save_state({**data, 'estado': 'sondeando'})
    accepted = []
    for level in e02.LEVELS:
        with tempfile.TemporaryDirectory(prefix='ext0203-sondeo-') as temp:
            start = {'id': 'sondeo-' + level, 'nivel': level, 'inicio_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
            result, receipt = invoke(Path(temp), level, True, start)
        e02.write(ART03 / MODEL / 'sondeos' / (level + '.json'), result)
        e02.write(ART03 / MODEL / 'recibos' / ('sondeo-' + level + '.json'), receipt)
        print(json.dumps({'modelo': TARGET_MODEL, 'sondeo': level, 'error': result['error'], 'efectivo': result['modelo_efectivo']}), flush=True)
        if not result['error']:
            accepted.append(level)
        elif result['error'] == 'nivel_no_admitido':
            continue
        else:
            save_state({**data, 'estado': 'no_disponible', 'niveles': accepted, 'motivo': result['error'], 'pendientes': 93})
            export()
            return
    save_state({**data, 'estado': 'sondeado' if accepted else 'no_disponible', 'niveles': accepted, 'motivo': '' if accepted else 'Ninguna llamada completó.'})
    export()


def run_one(item):
    record = {field: '' for field in FIELDS}
    record.update(item, modelo=MODEL, proveedor='anthropic', canal_auth='api_key', inicio_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cuota=0)
    task = next(t for t in medir.tasks() if t['id'] == item['tarea'])
    base = ROOT / 'tareas' / task['id']
    e02.write(ART03 / MODEL / 'iniciadas' / (item['id'] + '.json'), record)
    with tempfile.TemporaryDirectory(prefix='ext0203-corrida-') as temp:
        work = Path(temp) / 'work'
        shutil.copytree(base / 'inicio', work)
        shutil.copy(base / 'TAREA.md', work / 'TAREA.md')
        before = medir.files_at(work)
        result, receipt = invoke(work, item['nivel'], started=record)
        record.update(result)
        after = medir.files_at(work)
        added, deleted, extra, binaries = medir.measure_diff(before, after, task['permitidos'])
        quota = result['error'] == 'cuota'
        infra = result['error'] not in ('', 'timeout_agente')
        if not quota:
            ok, passed, total, eval_timeout = medir.evaluate(work, base / 'ocultos')
            record.update(
                tests_aprobados=passed,
                tests_total=total,
                resuelta=int(not infra and result['retorno_cli'] == 0 and not result['timeout'] and ok),
            )
            if not result['error'] and eval_timeout:
                record['error'] = 'timeout_tests'
            elif not result['error'] and not ok:
                record['error'] = 'tests_fallan'
        record.update(
            estado='cuota' if quota else ('infraestructura' if infra else ('timeout' if result['timeout'] else 'completa')),
            cuota=int(quota),
            lineas_agregadas=added,
            lineas_borradas=deleted,
            lineas_tocadas=added + deleted,
            fuera_alcance=int(bool(extra)),
            archivos_extra=json.dumps(extra, ensure_ascii=False),
            binarios=json.dumps(binaries, ensure_ascii=False),
        )
        if infra:
            record['resuelta'] = ''
        dest = ART03 / MODEL / 'codigo' / item['id']
        dest.mkdir(parents=True, exist_ok=True)
        for name in task['permitidos']:
            candidate = work / name
            if candidate.is_file() and not candidate.is_symlink():
                shutil.copy(candidate, dest / name)
        e02.write(ART03 / MODEL / 'recibos' / (item['id'] + '.json'), receipt)
    e02.write(ART03 / MODEL / 'corridas' / (item['id'] + '.json'), record)
    print(json.dumps({k: record[k] for k in ('modelo', 'id', 'estado', 'resuelta', 'segundos', 'tokens_totales', 'error')}), flush=True)
    return record


def run_matrix(phase):
    global SEQ
    data = state()
    allowed = ('sondeado', 'piloto') if phase == 'piloto' else ('piloto', 'principal')
    if data['estado'] not in allowed:
        raise RuntimeError('Estado inválido para esta fase.')
    rows = schedule(phase)
    order_path = ART03 / MODEL / ('orden-' + phase + '.json')
    if order_path.exists() and e02.read(order_path) != rows:
        raise RuntimeError('El orden persistido cambió.')
    e02.write(order_path, rows)
    existing = [e02.read(p).get('orden_real_inicio', 0) or 0 for p in (ART03 / MODEL / 'iniciadas').glob('*.json')]
    SEQ = max(existing, default=0)
    pending = []
    for item in rows:
        start = ART03 / MODEL / 'iniciadas' / (item['id'] + '.json')
        done = ART03 / MODEL / 'corridas' / (item['id'] + '.json')
        if start.exists() and not done.exists():
            raise RuntimeError('Iniciada sin cierre: auditoría manual, no reintento.')
        if not done.exists():
            pending.append(item)
    if phase == 'principal':
        pilots = export('piloto')
        if len(pilots) != 1 or pilots[0]['estado'] != 'completa' or pilots[0]['tokens_totales'] == '':
            raise RuntimeError('Piloto inválido por infraestructura/uso.')
    save_state({**data, 'estado': phase})
    step = 1 if phase == 'piloto' else 2
    for offset in range(0, len(pending), step):
        batch = pending[offset:offset + step]
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = []
            for item in batch:
                futures.append(pool.submit(run_one, item))
                time.sleep(0.05)
            results = [future.result() for future in futures]
        export(phase)
        bad = next((r for r in results if r['cuota']), None) or next((r for r in results if r['estado'] == 'infraestructura'), None)
        if bad:
            completed = export(phase)
            save_state({**data, 'estado': 'incompleto', 'motivo': bad['error'], 'observadas': len(completed), 'pendientes': len(rows) - len(completed)})
            return
    completed = export(phase)
    save_state({**data, 'estado': 'piloto' if phase == 'piloto' else 'completo', 'observadas': len(completed), 'pendientes': 0})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('accion', choices=('verificar', 'sondear', 'piloto', 'principal'))
    args = parser.parse_args()
    ART03.mkdir(parents=True, exist_ok=True)
    with (ART03 / '.ejecucion.lock').open('w') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('Otro runner de extensión 02-03 está activo.')
        if args.accion == 'verificar':
            evidence = verify()
            print(json.dumps({'hashes_coinciden': True, 'archivos': len(evidence['hashes']), 'p0202_intacto': len(evidence['protocolo_02_02_hashes']), 'versiones': VERSIONS}))
            return
        verify()
        if args.accion == 'sondear':
            probe()
        else:
            run_matrix(args.accion)


if __name__ == '__main__':
    main()
