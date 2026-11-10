"""Finite wire ownership ledger, not a DMA/data-value implementation.

Equality is by wire fields, never Python identity or a hidden incarnation.
IDs are quarantined until a trusted transport fence proves both peer quiescence
and empty completion queues. A false fence can cause ABA after reuse; no finite
identifier can distinguish an identical old packet under unbounded delay.
"""
from dataclasses import dataclass


class WouldBlock(RuntimeError):
    pass


@dataclass(frozen=True)
class QueryKey:
    query: int
    price: int


@dataclass(frozen=True)
class Binding:
    query: QueryKey
    slot: int
    generation: int
    page: int


@dataclass(frozen=True)
class Descriptor:
    transaction: int
    binding: Binding
    kind: str


class FiniteCompletionDomain:
    def __init__(self, slots=2, transaction_bits=2, query_bits=2,
                 generation_bits=2, price_bits=4, page_bits=8):
        shape=(slots,transaction_bits,query_bits,generation_bits,price_bits,page_bits)
        if any(type(v) is not int or v<1 for v in shape) or any(v>16 for v in shape[1:-1]) or page_bits>32:
            raise ValueError('Invalid finite shape')
        self.transaction_limit=1<<transaction_bits
        self.query_limit=1<<query_bits
        self.generation_limit=1<<generation_bits
        self.price_limit=1<<price_bits
        self.page_limit=1<<page_bits
        self.bindings=[None]*slots
        self.generations=[-1]*slots
        self.used_transactions=set()
        self.used_queries=set()
        self.pending={}
        self.active=None
        self.draining=False

    def _open(self):
        if self.draining:
            raise WouldBlock('Transport fence in progress')

    def begin_query(self, price):
        self._open()
        if type(price) is not int or not 0<=price<self.price_limit:
            raise ValueError('Price version does not fit')
        available=next((i for i in range(self.query_limit) if i not in self.used_queries),None)
        if available is None:raise WouldBlock('Query IDs exhausted; drain before reuse')
        key=QueryKey(available,price)
        self.used_queries.add(available)
        self.active=key
        return key

    def bind(self, query, slot, page):
        self._open()
        if type(query) is not QueryKey or query!=self.active:
            raise ValueError('Query invalidated')
        if type(slot) is not int or not 0<=slot<len(self.bindings) or type(page) is not int or not 0<=page<self.page_limit:
            raise ValueError('Binding out of range')
        if self.bindings[slot] is not None:raise WouldBlock('Slot still bound')
        generation=self.generations[slot]+1
        if generation>=self.generation_limit:raise WouldBlock('Slot generation exhausted; drain')
        binding=Binding(query,slot,generation,page)
        self.generations[slot]=generation
        self.bindings[slot]=binding
        return binding

    def _bound(self, binding):
        if type(binding) is not Binding or type(binding.slot) is not int or not 0<=binding.slot<len(self.bindings) or self.bindings[binding.slot]!=binding:
            raise ValueError('Unknown slot binding')

    def issue(self, binding, kind):
        self._open();self._bound(binding)
        if binding.query!=self.active:raise ValueError('Query invalidated')
        if kind not in ('refill','writeback','pin'):raise ValueError('Invalid operation')
        same=[d for d in self.pending.values() if d.binding.slot==binding.slot]
        if (kind!='pin' and same) or (kind=='pin' and any(d.kind!='pin' for d in same)):
            raise WouldBlock('Incompatible outstanding slot leases')
        transaction=next((i for i in range(self.transaction_limit) if i not in self.used_transactions),None)
        if transaction is None:raise WouldBlock('Transaction IDs exhausted; drain before reuse')
        d=Descriptor(transaction,binding,kind)
        self.used_transactions.add(transaction);self.pending[transaction]=d
        return d

    def complete(self, descriptor):
        if type(descriptor) is not Descriptor or type(descriptor.transaction) is not int:
            raise ValueError('Invalid completion')
        expected=self.pending.get(descriptor.transaction)
        if expected is None or descriptor!=expected:
            raise ValueError('Unknown, duplicate, or mismatched completion')
        self._bound(descriptor.binding)
        del self.pending[descriptor.transaction]
        return not self.draining and descriptor.binding.query==self.active

    def release(self, binding):
        self._bound(binding)
        if any(d.binding.slot==binding.slot for d in self.pending.values()):
            raise WouldBlock('Cannot reuse slot before every acknowledgment')
        self.bindings[binding.slot]=None

    def request_fence(self):
        self.draining=True;self.active=None

    def recycle_after_fence(self, *, peer_quiescent, completion_queue_empty):
        # These two predicates MUST come from a trusted transport implementation,
        # not merely local outstanding==0 or a host timeout.
        if not self.draining:raise ValueError('Fence not requested')
        if self.pending or any(b is not None for b in self.bindings):
            raise WouldBlock('Local leases/bindings not drained')
        if peer_quiescent is not True or completion_queue_empty is not True:
            raise WouldBlock('Transport not proven quiescent')
        self.used_transactions.clear();self.used_queries.clear()
        self.generations=[-1]*len(self.bindings)
        self.draining=False
