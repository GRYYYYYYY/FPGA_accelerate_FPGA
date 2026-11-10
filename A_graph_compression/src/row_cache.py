"""Identical bounded LRU policy for any adjacency representation."""
from collections import OrderedDict


class RowCache:
    def __init__(self,provider,capacity):
        if capacity<0:raise ValueError('Negative row cache capacity')
        self.provider=provider
        self.capacity=capacity
        self.cache=OrderedDict()
        self.hits=self.misses=self.evictions=0
        self.resident_edges=self.peak_rows=self.peak_edges=0

    def neighbors(self,node):
        if node in self.cache:
            self.hits+=1
            self.cache.move_to_end(node)
            return self.cache[node]
        self.misses+=1
        # Unknown adjacency exceptions propagate; never cache them as empty rows.
        row=self.provider.neighbors(node)
        if self.capacity:
            if len(self.cache)==self.capacity:
                _,old=self.cache.popitem(last=False)
                self.resident_edges-=len(old)
                self.evictions+=1
            self.cache[node]=row
            self.resident_edges+=len(row)
            self.peak_rows=max(self.peak_rows,len(self.cache))
            self.peak_edges=max(self.peak_edges,self.resident_edges)
        return row

    def statistics(self):
        return {'capacity_rows':self.capacity,'resident_rows':len(self.cache),
                'resident_edges':self.resident_edges,'peak_rows':self.peak_rows,
                'peak_edges':self.peak_edges,'hits':self.hits,'misses':self.misses,
                'evictions':self.evictions,
                'memory_scope':'Row and edge counts only; process memory must be measured separately.'}
