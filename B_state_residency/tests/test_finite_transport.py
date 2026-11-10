import random
import unittest
from dataclasses import replace
from src.finite_completion import FiniteCompletionDomain,WouldBlock
from src.finite_transport import FiniteTransport

class FiniteTransportTests(unittest.TestCase):
    def make(self,capacity=4):
        link=FiniteTransport(FiniteCompletionDomain(slots=2,transaction_bits=2,query_bits=2,generation_bits=2),capacity)
        query=link.domain.begin_query(0);binding=link.domain.bind(query,0,1)
        return link,binding

    def test_duplicate_request_executes_once_and_duplicate_ack_quarantined(self):
        link,b=self.make();t=link.submit(b,'writeback');link.duplicate_request()
        self.assertTrue(link.dispatch(1));self.assertFalse(link.dispatch());self.assertEqual(len(link.work),1)
        link.publish();link.duplicate_response();self.assertEqual(link.deliver(1),(t,'valid'));link.domain.release(b)
        link.request_fence();link.seal_peer()
        with self.assertRaises(WouldBlock):link.finish_fence()
        self.assertEqual(link.deliver(),(t,'duplicate'));link.finish_fence()
        q=link.domain.begin_query(0);b=link.domain.bind(q,0,1);new=link.submit(b,'writeback')
        self.assertEqual(t,new)  # Reuse is safe only because old queues are empty.
        self.assertEqual(len(link.responses),0)

    def test_request_and_work_block_peer_ack(self):
        link,b=self.make();link.submit(b,'refill');link.request_fence()
        with self.assertRaises(WouldBlock):link.submit(b,'pin')
        with self.assertRaises(WouldBlock):link.seal_peer()
        link.dispatch()
        with self.assertRaises(WouldBlock):link.seal_peer()
        link.publish();link.seal_peer()
        self.assertEqual(link.deliver()[1],'stale');link.domain.release(b);link.finish_fence()

    def test_local_empty_without_peer_ack_is_insufficient(self):
        link,b=self.make();t=link.submit(b,'pin');link.dispatch();link.publish();link.deliver();link.domain.release(b);link.request_fence()
        with self.assertRaises(WouldBlock):link.finish_fence()
        link.seal_peer();link.finish_fence()

    def test_out_of_order_cancel_and_old_slot_lease(self):
        link,b=self.make();old=link.submit(b,'refill');q=link.domain.begin_query(1);fresh=link.domain.bind(q,1,1);new=link.submit(fresh,'writeback')
        link.dispatch(1);link.dispatch();link.publish(1);link.publish()
        self.assertEqual(link.deliver(1),(new,'valid'))
        with self.assertRaises(WouldBlock):link.domain.release(b)
        self.assertEqual(link.deliver(),(old,'stale'));link.domain.release(b);link.domain.release(fresh)

    def test_backpressure_is_atomic(self):
        link,b=self.make(capacity=1);t=link.submit(b,'pin')
        pending=dict(link.domain.pending);used=set(link.domain.used_transactions)
        with self.assertRaises(WouldBlock):link.submit(b,'pin')
        self.assertEqual(link.domain.pending,pending);self.assertEqual(link.domain.used_transactions,used)
        link.dispatch();link.publish();self.assertEqual(link.deliver(),(t,'valid'))

    def test_corruption_does_not_consume_valid_completion(self):
        link,b=self.make();t=link.submit(b,'refill');link.dispatch();link.publish();link.responses.insert(0,replace(t,kind='writeback'))
        with self.assertRaises(ValueError):link.deliver()
        self.assertEqual(link.domain.pending[t.transaction],t);link.responses.pop(0)
        self.assertEqual(link.deliver(),(t,'valid'))

    def test_pin_ack_drain_requires_all_local_bindings_released(self):
        link,b=self.make();link.submit(b,'pin');link.submit(b,'pin');link.request_fence()
        link.dispatch();link.dispatch();link.publish();link.publish();link.seal_peer()
        link.deliver()
        with self.assertRaises(WouldBlock):link.domain.release(b)
        link.deliver()
        with self.assertRaises(WouldBlock):link.finish_fence()
        link.domain.release(b);link.finish_fence()

    def test_repeated_small_id_cycles_with_random_queue_order(self):
        rng=random.Random(317)
        domain=FiniteCompletionDomain(slots=2,transaction_bits=1,query_bits=1,generation_bits=1)
        link=FiniteTransport(domain,queue_capacity=4)
        for cycle in range(200):
            query=domain.begin_query(cycle%domain.price_limit)
            bindings=[domain.bind(query,i,i) for i in range(2)]
            for b in bindings:link.submit(b,'refill')
            link.duplicate_request(rng.randrange(2));link.request_fence()
            while link.requests:link.dispatch(rng.randrange(len(link.requests)))
            while link.work:link.publish(rng.randrange(len(link.work)))
            link.duplicate_response(rng.randrange(2));link.seal_peer()
            with self.assertRaises(WouldBlock):link.finish_fence()
            seen=set()
            while link.responses:
                packet,status=link.deliver(rng.randrange(len(link.responses)))
                self.assertEqual(status,'duplicate' if packet.transaction in seen else 'stale');seen.add(packet.transaction)
            for b in bindings:domain.release(b)
            link.finish_fence()
            self.assertFalse(domain.pending or link.peer_seen or domain.used_transactions)

if __name__=='__main__':unittest.main()
