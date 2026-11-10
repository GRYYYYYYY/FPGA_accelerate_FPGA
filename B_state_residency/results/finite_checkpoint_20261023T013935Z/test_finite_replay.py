import json
import struct
import tempfile
import unittest
from pathlib import Path
from scripts.replay_finite_page_values import replay

class FiniteReplayTests(unittest.TestCase):
    def test_real_format_fixture_forces_midquery_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix=Path(directory)/'trace';nodes=[i*64 for i in range(8)]*6
            prefix.with_suffix('.accesses').write_bytes(b''.join(struct.pack('<ii',n,100) for n in nodes))
            prefix.with_suffix('.jsonl').write_text(json.dumps(dict(access_byte_offset=0,accesses_selected=True,truncated=False,access_count=len(nodes),label_accesses=len(nodes)))+'\n')
            result=replay(prefix,lambda _:None,widths=dict(transaction_bits=1,generation_bits=2))
            self.assertEqual(result['accesses'],len(nodes));self.assertEqual(result['queries'],1)
            self.assertGreater(result['checkpoints'],0);self.assertGreater(result['refills'],0)
            self.assertEqual(result['fences'],result['checkpoints']+1)
            self.assertEqual(result['stale_completions_discarded']+result['boundary_probe_skips'],1)
    def test_truncated_query_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix=Path(directory)/'trace';prefix.with_suffix('.accesses').write_bytes(b'')
            prefix.with_suffix('.jsonl').write_text(json.dumps(dict(access_byte_offset=0,accesses_selected=True,truncated=True,access_count=1,label_accesses=1))+'\n')
            with self.assertRaises(ValueError):replay(prefix,lambda _:None)
if __name__=='__main__':unittest.main()
