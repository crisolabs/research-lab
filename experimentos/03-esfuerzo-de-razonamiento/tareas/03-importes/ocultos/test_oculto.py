import unittest
from importes import centavos

class Pruebas(unittest.TestCase):
    def test_validos(self):
        for t,n in [('12,3',1230),('-0,01',-1),('  +7  ',700),('0',0),('-0,00',0),('001,09',109),('99999999999999999999,99',9999999999999999999999),('0,29',29)]:
            with self.subTest(t=t): self.assertEqual(centavos(t),n)
    def test_invalidos(self):
        for t in ['',',1','1,','1,234','1.00','1e2','1 2','++2','１２','١',None,12,True]:
            with self.subTest(t=t),self.assertRaises(ValueError): centavos(t)


if __name__ == "__main__":
    unittest.main()
