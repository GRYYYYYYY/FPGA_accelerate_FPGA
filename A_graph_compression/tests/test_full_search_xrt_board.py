"""Synthetic rejection tests only; never produce hardware experiment evidence."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import search_xrt_board_link as link
from run_complete_search_xrt_router import BACKEND, validate_result


def fixture():
    reference = dict(status='routed', routes=[{'net': n} for n in range(1062)], iterations=[])
    batch = {**copy.deepcopy(reference), 'preparation_ms': 1, 'route_ms': 10, 'peak_kib': 1,
             'logical_bytes': 0, 'cache_hits': 0, 'cache_misses': 0, 'backend': BACKEND,
             'xrt_calls': 1, 'xrt_h2d_bytes': 804, 'xrt_d2h_bytes': 664,
             'xrt_h2d_ms': 1, 'xrt_d2h_ms': 1, 'xrt_kernel_wall_ms': 1}
    expected = dict(controller_counters=[[i, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1] for i in (0, 1)],
                    snapshot_counters=[[i, 1, 0, 0, 0, 0, 0, 0, 0, 0] for i in (0, 1)],
                    kernel_counters=[[i, 1, 1, 100, 100, 100, 2] for i in (0, 1)])
    log = ''.join(name + ' ' + ' '.join(map(str, row)) + '\n' for key, name in [
        ('controller_counters', 'CONTROLLER_COUNTERS'), ('snapshot_counters', 'SNAPSHOT_COUNTERS'),
        ('kernel_counters', 'KERNEL_COUNTERS')] for row in expected[key])
    raw = dict(execution='kernel', batches=[copy.deepcopy(batch), copy.deepcopy(batch)], materialization_ms=0, export_ms=[1, 1])
    transport = dict(backend=BACKEND, complete=True, mode='csr', layout='hbm_shared', device_bdf='synthetic',
                     device_name='synthetic', xclbin_uuid='synthetic', completed=2, attempts=2, setup_h2d_bytes=1144,
                     h2d_bytes=1608, d2h_bytes=1328, h2d_ms=2, d2h_ms=2, kernel_wall_ms=2,
                     open_ms=1, setup_ms=1, argument_groups=[-1 if i in (2, 5) else 40 for i in range(15)])
    return raw, transport, reference, expected, log


class BoardEvidenceTests(unittest.TestCase):
    def test_semantics_counters_and_transport_corruptions(self):
        raw, transport, reference, expected, log = fixture()
        self.assertEqual(validate_result(raw, transport, reference, expected, log, 'csr', 'hbm_shared', 1000)['calls'], 2)
        mutations = [
            lambda r,t:r['batches'][0]['routes'][0].update(net=99999),
            lambda r,t:r['batches'].pop(),
            lambda r,t:r['batches'][0].update(backend='cpu'),
            lambda r,t:r['batches'][0].update(cache_hits=1),
            lambda r,t:r['batches'][0].update(xrt_calls=0),
            lambda r,t:r['batches'][0].update(xrt_h2d_bytes=800),
            lambda r,t:r['batches'][0].update(xrt_d2h_bytes=663),
            lambda r,t:r['batches'][0].update(xrt_kernel_wall_ms=100),
            lambda r,t:r['batches'][0].update(xrt_h2d_ms=float('nan')),
            lambda r,t:t.update(complete=False),
            lambda r,t:t.update(mode='compact'),
            lambda r,t:t.update(layout='hbm_split'),
            lambda r,t:t.update(attempts=3),
            lambda r,t:t.update(setup_h2d_bytes=1),
            lambda r,t:t.update(d2h_bytes=1329),
            lambda r,t:t.update(device_bdf=''),
            lambda r,t:t['argument_groups'].__setitem__(2,0),
            lambda r,t:t['argument_groups'].__setitem__(0,True),
        ]
        for i, mutate in enumerate(mutations):
            raw, transport, reference, expected, log = fixture();mutate(raw, transport)
            with self.subTest(mutation=i), self.assertRaises(ValueError):
                validate_result(raw, transport, reference, expected, log, 'csr', 'hbm_shared', 1000)
        raw, transport, reference, expected, log = fixture()
        with self.assertRaises(ValueError):
            validate_result(raw, transport, reference, expected, log.replace('KERNEL_COUNTERS 1', 'KERNEL_COUNTERS 0'), 'csr', 'hbm_shared', 1000)

    def test_archive_binds_rtl_rom_and_abi(self):
        xml = link.ROOT / 'build/search_kernel_hls_20261024_v3/csr/kernel.xml'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);rtl = root / 'rtl';rtl.mkdir()
            (rtl / 'search_kernel_top.v').write_text('// synthetic CSR RTL\n')
            (rtl / 'widths.dat').write_text('0001\n')
            bound = {str(p): link.digest(p) for p in rtl.iterdir()}
            good = {'ip/hdl/verilog/search_kernel_top.v': b'// synthetic CSR RTL\n',
                    'ip/hdl/verilog/widths.dat': b'0001\n', 'kernel.xml': xml.read_bytes()}
            cases = [good, {**good, 'ip/hdl/verilog/search_kernel_top.v': b'// synthetic compact RTL\n'},
                     {**good, 'ip/hdl/verilog/widths.dat': b'0002\n'},
                     {k:v for k,v in good.items() if not k.endswith('.dat')},
                     {**good, 'other/hdl/verilog/search_kernel_top.v': good['ip/hdl/verilog/search_kernel_top.v']},
                     {**good, 'kernel.xml': good['kernel.xml'].replace(b'name="image"', b'name="different"')}]
            for index, entries in enumerate(cases):
                path = root / f'{index}.xo'
                with zipfile.ZipFile(path, 'w') as archive:
                    for name, data in entries.items():archive.writestr(name, data)
                if index == 0:
                    self.assertEqual(link.archive_binding(path, rtl, xml, bound), bound)
                else:
                    with self.subTest(index=index), self.assertRaises(ValueError):link.archive_binding(path, rtl, xml, bound)
            with self.assertRaises(ValueError):link.archive_binding(root / '0.xo', rtl, xml, {})

    def test_pending_rtl_gate_and_wrong_link_kind(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.dict(link.GATES, {root / 'missing.json': 'unavailable'}, clear=True), self.assertRaises(ValueError):
                link.gates()
            (root / 'plan.json').write_text(json.dumps({'kind': 'old_decoder_link'}))
            (root / 'receipt.json').write_text('{}')
            with self.assertRaises(ValueError):link.verify_link(root)


if __name__ == '__main__':
    unittest.main()
