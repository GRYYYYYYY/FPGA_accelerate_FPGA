import unittest
from lut_equation import equivalent, truth_table, MASK


class LutEquationTests(unittest.TestCase):
    def test_lut5_shares_lower_init_bits(self):
        self.assertEqual(truth_table('O5=A3',output='O5'),truth_table('O6=A3') & 0xffffffff)
        self.assertEqual(truth_table('O5=~0',output='O5'),0xffffffff)
        with self.assertRaises(ValueError):truth_table('O5=A6',output='O5')

    def test_equivalent_vivado_forms(self):
        self.assertTrue(equivalent('O6=(A6)','O6=A6'))
        self.assertTrue(equivalent('O6=(A6+~A6)*A2','O6=A2'))
        self.assertTrue(equivalent('O6=A1*A2+A1*~A2','O6=A1'))

    def test_distinct_requirements(self):
        self.assertFalse(equivalent('O6=1','O6=A5'))
        self.assertFalse(equivalent('O6=A2','O6=A4'))
        self.assertEqual(truth_table('O6=~0'),MASK)
        self.assertEqual(truth_table('O6=A1*~A1'),0)

    def test_reject_unsupported_or_malformed(self):
        for text in ('NOT CONFIGURED','O5=A1','O6=A7','O6=A1 A2',
                     'O6=(A1','O6=A1)','O6=A1+','O6=__import__(x)'):
            with self.subTest(text=text),self.assertRaises(ValueError):truth_table(text)
