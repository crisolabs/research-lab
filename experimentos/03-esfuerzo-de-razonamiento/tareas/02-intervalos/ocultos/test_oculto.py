import unittest
from intervalos import unir

class Pruebas(unittest.TestCase):
    def test_union(self):
        entrada=[[5,8],[1,3],[3,5],[11,11],[2,2]]
        self.assertEqual(unir(entrada),[[1,8],[11,11]])
        self.assertEqual(entrada,[[5,8],[1,3],[3,5],[11,11],[2,2]])
    def test_limites(self):
        self.assertEqual(unir([]),[])
        enorme=10**1000
        self.assertEqual(unir([(enorme,enorme+1)]),[[enorme,enorme+1]])
        self.assertEqual(unir(iter([(1,2),(1,2),(-3,-1)])),[[-3,-1],[1,2]])
        self.assertEqual(unir([(0.5,1.5),(1.6,2.5)]),[[0.5,1.5],[1.6,2.5]])
    def test_invalidos(self):
        for p in [None,3,[2,1],[1],[1,2,3],[True,3],[0,float('nan')],[0,float('inf')],['1',2]]:
            with self.subTest(p=p),self.assertRaises(ValueError): unir([p])


if __name__ == "__main__":
    unittest.main()
