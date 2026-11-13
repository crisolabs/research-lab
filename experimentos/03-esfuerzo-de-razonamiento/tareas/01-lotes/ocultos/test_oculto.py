import unittest
from lotes import lotes

class Pruebas(unittest.TestCase):
    def test_basicos(self):
        for entrada,n,esperado in [([],3,[]),([1],2,[[1]]),([1,2,3,4,5],2,[[1,2],[3,4],[5]]),([1,2],1,[[1],[2]]),([1,2],2,[[1,2]])]:
            with self.subTest(entrada=entrada,n=n):
                original=entrada.copy()
                self.assertEqual(lotes(entrada,n),esperado)
                self.assertEqual(entrada,original)
    def test_generador(self):
        self.assertEqual(lotes((x*x for x in range(5)),2),[[0,1],[4,9],[16]])
        self.assertEqual(lotes('abc',2),[['a','b'],['c']])
    def test_invalidos(self):
        for n in [0,-1,True,False,1.5,'2',None]:
            with self.subTest(n=n),self.assertRaises(ValueError): lotes([],n)


if __name__ == "__main__":
    unittest.main()
