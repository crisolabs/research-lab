#!/usr/bin/env python3
"""Verifica cierre, procedencia y separación de datos; nunca llama modelos."""
import csv
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import extension0202 as e
import resumir0202 as r


def git(*args):
    return subprocess.check_output(['git', *args], cwd=e.ROOT, text=True).strip()


def rows(path):
    with path.open(newline='') as handle: return list(csv.DictReader(handle))


def check():
    e.medir.check_frozen()
    baseline = e.read(e.ART / 'historicos-congelados.json')
    assert len(baseline) == 584
    assert all(e.sha(e.ROOT / name) == value for name, value in baseline.items())
    fixed_source = subprocess.check_output(['git','show','863dfe5:experimentos/03-esfuerzo-de-razonamiento/extension0202.py'], cwd=e.ROOT)
    assert hashlib.sha256(fixed_source).hexdigest() == e.sha(Path(e.__file__))
    files = git('diff-tree','--no-commit-id','--name-only','-r','0ad8fcd').splitlines()
    assert files == ['experimentos/03-esfuerzo-de-razonamiento/ENMIENDA-02-02.md']
    prereg_time = datetime.datetime.fromisoformat(git('show','-s','--format=%cI','0ad8fcd'))
    coverage = {}
    intervals = []
    for model, expected in (('claude-haiku-5-5',120),('claude-opus-5-5',120),('fable',28)):
        base = e.ART / model
        main = rows(r.csv_path(model))
        assert len(main) == expected
        assert [x['id'] for x in main] == [x['id'] for x in e.schedule(model,'principal')[:expected]]
        assert len({x['id'] for x in main}) == expected
        assert all(x['fase'] == 'principal' for x in main)
        pilot = rows(r.csv_path(model,'piloto'))
        assert len(pilot) == 1 and pilot[0]['fase'] == 'piloto'
        assert len(list((base/'sondeos').glob('*.json'))) == 5
        for start_path in (base/'iniciadas').glob('*.json'):
            start = e.read(start_path)
            phase = 'sondeos' if start['id'].startswith('sondeo-') else 'corridas'
            name = start['id'].removeprefix('sondeo-') if phase == 'sondeos' else start['id']
            result = e.read(base/phase/(name+'.json'))
            assert result is not None
            assert datetime.datetime.fromisoformat(start['inicio_utc']) > prereg_time
            beginning = start['inicio_monotonic_ns']/1e9
            intervals.append((beginning, beginning+float(result['segundos'])))
            assert start['concurrencia_al_inicio'] <= 2
        for row in main:
            record = e.read(base/'corridas'/(row['id']+'.json'))
            assert all(str(record[k]) == v for k,v in row.items())
            receipt = e.read(base/'recibos'/(row['id']+'.json'))
            assert int(row['denegaciones']) == receipt.get('permisos_denegados',{}).get('cantidad',0)
            uses = receipt['uso_por_modelo']
            if uses:
                ordered = sorted([(v['outputTokens'],k) for k,v in uses.items()], reverse=True)
                assert len(ordered) == 1 or ordered[0][0] > ordered[1][0]
                assert row['modelo_efectivo'] == ordered[0][1]
            else: assert row['modelo_efectivo'] == ''
            usage = receipt['uso']
            if row['tokens_totales']:
                assert int(row['tokens_totales']) == sum(usage.get(k,0) for k in ('input_tokens','cache_creation_input_tokens','cache_read_input_tokens','output_tokens'))
            if row['timeout'] == '1':
                assert row['resuelta'] == '0' and row['tokens_totales'] == '' and row['modelo_efectivo'] == ''
            if row['cuota'] == '1': assert row['resuelta'] == ''
            if row['resuelta'] == '1':
                assert row['retorno_cli'] == '0' and row['timeout'] == '0' and row['tests_aprobados'] == row['tests_total']
        coverage[model] = {'observadas':len(main),'evaluables':len(r.evaluable(main)),'resueltas':r.solved(r.evaluable(main)),
                           'cuota':sum(x['cuota']=='1' for x in main),'timeouts':sum(x['timeout']=='1' for x in main),
                           'pendientes':len(e.schedule(model,'principal'))-len(main)}
    audit_dir = e.ART/'fable/auditoria-cuota'
    audit = e.read(audit_dir/'correccion.json')
    original = e.read(audit_dir/'observacion-original.json')
    corrected = e.read(e.ART/'fable/corridas'/(original['id']+'.json'))
    assert {k for k in original if original[k] != corrected[k]} == {'estado','cuota','error'}
    assert e.sha(audit_dir/'observacion-original.json') == audit['original_sha256']
    assert e.sha(audit_dir/'crudo-original.csv') == audit['csv_original_sha256']
    assert e.sha(e.ART/'fable/recibos'/(original['id']+'.json')) == audit['recibo_intacto_sha256']
    assert corrected['error_textual'].startswith("You've reached your Fable limit.")
    assert e.read(e.ART/'cuota-anthropic.json')['proveedor'] == 'anthropic'
    diag = e.RESULTADOS/'extension-02/diagnostico-luna-low'
    diagnostic = rows(diag/'crudo.csv')
    assert len(diagnostic) == 6 and all(x['fase']=='diagnostico' for x in diagnostic)
    assert len((diag/'nota.md').read_text().splitlines()) == 10
    for task in ('04-espera','01-lotes','08-cache'):
        assert sum(x['tarea']==task for x in diagnostic) == 2
    for row in diagnostic:
        receipt = e.read(diag/'gpt-6-luna/recibos'/(row['id']+'.json'))['diagnostico']
        assert receipt['mensaje_final'] and receipt['comandos']
        assert all({'comando','estado','retorno'} <= c.keys() for c in receipt['comandos'])
        assert int(row['concurrencia_al_inicio']) == 1
        assert not any(Path(e.ART/'fable/iniciadas').glob(row['id']+'.json'))
    events = sorted([(a,1) for a,b in intervals]+[(b,-1) for a,b in intervals], key=lambda x:(x[0],x[1]))
    active = maximum = 0
    for _, delta in events: active += delta; maximum = max(maximum,active)
    assert maximum <= 2 and active == 0
    provenance = e.read(e.ART/'resumen-trazabilidad.json')
    assert provenance['conteos'] == {'observadas_principales':388,'evaluables':387,'resueltas_evaluables':367,
                                   'fallos_funcionales':20,'infraestructura':0,'cuota':1,'timeouts':8,'pilotos_excluidos':4,'sondeos_excluidos':20}
    assert 'crudo.csv' not in provenance['csv_entrada_sha256'] or provenance['csv_entrada_sha256']['crudo.csv'] == e.sha(e.RESULTADOS/'crudo.csv')
    assert all('diagnostico' not in name for name in provenance['csv_entrada_sha256'])
    assert provenance['razones_sobre_medianas_crudas']['claude-opus-5-5']['n_tokens_alto'] == 21
    assert 'fable' not in provenance['razones_sobre_medianas_crudas']
    old_summary = subprocess.check_output(['git','show','0ad8fcd^:experimentos/03-esfuerzo-de-razonamiento/resultados/resumen.md'],cwd=e.ROOT,text=True)
    assert old_summary.split(r.MARK)[0].rstrip() == (e.RESULTADOS/'resumen.md').read_text().split(r.MARK)[0].rstrip()
    old_root = subprocess.check_output(['git','show','0ad8fcd^:README.md'],cwd=e.ROOT,text=True).splitlines()
    new_root = (e.ROOT.parent.parent/'README.md').read_text().splitlines()
    assert len(old_root)==len(new_root)
    assert all(a==b or a.startswith('| 03 |') and b.startswith('| 03 |') for a,b in zip(old_root,new_root))
    result = {'banco_archivos_intactos':34,'historicos_intactos':584,'candidato_medicion_intacto':'863dfe5',
              'enmienda_commit_solo':'0ad8fcd','bloques':coverage,'max_concurrencia_reconstruida':maximum,
              'diagnosticos_separados':len(diagnostic),'diagnosticos_resueltos':sum(x['resuelta']=='1' for x in diagnostic),
              'nota_lineas':10,'prefijo_resumen_intacto':True,'readme_raiz_solo_fila03':True,'llamadas_proveedores_en_verificador':0}
    e.write(e.ART/'validacion-cierre.json', result)
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__': check()
