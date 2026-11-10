from pathlib import Path
import json
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from batch_trace_capacity_lower_bound import scan
class StreamingCapacityTests(unittest.TestCase):
    def test_large_records_across_chunks_and_eof(self):
        # A single search object exceeds the scanner's 1MiB read size.
        unknown=list(range(180000))
        search=dict(status='found',cost=3,expanded=7,blocked=0,unknown_sources=unknown,unknown_pips=[[2,3],[4,5]])
        batch=dict(status='routed',routes=[],iterations=[dict(connections=[[search]])],preparation_ms=0)
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'raw.json';p.write_text(json.dumps(dict(batches=[batch,batch]),separators=(',',':')))
            self.assertGreater(p.stat().st_size,2*1024*1024)
            r=scan(p);self.assertEqual(len(r),2)
            for b in r:
                self.assertEqual(b['searches'],1);self.assertEqual(b['unknown_nodes'],180000);self.assertEqual(b['unknown_pips'],2)
                self.assertEqual(b['search_words_lower_bound'],180092)
    def test_truncated_search_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'raw.json';p.write_text('{"iterations":[{"status":"found","unknown_sources":[1,2')
            with self.assertRaises(ValueError):scan(p)
    def test_missing_batch_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'raw.json';p.write_text('{}')
            with self.assertRaises(ValueError):scan(p)
if __name__=='__main__':unittest.main()
