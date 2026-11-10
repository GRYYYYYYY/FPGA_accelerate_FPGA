"""Ownership, multi-terminal trees, incomplete domains and negotiated congestion."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]
from netlist import ownership, read_snapshot, routing_queries
from netlist_routing import route_batch, validate_routes
from search_experiment import ExplicitCSR


def fixture(arcs, terminals, unknown=()):
    nodes = {n for arc in arcs for n in arc}
    graph = {"nodes": dict.fromkeys(nodes, {}), "roots": dict.fromkeys(nodes-set(unknown), {}), "edges": [], "pips": {}}
    for i, (src, dst) in enumerate(arcs):
        pip = f"P{i:03d}"
        graph["edges"].append({"src": src, "dst": dst, "pip": pip, "direction": "forward", "src_wire": src, "dst_wire": dst})
        graph["pips"][pip] = {"attributes": {"IS_EXCLUDED_PIP": "0", "IS_TEST_PIP": "0"}}
    snapshot, queries = {"nets": {}}, []
    for name, (source, sinks) in terminals.items():
        snapshot["nets"][name] = {"nodes": [source, *sinks], "pips": [], "site_pins": []}
        queries.append({"net": name, "source": source, "sinks": sinks})
    return graph, snapshot, queries


class NetlistRoutingTests(unittest.TestCase):
    def run_case(self, arcs, terminals, **kwargs):
        graph, snapshot, queries = fixture(arcs, terminals)
        result = route_batch(ExplicitCSR(graph), snapshot, queries, **kwargs)
        valid = validate_routes(graph, snapshot, queries, result)
        return graph, snapshot, queries, result, valid

    def test_multi_sink_shared_trunk_is_owned_once(self):
        _, _, _, result, valid = self.run_case([("a", "x"), ("x", "b"), ("x", "c")], {"n": ("a", ["b", "c"])})
        self.assertEqual("routed", result["status"])
        self.assertEqual(3, valid["total_pips"])
        self.assertEqual(["a", "b", "c", "x"], result["routes"]["n"]["nodes"])

    def test_negotiation_rips_up_conflict_and_uses_alternate(self):
        arcs = [("a", "x"), ("x", "ta"), ("a", "y"), ("y", "z"), ("z", "ta"), ("b", "x"), ("x", "tb")]
        _, _, _, result, valid = self.run_case(arcs, {"na": ("a", ["ta"]), "nb": ("b", ["tb"])})
        self.assertEqual("routed", result["status"])
        self.assertEqual(2, len(result["iterations"]))
        self.assertIn("x", result["iterations"][0]["conflicts"])
        self.assertNotIn("x", result["routes"]["na"]["nodes"])
        self.assertTrue(valid["all_nets_routed_without_conflicts"])

    def test_unsatisfiable_congestion_is_not_success(self):
        _, _, _, result, valid = self.run_case([("a", "x"), ("x", "ta"), ("b", "x"), ("x", "tb")],
                                              {"na": ("a", ["ta"]), "nb": ("b", ["tb"])}, max_iterations=3)
        self.assertEqual("incomplete", result["status"])
        self.assertFalse(valid["all_nets_routed_without_conflicts"])

    def test_protected_owner_cannot_be_evicted(self):
        graph, snapshot, queries = fixture([("a", "x"), ("x", "b"), ("a", "y"), ("y", "b")], {"n": ("a", ["b"])})
        snapshot["nets"]["clock"] = {"nodes": ["x"], "pips": [], "site_pins": []}
        result = route_batch(ExplicitCSR(graph), snapshot, queries)
        self.assertNotIn("x", result["routes"]["n"]["nodes"])
        self.assertTrue(validate_routes(graph, snapshot, queries, result)["all_nets_routed_without_conflicts"])

    def test_unknown_branch_does_not_hide_known_route(self):
        graph, snapshot, queries = fixture([("a", "x"), ("a", "y"), ("y", "z")], {"n": ("a", ["z"])}, unknown=["x"])
        result = route_batch(ExplicitCSR(graph), snapshot, queries)
        self.assertEqual("routed", result["status"])
        self.assertEqual(["x"], result["iterations"][0]["outcomes"][0]["connections"][0]["unknown_sources"])
        validate_routes(graph, snapshot, queries, result)

    def test_unknown_budget_and_disconnection_remain_distinct(self):
        graph, snapshot, queries = fixture([("a", "x"), ("x", "z")], {"n": ("a", ["z"])}, unknown=["x"])
        result = route_batch(ExplicitCSR(graph), snapshot, queries)
        self.assertEqual("incomplete_domain", result["iterations"][0]["outcomes"][0]["connections"][0]["status"])
        result = route_batch(ExplicitCSR(graph), snapshot, queries, max_expansions=1)
        self.assertEqual("budget_exhausted", result["iterations"][0]["outcomes"][0]["connections"][0]["status"])
        graph["roots"]["x"] = {}
        graph["edges"].pop()
        result = route_batch(ExplicitCSR(graph), snapshot, queries)
        self.assertEqual("no_path", result["iterations"][0]["outcomes"][0]["connections"][0]["status"])

    def test_parallel_pips_and_excluded_resource(self):
        graph, snapshot, queries = fixture([("a", "b"), ("a", "b")], {"n": ("a", ["b"])})
        graph["pips"]["P000"]["attributes"]["IS_EXCLUDED_PIP"] = "1"
        result = route_batch(ExplicitCSR(graph), snapshot, queries)
        self.assertEqual("P001", result["routes"]["n"]["edges"][0]["pip"])
        validate_routes(graph, snapshot, queries, result)

    def test_independent_verifier_rejects_corrupt_route(self):
        graph, snapshot, queries, result, _ = self.run_case([("a", "x"), ("x", "b")], {"n": ("a", ["b"])})
        altered = deepcopy(result)
        altered["routes"]["n"]["edges"][0]["direction"] = "reverse"
        with self.assertRaisesRegex(ValueError, "directed PIP"):
            validate_routes(graph, snapshot, queries, altered)
        altered = deepcopy(result)
        altered["routes"]["n"]["nodes"].append("unreachable")
        with self.assertRaisesRegex(ValueError, "Unreachable"):
            validate_routes(graph, snapshot, queries, altered)

    def test_incomplete_other_net_still_reserves_its_sink(self):
        graph, snapshot, queries = fixture([('a','x'),('x','ta'),('b','tb')],
                                           {'na':('a',['ta']), 'nb':('b',['x'])})
        # An individually reachable na tree must not consume nb's reserved sink,
        # even when nb is incomplete and therefore has no dynamic owner at x.
        result = {'status':'incomplete','routes':{
            'na':{'source':'a','sinks':['ta'],'nodes':['a','x','ta'],
                  'edges':graph['edges'][:2],'complete':True},
            'nb':{'source':'b','sinks':['x'],'nodes':['b'],'edges':[],'complete':False}}}
        with self.assertRaisesRegex(ValueError,'reserved terminal'):
            validate_routes(graph,snapshot,queries,result)

    def test_real_snapshot_hierarchy_and_shared_constants(self):
        snapshot = read_snapshot(ROOT / "data/netlist/routeracc_cost_u280_20261022_v1/snapshot.tsv")
        queries = routing_queries(snapshot)
        self.assertEqual(1062, len(queries))
        self.assertEqual(4209, sum(len(q["sinks"]) for q in queries))
        self.assertEqual(1833, len(snapshot["cells"]))
        nodes, _ = ownership(snapshot)
        for owners in nodes.values():
            if len(owners) > 1:
                self.assertTrue({snapshot["nets"][n]["type"] for n in owners} in [{"GROUND"}, {"POWER"}])
        protected, _ = ownership(snapshot, [q["net"] for q in queries])
        self.assertTrue(all(q["source"] not in protected and not(set(q["sinks"]) & set(protected)) for q in queries))


if __name__ == "__main__":
    unittest.main()
