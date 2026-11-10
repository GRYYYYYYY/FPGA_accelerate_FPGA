import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from analyze_real import classify, summarize_traces
from profile_real import parse_log, validate
from benchmark_paged_real import validate as validate_paged


class RealTraceTests(unittest.TestCase):
    def test_synthetic_input_rejected(self):
        with self.assertRaisesRegex(ValueError, "Only verified real"):
            validate({"dataset_kind": "synthetic_smoke"}, {})
        with self.assertRaisesRegex(ValueError, "Real dataset required"):
            validate_paged({"dataset_kind": "synthetic_state_microbenchmark"}, {})

    def test_failed_route_rejected(self):
        text = """1 overused=1 totalOveruse=1 unroutable=0 rerouted=2
ROUTE_SUMMARY iters=1 overused=1 direct=1.00 totalPushes=20 prog=0
WIRELENGTH usedNodes=5 totalLen=3
INFO: [cpp] timing: load=1 ms, route=2 ms, write .result=3 ms, total=6 ms
"""
        with self.assertRaisesRegex(ValueError, "did not converge"):
            parse_log(text)
        self.assertEqual(parse_log(text.replace("overused=1", "overused=0"))["route_ms"], 2)

    def test_exclusive_attribution(self):
        source = ["TLD(child).visited = sequence;", "auto x = queue.poll();"]
        label = {"function": "Router::push()", "file": "/build/profile.cpp", "line": 1}
        queue = {"function": "Router::DaryPQ::poll()", "file": "/build/profile.cpp", "line": 2}
        bbox = {"function": "Router::tightenBoundingBoxesCoarse()", "file": "/build/profile.cpp", "line": 2}
        self.assertEqual(classify([label], source), "label_related_source")
        self.assertEqual(classify([queue, label], source), "priority_queue")
        self.assertEqual(classify([queue, bbox], source), "bbox_preparation")

    def test_trace_bounds_continuity_and_density(self):
        def row(attempt, old, path):
            return {"attempt": attempt, "connection_index": 0, "connection_id": 17,
                    "net_index": 3, "iteration": attempt, "fanout": 1, "pops": 2,
                    "label_accesses": 3, "routed": True, "aborted": False,
                    "previous_path": old, "path": path, "accesses_selected": attempt == 2,
                    "truncated": False, "access_byte_offset": 0, "access_count": 3 if attempt == 2 else 0}
        rows = [row(1, [], [7, 0]), row(2, [7, 0], [7, 1, 0])]
        with tempfile.TemporaryDirectory() as directory:
            meta = Path(directory) / "trace.jsonl"; events = Path(directory) / "trace.accesses"
            events.write_bytes(b"".join(struct.pack("<ii", node, 10) for node in (1, 1, 513)))
            def run():
                meta.write_text("".join(json.dumps(r) + "\n" for r in rows))
                return summarize_traces(meta, events, 1024, 1, 2)
            result = run()
            self.assertEqual(result["counts"]["attempts"], 2)
            self.assertEqual(result["page_summary"][512]["page_clear_slots_per_unique_node"], 512)
            explicit = summarize_traces(meta, events, 1024, 1, 512, selected_ids={2})
            self.assertEqual(explicit["counts"]["captured_events"], 3)
            rows[1]["previous_path"] = [7, 6, 0]
            with self.assertRaisesRegex(ValueError, "Rip-up"):
                run()
            rows[1]["previous_path"] = [7, 0]
            events.write_bytes(struct.pack("<ii", 2000, 10) * 3)
            with self.assertRaisesRegex(ValueError, "Invalid trace event"):
                run()
            events.write_bytes(b"")
            with self.assertRaisesRegex(ValueError, "Truncated binary"):
                run()


if __name__ == "__main__": unittest.main()
