"""Shared cache must preserve ordering, unknown boundaries and eviction behavior."""
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from row_cache import RowCache
from search_experiment import IncompleteDomain


class Provider:
    def __init__(self):self.calls=[]
    def neighbors(self,node):
        self.calls.append(node)
        if node=='unknown':raise IncompleteDomain(node)
        return [] if node=='sink' else [('parallel_second',node),('parallel_first',node)]


class RowCacheTests(unittest.TestCase):
    def test_lru_eviction_preserves_parallel_order(self):
        provider=Provider();cache=RowCache(provider,2)
        for node in ['a','b','a','c','b']:
            self.assertEqual(cache.neighbors(node),[('parallel_second',node),('parallel_first',node)])
        self.assertEqual(provider.calls,['a','b','c','b'])
        self.assertEqual(cache.statistics()['evictions'],2)
        self.assertEqual(cache.statistics()['resident_edges'],4)

    def test_unknown_is_not_cached_as_sink(self):
        provider=Provider();cache=RowCache(provider,2)
        for _ in range(2):
            with self.assertRaises(IncompleteDomain):cache.neighbors('unknown')
        self.assertEqual(cache.neighbors('sink'),[])
        self.assertEqual(cache.neighbors('sink'),[])
        self.assertEqual(provider.calls,['unknown','unknown','sink'])

    def test_zero_capacity_disables_cache(self):
        provider=Provider();cache=RowCache(provider,0)
        cache.neighbors('a');cache.neighbors('a')
        self.assertEqual(provider.calls,['a','a'])
        self.assertEqual(cache.statistics()['peak_rows'],0)


if __name__=='__main__':unittest.main()
