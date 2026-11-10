"""Differential checks of native negotiated-cost search against Python."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from netlist_routing import connect
from search_experiment import IncompleteDomain


@unittest.skipUnless(shutil.which('g++'), 'g++ required')
class NativeConnectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.binary = Path(cls.tmp.name)/'connect'
        subprocess.run(['g++', '-std=c++17', '-O2', '-Wall', '-Wextra',
                        str(ROOT/'tests/native_connect_driver.cpp'), '-o', str(cls.binary)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def compare(self, *, unknown=(), protected=(), reserved=(), blocked=(),
                tree=(0,), target=5, budget=100, occupancy=None, history=None):
        # Parallel edges and an initially expensive destination exercise exact
        # edge retention, deterministic ties and improvement of queued labels.
        edges = [(0,1,0),(0,1,1),(0,2,2),(1,3,3),(2,3,4),(3,5,5),(0,4,6)]
        occupancy = occupancy or {1:3}; history = history or {}
        rows = [[] for _ in range(6)]
        for src,dst,pip in edges:
            rows[src].append(({'src':src,'dst':dst,'pip':pip}, {'attributes':{}}))
        class Provider:
            def neighbors(self, node):
                if node in unknown: raise IncompleteDomain(node)
                return rows[node]
        owners = {n:set(range(1,c+1)) for n,c in occupancy.items()}
        expected = connect(Provider(), set(tree), target, 0, set(protected), set(blocked),
                           {n:1 for n in reserved}, owners, history, 2, budget)
        expected['path'] = [e['pip'] for e in expected['path']]
        lines = [f'6 {len(edges)} {target} {budget} 2']
        lines += [f'{int(n not in unknown)} {occupancy.get(n,0)} {history.get(n,0)} '
                  f'{int(n in protected)} {int(n in reserved)}' for n in range(6)]
        lines += [f'{src} {dst} {pip} {int(pip in blocked)}' for src,dst,pip in edges]
        lines += [str(len(tree)), ' '.join(map(str,tree))]
        proc = subprocess.run([str(self.binary)], input='\n'.join(lines)+'\n',
                              text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(proc.stdout), expected)

    def test_cost_and_parallel_edges(self):
        self.compare()
        self.compare(occupancy={2:5}, history={3:2})

    def test_multisource_and_existing_target(self):
        self.compare(tree=(0,3))
        self.compare(tree=(0,5))

    def test_unknown_rows_do_not_hide_known_path(self):
        self.compare(unknown=(4,))
        self.compare(unknown=(3,4))

    def test_budget_and_no_path_are_distinct(self):
        self.compare(budget=1)
        self.compare(blocked=(5,))

    def test_protection_reservation_and_history(self):
        self.compare(protected=(1,), reserved=(4,))
        self.compare(blocked=(0,1), history={2:9})


if __name__ == '__main__':
    unittest.main()
