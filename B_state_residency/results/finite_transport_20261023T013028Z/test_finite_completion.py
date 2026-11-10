import random
import unittest
from dataclasses import replace
from src.finite_completion import Binding, Descriptor, FiniteCompletionDomain, QueryKey, WouldBlock

class FiniteCompletionTests(unittest.TestCase):
    def test_reconstructed_fields_and_duplicate(self):
        d=FiniteCompletionDomain();q=d.begin_query(1);b=d.bind(q,0,2);t=d.issue(b,'refill')
        clone=Descriptor(t.transaction,Binding(QueryKey(q.query,q.price),b.slot,b.generation,b.page),t.kind)
        self.assertIsNot(t,clone);self.assertTrue(d.complete(clone))
        with self.assertRaises(ValueError):d.complete(t)
        d.release(b)

    def test_mismatch_does_not_consume_lease(self):
        d=FiniteCompletionDomain();q=d.begin_query(1);b=d.bind(q,0,2);t=d.issue(b,'writeback')
        for bad in [replace(t,kind='refill'),replace(t,binding=replace(b,page=3)),replace(t,binding=replace(b,generation=1)),replace(t,binding=replace(b,query=QueryKey(q.query,2)))]:
            with self.assertRaises(ValueError):d.complete(bad)
        with self.assertRaises(WouldBlock):d.release(b)
        self.assertTrue(d.complete(t));d.release(b)

    def test_cancel_and_reordered_old_ack(self):
        d=FiniteCompletionDomain();old=d.begin_query(1);b=d.bind(old,0,2);t=d.issue(b,'refill')
        new=d.begin_query(2);fresh=d.bind(new,1,2);u=d.issue(fresh,'writeback')
        self.assertTrue(d.complete(u));self.assertFalse(d.complete(t));d.release(b);d.release(fresh)
        with self.assertRaises(ValueError):d.bind(old,0,2)

    def test_pin_blocks_io_and_release(self):
        d=FiniteCompletionDomain();q=d.begin_query(1);b=d.bind(q,0,2);a=d.issue(b,'pin');z=d.issue(b,'pin')
        with self.assertRaises(WouldBlock):d.issue(b,'writeback')
        self.assertTrue(d.complete(z))
        with self.assertRaises(WouldBlock):d.release(b)
        d.request_fence();self.assertFalse(d.complete(a));d.release(b)
        d.recycle_after_fence(peer_quiescent=True,completion_queue_empty=True)

    def test_all_finite_spaces_require_fence(self):
        d=FiniteCompletionDomain(transaction_bits=1,query_bits=1,generation_bits=1)
        q=d.begin_query(0)
        for _ in range(2):
            b=d.bind(q,0,2);t=d.issue(b,'refill');d.complete(t);d.release(b)
        with self.assertRaises(WouldBlock):d.bind(q,0,2)
        b=d.bind(q,1,3)
        with self.assertRaises(WouldBlock):d.issue(b,'pin')
        d.release(b);d.begin_query(1)
        with self.assertRaises(WouldBlock):d.begin_query(2)
        d.request_fence()
        with self.assertRaises(WouldBlock):d.begin_query(0)
        for peer,queue in [(False,True),(True,False)]:
            with self.assertRaises(WouldBlock):d.recycle_after_fence(peer_quiescent=peer,completion_queue_empty=queue)
        d.recycle_after_fence(peer_quiescent=True,completion_queue_empty=True)
        self.assertEqual(d.begin_query(0),q)

    def test_local_ack_is_not_transport_drain(self):
        d=FiniteCompletionDomain();q=d.begin_query(1);b=d.bind(q,0,2);t=d.issue(b,'refill');d.request_fence()
        with self.assertRaises(WouldBlock):d.recycle_after_fence(peer_quiescent=True,completion_queue_empty=True)
        self.assertFalse(d.complete(t));d.release(b)
        # A retained duplicate in the completion queue still prevents ID reuse.
        with self.assertRaises(ValueError):d.complete(t)
        with self.assertRaises(WouldBlock):d.recycle_after_fence(peer_quiescent=True,completion_queue_empty=False)
        d.recycle_after_fence(peer_quiescent=True,completion_queue_empty=True)

    def test_false_fence_has_identical_packet_aba(self):
        d=FiniteCompletionDomain();q=d.begin_query(1);b=d.bind(q,0,2);old=d.issue(b,'refill');d.complete(old);d.release(b)
        d.request_fence();d.recycle_after_fence(peer_quiescent=True,completion_queue_empty=True)
        q=d.begin_query(1);b=d.bind(q,0,2);new=d.issue(b,'refill')
        self.assertEqual(old,new)
        # Deliberately violate the transport promise. The ledger cannot detect
        # an identical old packet; this is an explicit impossibility boundary.
        self.assertTrue(d.complete(old))

    def test_small_width_random_reordered_epochs(self):
        rng=random.Random(819)
        d=FiniteCompletionDomain(slots=3,transaction_bits=4,query_bits=2,generation_bits=2)
        for _ in range(100):
            packets=[]
            for price in range(4):
                q=d.begin_query(price)
                for slot in range(3):
                    if d.bindings[slot] is None:
                        b=d.bind(q,slot,slot);packets.append(d.issue(b,'pin'))
                rng.shuffle(packets)
                while packets and rng.randrange(3):
                    t=packets.pop();self.assertEqual(d.complete(t),t.binding.query==d.active);d.release(t.binding)
            d.request_fence();rng.shuffle(packets)
            for t in packets:self.assertFalse(d.complete(t));d.release(t.binding)
            d.recycle_after_fence(peer_quiescent=True,completion_queue_empty=True)

if __name__=='__main__':unittest.main()
