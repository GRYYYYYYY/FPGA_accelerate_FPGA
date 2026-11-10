"""Reject owner-threshold stimulus corruption; not an RTL result."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_round_control_rtl_setup_v2 import verify_single_owner_frame

class ThresholdTests(unittest.TestCase):
    def test_every_owner_word(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'counts.dat'
            good=(3).to_bytes(8,'big')+bytes.fromhex('00000001')*3
            p.write_bytes(good)
            self.assertEqual(verify_single_owner_frame(p,3)['expected_conflict_groups'],0)
            for bad in [good[:-1],good[:8]+bytes(4)+good[12:],good[:-4]+bytes.fromhex('00000002'),(2).to_bytes(8,'big')+good[8:]]:
                p.write_bytes(bad)
                with self.assertRaises(ValueError):verify_single_owner_frame(p,3)

if __name__=='__main__':unittest.main()
