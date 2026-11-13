#!/usr/bin/env python3
"""Banco y medición: biblioteca estándar; no guarda transcripts del agente."""
import argparse
import csv
import difflib
import datetime
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import shutil
import signal
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parent
RESULTADOS = ROOT / 'resultados'
SEED = 20261113
MODEL = 'gpt-6.1-sol'
CLI_VERSION = 'codex-cli 0.166.0'
PYTHON_VERSION = '3.12.3'
LEVELS = ('low', 'medium', 'high')
PROMPT = ('Leé TAREA.md y resolvé la tarea implementando los requisitos completos. '
          'Editá sólo el módulo permitido. Usá herramientas locales si las necesitás. '
          'No accedas a Internet ni delegues. No agregues tests ni documentación. '
          'No leas archivos de configuración o autenticación del CLI. '
          'Al terminar, describí brevemente qué cambiaste.')
FIELDS = ['id','fase','orden','tarea','tipo','repeticion','nivel','inicio_utc','estado',
          'inicio_monotonic_ns','orden_real_inicio','concurrencia_al_inicio','retorno_cli','timeout','tests_aprobados','tests_total','resuelta','tokens_entrada',
          'tokens_cache','tokens_salida','tokens_razonamiento','tokens_totales','segundos',
          'lineas_agregadas','lineas_borradas','lineas_tocadas','fuera_alcance','archivos_extra',
          'binarios','error']
LOCK = threading.Lock()
ACTIVE = 0
START_SEQ = 0


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)


def tasks():
    return json.loads((ROOT / 'banco.json').read_text())


def bank_hashes():
    paths = [ROOT / 'banco.json', ROOT / 'medir.py']
    paths += sorted(p for p in (ROOT / 'tareas').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def run_process(command, timeout, cwd=None, env=None, on_start=None, on_finish=None):
    start = time.perf_counter()
    process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    timed_out = False
    if on_start: on_start()
    try:
        out, err = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGKILL)
        out, err = process.communicate()
    finally:
        try: os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError: pass
        if on_finish: on_finish()
    return process.returncode, timed_out, time.perf_counter() - start, out, err


def evaluate(directory, hidden):
    # Never follow candidate links or expose the evaluator to the host filesystem.
    for path in directory.rglob('*'):
        if path.is_symlink() or (not path.is_file() and not path.is_dir()):
            return False, 0, 0, False
    with tempfile.TemporaryDirectory(prefix='eval-03-') as temp:
        target = Path(temp) / 'work'
        shutil.copytree(directory,target,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc'))
        shutil.copy(hidden / 'test_oculto.py', target / 'test_oculto.py')
        runner = ("import json,sys,unittest\n"
                  "class Result(unittest.TextTestResult):\n"
                  "    successes=0\n"
                  "    def addSuccess(self,test):\n"
                  "        super().addSuccess(test); self.successes+=1\n"
                  "sys.path.insert(0,'/work')\n"
                  "s=unittest.defaultTestLoader.discover('/work',pattern='test_oculto.py')\n"
                  "r=unittest.TextTestRunner(verbosity=0,resultclass=Result).run(s)\n"
                  "print(json.dumps({'total':r.testsRun,'passed':r.successes,'ok':r.wasSuccessful()}))\n"
                  "raise SystemExit(not r.wasSuccessful())\n")
        command = ['bwrap','--die-with-parent','--new-session','--unshare-all','--clearenv',
                   '--ro-bind','/usr','/usr','--symlink','usr/lib','/lib',
                   '--symlink','usr/lib64','/lib64','--symlink','usr/bin','/bin',
                   '--proc','/proc','--dev','/dev','--tmpfs','/tmp',
                   '--ro-bind',str(target),'/work','--chdir','/work',
                   '--setenv','PATH','/usr/bin:/bin','--setenv','PYTHONHASHSEED','0',
                   '/usr/bin/python3','-I','-B','-c',runner]
        rc, timeout, _, out, _ = run_process(command,30,env={'PATH':'/usr/bin:/bin'})
        parsed = None
        for line in out.decode(errors='replace').splitlines():
            try:
                obj = json.loads(line)
                if isinstance(obj,dict) and 'total' in obj: parsed=obj
            except ValueError:
                pass
        total = parsed['total'] if parsed else 0
        passed = parsed['passed'] if parsed else 0
        return bool(rc == 0 and not timeout and parsed and parsed['ok'] and total > 0),passed,total,timeout


def validate():
    rows = []
    for task in tasks():
        base = ROOT / 'tareas' / task['id']
        initial = evaluate(base / 'inicio', base / 'ocultos')
        reference = evaluate(base / 'referencia', base / 'ocultos')
        row = {'tarea':task['id'],'inicio_pasa':initial[0], 'inicio_aprobados':initial[1],
               'inicio_total':initial[2],'referencia_pasa':reference[0],
               'referencia_aprobados':reference[1],'referencia_total':reference[2]}
        rows.append(row)
        print(json.dumps(row), flush=True)
    write_json(RESULTADOS / 'validacion_banco.json', rows)
    if any(r['inicio_pasa'] or not r['referencia_pasa'] for r in rows):
        raise SystemExit('Banco inválido: corregir antes de cualquier corrida del modelo.')
    write_json(ROOT / 'banco-congelado.json', bank_hashes())


def check_frozen():
    frozen = json.loads((ROOT / 'banco-congelado.json').read_text())
    if frozen != bank_hashes():
        raise SystemExit('El banco o arnés cambió desde el congelamiento; no se ejecuta el modelo.')


def cli_package():
    resolved = Path(shutil.which('codex') or '').resolve()
    # Official npm entrypoint, package contains its own platform dependency.
    package = resolved.parent.parent
    if not (package / 'package.json').exists() or not (package / 'bin/codex.js').exists():
        raise SystemExit('Se requiere el paquete npm oficial de Codex; no un wrapper.')
    return package


def command(work, effort):
    package = cli_package()
    auth = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'auth.json'
    if not auth.is_file():
        raise SystemExit('Falta autenticación oficial del CLI.')
    args = ['bwrap','--die-with-parent','--new-session','--unshare-all','--share-net',
            '--clearenv','--ro-bind','/usr','/usr','--symlink','usr/lib','/lib',
            '--symlink','usr/lib64','/lib64','--symlink','usr/bin','/bin',
            '--symlink','usr/sbin','/sbin','--proc','/proc','--dev','/dev',
            '--tmpfs','/tmp','--dir','/etc','--ro-bind','/etc/resolv.conf','/etc/resolv.conf',
            '--ro-bind','/etc/ssl','/etc/ssl','--dir','/opt','--ro-bind',str(package),'/opt/codex',
            '--dir','/codex-home','--ro-bind',str(auth),'/codex-home/auth.json',
            '--dir','/user','--bind',str(work),'/work',
            '--setenv','HOME','/user','--setenv','CODEX_HOME','/codex-home',
            '--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8',
            '--setenv','PYTHONDONTWRITEBYTECODE','1','--setenv','PYTHONHASHSEED','0',
            '--chdir','/work','/usr/bin/node','/opt/codex/bin/codex.js',
            'exec','--json','--ephemeral','--ignore-user-config','--ignore-rules',
            '--skip-git-repo-check','--color','never','-s','workspace-write',
            '-m',MODEL,'-c',f'model_reasoning_effort={effort}',
            '-c','project_doc_max_bytes=0','-c','skills.bundled.enabled=false',
            '-c','skills.include_instructions=false','-c','features.multi_agent=false',
            '-c','features.apps=false','-c','sandbox_workspace_write.network_access=false',
            '-c','shell_environment_policy.inherit="none"',PROMPT]
    return args


def preflight():
    if sys.version.split()[0] != PYTHON_VERSION:
        raise SystemExit('Versión Python distinta de la fijada.')
    version = subprocess.check_output(['codex','--version'], stdin=subprocess.DEVNULL, text=True).strip()
    if version != CLI_VERSION: raise SystemExit('Versión CLI distinta de la fijada.')
    if not shutil.which('bwrap'): raise SystemExit('Falta bubblewrap; no se reduce el aislamiento.')
    check_frozen()
    write_json(RESULTADOS / 'entorno.json', {
        'modelo':MODEL,'cli':version,'python':PYTHON_VERSION,'semilla':SEED,
        'timeout_segundos':600,'max_paralelo':2,'prompt':PROMPT,
        'aislamiento':'bubblewrap externo: sin archivos del host salvo runtime, bibliotecas, certificados y auth oficial en bind de solo lectura; sandbox workspace-write del CLI para herramientas, sin red',
        'limite_auth':'El CLI necesita leer auth oficial. El bind es sólo lectura y no se copia; no se afirma que un agente malicioso no pueda leerlo.',
        'eventos_guardados':'Sólo tipos de evento y uso; no texto de conversaciones ni configuración de cuentas',
        'orden_aleatorio':'random.Random(20261113).shuffle, separado para piloto y principal',
    })


def files_at(work):
    out = {}
    for p in sorted(work.rglob('*')):
        if '.git' in p.relative_to(work).parts: continue
        if p.is_symlink():
            out[str(p.relative_to(work))] = ('symlink:' + os.readlink(p)).encode()
        elif p.is_file(): out[str(p.relative_to(work))] = p.read_bytes()
    return out


def measure_diff(before, after, allowed):
    added = deleted = 0
    extra, binaries = [], []
    for name in sorted(before.keys() | after.keys()):
        a, b = before.get(name,b''), after.get(name,b'')
        if name in before and name in after and a == b: continue
        if name not in allowed: extra.append(name)
        try:
            if b'\0' in a or b'\0' in b: raise UnicodeError()
            aa, bb = a.decode('utf-8').splitlines(), b.decode('utf-8').splitlines()
            for op,i,j,k,l in difflib.SequenceMatcher(a=aa,b=bb,autojunk=False).get_opcodes():
                if op in ('replace','delete'): deleted += j-i
                if op in ('replace','insert'): added += l-k
        except UnicodeError: binaries.append(name)
    return added, deleted, extra, binaries


def parse_events(out):
    usage = {}
    event_types = []
    for line in out.decode(errors='replace').splitlines():
        try: obj = json.loads(line)
        except ValueError: continue
        event_types.append(obj.get('type','unknown'))
        if obj.get('type') == 'turn.completed': usage = obj.get('usage') or {}
    return usage,event_types


def schedule(phase):
    result = []
    for task, level, repetition in itertools.product(tasks()[:1] if phase == 'piloto' else tasks(),LEVELS,range(1,2 if phase == 'piloto' else 4)):
        result.append({'fase':phase,'tarea':task['id'],'tipo':task['tipo'],'nivel':level,'repeticion':repetition,
                       'id':f'{phase}-{task["id"]}-{level}-{repetition}'})
    random.Random(SEED).shuffle(result)
    for i, row in enumerate(result,1): row['orden']=i
    return result


def export_csv(phase):
    rows = []
    for item in schedule(phase):
        path = RESULTADOS / 'corridas' / (item['id'] + '.json')
        if path.exists(): rows.append(json.loads(path.read_text()))
    path = RESULTADOS / ('piloto.csv' if phase == 'piloto' else 'crudo.csv')
    temp = path.with_suffix('.tmp')
    with temp.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    temp.replace(path)
    return rows


def run_one(item):
    global ACTIVE, START_SEQ
    record = dict(item)
    task = next(t for t in tasks() if t['id'] == item['tarea'])
    base = ROOT / 'tareas' / task['id']
    started = RESULTADOS / 'iniciadas' / (item['id'] + '.json')
    record['inicio_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    write_json(started,record)
    def launched():
        global ACTIVE, START_SEQ
        with LOCK:
            ACTIVE += 1; START_SEQ += 1
            record.update(inicio_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                          inicio_monotonic_ns=time.monotonic_ns(),orden_real_inicio=START_SEQ,
                          concurrencia_al_inicio=ACTIVE)
            write_json(started,record)
    def finished():
        global ACTIVE
        with LOCK: ACTIVE -= 1
    with tempfile.TemporaryDirectory(prefix='agente-03-') as temp:
        work = Path(temp) / 'work'; shutil.copytree(base / 'inicio',work)
        shutil.copy(base / 'TAREA.md',work / 'TAREA.md')
        before = files_at(work)
        rc, timeout, seconds, out, err = run_process(command(work,item['nivel']),600,
                                                    env={'PATH':'/usr/bin:/bin'},on_start=launched,on_finish=finished)
        after = files_at(work)
        usage,types = parse_events(out)
        added,deleted,extra,binaries = measure_diff(before,after,task['permitidos'])
        ok,passed,total,eval_timeout = evaluate(work,base / 'ocultos')
        error = ''
        if timeout: error='timeout_agente'
        elif rc != 0: error='error_cli'
        elif eval_timeout: error='timeout_tests'
        elif not ok: error='tests_fallan'
        elif not usage: error='uso_no_disponible'
        record.update(estado='timeout' if timeout else ('cli_falla' if rc != 0 else 'completa'),
                      retorno_cli=rc,timeout=int(timeout),tests_aprobados=passed,tests_total=total,
                      resuelta=int(rc == 0 and not timeout and ok),
                      tokens_entrada=usage.get('input_tokens',''),tokens_cache=usage.get('cached_input_tokens',''),
                      tokens_salida=usage.get('output_tokens',''),
                      tokens_razonamiento=usage.get('reasoning_output_tokens',usage.get('reasoning_tokens','')),
                      tokens_totales=(usage['input_tokens']+usage['output_tokens']) if 'input_tokens' in usage and 'output_tokens' in usage else '',
                      segundos=round(seconds,3),lineas_agregadas=added,lineas_borradas=deleted,
                      lineas_tocadas=added+deleted,fuera_alcance=int(bool(extra)),
                      archivos_extra=json.dumps(extra,ensure_ascii=False),binarios=json.dumps(binaries,ensure_ascii=False),error=error)
        # Persist only public generated source, not auth, transcripts or external files.
        dest = RESULTADOS / 'codigo' / item['id']; dest.mkdir(parents=True,exist_ok=True)
        for name in task['permitidos']:
            candidate = work / name
            if candidate.is_file() and not candidate.is_symlink():
                shutil.copy(candidate,dest / name)
        write_json(RESULTADOS / 'recibos' / (item['id']+'.json'),{'tipos_eventos':types,'uso':usage,'stderr_bytes':len(err)})
        # Infrastructure errors are diagnosed ephemerally, without persisting arbitrary CLI output.
        if rc != 0:
            text=(err+out).decode(errors='replace').lower()
            category=next((key for key in ['usage limit','rate limit','unauthorized','authentication','model not found','network','sandbox'] if key in text),'no_clasificado')
            record['error']='error_cli:'+category
    with LOCK:
        write_json(RESULTADOS / 'corridas' / (item['id']+'.json'),record)
        export_csv(item['fase'])
        print(json.dumps({k:record[k] for k in ['id','orden','estado','resuelta','segundos','tokens_totales','error']}),flush=True)
    return record


def run_matrix(phase):
    preflight()
    global START_SEQ
    existing=[json.loads(p.read_text()).get('orden_real_inicio',0) for p in (RESULTADOS / 'iniciadas').glob('*.json')]
    START_SEQ=max(existing,default=0)
    queue = schedule(phase)
    write_json(RESULTADOS / f'orden-{phase}.json',queue)
    if phase == 'principal':
        pilot=export_csv('piloto')
        if len(pilot) != 3 or any(r['estado'] != 'completa' or r['tokens_totales'] == '' for r in pilot):
            raise SystemExit('Piloto incompleto o infraestructura/uso inválido: no lanzar matriz.')
    pending=[]
    for row in queue:
        done=RESULTADOS / 'corridas' / (row['id']+'.json')
        start=RESULTADOS / 'iniciadas' / (row['id']+'.json')
        if start.exists() and not done.exists(): raise SystemExit('Corrida iniciada sin cierre: requiere auditoría, no se repite.')
        if not done.exists(): pending.append(row)
    # Batches of two preserve the preregistered launch order; no queue is launched after a systemic failure.
    for position in range(0,len(pending),2):
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[]
            for row in pending[position:position+2]:
                futures.append(pool.submit(run_one,row))
                time.sleep(.05)
            results=[f.result() for f in futures]
        if any(r['estado'] == 'cli_falla' for r in results):
            raise SystemExit('Se pausa por error CLI; no se consumen las corridas pendientes.')
    export_csv(phase)


def median(rows,key):
    vals=[float(r[key]) for r in rows if r[key] != '']
    if not vals: return '—'
    return f'{statistics.median(vals):.1f}'


def summarize():
    rows=export_csv('principal')
    out=['# Resultados · esfuerzo de razonamiento','',f'Cobertura: {len(rows)}/72 corridas principales. Piloto excluido.','',
         '| Tipo | Nivel | n | Resueltas | Tokens mediana (n) | Segundos mediana | Fuera de alcance | Líneas mediana |',
         '|---|---|---:|---:|---:|---:|---:|---:|']
    for kind,level in itertools.product(['acotada','diseño'],LEVELS):
        group=[r for r in rows if r['tipo']==kind and r['nivel']==level]
        n=len(group)
        solved=sum(int(r['resuelta']) for r in group)
        extra=sum(int(r['fuera_alcance']) for r in group)
        nt=sum(r['tokens_totales'] != '' for r in group)
        out.append(f'| {kind} | {level} | {n} | {solved}/{n} ({100*solved/n:.1f} %) | {median(group,"tokens_totales")} ({nt}) | {median(group,"segundos")} | {extra}/{n} ({100*extra/n:.1f} %) | {median(group,"lineas_tocadas")} |' if n else f'| {kind} | {level} | 0 | — | — | — | — | — |')
    out+=['','## Sólo corridas resueltas','','| Tipo | Nivel | n | Tokens mediana | Segundos mediana | Líneas mediana |','|---|---|---:|---:|---:|---:|']
    for kind,level in itertools.product(['acotada','diseño'],LEVELS):
        group=[r for r in rows if r['tipo']==kind and r['nivel']==level and int(r['resuelta'])]
        out.append(f'| {kind} | {level} | {len(group)} | {median(group,"tokens_totales")} | {median(group,"segundos")} | {median(group,"lineas_tocadas")} |')
    out+=['','## Por tarea','','| Tarea | Nivel | Resueltas | Tokens mediana | Segundos mediana |','|---|---|---:|---:|---:|']
    for task,level in itertools.product(tasks(),LEVELS):
        group=[r for r in rows if r['tarea']==task['id'] and r['nivel']==level]
        out.append(f'| {task["id"]} | {level} | {sum(int(r["resuelta"]) for r in group)}/{len(group)} | {median(group,"tokens_totales")} | {median(group,"segundos")} |')
    out+=['','## Lo que este experimento no demuestra','',
          'Un único modelo, versión de CLI, lenguaje y banco artificial, con tres repeticiones por tarea y nivel, no permite generalizar a producción. High no es el esfuerzo máximo. Los tests no miden limpieza de código; los tokens no son importes monetarios. La semilla fija el orden, no las respuestas del modelo. El tiempo incluye carga y esperas del CLI. Los valores ausentes no cuentan como cero.',
          '','## Qué se puede decir en un reel','',
          'Pendiente de interpretar la cobertura y los resultados observados. No se sostiene todavía que Medium produzca el 90 % del código más limpio ni que el máximo tarde el triple.']
    (RESULTADOS / 'resumen.md').write_text('\n'.join(out)+'\n')


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('accion',choices=['validar','piloto','principal','resumir'])
    args=parser.parse_args(); RESULTADOS.mkdir(exist_ok=True)
    if args.accion == 'validar': validate()
    elif args.accion == 'resumir': summarize()
    else: run_matrix('piloto' if args.accion == 'piloto' else 'principal')

if __name__ == '__main__': main()
