import random
import unittest
from src.bounded_backing import IntegerPageCodec,BackingPool,BoundedPageValues
from src.finite_completion import WouldBlock
from src.finite_page_values import PageCheckpoint
from src.fence_control import FenceControl

class BoundedBackingTests(unittest.TestCase):
    def flush(self,c):
        while c.link.requests:c.dispatch()
        while c.link.work:c.publish()
        while c.link.responses:c.deliver()
    def fence(self,c):
        ctl=FenceControl(c);ctl.begin();self.flush(c);ctl.service();ctl.receive();ctl.finish()
    def test_fixed_codec_distinguishes_missing_zero_and_range(self):
        codec=IntegerPageCodec(6);self.assertEqual(codec.stride,576)
        values={0:0,1:-1,63:(1<<63)-1};self.assertEqual(codec.decode(codec.encode(values)),values)
        for bad in [{64:1},{0:1<<63},{0:None},{0:True}]:
            with self.assertRaises(ValueError):codec.encode(bad)
    def test_capacity_blocks_without_losing_dirty_value_or_burning_id(self):
        c=BoundedPageValues(backing_bytes=64,transaction_bits=4);q=c.begin_query(0)
        c.request(q,0);c.write(q,0,7);c.evict(q,0);self.flush(c)
        c.request(q,1);c.write(q,4,9);issued=set(c.domain.used_transactions)
        with self.assertRaises(WouldBlock):c.evict(q,1)
        self.assertEqual(c.read(q,4),9);self.assertEqual(c.domain.used_transactions,issued)
        self.assertEqual(len(c.pool.memory),64)
    def test_cancelled_late_dma_address_is_not_reassigned(self):
        c=BoundedPageValues(backing_bytes=64);old=c.begin_query(0);c.request(old,0);c.write(old,0,11);c.evict(old,0)
        address=c.pool.owners[(old,0)];new=c.begin_query(1);c.request(new,0);c.write(new,0,22)
        with self.assertRaises(WouldBlock):c.evict(new,0)
        c.dispatch();c.publish();self.assertEqual(c.codec.decode(c.pool.read((old,0))),{0:11})
        self.assertEqual(c.read(new,0),22);c.deliver()
        with self.assertRaises(WouldBlock):c.evict(new,0)  # ACK alone does not free old namespace.
        self.fence(c);q=c.begin_query(1);c.request(q,0);c.write(q,0,33);c.evict(q,0)
        self.assertEqual(c.pool.owners[(q,0)],address);self.flush(c);c.request(q,0);self.flush(c);self.assertEqual(c.read(q,0),33)
    def test_duplicate_completion_prevents_address_recycle(self):
        c=BoundedPageValues(backing_bytes=64);q=c.begin_query(0);c.request(q,0);c.write(q,0,3);c.evict(q,0);c.dispatch();c.publish();c.link.duplicate_response();c.deliver()
        ctl=FenceControl(c);ctl.begin();ctl.service();ctl.receive()
        with self.assertRaises(WouldBlock):ctl.finish()
        self.assertTrue(c.pool.owners);c.deliver();ctl.finish();self.assertFalse(c.pool.owners)
    def test_refill_uses_byte_memory_not_shadow_dictionary(self):
        c=BoundedPageValues(backing_bytes=64);q=c.begin_query(0);c.request(q,0);c.write(q,0,71);c.evict(q,0);self.flush(c)
        c.backing[q][0][0]=999  # Deliberate fault in diagnostic shadow.
        c.request(q,0);self.flush(c);self.assertEqual(c.read(q,0),71)
    def test_restore_capacity_is_atomic_and_leases_block_fence(self):
        c=BoundedPageValues(backing_bytes=64);q=c.begin_query(0)
        with self.assertRaises(WouldBlock):c.restore(q,PageCheckpoint(0,2,{0:{0:1},1:{0:2}}))
        self.assertFalse(c.backing[q] or c.pool.owners)
        c.restore(q,PageCheckpoint(0,2,{0:{0:5}}));c.request(q,0)
        self.assertEqual(len(c.pool.leases),1)
        self.fence(c);self.assertFalse(c.pool.leases or c.pool.owners)
    def test_queue_backpressure_does_not_reserve_physical_address(self):
        c=BoundedPageValues(backing_bytes=128,queue_capacity=1);q=c.begin_query(0)
        c.request(q,0);c.write(q,0,1);c.request(q,1);c.write(q,4,2);c.pin(q,0)
        before=set(c.domain.used_transactions)
        with self.assertRaises(WouldBlock):c.evict(q,1)
        self.assertFalse(c.pool.owners);self.assertEqual(c.domain.used_transactions,before)
        self.assertEqual(c.read(q,4),2)
    def test_byte_address_limits_and_alignment(self):
        with self.assertRaises(ValueError):BackingPool(64,128,address_bits=6)
        p=BackingPool(64,130,address_bits=8);self.assertEqual(len(p.memory),128)
        self.assertEqual([p.reserve(('q',i)) for i in range(2)],[0,64])
        with self.assertRaises(WouldBlock):p.reserve(('q',2))
    def test_random_physical_values_and_fence_reuse(self):
        rng=random.Random(161);c=BoundedPageValues(backing_bytes=8*64,transaction_bits=8,generation_bits=8,page_id_bits=8)
        for cycle in range(30):
            q=c.begin_query(cycle%16);oracle={}
            for step in range(40):
                node=rng.randrange(32);page=node//4
                b=next((b for b in c.domain.bindings if b and b.page==page),None)
                if b is None and all(c.domain.bindings):c.evict(q,c.domain.bindings[0].page);self.flush(c)
                c.request(q,page);self.flush(c);self.assertEqual(c.read(q,node),oracle.get(node))
                c.write(q,node,step);oracle[node]=step
                self.assertEqual(len(set(c.pool.owners.values())),len(c.pool.owners));self.assertLessEqual(len(c.pool.owners),8)
                actual={}
                for owner in c.pool.owners:
                    if owner[0]==q:
                        for offset,value in c.codec.decode(c.pool.read(owner)).items():actual[owner[1]*4+offset]=value
                for resident in c.domain.bindings:
                    if resident is not None:
                        for offset,value in c.values[resident.slot].items():actual[resident.page*4+offset]=value
                self.assertEqual(actual,oracle)
            self.fence(c)
if __name__=='__main__':unittest.main()
