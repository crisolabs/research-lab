#!/usr/bin/env python3
"""Aplica la regla preexistente de cuota al cierre, preservando el original."""
import hashlib
import json
from pathlib import Path
import shutil
import extension0202 as e

MODEL = 'fable'
RUN_ID = 'principal-07-planificador-xhigh-2'


def main():
    e.verify()
    base = e.ART / MODEL
    audit = base / 'auditoria-cuota'
    record_path = base / 'corridas' / (RUN_ID + '.json')
    receipt_path = base / 'recibos' / (RUN_ID + '.json')
    csv_path = e.RESULTADOS / 'crudo-fable-02-02.csv'
    audit.mkdir(parents=True, exist_ok=True)
    originals = ((record_path, 'observacion-original.json'), (csv_path, 'crudo-original.csv'), (base / 'estado.json', 'estado-original.json'))
    for source, name in originals:
        target = audit / name
        if not target.exists(): shutil.copyfile(source, target)
    original = e.read(audit / 'observacion-original.json')
    message = original['error_textual']
    if not message.startswith("You've reached your Fable limit."):
        raise RuntimeError('La evidencia no coincide con el mensaje explícito auditado.')
    corrected = {**original, 'estado': 'cuota', 'cuota': 1, 'error': 'cuota'}
    # Resolution remains absent; no measurements, tests or usage are adjusted.
    if original['resuelta'] != '': raise RuntimeError('Cierre inesperado: requiere auditoría.')
    current = e.read(record_path)
    if current not in (original, corrected): raise RuntimeError('La observación cambió fuera de esta corrección.')
    e.write(record_path, corrected)
    e.record_quota(MODEL, message)
    state = {**e.state(MODEL), 'estado': 'incompleto', 'motivo': 'cuota'}
    rows = e.export(MODEL)
    state.update(observadas=len(rows), pendientes=120-len(rows))
    e.save_state(MODEL, state)
    e.write(audit / 'correccion.json', {
        'regla': 'Cuota explícita excluida del denominador y cierre del proveedor, según EXTENSION-02.md.',
        'motivo': 'El parser no reconocía la frase reached your Fable limit y clasificó infraestructura; ese estado igualmente detuvo el lanzamiento al cerrar la tanda.',
        'campos_cambiados': {'estado': ['infraestructura','cuota'], 'cuota': [0,1], 'error': ['infraestructura','cuota']},
        'sin_cambios': 'Tiempos, tokens, tests, resolución ausente, recibo y candidato de medición.',
        'original_sha256': e.sha(audit / 'observacion-original.json'), 'csv_original_sha256': e.sha(audit / 'crudo-original.csv'),
        'recibo_intacto_sha256': e.sha(receipt_path), 'observacion_derivada_sha256': e.sha(record_path),
        'candidato_medicion_sha256': e.sha(Path(e.__file__)),
        'observadas': len(rows), 'pendientes': state['pendientes'],
        'sin_llamadas_posteriores_anthropic': 'La última iniciada y cerrada es la observación auditada; no se hizo comprobación, espera ni cambio de modelo/cuenta.'})
    print(json.dumps({'modelo':'claude-fable-5-2','observadas':len(rows),'evaluables':sum(r['resuelta'] in (0,1) for r in rows),'cuota':sum(r['cuota'] for r in rows),'pendientes':state['pendientes']}))


if __name__ == '__main__': main()
