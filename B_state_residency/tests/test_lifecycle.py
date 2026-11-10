import importlib.util
from pathlib import Path
import random
import sys
import unittest

spec = importlib.util.spec_from_file_location('lifecycle', Path(__file__).resolve().parents[1] / 'src/lifecycle.py')
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


class LifecycleTests(unittest.TestCase):
    def setup_protocol(self):
        authority = m.Authority({0: 7, 1: 7, 2: 8})
        replica = m.Replica(authority.design)
        contexts = [m.Context(authority, replica, i, epoch_bits=2) for i in range(2)]
        return authority, replica, contexts

    def test_shared_branches_count_distinct_nets(self):
        authority, replica, (context, _) = self.setup_protocol()
        for connection, resources in [(0, [5]), (1, [5]), (2, [5]), (0, []), (1, [])]:
            query = context.begin()
            replica.apply(context.commit(query, connection, resources))
        self.assertEqual(authority.occupancy(5), 1)
        self.assertEqual(authority.references[5], {8: 1})
        self.assertEqual(replica.values[5], (1, 0))

    def test_concurrent_stale_commit_does_not_mutate_authority(self):
        authority, replica, (a, b) = self.setup_protocol()
        qa, qb = a.begin(), b.begin()
        delta = a.commit(qa, 0, [2])
        with self.assertRaises(ValueError):
            b.commit(qb, 1, [3])
        self.assertEqual(authority.paths[1], frozenset())
        replica.apply(delta)
        with self.assertRaises(ValueError):
            b.read(qb, 3)
        b.finish(qb)

    def test_gap_duplicate_and_wrong_design(self):
        authority, replica, _ = self.setup_protocol()
        a = authority.add_history({4: 1})
        b = authority.add_history({4: 2})
        with self.assertRaises(ValueError):
            replica.apply(b)
        self.assertEqual(replica.values, {})
        replica.apply(a)
        replica.apply(a)
        replica.apply(b)
        self.assertEqual(replica.values[4], (0, 3))
        with self.assertRaises(ValueError):
            replica.apply(a)
        with self.assertRaises(ValueError):
            replica.apply(m.Authority({}).add_history({4: 1}))

    def test_page_lease_epoch_wrap_and_old_handle(self):
        authority, replica, (context, other) = self.setup_protocol()
        old = context.begin()
        context.write(old, 1, 19, page=0)
        with self.assertRaises(ValueError):
            context.reclaim(0)
        qother = other.begin()
        self.assertIsNone(other.read(qother, 1))
        other.finish(qother)
        context.finish(old)
        context.reclaim(0)
        for _ in range(10):
            query = context.begin()
            self.assertIsNone(context.read(query, 1))
            with self.assertRaises(ValueError):
                context.read(old, 1)
            context.finish(query)
        self.assertGreater(context.incarnation, 0)
        self.assertEqual(authority.version, replica.version)

    def test_randomized_reference_and_ordered_replay(self):
        authority, replica, contexts = self.setup_protocol()
        paths = {0: set(), 1: set(), 2: set()}
        history = {}
        rng = random.Random(3901)
        for step in range(1000):
            context = contexts[step % 2]
            if step % 7 == 0:
                resource = rng.randrange(12)
                history[resource] = history.get(resource, 0) + 1
                delta = authority.add_history({resource: 1})
            else:
                connection = rng.randrange(3)
                resources = set(rng.sample(range(12), rng.randrange(6)))
                query = context.begin()
                delta = context.commit(query, connection, resources)
                paths[connection] = resources
            # Queries cannot start from a stale replica, even if no labels exist.
            with self.assertRaises(ValueError):
                context.begin()
            replica.apply(delta)
            replica.apply(delta)
            for resource in range(12):
                nets = {authority.connection_nets[c] for c, path in paths.items() if resource in path}
                expected = (len(nets), history.get(resource, 0))
                self.assertEqual(replica.values.get(resource, (0, 0)), expected)
                self.assertEqual(authority.occupancy(resource), len(nets))

    def test_invalid_resource_does_not_partial_commit(self):
        authority, replica, (context, _) = self.setup_protocol()
        query = context.begin()
        with self.assertRaises(ValueError):
            context.commit(query, 0, [-1])
        self.assertEqual(authority.version, 0)
        self.assertEqual(authority.paths[0], frozenset())
        context.finish(query)

    def test_missing_delta_recovers_by_snapshot_without_resurrecting_query(self):
        authority, replica, (context, _) = self.setup_protocol()
        old = context.begin()
        context.write(old, 4, 12, page=1)
        stale = authority.snapshot()
        authority.add_history({4: 1})  # Lost delivery.
        delta = authority.add_history({4: 2})
        with self.assertRaises(ValueError):
            replica.apply(delta)
        replica.install(authority.snapshot())
        self.assertEqual(replica.values[4], (0, 3))
        with self.assertRaises(ValueError):
            context.commit(old, 0, [4])
        context.finish(old)
        with self.assertRaises(ValueError):
            replica.install(stale)
        query = context.begin()
        self.assertIsNone(context.read(query, 4))
        replica.install(authority.snapshot())  # Same price version, new recovery.
        with self.assertRaises(ValueError):
            context.read(query, 4)
        context.finish(query)

    def test_malformed_updates_and_snapshot_are_atomic(self):
        authority, replica, _ = self.setup_protocol()
        replica.apply(authority.add_history({1: 2}))
        before = (replica.version, dict(replica.values), replica.generation)
        for rows in [((2, 1, 1), (3, -1, 0)), ((2, 1, 1), (2, 2, 2))]:
            with self.assertRaises(ValueError):
                replica.apply(m.Delta(authority.design, 1, 2, rows))
            with self.assertRaises(ValueError):
                replica.install(m.Snapshot(authority.design, 2, rows))
            self.assertEqual((replica.version, replica.values, replica.generation), before)
