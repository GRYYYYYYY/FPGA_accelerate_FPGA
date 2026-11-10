"""Semantic checks for reference scaffolds, not performance benchmarks."""
import copy
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_shared/python"))
from research_common import shortest_path, verify_path

CATALOG = json.loads((ROOT / "_shared/project_catalog.json").read_text())
DIRECTORIES = {p["id"]: ROOT / p["folder"] for p in CATALOG}


def fixture(project):
    return json.loads((DIRECTORIES[project] / "data/toy.json").read_text())


def run_reference(project, case=None):
    path = DIRECTORIES[project] / "src/reference.py"
    spec = importlib.util.spec_from_file_location(f"test_reference_{project}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run(case if case is not None else fixture(project))


class ReferenceSemantics(unittest.TestCase):
    def test_all_fixtures_have_passing_nonempty_checks(self):
        for project in DIRECTORIES:
            with self.subTest(project=project):
                checks = run_reference(project)["checks"]
                self.assertTrue(checks)
                self.assertTrue(all(value is True for value in checks.values()))

    def test_template_attribute_corruption_is_detected(self):
        case = fixture("A")
        case["compact"]["add_edges"][0]["cost"] = 99
        self.assertFalse(run_reference("A", case)["checks"]["canonical_edges_and_attributes_equal"])

    def test_epoch_wrap_does_not_resurrect_old_label(self):
        output = run_reference("B")
        self.assertEqual(output["observations"]["epoch_wraps"], 1)
        reads = output["outputs"]["reads"]
        self.assertEqual([r["value"] for r in reads if r["search"] == 4], [None, None, 4])

    def test_state_access_requires_search_context(self):
        case = fixture("B")
        case["operations"] = [{"op": "read", "node": 1}]
        with self.assertRaises(ValueError):
            run_reference("B", case)

    def test_scheduler_rejects_cycles(self):
        case = fixture("C")
        case["tasks"][0]["predecessors"] = ["c"]
        with self.assertRaises(ValueError):
            run_reference("C", case)

    def test_scheduler_rejects_oversized_working_set(self):
        case = fixture("C")
        case["tasks"][0]["state_bytes"] = 999999
        with self.assertRaises(ValueError):
            run_reference("C", case)

    def test_scheduler_tracks_shared_resource_not_geometry(self):
        rows = {r["task"]: r for r in run_reference("C")["outputs"]["schedule"]}
        self.assertLessEqual(rows["b"]["end_units"], rows["d"]["start_units"])
        self.assertEqual(rows["a"]["start_units"], rows["b"]["start_units"])

    def test_parallel_edges_preserve_selected_edge_identity(self):
        route = run_reference("D")["outputs"]["route"]
        self.assertEqual(route["edges"], ["e01fast", "e13", "e34"])
        self.assertEqual(route["cost"], 3)

    def test_placement_rejects_type_fixed_and_cascade_violations(self):
        rows = {r["id"]: r for r in run_reference("E")["outputs"]["candidates"]}
        self.assertIn("resource_type:a", rows["wrong_type"]["violations"])
        self.assertIn("fixed_cell:b", rows["fixed_move"]["violations"])
        self.assertIn("cascade:d:e", rows["break_cascade"]["violations"])

    def test_local_budget_exhaustion_is_unknown_not_global_failure(self):
        rows = {r["id"]: r for r in run_reference("F")["outputs"]["candidates"]}
        self.assertEqual(rows["tiny_budget"]["local_status"], "unknown_budget_exhausted")
        self.assertTrue(all(r["global_routable"] is None for r in rows.values()))

    def test_vertical_portal_selected_using_complete_path_cost(self):
        output = run_reference("G")["outputs"]
        self.assertEqual(output["best"]["portal"], "p24")
        self.assertEqual(output["best"]["route"]["cost"], 4)
        self.assertEqual(output["unrestricted_reference"]["cost"], 4)

    def test_nonvertical_portal_is_rejected(self):
        case = fixture("G")
        case["portal_edge_ids"] = ["h01"]
        with self.assertRaises(ValueError):
            run_reference("G", case)


class GraphReferenceChecks(unittest.TestCase):
    def test_negative_cost_rejected(self):
        graph = fixture("D")["graph"]
        graph["edges"][0]["cost"] = -1
        with self.assertRaises(ValueError):
            shortest_path(graph, 0, [4])

    def test_source_target_identity_and_unreachable_target(self):
        graph = fixture("D")["graph"]
        self.assertEqual(shortest_path(graph, 0, [0])["cost"], 0)
        self.assertEqual(shortest_path(graph, 4, [0])["status"], "no_path")

    def test_against_independent_relaxation_reference(self):
        rng = random.Random(20261022)
        for sample in range(40):
            n = 6
            edges = []
            for src in range(n):
                for dst in range(n):
                    if src != dst and rng.random() < .3:
                        edges.append({"id": f"e{len(edges)}", "src": src, "dst": dst,
                                      "cost": rng.randint(0, 7)})
            graph = {"nodes": [{"id": i} for i in range(n)], "edges": edges}
            expected = [float("inf")] * n
            expected[0] = 0
            for _ in range(n - 1):
                for edge in edges:
                    expected[edge["dst"]] = min(expected[edge["dst"]], expected[edge["src"]] + edge["cost"])
            result = shortest_path(graph, 0, [n - 1])
            with self.subTest(sample=sample):
                if expected[-1] == float("inf"):
                    self.assertEqual(result["status"], "no_path")
                else:
                    self.assertEqual(result["cost"], expected[-1])
                    self.assertTrue(verify_path(graph, result, 0, [n - 1]))


class CommandLineChecks(unittest.TestCase):
    def invoke(self, *args):
        return subprocess.run([sys.executable, str(DIRECTORIES["D"] / "scripts/run.py"), *args],
                              cwd="/tmp", capture_output=True, text=True)

    def test_absolute_entrypoint_and_result_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "result.json"
            result = self.invoke("smoke", "--output", str(target))
            self.assertEqual(result.returncode, 0, result.stderr)
            record = json.loads(target.read_text())
            self.assertEqual(record["execution_kind"], "synthetic_smoke")
            self.assertEqual(len(record["input_sha256"]), 64)
            self.assertTrue(all(v is None for v in record["measurements"].values()))
            repeated = self.invoke("smoke", "--output", str(target))
            self.assertNotEqual(repeated.returncode, 0)

    def test_planned_variant_does_not_silently_run_reference(self):
        result = self.invoke("smoke", "--variant", "fpga_exact_queue")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Only --variant reference", result.stderr)

    def test_real_data_cannot_be_mislabeled_as_toy(self):
        case = fixture("D")
        case["dataset_kind"] = "real"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            source.write_text(json.dumps(case))
            result = self.invoke("smoke", "--input", str(source))
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
