"""Guard the semantic risks of native CHANZ import and paired reproduction."""
from pathlib import Path
import sqlite3
import tempfile
import unittest

from adapters.common import sha256, verified_file
from adapters.vpr_baseline import parse_metrics, route_fingerprint
from adapters.vpr_rrg import check_route_projection, export_graph
from adapters.route_audit import audit


GRAPH = '''<rr_graph tool_name="vpr" tool_version="fixture">
<switches>
<switch id="0" type="mux" name="delayless"><timing/></switch>
<switch id="8" type="mux" name="via"><timing Tdel="1.42e-10" R="0"/></switch>
</switches><rr_nodes>
<node id="10" type="SOURCE" capacity="1"><loc xlow="1" xhigh="1" ylow="1" yhigh="1" layer_low="0" layer_high="0" ptc="0"/><timing R="0" C="0"/></node>
<node id="42" type="CHANZ" direction="BI_DIR" capacity="1"><loc xlow="1" xhigh="1" ylow="1" yhigh="1" layer_low="0" layer_high="1" ptc="0"/><timing R="0" C="0"/><segment segment_id="0"/></node>
<node id="99" type="SINK" capacity="1"><loc xlow="1" xhigh="1" ylow="1" yhigh="1" layer_low="1" layer_high="1" ptc="0"/><timing R="0" C="0"/></node>
</rr_nodes><rr_edges>
<edge src_node="10" sink_node="42" switch_id="8"/>
<edge src_node="10" sink_node="42" switch_id="0"/>
<edge src_node="42" sink_node="99" switch_id="0"/>
<edge src_node="10" sink_node="99" switch_id="8"/>
</rr_edges></rr_graph>'''

TRACE = '''Net 0 (example)
Node: 10 SOURCE (1,1,0) Switch: 8
Node: 42 CHANZ (1,1,0) to (1,1,1) Switch: 0
Node: 99 SINK (1,1,1) Switch: -1 Net_pin_index: 1
'''


class NativeGraphTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.xml = self.root / "graph.xml"
        self.xml.write_text(GRAPH)
        self.route = self.root / "trace.route"
        self.route.write_text(TRACE)

    def export(self):
        return export_graph(self.xml, self.root / "export")

    def test_ids_parallel_edges_capacity_and_timing(self):
        result = self.export()
        with sqlite3.connect(result["database"]["path"]) as db:
            self.assertEqual(db.execute("SELECT id,resource_id,capacity,layer_low,layer_high FROM portals").fetchall(), [(42, "chanz:42", 1, 0, 1)])
            self.assertEqual(db.execute("SELECT id,switch_id FROM edges WHERE src=10 AND dst=42 ORDER BY id").fetchall(), [(0, 8), (1, 0)])
            self.assertIsNone(db.execute("SELECT tdel_seconds FROM switches WHERE id=0").fetchone()[0])
            self.assertAlmostEqual(db.execute("SELECT tdel_seconds*1e9 FROM switches WHERE id=8").fetchone()[0], .142)
            self.assertEqual(db.execute("SELECT count(*) FROM vertical_edges").fetchone()[0], 4)
            self.assertEqual(result["direct_layer_change_edges"], 1)
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.assertTrue(check_route_projection(result["database"]["path"], self.route)["passed"])
        evidence = audit(self.xml, self.route)
        self.assertTrue(evidence["passed"])
        self.assertEqual(evidence["route"]["cross_layer_sink_connections"], 1)

    def test_direction_and_switch_identity_are_not_discarded(self):
        result = self.export()
        for changed in (TRACE.replace("Switch: 8", "Switch: 7"),
                        TRACE.replace("Node: 10 SOURCE (1,1,0) Switch: 8\n", "").replace("Node: 99 SINK (1,1,1)", "Node: 10 SOURCE (1,1,0)")):
            self.route.write_text(changed)
            with self.assertRaises(ValueError):
                check_route_projection(result["database"]["path"], self.route)

    def test_invalid_graphs_fail_without_complete_manifest(self):
        for i, changed in enumerate((GRAPH.replace('sink_node="99"', 'sink_node="777"'),
                                      GRAPH.replace('Tdel="1.42e-10"', 'Tdel="nan"'),
                                      GRAPH.replace('capacity="1"', 'capacity="-1"'),
                                      GRAPH.replace('id="42" type="CHANZ"', 'id="10" type="CHANZ"'))):
            self.xml.write_text(changed)
            destination = self.root / str(i)
            with self.assertRaises((ValueError, sqlite3.IntegrityError)):
                export_graph(self.xml, destination)
            self.assertFalse((destination / "summary.json").exists())
            self.assertTrue((destination / "failure.json").exists())

    def test_hash_drift_and_overwrite_rejected(self):
        record = {"path": str(self.xml), "sha256": sha256(self.xml)}
        self.export()
        with self.assertRaises(FileExistsError):
            self.export()
        self.xml.write_text(GRAPH + "\n")
        with self.assertRaises(ValueError):
            verified_file(record)
        with self.assertRaises(ValueError):
            export_graph(self.xml, self.root / "mismatch", record["sha256"])

    def test_audit_rejects_shared_capacity_overuse_and_broken_branch(self):
        self.route.write_text(TRACE + TRACE.replace("Net 0", "Net 1"))
        self.assertFalse(audit(self.xml, self.route)["passed"])
        self.route.write_text(TRACE + 'Node: 99 SINK (1,1,1) Switch: -1 Net_pin_index: 2\n')
        self.assertFalse(audit(self.xml, self.route)["passed"])

    def test_route_comparison_ignores_headers_only(self):
        first = route_fingerprint(self.route)
        self.route.write_text("Placement file: elsewhere\n" + TRACE)
        self.assertEqual(first, route_fingerprint(self.route))
        self.route.write_text(TRACE.replace("Switch: 8", "Switch: 0"))
        self.assertNotEqual(first, route_fingerprint(self.route))

    def test_missing_metrics_remain_unknown(self):
        metrics = parse_metrics("Routing failed")
        self.assertIsNone(metrics["routing_seconds"])
        self.assertIsNone(metrics["critical_path_delay_ns"])
        self.assertFalse(metrics["routing_success"])


if __name__ == "__main__":
    unittest.main()
