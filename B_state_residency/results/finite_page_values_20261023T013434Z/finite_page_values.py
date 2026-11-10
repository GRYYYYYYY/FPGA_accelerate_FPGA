"""Finite wire page-value model over the closed bounded transport simulator.

Peer publication writes query-namespaced backing BEFORE host acknowledgment.
Namespaces/transfer buffers remain quarantined until the modeled transport fence.
No real DMA, shared address reuse, price computation, or concurrent host is modeled.
"""
from copy import deepcopy
from .finite_completion import FiniteCompletionDomain,WouldBlock
from .finite_transport import FiniteTransport


class FinitePageValues:
    def __init__(self, slots=2, page_bits=2, queue_capacity=4, **widths):
        if type(page_bits) is not int or not 1<=page_bits<=12:
            raise ValueError('Invalid page shape')
        self.link=FiniteTransport(FiniteCompletionDomain(slots=slots,**widths),queue_capacity)
        self.page_bits=page_bits
        self.values=[{} for _ in range(slots)]
        self.dirty=[False]*slots
        self.backing={}
        self.outbound={}
        self.inbound={}
        self.writeback_effects=0
        self.refill_effects=0

    @property
    def domain(self):return self.link.domain

    def _pending(self, slot):
        return [t for t in self.domain.pending.values() if t.binding.slot==slot]

    def _release(self, binding):
        self.domain.release(binding)
        self.values[binding.slot]={};self.dirty[binding.slot]=False

    def begin_query(self, price):
        q=self.domain.begin_query(price)
        self.backing[q]={}
        for b in list(self.domain.bindings):
            if b is not None and not self._pending(b.slot):self._release(b)
        return q

    def _check(self, query):
        if self.domain.draining or query!=self.domain.active:
            raise ValueError('Query invalidated')

    def _find(self, query, page):
        self._check(query)
        if type(page) is not int or not 0<=page<self.domain.page_limit:
            raise ValueError('Page out of range')
        return next((b for b in self.domain.bindings if b is not None and b.query==query and b.page==page),None)

    def _preflight_submit(self):
        if len(self.link.requests)>=self.link.capacity:raise WouldBlock('Request queue full')
        if len(self.domain.used_transactions)>=self.domain.transaction_limit:
            raise WouldBlock('Finite transaction IDs exhausted; fence required')

    def request(self, query, page):
        b=self._find(query,page)
        if b is not None:
            if any(t.kind!='pin' for t in self._pending(b.slot)):raise WouldBlock('Page IO pending')
            return b
        slot=next((i for i,b in enumerate(self.domain.bindings) if b is None),None)
        if slot is None:raise WouldBlock('No free slot')
        saved=page in self.backing[query]
        # Single-owner preflight: failure cannot burn a slot generation on retry.
        if saved:self._preflight_submit()
        b=self.domain.bind(query,slot,page)
        self.values[slot]={};self.dirty[slot]=False
        if saved:self.link.submit(b,'refill')
        return b

    def _ready(self, query, node):
        if type(node) is not int or node<0:raise ValueError('Node out of range')
        b=self._find(query,node>>self.page_bits)
        if b is None or any(t.kind!='pin' for t in self._pending(b.slot)):
            raise WouldBlock('Page not ready')
        return b,node&((1<<self.page_bits)-1)

    def read(self, query, node):
        b,offset=self._ready(query,node)
        return deepcopy(self.values[b.slot].get(offset))

    def write(self, query, node, value):
        b,offset=self._ready(query,node)
        self.values[b.slot][offset]=deepcopy(value);self.dirty[b.slot]=True

    def pin(self, query, page):
        b,_=self._ready(query,page<<self.page_bits)
        return self.link.submit(b,'pin')

    def evict(self, query, page):
        b=self._find(query,page)
        if b is None:raise ValueError('Page absent')
        if self._pending(b.slot):raise WouldBlock('Page leased')
        if not self.dirty[b.slot]:self._release(b);return None
        snapshot=deepcopy(self.values[b.slot])
        t=self.link.submit(b,'writeback')
        self.outbound[t.transaction]=snapshot
        return t

    def dispatch(self, index=0):return self.link.dispatch(index)

    def publish(self, index=0):
        t=self.link.work[index]
        if t.kind=='writeback':payload=deepcopy(self.outbound[t.transaction])
        elif t.kind=='refill':payload=deepcopy(self.backing[t.binding.query][t.binding.page])
        else:payload=None
        self.link.publish(index)  # Backpressure checked before any data side effect.
        if t.kind=='writeback':
            self.backing[t.binding.query][t.binding.page]=payload
            self.writeback_effects+=1
        elif t.kind=='refill':
            self.inbound[t.transaction]=payload
            self.refill_effects+=1

    def deliver(self, index=0):
        t,status=self.link.deliver(index)
        if status=='duplicate':return t,status
        if status=='valid' and t.kind=='refill':
            self.values[t.binding.slot]=self.inbound[t.transaction]
            self.dirty[t.binding.slot]=False
        self.inbound.pop(t.transaction,None);self.outbound.pop(t.transaction,None)
        if ((status=='valid' and t.kind=='writeback') or status=='stale') and not self._pending(t.binding.slot):
            self._release(t.binding)
        return t,status

    def request_fence(self):
        self.link.request_fence()
        for b in list(self.domain.bindings):
            if b is not None and not self._pending(b.slot):self._release(b)

    def seal_peer(self):self.link.seal_peer()

    def finish_fence(self):
        if self.outbound or self.inbound:raise WouldBlock('Payload leases remain')
        self.link.finish_fence()
        self.backing.clear()
