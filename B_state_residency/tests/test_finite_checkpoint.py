import unittest
from src.finite_completion import WouldBlock,FiniteCompletionDomain
from src.finite_page_values import FinitePageValues,PageCheckpoint

class CheckpointTests(unittest.TestCase):
    def flush(self,c):
        while c.link.requests:c.dispatch()
        while c.link.work:c.publish()
        while c.link.responses:c.deliver()
    def test_actual_dirty_and_saved_values_survive_midquery_fence(self):
        c=FinitePageValues(transaction_bits=1);q=c.begin_query(3)
        c.request(q,0);c.write(q,1,11);c.evict(q,0);self.flush(c)
        c.request(q,1);c.write(q,4,22)
        checkpoint=c.checkpoint(q)
        c.request_fence();c.seal_peer();c.finish_fence();new=c.begin_query(3);c.restore(new,checkpoint)
        for page,node,value in [(0,1,11),(1,4,22)]:
            c.request(new,page);self.flush(c);self.assertEqual(c.read(new,node),value)
        self.assertEqual(c.domain.used_transactions,{0,1})
    def test_pin_or_io_prevents_checkpoint(self):
        c=FinitePageValues();q=c.begin_query(0);c.request(q,0);c.pin(q,0)
        with self.assertRaises(WouldBlock):c.checkpoint(q)
        self.flush(c);c.write(q,0,9);c.evict(q,0)
        with self.assertRaises(WouldBlock):c.checkpoint(q)
    def test_price_change_rejects_distance_snapshot(self):
        c=FinitePageValues();q=c.begin_query(1);snapshot=c.checkpoint(q);new=c.begin_query(2)
        with self.assertRaises(ValueError):c.restore(new,snapshot)
    def test_malformed_restore_is_atomic(self):
        c=FinitePageValues();q=c.begin_query(0)
        for pages in [{0:{0:7},c.domain.page_limit:{0:8}},{0:{4:8}}]:
            with self.assertRaises(ValueError):c.restore(q,PageCheckpoint(0,2,pages))
            self.assertEqual(c.backing[q],{})
    def test_snapshot_and_restore_do_not_alias_values(self):
        c=FinitePageValues();q=c.begin_query(0);c.request(q,0);c.write(q,0,[7]);snap=c.checkpoint(q);c.write(q,0,[8])
        self.assertEqual(snap.pages[0][0],[7]);c.request_fence();c.seal_peer();c.finish_fence();q=c.begin_query(0);c.restore(q,snap);snap.pages[0][0][0]=99
        c.request(q,0);self.flush(c);self.assertEqual(c.read(q,0),[7])
    def test_real_graph_page_address_width(self):
        c=FinitePageValues(page_bits=6,page_id_bits=18)
        q=c.begin_query(0);self.assertEqual(c.request(q,9089008>>6).page,142015)
        with self.assertRaises(ValueError):FiniteCompletionDomain(page_bits=33)
if __name__=='__main__':unittest.main()
