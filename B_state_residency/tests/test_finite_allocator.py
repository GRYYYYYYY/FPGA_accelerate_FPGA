import random
import unittest
from src.finite_completion import FiniteCompletionDomain
from src.finite_completion_fast import SequentialFiniteDomain

class FiniteAllocatorTests(unittest.TestCase):
    def test_random_event_by_event_differential(self):
        rng=random.Random(78291)
        for bits in [1,2,4]:
            a=FiniteCompletionDomain(slots=3,transaction_bits=bits,query_bits=2,generation_bits=2)
            b=SequentialFiniteDomain(slots=3,transaction_bits=bits,query_bits=2,generation_bits=2)
            def call(method,*args,**kwargs):
                results=[]
                for model in [a,b]:
                    try:results.append(('ok',getattr(model,method)(*args,**kwargs)))
                    except (ValueError,RuntimeError) as e:results.append((type(e).__name__,str(e)))
                self.assertEqual(results[0],results[1]);self.assertEqual(a.__dict__,b.__dict__)
                self.assertEqual(b.used_transactions,set(range(len(b.used_transactions))))
            for step in range(5000):
                action=rng.randrange(7)
                if action==0:call('begin_query',rng.randrange(16))
                elif action==1 and a.active is not None:call('bind',a.active,rng.randrange(3),rng.randrange(8))
                elif action==2 and any(a.bindings):call('issue',rng.choice([x for x in a.bindings if x]),rng.choice(['pin','refill','writeback','bad']))
                elif action==3 and a.pending:call('complete',rng.choice(list(a.pending.values())))
                elif action==4 and any(a.bindings):call('release',rng.choice([x for x in a.bindings if x]))
                elif action==5:call('request_fence')
                elif action==6:call('recycle_after_fence',peer_quiescent=True,completion_queue_empty=True)
    def test_16_bit_exhaustion_never_reuses_before_fence(self):
        d=SequentialFiniteDomain(transaction_bits=16);q=d.begin_query(0);binding=d.bind(q,0,0)
        for index in range(1<<16):
            t=d.issue(binding,'pin');self.assertEqual(t.transaction,index);self.assertTrue(d.complete(t))
        with self.assertRaises(RuntimeError):d.issue(binding,'pin')
        d.release(binding);d.request_fence();d.recycle_after_fence(peer_quiescent=True,completion_queue_empty=True)
        q=d.begin_query(0);binding=d.bind(q,0,0);self.assertEqual(d.issue(binding,'pin').transaction,0)
if __name__=='__main__':unittest.main()
