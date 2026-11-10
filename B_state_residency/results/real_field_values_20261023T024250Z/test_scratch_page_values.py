import random
import unittest
from dataclasses import replace
from src.scratch_page_values import ScratchLabel, ScratchPageCodec, ScratchPageValues
from src.finite_completion import WouldBlock
from src.fence_control import FenceControl


class ScratchPageTests(unittest.TestCase):
    def flush(self, pages):
        while pages.link.requests: pages.dispatch()
        while pages.link.work: pages.publish()
        while pages.link.responses: pages.deliver()

    def fence(self, pages):
        control = FenceControl(pages)
        control.begin(); self.flush(pages); control.service(); control.receive(); control.finish()

    def test_bit_exact_codec_and_distinct_missing_default(self):
        codec = ScratchPageCodec(6)
        self.assertEqual(codec.record.size, 20)
        self.assertEqual(codec.stride, 1344)
        values = {0: ScratchLabel(), 63: ScratchLabel(0x7fc12345, 0x80000000, -(1 << 31), (1 << 31)-1, 255),
                  17: ScratchLabel(0x7f800000, 0xff800000, -1, 0, 1)}
        self.assertEqual(codec.decode(codec.encode(values)), values)
        self.assertNotIn(1, codec.decode(codec.encode(values)))

    def test_invalid_fields_rejected_before_write(self):
        codec = ScratchPageCodec(6)
        for bad in (ScratchLabel(lb_bits=-1), ScratchLabel(upstream_bits=1 << 32),
                    ScratchLabel(prev=1 << 31), ScratchLabel(visited=True), ScratchLabel(target=256)):
            with self.assertRaises(ValueError): codec.encode({0: bad})
        with self.assertRaises(TypeError): ScratchLabel(hist=1)
        with self.assertRaises(ValueError): codec.encode({64: ScratchLabel()})

    def test_real_field_bytes_survive_refill_and_checkpoint(self):
        pages = ScratchPageValues(backing_bytes=4 * 1344)
        query = pages.begin_query(3)
        value = ScratchLabel(0x7fa12345, 0x80000000, -1, 777, 1)
        pages.request(query, 0); pages.write(query, 0, value); pages.evict(query, 0); self.flush(pages)
        pages.backing[query][0][0] = ScratchLabel()  # Refill must use raw memory.
        pages.request(query, 0); self.flush(pages)
        self.assertEqual(pages.read(query, 0), value)
        snapshot = pages.checkpoint(query)
        self.fence(pages)
        query = pages.begin_query(3); pages.restore(query, snapshot)
        pages.request(query, 0); self.flush(pages)
        self.assertEqual(pages.read(query, 0), value)
        self.fence(pages)
        query = pages.begin_query(4); pages.request(query, 0)
        self.assertIsNone(pages.read(query, 0))

    def test_capacity_backpressure_preserves_all_fields(self):
        pages = ScratchPageValues(backing_bytes=1344)
        query = pages.begin_query(0)
        pages.request(query, 0); pages.write(query, 0, ScratchLabel(prev=-1)); pages.evict(query, 0); self.flush(pages)
        pages.request(query, 1); value = ScratchLabel(visited=42, target=1); pages.write(query, 64, value)
        before = set(pages.domain.used_transactions)
        with self.assertRaises(WouldBlock): pages.evict(query, 1)
        self.assertEqual(pages.read(query, 64), value)
        self.assertEqual(pages.domain.used_transactions, before)

    def test_random_mixed_fields_raw_oracle_and_fence_reuse(self):
        rng = random.Random(522)
        pages = ScratchPageValues(backing_bytes=8 * 128, page_bits=2,
                                  transaction_bits=8, generation_bits=8)
        for cycle in range(20):
            query = pages.begin_query(cycle % 16); oracle = {}
            for step in range(60):
                node = rng.randrange(32); page = node >> 2
                if not any(b and b.page == page for b in pages.domain.bindings) and all(pages.domain.bindings):
                    pages.evict(query, pages.domain.bindings[0].page); self.flush(pages)
                pages.request(query, page); self.flush(pages)
                self.assertEqual(pages.read(query, node), oracle.get(node))
                field = rng.choice(('lb_bits', 'upstream_bits', 'prev', 'visited', 'target'))
                value = rng.randrange(1 << 32) if field.endswith('bits') else rng.randrange(256) if field == 'target' else rng.randrange(-(1 << 31), 1 << 31)
                expected = replace(oracle.get(node, ScratchLabel()), **{field: value})
                pages.write(query, node, expected); oracle[node] = expected
            snapshot = pages.checkpoint(query)
            self.fence(pages); query = pages.begin_query(cycle % 16); pages.restore(query, snapshot)
            raw = {page * 4 + offset: value for owner, page in pages.pool.owners
                   for offset, value in pages.codec.decode(pages.pool.read((owner, page))).items()}
            self.assertEqual(raw, oracle)
            self.fence(pages)


if __name__ == '__main__': unittest.main()
