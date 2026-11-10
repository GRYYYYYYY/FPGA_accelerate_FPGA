from dataclasses import replace
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from lifecycle import Authority, Context, Replica
from page_residency import ResidentPages, WouldBlock


class ResidencyTests(unittest.TestCase):
    def protocol(self, capacity=1):
        authority = Authority({0: 7})
        replica = Replica(authority.design)
        context = Context(authority, replica, 0, epoch_bits=2)
        pages = ResidentPages(context, capacity, page_bits=2)
        query = context.begin()
        pages.bind(query)
        return authority, replica, context, pages, query

    def test_dirty_eviction_holds_slot_until_ack_and_refill_restores_values(self):
        _, _, _, pages, query = self.protocol()
        pages.request(query, 0)
        pages.write(query, 1, {'distance': 12})
        token = pages.evict(query, 0)
        with self.assertRaises(WouldBlock):
            pages.request(query, 1)
        with self.assertRaises(WouldBlock):
            pages.read(query, 1)
        self.assertTrue(pages.complete(token))
        pages.request(query, 1)
        self.assertIsNone(pages.read(query, 4))
        pages.evict(query, 1)
        refill = pages.request(query, 0)
        with self.assertRaises(WouldBlock):
            pages.read(query, 1)
        pages.complete(refill)
        value = pages.read(query, 1)
        self.assertEqual(value, {'distance': 12})
        value['distance'] = 999  # Reads cannot mutate a clean cache line.
        self.assertEqual(pages.read(query, 1), {'distance': 12})

    def test_late_writeback_does_not_populate_new_query(self):
        _, _, context, pages, old = self.protocol()
        pages.request(old, 0)
        pages.write(old, 1, 9)
        token = pages.evict(old, 0)
        context.finish(old)
        new = context.begin()
        pages.bind(new)
        with self.assertRaises(WouldBlock):
            pages.request(new, 0)
        self.assertFalse(pages.complete(token))
        pages.request(new, 0)
        self.assertIsNone(pages.read(new, 1))
        pages.write(new, 1, 100)
        with self.assertRaises(ValueError):
            pages.complete(token)
        self.assertEqual(pages.read(new, 1), 100)

    def test_late_refill_and_forged_completion_rejected(self):
        _, _, context, pages, old = self.protocol()
        pages.request(old, 0)
        pages.write(old, 0, 42)
        pages.complete(pages.evict(old, 0))
        refill = pages.request(old, 0)
        with self.assertRaises(ValueError):
            pages.complete(replace(refill))
        context.finish(old)
        new = context.begin()
        pages.bind(new)
        self.assertFalse(pages.complete(refill))
        pages.request(new, 0)
        self.assertIsNone(pages.read(new, 0))

    def test_price_or_recovery_invalidates_pending_io(self):
        for change in ('price', 'recovery'):
            authority, replica, context, pages, query = self.protocol()
            pages.request(query, 0)
            pages.write(query, 0, 3)
            token = pages.evict(query, 0)
            if change == 'price':
                replica.apply(authority.add_history({0: 1}))
            else:
                replica.install(authority.snapshot())
            self.assertFalse(pages.complete(token))
            self.assertEqual(pages.backing, {})
            with self.assertRaises(ValueError):
                pages.request(query, 0)
            context.finish(query)

    def test_old_pin_prevents_reuse_until_ack(self):
        _, _, context, pages, old = self.protocol()
        pages.request(old, 0)
        pin = pages.pin(old, 0)
        with self.assertRaises(WouldBlock):
            pages.evict(old, 0)
        context.finish(old)
        new = context.begin()
        pages.bind(new)
        with self.assertRaises(WouldBlock):
            pages.request(new, 0)
        pages.unpin(pin)
        pages.request(new, 0)
        pages.write(new, 0, 88)
        with self.assertRaises(ValueError):
            pages.unpin(pin)
        self.assertEqual(pages.read(new, 0), 88)

    def test_random_values_survive_eviction_and_out_of_order_acks(self):
        _, _, context, pages, query = self.protocol(capacity=3)
        rng = random.Random(4821)
        oracle = {}
        for step in range(2000):
            if step and step % 200 == 0:
                context.finish(query)
                query = context.begin()
                pages.bind(query)
                oracle = {}
            node = rng.randrange(64)
            page = node >> 2
            if pages._find(query, page) is None:
                free = any(slot.query is None for slot in pages.slots)
                if not free:
                    # Start all evictions, then acknowledge in a shuffled order.
                    tokens = [pages.evict(query, slot.page) for slot in pages.slots]
                    rng.shuffle(tokens)
                    for token in tokens:
                        if token is not None:
                            pages.complete(token)
                token = pages.request(query, page)
                if token is not None:
                    pages.complete(token)
            self.assertEqual(pages.read(query, node), oracle.get(node))
            if rng.randrange(2):
                value = rng.randrange(100000)
                pages.write(query, node, value)
                oracle[node] = value
        self.assertGreater(query.incarnation, 0)
