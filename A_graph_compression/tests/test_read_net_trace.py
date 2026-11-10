from pathlib import Path
import struct
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from read_net_trace import decode_words

class NetTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (ROOT/'build/net_trace_cpu_20261025_v1/fixture.bin').read_bytes()
        cls.words = list(struct.unpack('<%dQ' % (len(raw)//8), raw))
    def test_literal_snapshot(self):
        d = decode_words(self.words, 8)
        self.assertFalse(d['complete_batch'])
        r = d['records'][0]
        self.assertEqual(r['net'], 7)
        self.assertEqual(r['roots'], [0, 1])
        self.assertEqual(r['retained'], [0, 1])
        self.assertEqual(sorted(r['owned_keys']), [7 << 32, (7 << 32)|1])
        self.assertEqual(r['occupancy'], [[1, 0], [1, 0]])
        self.assertEqual(r['edges'], [[0, 1, 9, 11, 2, 3, 4, 1]])
        self.assertEqual(r['site_owners'], [[3, 7, 0, 0], [(1 << 32)|4, 7, 1, 1], [(2 << 32)|5, 7, 0, 2]])
    def test_corruptions(self):
        # Literal byte-layout offsets, independently specified from this fixture.
        changes = [(0, 0), (2, 139), (3, 2), (4, 2), (5, 9),
                   (8, 1), (9, 139), (12, 1 << 32), (18, 1),
                   (24, 1), (25, 9), (26, 1), (29, 2), (30, 1),
                   (98, 9), (99, 7), (100, 3), (101, 7),
                   (102, 0), (103, 7), (104, 1), (106, 0),
                   (112, 0), (113, 7), (114, 0), (115, 2),
                   (116, 2), (117, 0), (118, 0), (119, 65537),
                   (124, 0), (125, 0), (126, 6 << 32),
                   (128, 0), (132, (2 << 32)|0), (135, 2 << 32),
                   (136, 4), (137, 8), (140, 0), (143, 0), (147, 3)]
        for offset, value in changes:
            with self.subTest(offset=offset):
                w = self.words.copy()
                self.assertNotEqual(w[offset], value)
                w[offset] = value
                with self.assertRaises(ValueError): decode_words(w, 8)
        for w in [self.words[:-1], self.words+[0]]:
            with self.assertRaises(ValueError): decode_words(w, 8)

if __name__ == '__main__': unittest.main()
