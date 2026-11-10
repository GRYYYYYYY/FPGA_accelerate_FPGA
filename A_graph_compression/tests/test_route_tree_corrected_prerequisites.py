"""Admission regressions with synthetic receipts; these never accept actual RTL."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_vitis_kernel import digest
from route_tree_serial_prerequisites_v2 import validate_predecessors, NATIVE, CSR, COMPACT


class CorrectedPredecessors(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'results').mkdir()
        payload = self.root / 'synthetic_evidence'
        payload.write_text('unit fixture only, not actual RTL')
        self.payload = payload
        bindings = {str(payload): digest(payload)}
        for mode, name in ((None, NATIVE), (0, CSR), (1, COMPACT)):
            report = dict(status=(
                'recovered_collision_safe_native_full4tx_full44_original_C_independently_verified'
                if mode is None else
                'collision_safe_bus64_full4tx_full44_original_C_oracle_independently_verified'),
                rtl_verified=True, transactions=4, pointers=44, models=30,
                cycles=[1, 2, 3, 4], files=dict(bindings),
                snapshots=[dict(transaction=tx, bytes=946498280, sha256='0'*64) for tx in range(4)])
            if mode is not None:
                report.update(graph_mode=mode, pointer_address_offset=4096)
            path = self.root / 'results' / name
            path.write_text(json.dumps(report))
            bindings[str(path)] = digest(path)

    def alter(self, name, change):
        path = self.root / 'results' / name
        report = json.loads(path.read_text())
        change(report)
        path.write_text(json.dumps(report))

    def test_complete_synthetic_fixture_and_changed_payload(self):
        validate_predecessors(self.root)
        self.payload.write_text('tampered')
        with self.assertRaisesRegex(Exception, 'Changed predecessor evidence'):
            validate_predecessors(self.root)

    def test_missing_native(self):
        (self.root / 'results' / NATIVE).unlink()
        with self.assertRaisesRegex(Exception, 'prerequisite missing'):
            validate_predecessors(self.root)

    def test_wrong_mode(self):
        self.alter(COMPACT, lambda r: r.update(graph_mode=0))
        with self.assertRaisesRegex(Exception, 'Different bus64 mode'):
            validate_predecessors(self.root)

    def test_partial_transactions(self):
        self.alter(COMPACT, lambda r: r.update(cycles=[1, 2, 3]))
        with self.assertRaisesRegex(Exception, 'Incomplete positive actual cycles'):
            validate_predecessors(self.root)

    def test_different_native_acceptance(self):
        self.alter(COMPACT, lambda r: r['files'].update(
            {str(self.root / 'results' / NATIVE): 'f'*64}))
        with self.assertRaisesRegex(Exception, 'different earlier audit'):
            validate_predecessors(self.root)


if __name__ == '__main__':
    unittest.main()
