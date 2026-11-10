"""Executable CPU protocol specification, not a concurrent/device implementation.

Paths here are already filtered resource sets, not raw source/sink node paths.
Versions are unbounded integers; finite-width hardware needs a drain protocol.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class Delta:
    design: object
    before: int
    after: int
    # resource, distinct-net occupancy, historical price
    rows: tuple


@dataclass(frozen=True)
class Query:
    design: object
    context: int
    incarnation: int
    epoch: int
    price_version: int
    replica_generation: int


@dataclass(frozen=True)
class Snapshot:
    design: object
    version: int
    rows: tuple


def checked_rows(rows):
    values = {}
    for resource, occupancy, history in rows:
        if any(type(v) is not int or v < 0 for v in (resource, occupancy, history)):
            raise ValueError('Invalid price row')
        if resource in values:
            raise ValueError('Duplicate resource in update')
        values[resource] = (occupancy, history)
    return values


class Authority:
    """CPU owns references and serializes commits by global version validation."""
    def __init__(self, connection_nets):
        self.design = object()
        self.connection_nets = dict(connection_nets)
        self.paths = {c: frozenset() for c in connection_nets}
        self.references = defaultdict(Counter)
        self.history = {}
        self.version = 0

    def occupancy(self, resource):
        return len(self.references.get(resource, {}))

    def snapshot(self):
        resources = self.references.keys() | self.history.keys()
        return Snapshot(self.design, self.version, tuple(
            (r, self.occupancy(r), self.history.get(r, 0)) for r in sorted(resources)))

    def _replace(self, connection, resources, query):
        if query.design is not self.design or query.price_version != self.version:
            raise ValueError('Stale or foreign price snapshot')
        net = self.connection_nets[connection]
        new = frozenset(resources)
        if any(type(r) is not int or r < 0 for r in new):
            raise ValueError('Resources must be nonnegative integer IDs')
        old = self.paths[connection]
        dirty = old ^ new
        for resource in old - new:
            owners = self.references[resource]
            owners[net] -= 1
            if not owners[net]:
                del owners[net]
            if not owners:
                del self.references[resource]
        for resource in new - old:
            self.references[resource][net] += 1
        self.paths[connection] = new
        return self._delta(dirty)

    def add_history(self, increments):
        increments = dict(increments)
        if any(type(r) is not int or r < 0 or type(value) is not int or value < 0
               for r, value in increments.items()):
            raise ValueError('Historical price must not decrease')
        for resource, value in increments.items():
            self.history[resource] = self.history.get(resource, 0) + value
        return self._delta(increments)

    def _delta(self, dirty):
        before = self.version
        self.version += 1
        rows = tuple((r, self.occupancy(r), self.history.get(r, 0)) for r in sorted(dirty))
        return Delta(self.design, before, self.version, rows)


class Replica:
    """Ordered exact-value updates; duplicate delivery is idempotent, gaps fail."""
    def __init__(self, design):
        self.design = design
        self.version = 0
        self.values = {}
        self.last = None
        self.generation = 0

    def install(self, snapshot):
        if snapshot.design is not self.design or snapshot.version < self.version:
            raise ValueError('Foreign or obsolete snapshot')
        values = checked_rows(snapshot.rows)
        self.values = values
        self.version = snapshot.version
        self.last = None
        # Even a same-version recovery invalidates in-flight query handles.
        self.generation += 1
        return self.version

    def apply(self, delta):
        if delta.design is not self.design:
            raise ValueError('Foreign design')
        if delta == self.last:
            return self.version
        if delta.before != self.version or delta.after != delta.before + 1:
            raise ValueError('Out-of-order update; replay missing deltas or resnapshot')
        # Validation completes before any mutation; integer keys cannot invoke
        # user callbacks. This is atomic in this sequential specification only.
        values = checked_rows(delta.rows)
        self.values.update(values)
        self.version = delta.after
        self.last = delta
        return self.version


class Context:
    """One active query per context; pinned pages cannot be reclaimed mid-query."""
    def __init__(self, authority, replica, context, epoch_bits=32):
        if not 1 <= epoch_bits <= 32 or replica.design is not authority.design:
            raise ValueError('Invalid epoch width or design binding')
        self.authority, self.replica, self.context = authority, replica, context
        self.limit = (1 << epoch_bits) - 1
        self.epoch = self.incarnation = 0
        self.active = None
        self.labels = {}
        self.pages = set()
        self.pinned = set()

    def begin(self):
        if self.active is not None or self.replica.version != self.authority.version:
            raise ValueError('Context busy or replica is behind authority')
        self.epoch += 1
        if self.epoch > self.limit:
            self.labels.clear()
            self.epoch = 1
            self.incarnation += 1
        self.active = Query(self.authority.design, self.context, self.incarnation,
                            self.epoch, self.replica.version, self.replica.generation)
        return self.active

    def _check(self, query):
        if query is None or query is not self.active:
            raise ValueError('Inactive or foreign query handle')
        if (query.price_version != self.replica.version or
                query.replica_generation != self.replica.generation):
            raise ValueError('Price changed; discard labels and restart query')

    def write(self, query, node, value, page):
        self._check(query)
        self.pages.add(page)
        self.pinned.add(page)
        self.labels[node] = (query, value, page)

    def read(self, query, node):
        self._check(query)
        label = self.labels.get(node)
        return label[1] if label and label[0] is query else None

    def reclaim(self, page):
        if page in self.pinned:
            raise ValueError('Page has an active lease')
        self.pages.discard(page)
        self.labels = {n: label for n, label in self.labels.items() if label[2] != page}

    def finish(self, query):
        # Cancellation is allowed even after a price update invalidated labels.
        if query is None or query is not self.active:
            raise ValueError('Inactive or foreign query handle')
        self.active = None
        self.pinned.clear()

    def commit(self, query, connection, resources):
        self._check(query)
        delta = self.authority._replace(connection, resources, query)
        self.finish(query)
        return delta
