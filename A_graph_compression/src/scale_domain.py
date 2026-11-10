"""Nested real source-tile prefixes; selected rows retain complete adjacency."""
from canonical_graph import split_name
from heldout import select_sources


def source_prefix(graph, denominator):
    if type(denominator) is not int or denominator < 1:
        raise ValueError('Positive integer denominator required')
    tiles = {split_name(root)[0] for root in graph['roots']}
    def order(tile):
        attrs = graph['tiles'][tile]
        return (int(attrs['SLR_REGION_ID']), int(attrs['COLUMN']), int(attrs['ROW']), tile)
    tiles = sorted(tiles, key=order)
    count = max(1, (len(tiles)+denominator-1)//denominator)
    selected = set(tiles[:count])
    roots = sorted(root for root in graph['roots'] if split_name(root)[0] in selected)
    return roots, tiles[:count]


def make_domain(graph, denominator):
    roots, tiles = source_prefix(graph, denominator)
    # Keep the original full-domain control exactly, including its provenance.
    domain = graph if denominator == 1 else select_sources(graph, roots)
    return domain, {'denominator': denominator, 'source_tiles': tiles, 'sources': roots}
