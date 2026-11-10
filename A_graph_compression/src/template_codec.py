"""Exact sampled-adjacency templates with multiset exceptions and lazy decoding.

Only static edge rules are shared. Canonical nodes, all aliases and node attributes
remain explicit. This is a semantic prototype, not a packed/hardware representation.
"""
from collections import Counter, defaultdict
from copy import deepcopy
import json

from canonical_graph import signature, split_name, validate


def coordinates(attrs):
    return int(attrs["COLUMN"]), int(attrs["ROW"])


def family(graph, node):
    tile, wire = split_name(node)
    return graph["tiles"][tile]["TYPE"], wire


def normalize(graph, edge):
    source_tile, _ = split_name(edge["src"])
    pip_tile, pip_suffix = split_name(edge["pip"])
    ax, ay = coordinates(graph["tiles"][source_tile])
    px, py = coordinates(graph["tiles"][pip_tile])
    attrs = dict(graph["pips"][edge["pip"]]["attributes"])
    del attrs["TILE"]
    return {"tile_offset": [px - ax, py - ay], "pip_suffix": pip_suffix,
            "direction": edge["direction"], "src_wire": split_name(edge["src_wire"])[1],
            "dst_wire": split_name(edge["dst_wire"])[1], "attributes": attrs}


def encode(graph):
    adjacency = validate(graph)
    groups = defaultdict(list)
    rules_by_root = {}
    for root in sorted(graph["roots"]):
        groups[family(graph, root)].append(root)
        rules_by_root[root] = sorted((normalize(graph, e) for e in adjacency[root]), key=signature)
    # Node properties and canonical identity tables are intentionally lossless and uncompressed.
    compact = {"schema": "adjacency_templates_v1",
               "context": deepcopy({k: v for k, v in graph.items() if k not in {"edges", "pips"}}),
               "templates": {}, "instances": {}}
    for index, (group, roots) in enumerate(sorted(groups.items())):
        template_id = f"t{index:04d}"
        # Mode maximizes sources needing no exceptions; this does not optimize packed bytes.
        patterns = Counter(signature(rules_by_root[r]) for r in roots)
        best = min(patterns, key=lambda pattern: (-patterns[pattern], pattern))
        base = json.loads(best)
        compact["templates"][template_id] = {"family": list(group), "rules": base}
        base_counts = Counter(map(signature, base))
        for root in roots:
            actual = Counter(map(signature, rules_by_root[root]))
            compact["instances"][root] = {
                "template": template_id,
                "remove": [json.loads(s) for s in sorted((base_counts - actual).elements())],
                "add": [json.loads(s) for s in sorted((actual - base_counts).elements())]}
    return compact


class DirectDecoder:
    """Expand only the requested source; unexpanded targets raise, never look like sinks."""
    def __init__(self, compact):
        if not isinstance(compact, dict) or compact.get("schema") not in {
                "adjacency_templates_v1", "frozen_adjacency_v1"}:
            raise ValueError("Unsupported template schema")
        self.compact = compact
        self.context = compact["context"]
        if set(compact["instances"]) != set(self.context["roots"]):
            raise ValueError("Instance/source domain differs")
        self.grid = {}
        for tile, attrs in self.context["tiles"].items():
            point = coordinates(attrs)
            if point in self.grid:
                raise ValueError(f"Ambiguous tile coordinate {point}")
            self.grid[point] = tile
        for root, instance in compact["instances"].items():
            if instance["template"] is None:
                if compact["schema"] != "frozen_adjacency_v1" or not isinstance(instance.get("fallback_rules"), list):
                    raise ValueError("Explicit fallback requires frozen schema and rules")
                continue
            template = compact["templates"][instance["template"]]
            if template["family"] != list(family(self.context, root)):
                raise ValueError("Template family differs from source")

    def rules(self, root, apply_exceptions=True):
        instance = self.compact["instances"][root]
        if instance["template"] is None:
            return deepcopy(instance["fallback_rules"])
        template = self.compact["templates"][instance["template"]]
        counts = Counter(map(signature, template["rules"]))
        if apply_exceptions:
            removed = Counter(map(signature, instance["remove"]))
            if removed - counts:
                raise ValueError(f"Exception removes an absent rule: {root}")
            counts.subtract(removed)
            counts.update(map(signature, instance["add"]))
        return [json.loads(s) for s in sorted(counts) for _ in range(counts[s])]

    def neighbors(self, root, apply_exceptions=True):
        if root not in self.context["roots"]:
            raise KeyError(f"Adjacency not exported for {root}")
        source_tile, _ = split_name(root)
        ax, ay = coordinates(self.context["tiles"][source_tile])
        for rule in self.rules(root, apply_exceptions):
            dx, dy = rule["tile_offset"]
            tile = self.grid[(ax + dx, ay + dy)]
            sw, dw = (f"{tile}/{rule[k]}" for k in ("src_wire", "dst_wire"))
            src, dst = (self.context["aliases"][w] for w in (sw, dw))
            if src != root:
                raise ValueError(f"Template resolves to another canonical source: {root} -> {src}")
            attrs = {**rule["attributes"], "TILE": tile}
            edge = {"pip": f"{tile}/{rule['pip_suffix']}", "direction": rule["direction"],
                    "src": src, "dst": dst, "src_wire": sw, "dst_wire": dw}
            if rule["direction"] == "forward":
                up, down = sw, dw
            elif rule["direction"] == "reverse" and attrs["IS_DIRECTIONAL"] == "0":
                up, down = dw, sw
            else:
                raise ValueError("Invalid PIP direction in rule")
            yield edge, {"up_wire": up, "down_wire": down, "attributes": attrs}

    def materialize(self):
        graph = deepcopy(self.context)
        graph["edges"], graph["pips"] = [], {}
        for root in sorted(graph["roots"]):
            for edge, pip in self.neighbors(root):
                graph["edges"].append(edge)
                name = edge["pip"]
                if name in graph["pips"] and graph["pips"][name] != pip:
                    raise ValueError(f"Conflicting attributes for shared physical PIP: {name}")
                graph["pips"][name] = pip
        return graph


class PreparedDecoder(DirectDecoder):
    """Prepare exception masks once; borrow rule payloads without expanding node edges.

    The compact input is read-only for this decoder's lifetime. Extra persistent
    state consists of removed template indices per source. Template and added-rule
    payloads stay shared with the input; fallback rows are also borrowed.
    """
    def __init__(self, compact):
        super().__init__(compact)
        signatures = {tid: [signature(rule) for rule in template["rules"]]
                      for tid, template in compact["templates"].items()}
        self.removed_indices = {}
        for root, instance in compact["instances"].items():
            if instance["template"] is None:
                continue
            removed = Counter(map(signature, instance["remove"]))
            indices = set()
            for index, key in enumerate(signatures[instance["template"]]):
                if removed[key] > 0:
                    indices.add(index)
                    removed[key] -= 1
            if any(removed.values()):
                raise ValueError(f"Exception removes an absent rule: {root}")
            self.removed_indices[root] = frozenset(indices)

    def rules(self, root, apply_exceptions=True):
        instance = self.compact["instances"][root]
        if instance["template"] is None:
            yield from instance["fallback_rules"]
            return
        template = self.compact["templates"][instance["template"]]
        removed = self.removed_indices[root] if apply_exceptions else frozenset()
        for index, rule in enumerate(template["rules"]):
            if index not in removed:
                yield rule
        if apply_exceptions:
            yield from instance["add"]
