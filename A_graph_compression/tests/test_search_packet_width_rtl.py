"""Performance parser rejects incomplete or invalid execution evidence."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_search_packet_width_rtl import cycles
class Timing(unittest.TestCase):
    def test_strict_two_transactions(self):
        good='transaction 0: 200 x\ntransaction 1: 20 4\n'
        self.assertEqual(cycles(good),[200,20])
        for bad in [good.splitlines()[0],good+good,good.replace('0: 200','0: 0'),good.replace('1: 20','2: 20'),'\n'.join(good.splitlines()[::-1])]:
            with self.assertRaises(ValueError):cycles(bad)
if __name__=='__main__':unittest.main()
