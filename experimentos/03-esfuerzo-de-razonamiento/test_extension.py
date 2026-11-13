"""Pruebas del orden y aislamiento de destinos; no invocan modelos."""
import collections
import unittest
from pathlib import Path

import extension
import medir


class ExtensionTests(unittest.TestCase):
    def test_celdas_y_controles_con_orden_estable(self):
        rows = extension.schedule('extension')
        self.assertEqual(rows, extension.schedule('extension'))
        self.assertEqual(len(rows), 56)
        self.assertEqual(len({row['id'] for row in rows}), 56)
        counts = collections.Counter((row['tarea'], row['nivel']) for row in rows)
        self.assertEqual(len(counts), 24)
        for (_, level), count in counts.items():
            self.assertEqual(count, 1 if level == 'high' else 3)
        self.assertEqual([row['orden'] for row in rows], list(range(1, 57)))
        controls = [row['orden'] for row in rows if row['nivel'] == 'high']
        self.assertTrue(any(position < 28 for position in controls))
        self.assertTrue(any(position > 28 for position in controls))

    def test_piloto_no_se_solapa_y_destinos_separados(self):
        pilot = extension.schedule('piloto-extension')
        self.assertEqual(len(pilot), 2)
        self.assertEqual({r['nivel'] for r in pilot}, {'xhigh', 'max'})
        self.assertEqual({r['tarea'] for r in pilot}, {'01-lotes'})
        self.assertFalse({r['id'] for r in pilot} & {r['id'] for r in extension.schedule('extension')})
        self.assertEqual(extension.ARTEFACTOS, medir.ROOT / 'resultados/extension-01')
        self.assertNotEqual(extension.SEED, medir.SEED)

    def test_congelado_original_sigue_igual(self):
        medir.check_frozen()


if __name__ == '__main__':
    unittest.main()
