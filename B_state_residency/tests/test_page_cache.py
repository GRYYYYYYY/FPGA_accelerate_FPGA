import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('page_cache_model', Path(__file__).resolve().parents[1] / 'scripts/analyze_page_cache.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PageCacheTests(unittest.TestCase):
    def test_reentry_requires_refill_not_reinitialization(self):
        result = m.simulate([0, 64, 0], 6, 1)
        self.assertEqual((result['first_page_touches'], result['refills'], result['evictions']), (2, 1, 2))

    def test_lru_promotes_hit(self):
        result = m.simulate([0, 64, 0, 128, 0], 6, 2)
        self.assertEqual((result['hits'], result['refills'], result['evictions']), (2, 0, 1))

    def test_page_aliasing_and_query_independence(self):
        self.assertEqual(m.simulate([0, 63, 0], 6, 1)['hits'], 2)
        self.assertEqual(m.simulate([0], 6, 1)['first_page_touches'], 1)
        self.assertEqual(m.simulate([0], 6, 1)['first_page_touches'], 1)

    def test_invalid_capacity(self):
        with self.assertRaises(ValueError):
            m.simulate([0], 6, 0)
