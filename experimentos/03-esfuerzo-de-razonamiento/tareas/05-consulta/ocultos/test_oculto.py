import unittest
from consulta import actualizar

class Pruebas(unittest.TestCase):
    def test_repetidos(self):
        self.assertEqual(actualizar('https://ejemplo.test/r?a=1&b=&a=2&c=3#fin',{'a':'9'}),'https://ejemplo.test/r?b=&c=3&a=9#fin')
        self.assertEqual(actualizar('/r?a=1&a=2&b=3&b=4',{'a':None}),'/r?b=3&b=4')
    def test_codificacion(self):
        self.assertEqual(actualizar('/r?q=a+b&v=%2B',{'q':'ñ &+'}),'/r?v=%2B&q=%C3%B1+%26%2B')
        self.assertEqual(actualizar('/r#f',{'x':'','y':None}),'/r?x=#f')
    def test_conservacion(self):
        cambios={'b':'dos','a':'uno'}
        self.assertEqual(actualizar('/r?a=1&x=&x=3',cambios),'/r?x=&x=3&b=dos&a=uno')
        self.assertEqual(cambios,{'b':'dos','a':'uno'})
        self.assertEqual(actualizar('/r?a=1&a=2',{}),'/r?a=1&a=2')


if __name__ == "__main__":
    unittest.main()
