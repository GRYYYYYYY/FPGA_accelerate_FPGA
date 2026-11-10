import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('page_protocol_replay', Path(__file__).resolve().parents[1] / 'scripts/replay_page_protocol.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ProtocolReplayTests(unittest.TestCase):
    def test_real_trace_format_fixture_forces_refill_and_query_cancellation(self):
        nodes = [0, 64, 128, 192, 256, 0, 1, 64]
        raw = b''.join(struct.pack('<ii', node, 123) for node in nodes)
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / 'trace'
            rows = [{'access_byte_offset': i * len(raw), 'accesses_selected': True,
                     'truncated': False, 'access_count': len(nodes), 'label_accesses': len(nodes)} for i in range(2)]
            prefix.with_suffix('.jsonl').write_text('\n'.join(map(json.dumps, rows)) + '\n')
            prefix.with_suffix('.accesses').write_bytes(raw * 2)
            result = m.replay(prefix, lambda counts: None)
            self.assertEqual(result['queries'], 2)
            self.assertEqual(result['accesses'], 16)
            self.assertGreater(result['refills'], 0)
            self.assertGreater(result['writebacks'], 0)
            self.assertEqual(result['stale_completions_discarded'], 2)

    def test_truncated_selected_query_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / 'trace'
            prefix.with_suffix('.jsonl').write_text(json.dumps(dict(access_byte_offset=0,
                accesses_selected=True, truncated=True, access_count=1, label_accesses=2)) + '\n')
            prefix.with_suffix('.accesses').write_bytes(struct.pack('<ii', 0, 123))
            with self.assertRaises(ValueError):
                m.replay(prefix, lambda counts: None)
