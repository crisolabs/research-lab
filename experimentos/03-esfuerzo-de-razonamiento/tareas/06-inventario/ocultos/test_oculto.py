import unittest
from inventario import Inventario

class Pruebas(unittest.TestCase):
    def test_flujo(self):
        x=Inventario(); self.assertEqual(x.saldo('A'),0)
        self.assertIsNone(x.ingresar('i','A',10)); x.transferir('t','A','B',4); x.retirar('r','B',1)
        self.assertEqual((x.saldo('A'),x.saldo('B')),(6,3))
        x.revertir('v','r'); x.revertir('w','t')
        self.assertEqual((x.saldo('A'),x.saldo('B')),(10,0))
        self.assertEqual(x.historial()[-1],dict(id='w',tipo='reversion',origen='B',destino='A',cantidad=4,original='t'))
    def test_idempotencia(self):
        x=Inventario(); x.ingresar('i','A',5); x.ingresar('i','A',5)
        with self.assertRaises(ValueError): x.ingresar('i','A',6)
        with self.assertRaises(ValueError): x.retirar('i','A',5)
        x.revertir('v','i'); x.revertir('v','i')
        self.assertEqual(x.saldo('A'),0); self.assertEqual(len(x.historial()),2)
        with self.assertRaises(ValueError): x.revertir('w','i')
        with self.assertRaises(ValueError): x.revertir('w','v')
    def test_atomicidad(self):
        x=Inventario(); x.ingresar('i','A',5)
        for f in [lambda:x.transferir('t','A','B',6),lambda:x.retirar('r','A',6),lambda:x.revertir('v','z')]:
            with self.assertRaises(ValueError): f()
            self.assertEqual(x.saldo('A'),5); self.assertEqual(len(x.historial()),1)
        x.transferir('t','A','B',5)
        with self.assertRaises(ValueError): x.revertir('v','i')
        x.revertir('w','t'); x.revertir('v','i'); self.assertEqual(x.saldo('A'),0)
        x.ingresar('r','A',2); self.assertEqual(x.saldo('A'),2)
    def test_validacion(self):
        x=Inventario()
        for valor in [0,-1,True,1.2,'1']:
            with self.subTest(valor=valor),self.assertRaises(ValueError): x.ingresar('i','A',valor)
        for valor in ['',None,1]:
            with self.subTest(valor=valor),self.assertRaises(ValueError): x.saldo(valor)
            with self.assertRaises(ValueError): x.ingresar(valor,'A',1)
        with self.assertRaises(ValueError): x.transferir('t','A','A',1)
        self.assertEqual(x.historial(),[])
    def test_copias(self):
        x=Inventario(); x.ingresar('i','A',3); h=x.historial(); h[0]['cantidad']=100; h.clear()
        self.assertEqual(x.historial()[0]['cantidad'],3); self.assertEqual(x.saldo('A'),3)


if __name__ == "__main__":
    unittest.main()
