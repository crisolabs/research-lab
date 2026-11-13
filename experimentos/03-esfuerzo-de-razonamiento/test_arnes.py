"""Controles locales del arnés; no invocan el modelo."""
import collections
from pathlib import Path
import tempfile
import unittest

import medir


class PruebasArnes(unittest.TestCase):
    def test_matriz_balanceada_y_reproducible(self):
        matriz = medir.schedule('principal')
        self.assertEqual(len(matriz),72)
        self.assertEqual(matriz,medir.schedule('principal'))
        self.assertEqual(set(collections.Counter((r['tarea'],r['nivel']) for r in matriz).values()),{3})
        self.assertEqual(len({r['id'] for r in matriz}),72)
        self.assertEqual(len(medir.schedule('piloto')),3)

    def test_diff_cuenta_reemplazo_nuevos_borrados_y_binarios(self):
        a={'mod.py':b'a\nb\n','borrado':b'x\n','igual':b'mismo'}
        b={'mod.py':b'a\nc\nd\n','nuevo':b'n\n','igual':b'mismo','bin':b'\0'}
        added,deleted,extra,binaries=medir.measure_diff(a,b,['mod.py'])
        self.assertEqual((added,deleted),(3,2))
        self.assertEqual(extra,['bin','borrado','nuevo'])
        self.assertEqual(binaries,['bin'])

    def test_evento_uso_no_duplica_cache_ni_razonamiento(self):
        output=b'{"type":"item.completed"}\n{"type":"turn.completed","usage":{"input_tokens":10,"cached_input_tokens":8,"output_tokens":4,"reasoning_output_tokens":3}}\n'
        uso,tipos=medir.parse_events(output)
        self.assertEqual(uso['input_tokens']+uso['output_tokens'],14)
        self.assertEqual(uso['reasoning_output_tokens'],3)
        self.assertEqual(tipos,['item.completed','turn.completed'])
        self.assertEqual(medir.parse_events(b'no json\n')[0],{})

    def test_timeout_y_cierre_real(self):
        rc,timeout,seconds,_,_=medir.run_process(['/usr/bin/python3','-c','import time; time.sleep(30)'],.05)
        self.assertTrue(timeout)
        self.assertNotEqual(rc,0)
        self.assertLess(seconds,3)

    def test_evaluador_rechaza_symlink_sin_seguir(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp); (p/'lotes.py').symlink_to('/archivo-inexistente')
            result=medir.evaluate(p,medir.ROOT/'tareas/01-lotes/ocultos')
            self.assertEqual(result,(False,0,0,False))

    def test_evaluador_preimporta_unittest_frente_a_shadow(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            (p/'lotes.py').write_text((medir.ROOT/'tareas/01-lotes/referencia/lotes.py').read_text())
            (p/'unittest.py').write_text('raise RuntimeError("sombra")')
            result=medir.evaluate(p,medir.ROOT/'tareas/01-lotes/ocultos')
            self.assertTrue(result[0])
            self.assertEqual(result[1:3],(3,3))


if __name__ == '__main__':
    unittest.main()
