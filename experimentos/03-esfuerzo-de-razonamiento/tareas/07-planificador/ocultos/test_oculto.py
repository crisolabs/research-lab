import unittest
from planificador import Planificador

class Pruebas(unittest.TestCase):
    def test_flujo(self):
        p=Planificador({'d':['b','c'],'c':['a'],'b':['a'],'a':[]},2)
        self.assertEqual(p.tomar(),['a']); self.assertEqual(p.tomar(),[])
        p.completar('a'); self.assertEqual(p.tomar(),['b','c']); p.completar('b')
        self.assertEqual(p.tomar(),[]); p.completar('c'); self.assertEqual(p.tomar(),['d'])
        self.assertFalse(p.terminado()); p.completar('d'); self.assertTrue(p.terminado())
    def test_capacidad(self):
        p=Planificador({'z':[],'a':[],'b':[]},2)
        self.assertEqual(p.tomar(),['a','b']); self.assertEqual(p.tomar(),[])
        p.completar('b'); self.assertEqual(p.tomar(),['z'])
    def test_fallos(self):
        p=Planificador({'a':[],'b':['a'],'c':['b'],'d':[]},2)
        self.assertEqual(p.tomar(),['a','d']); p.completar('a',False)
        self.assertEqual(p.estados(),{'a':'fallo','b':'bloqueado','c':'bloqueado','d':'en_curso'})
        self.assertFalse(p.terminado()); p.completar('d'); self.assertTrue(p.terminado())
    def test_invalidos(self):
        for deps in [{'a':['a']},{'a':['b'],'b':['a']},{'a':['z']},{'':[]},{'a':[1]}]:
            with self.subTest(deps=deps),self.assertRaises(ValueError): Planificador(deps,1)
        for c in [0,-1,True,1.5]:
            with self.assertRaises(ValueError): Planificador({},c)
        self.assertTrue(Planificador({},1).terminado())
    def test_copias_y_errores(self):
        deps={'a':[],'b':['a','a']}; p=Planificador(deps,1); deps['b'].clear()
        estado=p.estados(); estado['a']='listo'
        for n,e in [('a',True),('z',True),('b',False)]:
            with self.assertRaises(ValueError): p.completar(n,e)
        self.assertEqual(p.tomar(),['a'])
        with self.assertRaises(ValueError): p.completar('a',1)
        self.assertEqual(p.estados()['a'],'en_curso'); p.completar('a'); self.assertEqual(p.tomar(),['b'])


if __name__ == "__main__":
    unittest.main()
