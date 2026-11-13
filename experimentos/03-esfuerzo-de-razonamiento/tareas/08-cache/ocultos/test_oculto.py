import unittest
from cache import Cache

class Reloj:
    def __init__(self): self.t=0
    def __call__(self): return self.t

class Pruebas(unittest.TestCase):
    def test_lru(self):
        r=Reloj(); c=Cache(2,10,r); c.poner('a',1); c.poner('b',2)
        self.assertEqual(c.obtener('a'),1); c.poner('c',3)
        self.assertEqual(c.claves(),['a','c']); self.assertIsNone(c.obtener('b'))
        self.assertEqual(c.estadisticas(),{'hits':1,'misses':1})
    def test_vencimiento(self):
        r=Reloj(); c=Cache(2,10,r); c.poner('a',None); r.t=5; c.poner('b',2)
        self.assertIsNone(c.obtener('a','falta')); r.t=10
        self.assertEqual(c.obtener('a','falta'),'falta'); self.assertEqual(c.claves(),['b'])
        c.poner('b',3); r.t=15; self.assertEqual(c.obtener('b'),3); r.t=20; self.assertEqual(c.claves(),[])
    def test_fabrica(self):
        r=Reloj(); c=Cache(1,10,r); llamadas=[]
        def crear(): llamadas.append(1); r.t=8; return 4
        self.assertEqual(c.obtener_o_crear('a',crear),4); r.t=15
        self.assertEqual(c.obtener_o_crear('a',lambda:99),4); self.assertEqual(llamadas,[1]); r.t=18
        self.assertEqual(c.obtener('a','falta'),'falta')
        self.assertEqual(c.estadisticas(),{'hits':1,'misses':2})
    def test_fallo_no_desaloja(self):
        r=Reloj(); c=Cache(1,10,r); c.poner('a',1)
        def falla(): raise RuntimeError('falla esperada')
        with self.assertRaises(RuntimeError): c.obtener_o_crear('b',falla)
        self.assertEqual(c.claves(),['a']); self.assertEqual(c.obtener_o_crear('b',lambda:None),None)
        self.assertEqual(c.claves(),['b']); self.assertEqual(c.estadisticas(),{'hits':0,'misses':2})
    def test_borrado_y_copias(self):
        r=Reloj(); c=Cache(2,1,r); c.poner('a',1); lista=c.claves(); lista.clear(); e=c.estadisticas(); e['hits']=99
        self.assertEqual(c.claves(),['a']); self.assertFalse(c.borrar('z')); self.assertTrue(c.borrar('a'))
        c.poner('b',2); r.t=1; self.assertFalse(c.borrar('b')); self.assertEqual(c.estadisticas(),{'hits':0,'misses':0})
    def test_validacion(self):
        for n in [0,-1,True,1.5]:
            with self.assertRaises(ValueError): Cache(n,1,lambda:0)
        for ttl in [0,-1,True,float('inf'),float('nan'),'1']:
            with self.assertRaises(ValueError): Cache(1,ttl,lambda:0)


if __name__ == "__main__":
    unittest.main()
