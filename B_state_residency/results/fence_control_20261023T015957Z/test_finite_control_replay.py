import json
import struct
import tempfile
import unittest
from pathlib import Path
from scripts.replay_finite_page_values_fast import replay as reference
from scripts.replay_finite_control import replay

class ControlReplayTests(unittest.TestCase):
    def test_control_packets_preserve_page_events_and_values(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix=Path(directory)/'trace';nodes=[i*64 for i in range(8)]*6
            prefix.with_suffix('.accesses').write_bytes(b''.join(struct.pack('<ii',n,100) for n in nodes))
            prefix.with_suffix('.jsonl').write_text(json.dumps(dict(access_byte_offset=0,accesses_selected=True,truncated=False,access_count=len(nodes),label_accesses=len(nodes)))+'\n')
            widths=dict(transaction_bits=1,generation_bits=2)
            expected=reference(prefix,lambda _:None,widths=widths);actual=replay(prefix,lambda _:None,widths=widths)
            self.assertEqual(expected,{k:actual[k] for k in expected})
            self.assertGreater(actual['control_tag_wraps'],0)
            self.assertEqual(actual['control_requests'],2*actual['fences'])
            self.assertEqual(actual['control_ack_packets'],3*actual['fences'])
            self.assertEqual(actual['control_duplicate_acks'],2*actual['fences'])
if __name__=='__main__':unittest.main()
