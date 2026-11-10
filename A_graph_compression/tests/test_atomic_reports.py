"""Downstream processes must see complete JSON, never an in-progress report."""
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from real_experiment import write_new


class AtomicReportTests(unittest.TestCase):
    def test_serialization_failure_does_not_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'report.json'
            with self.assertRaises(ValueError):write_new(path,{'invalid':float('nan')})
            self.assertFalse(path.exists())
            self.assertEqual([],list(Path(directory).iterdir()))

    def test_downstream_cannot_observe_partial_json(self):
        writing=threading.Event();resume=threading.Event();errors=[]
        class SlowRecord(dict):
            def items(self):
                writing.set()
                if not resume.wait(5):raise RuntimeError('Test writer timed out')
                return super().items()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'report.json'
            def writer():
                try:write_new(path,SlowRecord({'complete':True,'data':list(range(100))}))
                except BaseException as exc:errors.append(exc)
            thread=threading.Thread(target=writer);thread.start()
            try:
                self.assertTrue(writing.wait(5))
                self.assertFalse(path.exists())
            finally:
                resume.set();thread.join(5)
            self.assertFalse(thread.is_alive());self.assertEqual([],errors)
            self.assertTrue(json.loads(path.read_text())['complete'])
            original=path.read_bytes()
            with self.assertRaises(FileExistsError):write_new(path,{'replacement':True})
            self.assertEqual(original,path.read_bytes())


if __name__=='__main__':unittest.main()
