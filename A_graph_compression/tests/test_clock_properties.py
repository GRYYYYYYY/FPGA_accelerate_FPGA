"""Reject incomplete, repeated and mislabeled physical property captures."""
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_clock_properties import parse


class ClockPropertyTests(unittest.TestCase):
    def test_actual_capture_and_corruptions(self):
        text=(ROOT/'data/netlist/clock_property_observation_20261023_v1/probe.tsv').read_text()
        self.assertEqual(len(parse(text,'probe')[2]),1132)
        lines=text.splitlines();prop=next(line for line in lines if line.startswith('property\t'))
        mutations=[text.replace('meta\tstage\tprobe','meta\tstage\tbaseline'),
            '\n'.join(lines[:-1])+'\n',text.replace(prop+'\n','',1),
            text.replace(prop+'\n',prop+'\n'+prop+'\n',1),text+'meta\textra\tvalue\n']
        for i,bad in enumerate(mutations):
            with self.subTest(mutation=i),self.assertRaises(ValueError):parse(bad,'probe')


if __name__=='__main__':unittest.main()
