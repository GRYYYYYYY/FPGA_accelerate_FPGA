"""Closed, bounded, single-owner transport simulator for finite descriptors.

Every delayed/duplicated packet must remain in one of these queues. No packets
may be injected from an unmodeled channel after the peer fence. This simulator
provides no real DMA, payload effects, authentication, or concurrent producers.
"""
from copy import deepcopy
from .finite_completion import FiniteCompletionDomain, WouldBlock


class FiniteTransport:
    def __init__(self, domain=None, queue_capacity=4):
        if type(queue_capacity) is not int or queue_capacity<1:
            raise ValueError('Invalid queue capacity')
        self.domain=domain if domain is not None else FiniteCompletionDomain()
        self.capacity=queue_capacity
        self.requests=[]
        self.work=[]
        self.responses=[]
        self.peer_seen={}
        self.peer_sealed=False

    def submit(self, binding, kind):
        if len(self.requests)>=self.capacity:raise WouldBlock('Request queue full')
        packet=self.domain.issue(binding,kind)
        self.requests.append(deepcopy(packet))
        return packet

    def duplicate_request(self, index=0):
        if len(self.requests)>=self.capacity:raise WouldBlock('Request queue full')
        self.requests.append(deepcopy(self.requests[index]))

    def dispatch(self, index=0):
        if self.peer_sealed:raise WouldBlock('Peer sealed')
        packet=self.requests[index]
        prior=self.peer_seen.get(packet.transaction)
        if prior is not None:
            if prior!=packet:raise ValueError('Transaction reused before fence')
            self.requests.pop(index)
            return False  # Peer accepts this transaction only once.
        if len(self.work)>=self.capacity:raise WouldBlock('Peer work queue full')
        if self.domain.pending.get(packet.transaction)!=packet:
            raise ValueError('Request not issued by domain')
        self.requests.pop(index)
        self.peer_seen[packet.transaction]=packet
        self.work.append(packet)
        return True

    def publish(self, index=0):
        if self.peer_sealed:raise WouldBlock('Peer sealed')
        if len(self.responses)>=self.capacity:raise WouldBlock('Completion queue full')
        packet=self.work[index]
        self.work.pop(index);self.responses.append(deepcopy(packet))

    def duplicate_response(self, index=0):
        if len(self.responses)>=self.capacity:raise WouldBlock('Completion queue full')
        self.responses.append(deepcopy(self.responses[index]))

    def deliver(self, index=0):
        packet=self.responses[index]
        if self.peer_seen.get(packet.transaction)!=packet:
            raise ValueError('Completion not produced by peer')
        if packet.transaction not in self.domain.pending:
            self.responses.pop(index)
            return packet,'duplicate'
        valid=self.domain.complete(packet)
        self.responses.pop(index)
        return packet,'valid' if valid else 'stale'

    def request_fence(self):
        self.domain.request_fence()

    def seal_peer(self):
        if not self.domain.draining:raise ValueError('Fence not requested')
        if self.requests or self.work:raise WouldBlock('Peer still has requests/work')
        self.peer_sealed=True

    def finish_fence(self):
        if not self.peer_sealed:raise WouldBlock('No peer fence acknowledgment')
        if self.requests or self.work or self.responses:
            raise WouldBlock('Packets still buffered')
        # No caller-supplied quiescence boolean: derive it from this simulator.
        self.domain.recycle_after_fence(peer_quiescent=True,completion_queue_empty=True)
        self.peer_seen.clear();self.peer_sealed=False
