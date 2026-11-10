"""Reject ambiguous or incomplete physical endpoint evidence."""
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_clock_row_mapping import parse_capture

class ClockRowMappingTests(unittest.TestCase):
    def test_actual_capture_and_invalid_variants(self):
        source=ROOT/'data/raw/region_u280_20261022_v1/clock_row_pins_20261023_v1.tsv'
        text=source.read_text();endpoints,sites,configs=parse_capture(source)
        self.assertEqual((len(endpoints),len(sites)),(39,13))
        lines=text.splitlines();pin=next(line for line in lines if line.startswith('pin\t'))
        endpoint=next(line for line in lines if line.startswith('endpoint\t'))
        variants={'truncated':'\n'.join(lines[:-1]),'duplicate_endpoint':text+'\n'+endpoint,
                  'ambiguous_pin':text+'\n'+pin,'bad_type':text.replace('\tBUFCE_ROW_FSR\n','\tSLICEL\n'),
                  'bad_direction':text.replace('\tIN\t0','\tINVALID\t0')}
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'capture.tsv'
            for name,value in variants.items():
                with self.subTest(name=name):
                    p.write_text(value)
                    with self.assertRaises(ValueError):parse_capture(p)

if __name__=='__main__':unittest.main()
