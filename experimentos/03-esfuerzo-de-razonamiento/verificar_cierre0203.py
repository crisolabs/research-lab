#!/usr/bin/env python3
"""Verifica cierre completo de protocolo-02-03 manteniendo intacto protocolo-02-02."""
import csv
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

import extension0202 as e02
import extension0203 as e03
import resumir0202 as r02


def git(*args):
    return subprocess.check_output(['git', *args], cwd=e03.ROOT, text=True).strip()


def rows(path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


def check():
    # 1. Verify frozen bank & 584 historical files untouched
    e03.medir.check_frozen()
    baseline = e02.read(e02.ART / 'historicos-congelados.json')
    assert len(baseline) == 584
    assert all(e02.sha(e03.ROOT / name) == value for name, value in baseline.items())

    # 2. Verify ENMIENDA-02-03 was committed alone and extension0203.py matches commit 104633d
    files = git('diff-tree', '--no-commit-id', '--name-only', '-r', '0a7ee11').splitlines()
    assert files == ['experimentos/03-esfuerzo-de-razonamiento/ENMIENDA-02-03.md'], files
    prereg_time = datetime.datetime.fromisoformat(git('show', '-s', '--format=%cI', '0a7ee11'))
    fixed_source = subprocess.check_output(['git', 'show', '104633d:experimentos/03-esfuerzo-de-razonamiento/extension0203.py'], cwd=e03.ROOT)
    assert hashlib.sha256(fixed_source).hexdigest() == e02.sha(Path(e03.__file__))

    # 3. Verify sealed protocolo-02-02 artifacts match pre-run snapshot in verificacion-congelado.json
    verif03 = e02.read(e03.ART03 / 'verificacion-congelado.json')
    assert verif03['protocolo_02_02_hashes'] == e03.p0202_hashes()

    # 4. Verify all 93 Fable API runs, pilot, probes, concurrency <= 2, and zero overlap with 02-02 evaluables
    base = e03.ART03 / 'fable'
    main = rows(e03.RESULTADOS / 'crudo-fable-02-03.csv')
    expected_items = e03.schedule('principal')
    assert len(main) == 93
    assert [x['id'] for x in main] == [x['id'] for x in expected_items]
    assert len({x['id'] for x in main}) == 93
    assert all(x['fase'] == 'principal' and x['canal_auth'] == 'api_key' for x in main)

    eval_02 = {r['id'] for r in rows(e03.RESULTADOS / 'crudo-fable-02-02.csv') if r['resuelta'] in ('0', '1') and r['cuota'] != '1'}
    assert len(eval_02) == 27
    assert not (eval_02 & {x['id'] for x in main})
    assert len(eval_02 | {x['id'] for x in main}) == 120

    pilot = rows(e03.RESULTADOS / 'piloto-fable-02-03.csv')
    assert len(pilot) == 1 and pilot[0]['fase'] == 'piloto' and pilot[0]['resuelta'] == '1'
    assert len(list((base / 'sondeos').glob('*.json'))) == 5

    intervals = []
    for start_path in (base / 'iniciadas').glob('*.json'):
        start = e02.read(start_path)
        phase = 'sondeos' if start['id'].startswith('sondeo-') else 'corridas'
        name = start['id'].removeprefix('sondeo-') if phase == 'sondeos' else start['id']
        result = e02.read(base / phase / (name + '.json'))
        assert result is not None
        assert datetime.datetime.fromisoformat(start['inicio_utc']) > prereg_time
        beginning = start['inicio_monotonic_ns'] / 1e9
        intervals.append((beginning, beginning + float(result['segundos'])))
        assert start['concurrencia_al_inicio'] <= 2

    for row in main:
        record = e02.read(base / 'corridas' / (row['id'] + '.json'))
        assert all(str(record[k]) == v for k, v in row.items())
        receipt = e02.read(base / 'recibos' / (row['id'] + '.json'))
        uses = receipt['uso_por_modelo']
        if uses:
            ordered = sorted([(v['outputTokens'], k) for k, v in uses.items()], reverse=True)
            assert len(ordered) == 1 or ordered[0][0] > ordered[1][0]
            assert row['modelo_efectivo'] == 'claude-fable-5-2' == ordered[0][1]
        else:
            assert row['modelo_efectivo'] == ''
        usage = receipt['uso']
        if row['tokens_totales']:
            assert int(row['tokens_totales']) == sum(usage.get(k, 0) for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens'))
        if row['timeout'] == '1':
            assert row['resuelta'] == '0' and row['tokens_totales'] == '' and row['modelo_efectivo'] == ''
        if row['resuelta'] == '1':
            assert row['retorno_cli'] == '0' and row['timeout'] == '0' and row['tests_aprobados'] == row['tests_total']

    events = sorted([(a, 1) for a, b in intervals] + [(b, -1) for a, b in intervals], key=lambda x: (x[0], x[1]))
    active = maximum = 0
    for _, delta in events:
        active += delta
        maximum = max(maximum, active)
    assert maximum <= 2 and active == 0

    # 5. Verify provenance, summary prefix, and root README
    provenance = e02.read(e03.ART03 / 'resumen-trazabilidad.json')
    assert provenance['conteos']['evaluables'] == 480
    assert len(provenance['razones_sobre_medianas_crudas']) == 5
    old_summary = subprocess.check_output(['git', 'show', '0ad8fcd^:experimentos/03-esfuerzo-de-razonamiento/resultados/resumen.md'], cwd=e03.ROOT, text=True)
    assert old_summary.split(r02.MARK)[0].rstrip() == (e03.RESULTADOS / 'resumen.md').read_text().split(r02.MARK)[0].rstrip()

    old_root = subprocess.check_output(['git', 'show', '0ad8fcd^:README.md'], cwd=e03.ROOT, text=True).splitlines()
    new_root = (e03.ROOT.parent.parent / 'README.md').read_text().splitlines()
    assert len(old_root) == len(new_root)
    assert all(a == b or (a.startswith('| 03 |') and b.startswith('| 03 |')) for a, b in zip(old_root, new_root))

    result = {
        'banco_archivos_intactos': 34,
        'historicos_intactos': 584,
        'protocolo_02_02_intacto': True,
        'enmienda_commit_solo': '0a7ee11',
        'candidato_02_03_intacto': '104633d',
        'fable_02_02_evaluables': 27,
        'fable_02_03_evaluables': 93,
        'fable_combinado_evaluables': 120,
        'fable_max_resueltas': sum(r['resuelta'] == '1' for r in (rows(e03.RESULTADOS / 'crudo-fable-02-02.csv') + main) if r['nivel'] == 'max' and r['cuota'] != '1'),
        'max_concurrencia_reconstruida': maximum,
        'prefijo_resumen_intacto': True,
        'readme_raiz_solo_fila03': True,
        'llamadas_proveedores_en_verificador': 0,
    }
    e02.write(e03.ART03 / 'validacion-cierre.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    check()
