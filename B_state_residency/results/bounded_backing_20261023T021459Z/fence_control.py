"""Finite fence control packets over explicitly bounded closed queues.

Wire packet: opcode u8, tag u16 little-endian; only configured low tag bits used.
All delayed requests/ACKs must stay in modeled queues. Single owner; no hidden
network/old producers, authentication, packet loss, or device reset recovery.
"""
import struct
from .finite_completion import WouldBlock


class FenceControl:
    def __init__(self, target, tag_bits=2, capacity=4):
        if type(tag_bits) is not int or not 1<=tag_bits<=16 or type(capacity) is not int or capacity<1:
            raise ValueError('Invalid control channel shape')
        self.target=target
        self.data=target.link if hasattr(target,'link') else target
        self.tag_limit=1<<tag_bits
        self.capacity=capacity
        self.next_tag=0
        self.active_tag=None
        self.acknowledged=False
        self.requests=[]
        self.acks=[]

    def encode(self, operation, tag):
        if operation not in ('fence','ack') or type(tag) is not int or not 0<=tag<self.tag_limit:
            raise ValueError('Invalid control message')
        return struct.pack('<BH',operation=='ack',tag)

    def decode(self, packet):
        if type(packet) is not bytes or len(packet)!=3:raise ValueError('Malformed control packet')
        opcode,tag=struct.unpack('<BH',packet)
        if opcode>1 or tag>=self.tag_limit:raise ValueError('Control field out of range')
        return ('ack' if opcode else 'fence'),tag

    def begin(self):
        if self.active_tag is not None or self.requests or self.acks:
            raise WouldBlock('Prior control fence not retired')
        self.target.request_fence()
        self.active_tag=self.next_tag
        self.acknowledged=False
        self.requests.append(self.encode('fence',self.active_tag))
        return self.active_tag

    def retransmit(self):
        if self.active_tag is None:raise ValueError('No active fence')
        if len(self.requests)>=self.capacity:raise WouldBlock('Control request queue full')
        self.requests.append(self.encode('fence',self.active_tag))

    def duplicate_request(self, index=0):
        if len(self.requests)>=self.capacity:raise WouldBlock('Control request queue full')
        self.requests.append(bytes(bytearray(self.requests[index])))

    def service(self, index=0):
        operation,tag=self.decode(self.requests[index])
        if operation!='fence':raise ValueError('ACK on request channel')
        if self.active_tag is None or tag!=self.active_tag:
            self.requests.pop(index);return 'stale'
        if len(self.acks)>=self.capacity:raise WouldBlock('Control ACK queue full')
        # seal_peer refuses while data requests/work remain; data completions
        # can still be buffered, and do NOT become safe merely from this ACK.
        self.target.seal_peer()
        self.requests.pop(index)
        self.acks.append(self.encode('ack',tag))
        return 'ack_queued'

    def duplicate_ack(self, index=0):
        if len(self.acks)>=self.capacity:raise WouldBlock('Control ACK queue full')
        self.acks.append(bytes(bytearray(self.acks[index])))

    def receive(self, index=0):
        operation,tag=self.decode(self.acks[index])
        if operation!='ack':raise ValueError('Request on ACK channel')
        self.acks.pop(index)
        if self.active_tag is None or tag!=self.active_tag:return 'stale'
        if self.acknowledged:return 'duplicate'
        self.acknowledged=True
        return 'acknowledged'

    def finish(self):
        if self.active_tag is None or not self.acknowledged:
            raise WouldBlock('Current fence ACK not received')
        if self.requests or self.acks:raise WouldBlock('Control packets still queued')
        self.target.finish_fence()  # Also drains data queues, local bindings/payload.
        self.next_tag=(self.active_tag+1)%self.tag_limit
        self.active_tag=None;self.acknowledged=False
