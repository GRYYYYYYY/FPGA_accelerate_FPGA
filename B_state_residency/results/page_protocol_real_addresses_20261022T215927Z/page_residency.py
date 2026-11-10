"""Sequential executable specification for leased page writeback and refill.

Transfer completion is an explicit event, not a DMA implementation. A slot stays
leased until its transfer or pin is acknowledged, including after cancellation.
Versions/generations are unbounded. Backing capacity and reliable acknowledgments
are assumed; no throughput or finite-width ABA claim is made.
"""
from copy import deepcopy
from dataclasses import dataclass, field


class WouldBlock(RuntimeError):
    pass


@dataclass(frozen=True, eq=False)
class Transfer:
    query: object
    slot: int
    generation: int
    page: int
    kind: str


@dataclass(frozen=True, eq=False)
class Pin:
    query: object
    slot: int
    generation: int


@dataclass
class Slot:
    generation: int = 0
    query: object = None
    page: int = None
    values: dict = field(default_factory=dict)
    dirty: bool = False
    transfer: object = None
    pins: set = field(default_factory=set)


class ResidentPages:
    def __init__(self, context, capacity, page_bits=6):
        if type(capacity) is not int or capacity < 1 or not 1 <= page_bits <= 12:
            raise ValueError('Invalid page cache shape')
        self.context, self.page_bits = context, page_bits
        self.slots = [Slot() for _ in range(capacity)]
        self.query = None
        self.backing = {}
        self.pending = {}

    def _check(self, query):
        self.context._check(query)
        if query is not self.query:
            raise ValueError('Query not bound to this page cache')

    def bind(self, query):
        self.context._check(query)
        if query is self.query:
            return
        self.query = query
        self.backing = {}
        for slot in self.slots:
            # Old in-flight transfers/pins retain their physical slot leases.
            if not slot.transfer and not slot.pins:
                self._release(slot)

    @staticmethod
    def _release(slot):
        slot.query = slot.page = None
        slot.values = {}
        slot.dirty = False

    def _find(self, query, page):
        return next(((i, s) for i, s in enumerate(self.slots)
                     if s.query is query and s.page == page), None)

    def request(self, query, page):
        self._check(query)
        if type(page) is not int or page < 0:
            raise ValueError('Invalid page')
        found = self._find(query, page)
        if found:
            if found[1].transfer:
                raise WouldBlock('Page transfer pending')
            return None
        free = next(((i, s) for i, s in enumerate(self.slots) if s.query is None), None)
        if free is None:
            raise WouldBlock('Evict a page or await a slot acknowledgment')
        index, slot = free
        slot.generation += 1
        slot.query, slot.page = query, page
        if page not in self.backing:
            return None  # Never touched in this query: logical zero page.
        return self._transfer(index, 'refill', self.backing[page])

    def _transfer(self, index, kind, values):
        slot = self.slots[index]
        token = Transfer(slot.query, index, slot.generation, slot.page, kind)
        self.pending[token] = deepcopy(values)
        slot.transfer = token
        return token

    def _resident(self, query, node):
        self._check(query)
        if type(node) is not int or node < 0:
            raise ValueError('Invalid node')
        found = self._find(query, node >> self.page_bits)
        if not found or found[1].transfer:
            raise WouldBlock('Page not resident and ready')
        return found

    def read(self, query, node):
        _, slot = self._resident(query, node)
        return deepcopy(slot.values.get(node & ((1 << self.page_bits) - 1)))

    def write(self, query, node, value):
        _, slot = self._resident(query, node)
        slot.values[node & ((1 << self.page_bits) - 1)] = deepcopy(value)
        slot.dirty = True

    def pin(self, query, page):
        index, slot = self._resident(query, page << self.page_bits)
        token = Pin(query, index, slot.generation)
        slot.pins.add(token)
        return token

    def unpin(self, token):
        if not isinstance(token, Pin) or not 0 <= token.slot < len(self.slots):
            raise ValueError('Unknown pin acknowledgment')
        slot = self.slots[token.slot]
        if token not in slot.pins or token.generation != slot.generation or slot.query is not token.query:
            raise ValueError('Stale or duplicate pin acknowledgment')
        slot.pins.remove(token)
        if slot.query is not self.query and not slot.pins and not slot.transfer:
            self._release(slot)

    def evict(self, query, page):
        self._check(query)
        found = self._find(query, page)
        if found is None:
            raise ValueError('Page not present')
        index, slot = found
        if slot.transfer or slot.pins:
            raise WouldBlock('Page is leased')
        if slot.dirty:
            return self._transfer(index, 'writeback', slot.values)
        self._release(slot)
        return None

    def complete(self, token):
        # Caller must present the exact issued token, not a reconstructed tuple.
        if token not in self.pending:
            raise ValueError('Unknown, forged or duplicate transfer completion')
        slot = self.slots[token.slot]
        if slot.transfer is not token or slot.generation != token.generation or slot.query is not token.query:
            raise ValueError('Transfer lease mismatch')
        valid = token.query is self.query
        if valid:
            try:
                self.context._check(token.query)
            except ValueError:
                valid = False
        values = self.pending.pop(token)
        slot.transfer = None
        if not valid:
            self._release(slot)
            return False
        if token.kind == 'writeback':
            self.backing[token.page] = values
            self._release(slot)
        else:
            slot.values = values
            slot.dirty = False
        return True
