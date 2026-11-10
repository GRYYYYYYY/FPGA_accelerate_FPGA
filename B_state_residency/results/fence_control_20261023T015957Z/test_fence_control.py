import random
import unittest
from src.finite_completion import FiniteCompletionDomain,WouldBlock
from src.finite_transport import FiniteTransport
from src.finite_page_values import FinitePageValues
from src.fence_control import FenceControl

class FenceControlTests(unittest.TestCase):
    def test_wire_codec_and_invalid_fields(self):
        c=FenceControl(FiniteTransport(),tag_bits=1)
        self.assertEqual(c.decode(c.encode('fence',1)),('fence',1))
        self.assertEqual(c.decode(bytes([1,0,0])),('ack',0))
        for raw in [b'',b'xxxx',bytes([2,0,0]),bytes([1,2,0])]:
            with self.assertRaises(ValueError):c.decode(raw)
    def test_data_request_and_work_prevent_peer_ack(self):
        link=FiniteTransport();q=link.domain.begin_query(0);b=link.domain.bind(q,0,0);link.submit(b,'pin');c=FenceControl(link);c.begin()
        with self.assertRaises(WouldBlock):c.service()
        link.dispatch()
        with self.assertRaises(WouldBlock):c.service()
        link.publish();c.service();self.assertEqual(c.receive(),'acknowledged')
        with self.assertRaises(WouldBlock):c.finish()
        self.assertEqual(link.deliver()[1],'stale');link.domain.release(b);c.finish()
    def test_duplicate_request_and_acks_block_reuse_until_consumed(self):
        c=FenceControl(FiniteTransport(),tag_bits=1);c.begin();c.duplicate_request();c.service(1);c.receive()
        with self.assertRaises(WouldBlock):c.finish()
        c.service();c.duplicate_ack();self.assertEqual(c.receive(1),'duplicate')
        with self.assertRaises(WouldBlock):c.finish()
        self.assertEqual(c.receive(),'duplicate');c.finish();self.assertEqual(c.begin(),1)
    def test_wrong_tag_cannot_ack_current_fence(self):
        c=FenceControl(FiniteTransport());c.begin();c.acks.append(c.encode('ack',1));self.assertEqual(c.receive(),'stale')
        with self.assertRaises(WouldBlock):c.finish()
        c.service();c.receive();c.finish()
    def test_old_data_duplicate_still_blocks_after_control_ack(self):
        link=FiniteTransport();q=link.domain.begin_query(0);b=link.domain.bind(q,0,0);link.submit(b,'refill');link.dispatch();link.publish();link.duplicate_response();link.deliver();link.domain.release(b)
        c=FenceControl(link);c.begin();c.service();c.receive()
        with self.assertRaises(WouldBlock):c.finish()
        self.assertEqual(link.deliver()[1],'duplicate');c.finish()
    def test_control_backpressure_does_not_consume_request(self):
        c=FenceControl(FiniteTransport(),capacity=1);c.begin()
        with self.assertRaises(WouldBlock):c.duplicate_request()
        c.service();c.retransmit()
        with self.assertRaises(WouldBlock):c.service()
        self.assertEqual(len(c.requests),1);c.receive();c.service();c.receive();c.finish()
    def test_page_payload_cancel_before_fence_ack(self):
        page=FinitePageValues();q=page.begin_query(0);page.request(q,0);page.write(q,0,[7]);page.evict(q,0)
        c=FenceControl(page);c.begin();page.dispatch();page.publish();self.assertEqual(page.backing[q][0],{0:[7]})
        c.service();c.receive()
        with self.assertRaises(WouldBlock):c.finish()
        self.assertEqual(page.deliver()[1],'stale');c.finish();self.assertEqual(page.backing,{})
    def test_one_bit_fence_wraps_with_all_queued_duplicates_drained(self):
        rng=random.Random(718);domain=FiniteCompletionDomain(transaction_bits=1,query_bits=1,generation_bits=1)
        link=FiniteTransport(domain);c=FenceControl(link,tag_bits=1)
        for cycle in range(200):
            q=domain.begin_query(0);b=domain.bind(q,0,0);link.submit(b,'pin');self.assertEqual(c.begin(),cycle%2)
            c.duplicate_request();link.dispatch();link.publish();link.duplicate_response()
            while c.requests:c.service(rng.randrange(len(c.requests)))
            c.duplicate_ack()
            while c.acks:c.receive(rng.randrange(len(c.acks)))
            with self.assertRaises(WouldBlock):c.finish()
            while link.responses:link.deliver(rng.randrange(len(link.responses)))
            domain.release(b);c.finish()
            self.assertFalse(c.requests or c.acks or link.peer_seen or domain.pending)
if __name__=='__main__':unittest.main()
