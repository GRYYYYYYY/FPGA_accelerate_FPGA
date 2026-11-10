import random
import unittest
from src.finite_completion import WouldBlock
from src.finite_page_values import FinitePageValues

class FiniteValueTests(unittest.TestCase):
    def flush(self, c, rng=None):
        rng=rng or random.Random(1)
        while c.link.requests:c.dispatch(rng.randrange(len(c.link.requests)))
        while c.link.work:c.publish(rng.randrange(len(c.link.work)))
        while c.link.responses:c.deliver(rng.randrange(len(c.link.responses)))

    def test_peer_write_precedes_ack_and_refill_not_visible_early(self):
        c=FinitePageValues();q=c.begin_query(1);c.request(q,0);c.write(q,1,{'x':[11]});t=c.evict(q,0)
        c.dispatch();c.publish()
        self.assertEqual(c.backing[q][0],{1:{'x':[11]}})
        with self.assertRaises(WouldBlock):c.read(q,1)
        with self.assertRaises(WouldBlock):c.request(q,0)
        c.deliver();c.request(q,0)
        with self.assertRaises(WouldBlock):c.read(q,1)
        c.dispatch();c.publish()
        with self.assertRaises(WouldBlock):c.read(q,1)
        c.deliver();value=c.read(q,1);value['x'][0]=99
        self.assertEqual(c.read(q,1),{'x':[11]})

    def test_cancel_before_late_writeback_is_namespace_isolated(self):
        c=FinitePageValues();old=c.begin_query(1);b=c.request(old,0);c.write(old,0,111);c.evict(old,0)
        new=c.begin_query(2);fresh=c.request(new,0);c.write(new,0,222)
        c.dispatch();c.publish()
        self.assertEqual(c.backing[old][0],{0:111});self.assertNotIn(0,c.backing[new])
        self.assertEqual(c.deliver()[1],'stale');self.assertIsNone(c.domain.bindings[b.slot])
        self.assertEqual(c.domain.bindings[fresh.slot],fresh);self.assertEqual(c.read(new,0),222)

    def test_cancel_after_peer_write_before_ack(self):
        c=FinitePageValues();old=c.begin_query(1);c.request(old,0);c.write(old,0,7);c.evict(old,0);c.dispatch();c.publish()
        new=c.begin_query(1);c.request(new,0)
        self.assertIsNone(c.read(new,0));self.assertEqual(c.deliver()[1],'stale');self.assertIsNone(c.read(new,0))

    def test_late_refill_cannot_publish_into_new_query(self):
        c=FinitePageValues();old=c.begin_query(1);c.request(old,0);c.write(old,0,13);c.evict(old,0);self.flush(c)
        stale=c.request(old,0);c.dispatch();c.publish()
        new=c.begin_query(2);fresh=c.request(new,0);c.write(new,0,29)
        self.assertEqual(c.deliver()[1],'stale');self.assertIsNone(c.domain.bindings[stale.slot])
        self.assertEqual(c.read(new,0),29);self.assertEqual(c.domain.bindings[fresh.slot],fresh)

    def test_duplicate_request_or_response_does_not_repeat_data_effects(self):
        c=FinitePageValues();q=c.begin_query(0);c.request(q,0);c.write(q,0,9);c.evict(q,0);c.link.duplicate_request()
        c.dispatch(1);c.dispatch();c.publish();c.link.duplicate_response();c.deliver(1);c.deliver()
        self.assertEqual(c.writeback_effects,1)
        c.request(q,0);c.link.duplicate_request();c.dispatch();c.dispatch();c.publish();c.link.duplicate_response();c.deliver();c.deliver()
        self.assertEqual(c.refill_effects,1);self.assertEqual(c.read(q,0),9)

    def test_fence_waits_for_payload_and_duplicate_queues(self):
        c=FinitePageValues();q=c.begin_query(0);c.request(q,0);c.write(q,0,99);c.evict(q,0);c.dispatch();c.publish();c.link.duplicate_response()
        c.request_fence();c.seal_peer()
        with self.assertRaises(WouldBlock):c.finish_fence()
        c.deliver()
        with self.assertRaises(WouldBlock):c.finish_fence()
        c.deliver();c.finish_fence();self.assertFalse(c.backing or c.inbound or c.outbound)
        new=c.begin_query(0);self.assertEqual(q,new);c.request(new,0);self.assertIsNone(c.read(new,0))

    def test_pin_and_request_backpressure_keep_values_and_generation(self):
        c=FinitePageValues(queue_capacity=1,transaction_bits=4);q=c.begin_query(0);b=c.request(q,0);c.write(q,0,3)
        c.pin(q,0)
        with self.assertRaises(WouldBlock):c.evict(q,0)
        self.flush(c);c.evict(q,0);self.flush(c)
        c.request(q,1);c.pin(q,1)
        before=list(c.domain.generations)
        with self.assertRaises(WouldBlock):c.request(q,0)
        self.assertEqual(before,c.domain.generations);self.flush(c)
        c.request(q,0);self.flush(c);self.assertEqual(c.read(q,0),3)

    def test_small_width_random_values_with_fence_recovery(self):
        rng=random.Random(619);c=FinitePageValues(slots=2,transaction_bits=3,query_bits=2,generation_bits=2)
        oracle={};q=c.begin_query(0);fences=0;successful=0
        for step in range(2000):
            node=rng.randrange(32);page=node>>c.page_bits
            try:
                resident=next((b for b in c.domain.bindings if b and b.query==q and b.page==page),None)
                if resident is None and all(c.domain.bindings):
                    victim=rng.choice(c.domain.bindings);c.evict(q,victim.page);self.flush(c,rng)
                c.request(q,page);self.flush(c,rng)
                self.assertEqual(c.read(q,node),oracle.get(node))
                if rng.randrange(2):c.write(q,node,step);oracle[node]=step
                logical={page*c_page_size+offset:value for page,values in c.backing[q].items() for offset,value in values.items() for c_page_size in [1<<c.page_bits]}
                for binding in c.domain.bindings:
                    if binding is not None and binding.query==q:
                        for offset,value in c.values[binding.slot].items():logical[(binding.page<<c.page_bits)+offset]=value
                self.assertEqual(logical,oracle);successful+=1
            except WouldBlock:
                self.flush(c,rng);c.request_fence();self.flush(c,rng);c.seal_peer();c.finish_fence();fences+=1
                q=c.begin_query(fences%c.domain.price_limit);oracle={}
        self.assertGreater(fences,50)
        self.assertGreater(successful,1000)
        self.assertGreater(c.writeback_effects,100)
        self.assertGreater(c.refill_effects,10)

if __name__=='__main__':unittest.main()
