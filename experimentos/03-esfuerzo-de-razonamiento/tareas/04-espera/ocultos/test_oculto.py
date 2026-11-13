import unittest
from espera import espera

class Pruebas(unittest.TestCase):
    def test_formula(self):
        for args,valor in [((0,2,10,.5),1),((2,2,10,1),8),((3,2,10,.5),5),((1000000,1,100,1),100),((2,.1,.3,1),.3),((0,3,3,0),0),((0,1e-300,1e300,1),1e-300)]:
            with self.subTest(args=args): self.assertAlmostEqual(espera(*args),valor)
    def test_invalidos(self):
        for args in [(0,10**1000,10**1001,.5),(-1,1,2,.5),(True,1,2,.5),(1.2,1,2,.5),(0,0,2,.5),(0,3,2,.5),(0,1,2,-.1),(0,1,2,1.1),(0,1,float('inf'),.5),(0,True,2,.5),(0,1,2,float('nan')),(0,1,2,True)]:
            with self.subTest(args=args),self.assertRaises(ValueError): espera(*args)


if __name__ == "__main__":
    unittest.main()
