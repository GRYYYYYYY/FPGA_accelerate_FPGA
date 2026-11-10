"""Device-sample multigraph validation; no node merging by geometry or template ID."""
from collections import Counter, defaultdict
import json


def signature(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def split_name(name):
    tile, wire = name.split("/", 1)
    if not tile or not wire:
        raise ValueError(f"Invalid resource name {name!r}")
    return tile, wire


def validate(graph, check_oracle=True):
    if not isinstance(graph, dict) or graph.get("schema") != "canonical_graph_v1":
        raise ValueError("Unsupported graph schema")
    nodes, aliases, pips, roots = (graph[k] for k in ("nodes", "aliases", "pips", "roots"))
    if not roots or not nodes:
        raise ValueError("Empty sample")
    wires = Counter(aliases.values())
    for wire, node in aliases.items():
        if node not in nodes or split_name(wire)[0] not in graph["tiles"]:
            raise ValueError(f"Unknown alias target/tile: {wire}")
    for node, attrs in nodes.items():
        if aliases.get(node) != node:
            raise ValueError(f"Canonical base wire missing or remapped: {node}")
        if wires[node] != int(attrs["NUM_WIRES"]):
            raise ValueError(f"Wire count differs: {node}")
    for name, pip in pips.items():
        ptile = split_name(name)[0]
        if pip["attributes"]["TILE"] != ptile:
            raise ValueError(f"PIP tile differs: {name}")
        if pip["attributes"]["IS_DIRECTIONAL"] not in {"0", "1"}:
            raise ValueError(f"Invalid directional flag: {name}")
        for endpoint in ("up_wire", "down_wire"):
            if pip[endpoint] not in aliases or split_name(pip[endpoint])[0] != ptile:
                raise ValueError(f"PIP endpoint missing: {name}")
    adjacency = defaultdict(list)
    identities = set()
    used_pips = set()
    for edge in graph["edges"]:
        src, dst, name = edge["src"], edge["dst"], edge["pip"]
        if src not in roots or src not in nodes or dst not in nodes:
            raise ValueError("Edge outside declared node/root domain")
        pip = pips[name]
        if edge["direction"] == "forward":
            sw, dw = pip["up_wire"], pip["down_wire"]
        elif edge["direction"] == "reverse" and pip["attributes"]["IS_DIRECTIONAL"] == "0":
            sw, dw = pip["down_wire"], pip["up_wire"]
        else:
            raise ValueError(f"Invalid traversal direction: {edge}")
        if (edge["src_wire"], edge["dst_wire"]) != (sw, dw):
            raise ValueError("Endpoint wire differs")
        if (aliases[sw], aliases[dw]) != (src, dst):
            raise ValueError("Endpoint canonical node differs")
        identity = (src, name, edge["direction"])
        if identity in identities:
            raise ValueError(f"Duplicate directed PIP identity: {identity}")
        identities.add(identity)
        used_pips.add(name)
        adjacency[src].append(edge)
    if used_pips != set(pips):
        raise ValueError("Unused or missing PIP records")
    if set(roots) - set(nodes):
        raise ValueError("Unknown source node")
    if check_oracle:
        if set(graph["oracle_children"]) != set(roots):
            raise ValueError("Oracle source domain differs")
        for root, counts in roots.items():
            edges = adjacency[root]
            # Bidirectional self-loops could have two traversals for the same physical PIP.
            if len({e["pip"] for e in edges}) != counts["pip_count"]:
                raise ValueError(f"Downhill PIP count differs: {root}")
            children = graph["oracle_children"][root]
            if len(children) != counts["child_count"] or len(children) != len(set(children)):
                raise ValueError(f"Oracle child count differs: {root}")
            if {e["dst"] for e in edges} != set(children):
                raise ValueError(f"Independent downhill node query differs: {root}")
    return adjacency


def compare(reference, candidate):
    """All retained attributes, aliases, IDs, directions and parallel edges must agree."""
    validate(reference)
    validate(candidate)
    differences = {}
    for key in ("tiles", "nodes", "aliases", "pips", "roots"):
        if reference[key] != candidate[key]:
            differences[key] = "records differ"
    if {r: sorted(v) for r, v in reference["oracle_children"].items()} != {
            r: sorted(v) for r, v in candidate["oracle_children"].items()}:
        differences["oracle_children"] = "records differ"
    left = Counter(map(signature, reference["edges"]))
    right = Counter(map(signature, candidate["edges"]))
    if left != right:
        differences["edges"] = {"missing": list((left - right).elements())[:5],
                                "extra": list((right - left).elements())[:5]}
    return {"equal": not differences, "differences": differences}


class NodeState:
    """One mutable occupancy slot per canonical physical resource, never per template."""
    def __init__(self, graph):
        self.aliases = graph["aliases"]
        self.occupancy = dict.fromkeys(graph["nodes"], 0)

    def get(self, wire):
        return self.occupancy[self.aliases[wire]]

    def add(self, wire, delta):
        self.occupancy[self.aliases[wire]] += delta
