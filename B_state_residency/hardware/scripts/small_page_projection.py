"""Public command projection for eight-node, 192-byte pages."""
from collections import Counter

class Projection:
    def __init__(self, host, pages):
        self.host = host; self.pages = pages
        self.owners = {}; self.pending = None; self.labels = []; self.bitmap = 0
        self.counts = Counter(); self.transfers = 0; self.peak = 0; self.queries = 0
        self.max_generation = 0; self.max_transaction = 0

    def public(self, a, frame=0, page_index=0):
        row = (a[0], a[1], a[2], a[3], a[4], a[5], a[9], a[10], a[11],
               a[15], a[16], a[17], a[18], a[19], a[20], frame, page_index)
        self.host.write(' '.join(format(x, 'x') for x in row) + '\n')
        self.counts[str(a[0])] += 1

    def emit_row(self, a):
        if a[15] != 0:
            raise ValueError('Unexpected failing actual command')
        if not 0 <= a[5] < 65536:
            raise ValueError('Generation cannot be represented')
        self.max_generation = max(self.max_generation, a[5])
        op = a[0]
        if self.pending is not None:
            header, frame = self.pending
            reading = header[0] == 6
            if a[1:6] != header[1:6] or a[6] != header[19] or a[7] != reading:
                raise ValueError('Transport descriptor changed')
            if len(self.labels) < 8:
                if op != (7 if reading else 9) or a[9] != len(self.labels):
                    raise ValueError('Transport records reordered')
                present, word = (a[8], a[12]) if reading else (a[17], a[16])
                if word >> 136 or (not present and word):
                    raise ValueError('Noncanonical raw record')
                self.bitmap |= present << len(self.labels)
                self.labels.append(word.to_bytes(20, 'little'))
            else:
                if op != 8:
                    raise ValueError('Missing completion')
                blob = self.bitmap.to_bytes(1, 'little') + b''.join(self.labels) + bytes(31)
                for offset in range(0, 192, 64):
                    self.pages.write(format(int.from_bytes(blob[offset:offset + 64], 'little'), '0128x') + '\n')
                self.public(header, frame, self.transfers)
                self.transfers += 1; self.pending = None
            return
        if op in (5, 6):
            key = a[4], a[3], a[2]
            if op == 5 and key not in self.owners:
                self.owners[key] = len(self.owners)
            if key not in self.owners or len(self.owners) > 163840:
                raise ValueError('Unknown or oversized backing owner')
            self.peak = max(self.peak, len(self.owners))
            if not 0 <= a[19] < 65536:
                raise ValueError('Transaction cannot be represented')
            self.max_transaction = max(self.max_transaction, a[19])
            self.pending = (a, self.owners[key]); self.labels = []; self.bitmap = 0
        elif op in (7, 8, 9):
            raise ValueError('Orphan internal command')
        else:
            if op == 11:
                self.owners.clear()
            if op == 0:
                self.queries += 1
            self.public(a)

