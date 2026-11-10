"""Real graph boundary, identity and native decoder checks for nested scale domains."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/p) for p in ('src', 'scripts', 'adapters')]
from import_vivado import read_export
from heldout import fit_bank, select_sources, source_slr
from packed_graph import write_packed
from scale_domain import make_domain
from check_scale_domain import check_image, check_selection


class ScaleDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(); cls.path = Path(cls.temp.name)
        cfg = json.loads((ROOT/'configs/region_query.json').read_text())
        training = read_export(ROOT/cfg['training']['path'])
        cls.bank = fit_bank(select_sources(training, [r for r in training['roots'] if source_slr(training,r)==0]))
        cls.graph = read_export(ROOT/cfg['heldout']['path'])
        cls.binary = cls.path/'scan'
        subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',
                        str(ROOT/'src/native/scale_domain_scan.cpp'),'-o',str(cls.binary)], check=True)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_nested_real_domains_and_both_native_decoders(self):
        previous = set()
        for denominator in (16,4,2,1):
            domain, selection = make_domain(self.graph, denominator)
            self.assertLessEqual(previous, set(domain['roots'])); previous = set(domain['roots'])
            check_selection(self.graph, domain, selection)
            for mode in ('csr','compact'):
                path = self.path/f'{denominator}_{mode}.agr'; dump = path.with_suffix('.bin')
                write_packed(path, domain, mode, self.bank if mode=='compact' else None)
                result = subprocess.run([str(self.binary),str(path),str(dump)],capture_output=True,text=True,check=True)
                counts = check_image(domain,path,dump,json.loads(result.stdout))
                self.assertEqual(counts['directed_edges'],len(domain['edges']))
                self.assertEqual(counts['unknown_rows'],len(domain['nodes'])-len(domain['roots']))
        self.assertEqual(previous,set(self.graph['roots']))

    def test_clipped_edge_alias_and_promoted_boundary_rejected(self):
        domain, selection = make_domain(self.graph,4)
        bad = deepcopy(domain);bad['edges'].pop()
        with self.assertRaises(ValueError): check_selection(self.graph,bad,selection)
        bad = deepcopy(domain);bad['aliases'].pop(next(iter(bad['aliases'])))
        with self.assertRaises(ValueError): check_selection(self.graph,bad,selection)
        bad = deepcopy(domain);node = next(iter(set(bad['nodes'])-set(bad['roots'])))
        bad['roots'][node]={'pip_count':0,'child_count':0};bad['oracle_children'][node]=[]
        with self.assertRaises(ValueError): check_selection(self.graph,bad,selection)

    def test_native_extra_and_corrupt_records_rejected(self):
        domain, selection = make_domain(self.graph,16)
        path=self.path/'mutation.agr';dump=path.with_suffix('.bin')
        write_packed(path,domain,'csr')
        raw=json.loads(subprocess.check_output([str(self.binary),str(path),str(dump)]))
        original=dump.read_bytes();self.assertTrue(original)
        for changed in (original+b'X', bytes([original[0]^1])+original[1:]):
            dump.write_bytes(changed)
            with self.assertRaises(ValueError): check_image(domain,path,dump,raw)

    def test_invalid_selection_rejected(self):
        for value in (0,-1,True,1.5):
            with self.assertRaises(ValueError): make_domain(self.graph,value)
        domain, selection=make_domain(self.graph,4);selection['sources'].pop()
        with self.assertRaises(ValueError): check_selection(self.graph,domain,selection)


if __name__=='__main__': unittest.main()
