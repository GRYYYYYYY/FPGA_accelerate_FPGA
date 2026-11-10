"""Real SLR split, frozen templates, closure completeness and common-search regressions."""
from collections import deque
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "adapters"), str(ROOT / "scripts")]
from canonical_graph import compare
from heldout import encode_frozen, fit_bank, object_digest, select_sources, source_slr
from import_vivado import read_export
from region_experiment import closure_check
from search_experiment import ExplicitCSR, LazyTemplates, make_queries, search, validate_path
from template_codec import DirectDecoder, PreparedDecoder


class RegionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = json.loads((ROOT / "configs/region_query.json").read_text())
        raw = read_export(ROOT / cls.cfg["training"]["path"])
        cls.train = select_sources(raw, [r for r in raw["roots"] if source_slr(raw, r) == 0])
        cls.bank = fit_bank(cls.train)
        cls.held = read_export(ROOT / cls.cfg["heldout"]["path"])
        cls.domain = read_export(ROOT / cls.cfg["search_domain"]["path"])
        cls.compact = encode_frozen(cls.domain, cls.bank)
        cls.queries = make_queries(cls.domain, cls.cfg["search_domain"]["seeds"], 4, 10000)

    def test_real_source_slr_split(self):
        self.assertEqual({0}, {source_slr(self.train, r) for r in self.train["roots"]})
        self.assertEqual({1, 2, 3}, {source_slr(self.held, r) for r in self.held["roots"]})
        self.assertFalse(set(self.train["roots"]) & set(self.held["roots"]))

    def test_frozen_bank_does_not_learn_evaluation_changes(self):
        before = object_digest(self.bank)
        changed = deepcopy(self.domain)
        pip = next(iter(changed["pips"]))
        changed["pips"][pip]["attributes"]["SPEED_INDEX"] = "-1234"
        result = encode_frozen(changed, self.bank)
        self.assertEqual(before, object_digest(self.bank))
        self.assertEqual(result["templates"], self.bank["templates"])
        self.assertTrue(compare(changed, DirectDecoder(result).materialize())["equal"])
        self.assertNotEqual(result["instances"], self.compact["instances"])

    def test_reject_source_leakage(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            encode_frozen(self.train, self.bank)

    def test_heldout_exact_with_fixed_templates(self):
        compact = encode_frozen(self.held, self.bank)
        self.assertTrue(compare(self.held, DirectDecoder(compact).materialize())["equal"])
        self.assertEqual(compact["templates"], self.bank["templates"])

    def test_unseen_family_fallback_preserves_edges(self):
        self.assertGreater(sum(i["template"] is None for i in self.compact["instances"].values()), 0)
        self.assertTrue(compare(self.domain, DirectDecoder(self.compact).materialize())["equal"])
        self.assertEqual(self.compact["templates"], self.bank["templates"])

    def test_corrupt_fallback_is_detected(self):
        compact = deepcopy(self.compact)
        instance = next(i for i in compact["instances"].values() if i["template"] is None and i["fallback_rules"])
        instance["fallback_rules"].pop()
        with self.assertRaises(ValueError):
            compare(self.domain, DirectDecoder(compact).materialize())

    def test_full_depth_contract(self):
        outcome = closure_check(self.domain, self.cfg["search_domain"])
        self.assertTrue(outcome["passed"])
        self.assertGreater(outcome["unexpanded_boundary_nodes"], 0)

    def test_missing_preboundary_row_not_certified(self):
        graph = deepcopy(self.domain)
        del graph["roots"][self.cfg["search_domain"]["seeds"][0]]
        with self.assertRaisesRegex(ValueError, "Missing adjacency"):
            closure_check(graph, self.cfg["search_domain"])

    def test_export_budget_hit_not_certified(self):
        graph = deepcopy(self.domain)
        graph["metadata"]["bfs_budget_hit"] = "1"
        with self.assertRaisesRegex(ValueError, "budget"):
            closure_check(graph, self.cfg["search_domain"])

    def test_same_trace_paths_and_termination_status(self):
        csr, lazy = ExplicitCSR(self.domain), LazyTemplates(self.compact)
        statuses = set()
        for query in self.queries:
            with self.subTest(query["id"]):
                args = query["source"], query["target"], query["max_expansions"]
                a, b = search(csr, *args, trace=True), search(lazy, *args, trace=True)
                self.assertEqual(a, b)
                self.assertTrue(validate_path(self.domain, query, a))
                statuses.add(a["status"])
                if query["kind"] == "reachable_by_exported_edges":
                    self.assertEqual("found", a["status"])
                    self.assertEqual(query["discovery_distance"], a["distance"])
        self.assertEqual({"found", "budget_exhausted", "incomplete_domain", "no_path"}, statuses)

    def test_distances_match_independent_vivado_node_oracle(self):
        provider = LazyTemplates(self.compact)
        for seed in self.cfg["search_domain"]["seeds"]:
            levels, frontier = {seed: 0}, deque([seed])
            while frontier:
                n = frontier.popleft()
                if levels[n] == 4:
                    continue
                for child in self.domain["oracle_children"][n]:
                    if child not in levels:
                        levels[child] = levels[n] + 1
                        frontier.append(child)
            for q in self.queries:
                if q["source"] == seed and q["kind"] == "reachable_by_exported_edges":
                    result = search(provider, seed, q["target"], q["max_expansions"])
                    self.assertEqual(levels[q["target"]], result["distance"])

    def test_frontier_target_does_not_require_its_adjacency(self):
        query = next(q for q in self.queries if q.get("discovery_distance") == 4)
        self.assertNotIn(query["target"], self.domain["roots"])
        result = search(LazyTemplates(self.compact), query["source"], query["target"], 10000)
        self.assertEqual("found", result["status"])
        self.assertEqual(4, result["distance"])

    def test_prepared_rules_roundtrip_and_input_immutability(self):
        before = object_digest(self.compact)
        decoder = PreparedDecoder(self.compact)
        self.assertTrue(compare(self.domain, decoder.materialize())["equal"])
        self.assertEqual(before, object_digest(self.compact))
        instance = next(i for i in self.compact["instances"].values() if i["template"] is None and i["fallback_rules"])
        root = next(r for r, i in self.compact["instances"].items() if i is instance)
        self.assertIs(instance["fallback_rules"][0], next(decoder.rules(root)))

    def test_prepared_search_trace_matches_csr(self):
        csr = ExplicitCSR(self.domain)
        prepared = LazyTemplates(self.compact, PreparedDecoder)
        for q in self.queries:
            with self.subTest(q["id"]):
                args = q["source"], q["target"], q["max_expansions"]
                self.assertEqual(search(csr, *args, trace=True), search(prepared, *args, trace=True))

    def test_prepared_exception_removal_is_strict(self):
        compact = deepcopy(self.compact)
        instance = next(i for i in compact["instances"].values() if i["template"] is not None)
        instance["remove"].append({"nonexistent": True})
        with self.assertRaisesRegex(ValueError, "absent rule"):
            PreparedDecoder(compact)


if __name__ == "__main__":
    unittest.main()
