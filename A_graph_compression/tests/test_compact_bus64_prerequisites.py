import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from compact_bus64_prerequisites_v1 import EXPECTED, validate_prerequisites
from check_vitis_kernel import digest


class PrerequisiteTests(unittest.TestCase):
    def fixture(self, root):
        source = root / 'closed.log'
        source.write_text('closed original evidence')
        for name, status in EXPECTED.items():
            (root / name).write_text(json.dumps(dict(
                status=status, files={str(source): digest(source)})))
        return source

    def test_accepts_all_current_bound_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.fixture(root)
            bindings = validate_prerequisites(root)
            self.assertEqual(len(bindings), 4)
            self.assertEqual(bindings[str(source)], digest(source))

    def test_filename_and_failed_status_are_insufficient(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            path = root / next(iter(EXPECTED))
            data = json.loads(path.read_text())
            data['status'] = 'failed'
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                validate_prerequisites(root)

    def test_modified_closed_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root).write_text('changed after acceptance')
            with self.assertRaises(ValueError):
                validate_prerequisites(root)


if __name__ == '__main__':
    unittest.main()
