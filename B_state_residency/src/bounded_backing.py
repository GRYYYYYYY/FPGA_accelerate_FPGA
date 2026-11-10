"""Bounded byte-addressed backing for synthetic signed-int64 page values.

A bitmap distinguishes an absent label from zero. Addresses and owners stay
quarantined until the enclosing closed transport fence retires all packets.
This is not the router's NodeDyn ABI, an allocator for actual DDR, or total RSS.
"""
from collections import deque
import struct
from .finite_completion import WouldBlock
from .finite_page_values import FinitePageValues,PageCheckpoint


class IntegerPageCodec:
    def __init__(self,page_bits):
        if type(page_bits) is not int or not 1<=page_bits<=12:raise ValueError('Invalid page bits')
        self.entries=1<<page_bits
        self.bitmap_bytes=(self.entries+7)//8
        self.payload_bytes=self.bitmap_bytes+8*self.entries
        self.stride=((self.payload_bytes+63)//64)*64

    def encode(self,values):
        if type(values) is not dict:raise ValueError('Invalid page map')
        payload=bytearray(self.stride)
        for offset,value in values.items():
            if type(offset) is not int or not 0<=offset<self.entries or type(value) is not int or not -(1<<63)<=value<(1<<63):
                raise ValueError('Value/offset does not fit fixed page codec')
            payload[offset//8]|=1<<(offset%8)
            struct.pack_into('<q',payload,self.bitmap_bytes+8*offset,value)
        return bytes(payload)

    def decode(self,payload):
        if type(payload) is not bytes or len(payload)!=self.stride:raise ValueError('Invalid page payload')
        return {i:struct.unpack_from('<q',payload,self.bitmap_bytes+8*i)[0] for i in range(self.entries) if payload[i//8]&(1<<(i%8))}


class BackingPool:
    def __init__(self,stride,budget_bytes,address_bits=32):
        if (type(stride) is not int or stride<=0 or stride%64 or type(budget_bytes) is not int
                or budget_bytes<stride or type(address_bits) is not int or not 1<=address_bits<=64
                or budget_bytes>(1<<address_bits)):
            raise ValueError('Invalid backing byte/address budget')
        self.stride=stride;self.pages=budget_bytes//stride
        self.memory=bytearray(self.pages*stride)
        self.free=deque(range(self.pages));self.owners={};self.leases={}

    def preflight(self,owner):
        if owner not in self.owners and not self.free:raise WouldBlock('Backing byte capacity exhausted')

    def reserve(self,owner):
        self.preflight(owner)
        if owner not in self.owners:self.owners[owner]=self.free.popleft()*self.stride
        return self.owners[owner]

    def pin(self,owner,descriptor):
        if descriptor in self.leases:raise ValueError('Duplicate backing lease')
        if owner not in self.owners:raise ValueError('Backing owner not reserved')
        self.leases[descriptor]=(owner,self.owners[owner])

    def write(self,owner,payload):
        if type(payload) is not bytes or len(payload)!=self.stride:raise ValueError('Wrong backing page bytes')
        address=self.owners[owner];self.memory[address:address+self.stride]=payload

    def read(self,owner):
        address=self.owners[owner];return bytes(self.memory[address:address+self.stride])

    def unpin(self,descriptor):
        if descriptor not in self.leases:raise ValueError('Unknown backing lease')
        del self.leases[descriptor]

    def reset_after_fence(self):
        if self.leases:raise WouldBlock('Backing payload still leased')
        self.owners.clear();self.free=deque(range(self.pages))
        # Do not rely on clearing memory: every newly published page overwrites
        # the complete stride. Ownership and host readiness gate all reads.


class BoundedPageValues(FinitePageValues):
    def __init__(self,*,backing_bytes,page_bits=2,address_bits=32,**configuration):
        super().__init__(page_bits=page_bits,**configuration)
        self.codec=IntegerPageCodec(page_bits)
        self.pool=BackingPool(self.codec.stride,backing_bytes,address_bits)

    def write(self,query,node,value):
        if type(value) is not int or not -(1<<63)<=value<(1<<63):raise ValueError('Only signed int64 synthetic values supported')
        super().write(query,node,value)

    def evict(self,query,page):
        b=self._find(query,page)
        if b is None:raise ValueError('Page absent')
        if self._pending(b.slot):raise WouldBlock('Page leased')
        if not self.dirty[b.slot]:return super().evict(query,page)
        owner=(query,page)
        self.codec.encode(self.values[b.slot])
        self.pool.preflight(owner);self._preflight_submit()
        self.pool.reserve(owner)
        descriptor=super().evict(query,page)
        self.pool.pin(owner,descriptor)
        return descriptor

    def request(self,query,page):
        b=super().request(query,page)
        for t in self._pending(b.slot):
            if t.kind=='refill':self.pool.pin((query,page),t)
        return b

    def publish(self,index=0):
        t=self.link.work[index];owner=(t.binding.query,t.binding.page)
        if t.kind=='writeback':payload=self.codec.encode(self.outbound[t.transaction])
        elif t.kind=='refill':payload=self.codec.decode(self.pool.read(owner))
        else:payload=None
        self.link.publish(index)
        if t.kind=='writeback':
            self.pool.write(owner,payload)
            self.backing[t.binding.query][t.binding.page]=self.codec.decode(payload)
            self.writeback_effects+=1
        elif t.kind=='refill':
            self.inbound[t.transaction]=payload;self.refill_effects+=1

    def deliver(self,index=0):
        descriptor,status=super().deliver(index)
        if status!='duplicate' and descriptor.kind in ('writeback','refill'):self.pool.unpin(descriptor)
        return descriptor,status

    def restore(self,query,checkpoint):
        if type(checkpoint) is not PageCheckpoint or type(checkpoint.pages) is not dict:
            raise ValueError('Invalid checkpoint')
        encoded={page:self.codec.encode(values) for page,values in checkpoint.pages.items()}
        new_owners=sum((query,page) not in self.pool.owners for page in encoded)
        if new_owners>len(self.pool.free):raise WouldBlock('Checkpoint exceeds remaining backing capacity')
        super().restore(query,checkpoint)
        for page,payload in encoded.items():self.pool.reserve((query,page));self.pool.write((query,page),payload)

    def finish_fence(self):
        if self.pool.leases:raise WouldBlock('Physical backing references remain')
        super().finish_fence()
        self.pool.reset_after_fence()
