import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.benchmark import validate, verify_samples


class BenchmarkContractTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "configs/state_microbench.json").read_text())

    def test_real_input_rejected(self):
        self.config["dataset_kind"] = "real_benchmark"
        with self.assertRaises(ValueError):
            validate(self.config)

    def test_unknown_variant_rejected(self):
        self.config["variants"] = ["fpga_resident"]
        with self.assertRaises(ValueError):
            validate(self.config)

    def test_invalid_workload_rejected(self):
        for key, value in [("queries", 0), ("touches", -1), ("fanout", 65536), ("scattered", "false")]:
            with self.subTest(key=key):
                config = copy.deepcopy(self.config)
                config["workloads"][0][key] = value
                with self.assertRaises(ValueError):
                    validate(config)

    def test_cross_variant_mismatch_rejected(self):
        phase = {"label_checksum": "1", "share_checksum": "2", "packet_checksum": "3",
                 "packed_nodes": 4, "reset_ms": 0.1}
        row = {"workload": "fixture", "seed": 1, "variant": "cpu_serial_stamp",
               "result": {"trace_fingerprint": "5", "first": phase, "reuse": dict(phase)}}
        for field in ("label_checksum", "share_checksum", "packet_checksum", "packed_nodes"):
            with self.subTest(field=field):
                changed = copy.deepcopy(row)
                changed["result"]["reuse"][field] = 999
                with self.assertRaises(ValueError):
                    verify_samples([row, changed])

    def test_existing_result_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "result.json"
            output.write_text("preserved")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/run.py"), "benchmark",
                                     "--output", str(output)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_text(), "preserved")


if __name__ == "__main__":
    unittest.main()
