"""Bit-preserving five-field search scratch; global history is deliberately separate."""
from dataclasses import dataclass
import struct
from .bounded_backing import BackingPool, BoundedPageValues
from .finite_page_values import FinitePageValues


@dataclass(frozen=True)
class ScratchLabel:
    lb_bits: int = 0
    upstream_bits: int = 0
    prev: int = 0
    visited: int = 0
    target: int = 0

    def validate(self):
        for value in (self.lb_bits, self.upstream_bits):
            if type(value) is not int or not 0 <= value < (1 << 32):
                raise ValueError('Invalid float32 bits')
        for value in (self.prev, self.visited):
            if type(value) is not int or not -(1 << 31) <= value < (1 << 31):
                raise ValueError('Invalid signed int32')
        if type(self.target) is not int or not 0 <= self.target <= 255:
            raise ValueError('Invalid target byte')


class ScratchPageCodec:
    record = struct.Struct('<IIiiB3x')

    def __init__(self, page_bits):
        if type(page_bits) is not int or not 1 <= page_bits <= 12:
            raise ValueError('Invalid page shape')
        self.entries = 1 << page_bits
        self.bitmap_bytes = (self.entries + 7) // 8
        self.payload_bytes = self.bitmap_bytes + self.entries * self.record.size
        self.stride = ((self.payload_bytes + 63) // 64) * 64

    def encode(self, values):
        if type(values) is not dict:
            raise ValueError('Invalid page map')
        payload = bytearray(self.stride)
        for offset, value in values.items():
            if type(offset) is not int or not 0 <= offset < self.entries or type(value) is not ScratchLabel:
                raise ValueError('Invalid scratch entry')
            value.validate()
            payload[offset // 8] |= 1 << (offset % 8)
            self.record.pack_into(payload, self.bitmap_bytes + offset * self.record.size,
                                  value.lb_bits, value.upstream_bits, value.prev, value.visited, value.target)
        return bytes(payload)

    def decode(self, payload):
        if type(payload) is not bytes or len(payload) != self.stride:
            raise ValueError('Invalid page payload')
        return {offset: ScratchLabel(*self.record.unpack_from(payload, self.bitmap_bytes + offset * self.record.size))
                for offset in range(self.entries) if payload[offset // 8] & (1 << (offset % 8))}


class ScratchPageValues(BoundedPageValues):
    def __init__(self, *, backing_bytes, page_bits=6, address_bits=32, **configuration):
        FinitePageValues.__init__(self, page_bits=page_bits, **configuration)
        self.codec = ScratchPageCodec(page_bits)
        self.pool = BackingPool(self.codec.stride, backing_bytes, address_bits)

    def write(self, query, node, value):
        if type(value) is not ScratchLabel:
            raise ValueError('Expected five-field scratch value')
        value.validate()
        FinitePageValues.write(self, query, node, value)
