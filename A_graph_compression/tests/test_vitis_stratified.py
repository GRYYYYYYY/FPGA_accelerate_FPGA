import pathlib
import struct
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from prepare_vitis_stratified import read_full_case, encode_case


class StratifiedGoldenTests(unittest.TestCase):
    def test_complete_edge_records_status_and_boundaries(self):
        # Two parallel edges retain distinct PIP/direction/property records.
        edges = struct.pack('<16I', 7,9,2,11,12,13,14,0, 7,9,2,15,16,17,18,1)
        rows = {7: (0,2,edges), 8: (0,0,b''), 10: (1,0,b'')}
        valid = encode_case(rows, [10,7,8])
        self.assertEqual(read_full_case(valid), rows)
        def replace(index, value):
            bad = bytearray(valid); struct.pack_into('<I', bad, index*4, value); return bad
        # Header n/capacity/record/failure count; request duplication; wrong offsets,
        # unknown-with-edges; unsupported statuses; wrong source; unsorted edges.
        invalid = [valid[:-1], valid+b'\0\0\0\0', replace(0,65537), replace(1,0),
                   replace(2,1), replace(3,0), replace(6,7), replace(7,1),
                   replace(8,1), replace(9,2), replace(10,1), replace(16,8)]
        shuffled = bytearray(valid)
        shuffled[64:128] = valid[96:128]+valid[64:96]
        invalid.append(shuffled)
        for i, bad in enumerate(invalid):
            with self.subTest(mutation=i), self.assertRaises(ValueError):
                read_full_case(bad)


if __name__ == '__main__':
    unittest.main()
