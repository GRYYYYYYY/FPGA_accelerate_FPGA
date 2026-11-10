"""Strict reader for export_vivado.tcl; names and raw property values are lossless."""
import hashlib
from pathlib import Path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def properties(fields):
    if len(fields) % 2:
        raise ValueError("Odd property field count")
    result = dict(zip(fields[::2], fields[1::2]))
    if len(result) * 2 != len(fields):
        raise ValueError("Duplicate property")
    return result


def insert(table, key, value):
    if key in table:
        raise ValueError(f"Duplicate record: {key}")
    table[key] = value


def read_export(path):
    graph = {"schema": "canonical_graph_v1", "dataset_kind": "real_device_sample",
             "metadata": {}, "tiles": {}, "nodes": {}, "aliases": {}, "pips": {},
             "roots": {}, "edges": [], "oracle_children": {},
             "seed_tiles": [], "selections": []}
    completed = False
    with Path(path).open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            fields = line.rstrip("\n").split("\t")
            tag, *f = fields
            try:
                if completed:
                    raise ValueError("Records after completion marker")
                if tag == "meta":
                    key, value = f
                    insert(graph["metadata"], key, value)
                elif tag in {"node", "tile"}:
                    insert(graph[tag + "s"], f[0], properties(f[1:]))
                elif tag == "alias":
                    wire, node = f
                    insert(graph["aliases"], wire, node)
                elif tag == "pip":
                    insert(graph["pips"], f[0], {"up_wire": f[1], "down_wire": f[2],
                                                    "attributes": properties(f[3:])})
                elif tag == "root":
                    node, pips, children = f
                    insert(graph["roots"], node, {"pip_count": int(pips), "child_count": int(children)})
                    graph["oracle_children"][node] = []
                elif tag == "edge":
                    pip, direction, src, dst, sw, dw = f
                    graph["edges"].append(dict(pip=pip, direction=direction, src=src, dst=dst,
                                                src_wire=sw, dst_wire=dw))
                elif tag == "oracle_child":
                    root, child = f
                    graph["oracle_children"][root].append(child)
                elif tag == "seed_tile":
                    seed, = f
                    graph["seed_tiles"].append(seed)
                elif tag == "selection":
                    node, seed, reason = f
                    graph["selections"].append(dict(node=node, seed_tile=seed, reason=reason))
                elif tag == "complete":
                    observed = tuple(len(graph[k]) for k in ("roots", "nodes", "pips"))
                    if tuple(map(int, f)) != observed:
                        raise ValueError(f"Completion counts differ: {f} vs {observed}")
                    completed = True
                else:
                    raise ValueError(f"Unknown record {tag}")
            except (ValueError, KeyError, IndexError) as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
    if not completed or graph["metadata"].get("schema") != "vivado_graph_tsv_v1":
        raise ValueError("Incomplete export or unsupported schema")
    graph["provenance"] = {"raw_path": str(Path(path).resolve()), "raw_sha256": sha256(path)}
    return graph
