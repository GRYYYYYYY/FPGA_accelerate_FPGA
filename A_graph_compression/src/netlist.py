"""Strict physical-net-group snapshot and canonical ownership helpers."""
from collections import Counter, defaultdict
from pathlib import Path


def read_snapshot(path):
    result = {"schema": "routed_netlist_v1", "metadata": {}, "nets": {}, "cells": {}}
    counts = Counter()
    complete = False
    with Path(path).open() as f:
        for number, line in enumerate(f, 1):
            tag, *fields = line.rstrip("\n").split("\t")
            try:
                if complete:
                    raise ValueError("Records after completion")
                if tag == "meta":
                    key, value = fields
                    if key in result["metadata"]:
                        raise ValueError("Duplicate metadata")
                    result["metadata"][key] = value
                elif tag == "net":
                    name, ty, status, fixed, route, fixed_route = fields
                    if name in result["nets"] or fixed not in {"0", "1"}:
                        raise ValueError("Duplicate net or invalid fixed flag")
                    result["nets"][name] = {"type": ty, "status": status, "fixed": fixed == "1",
                                            "route": route, "fixed_route": fixed_route,
                                            "segments": [], "nodes": [], "pips": [], "site_pins": [], "leaf_pins": []}
                elif tag in {"segment", "node", "pip"}:
                    name, value = fields
                    result["nets"][name][tag+"s"].append(value)
                elif tag == "site_pin":
                    name, pin, direction, used, node = fields
                    if direction not in {"IN", "OUT", "INOUT"} or used not in {"0", "1"}:
                        raise ValueError("Invalid site pin flags")
                    if used == "1" and not node:
                        raise ValueError("Used site pin has no canonical node")
                    result["nets"][name]["site_pins"].append({"pin": pin, "direction": direction, "used": used == "1", "node": node})
                elif tag == "leaf_pin":
                    name, pin, direction = fields
                    result["nets"][name]["leaf_pins"].append({"pin": pin, "direction": direction})
                elif tag == "cell":
                    name, ref, loc, bel = fields
                    if name in result["cells"]:
                        raise ValueError("Duplicate cell")
                    result["cells"][name] = {"ref": ref, "loc": loc, "bel": bel}
                elif tag == "complete":
                    observed = [counts[k] for k in ["net", "node", "pip", "site_pin", "cell"]]
                    if list(map(int, fields)) != observed:
                        raise ValueError("Completion counts differ")
                    complete = True
                else:
                    raise ValueError(f"Unknown tag {tag}")
                counts[tag] += 1
            except (ValueError, KeyError) as exc:
                raise ValueError(f"{path}:{number}: {exc}") from exc
    if not complete or result["metadata"].get("schema") != "routed_netlist_tsv_v1":
        raise ValueError("Incomplete/unsupported netlist snapshot")
    segments = {}
    duplicates = Counter()
    for name, net in result["nets"].items():
        for field in ["segments", "nodes", "pips"]:
            if len(set(net[field])) != len(net[field]):
                raise ValueError(f"Duplicate {field}: {name}")
        for segment in net["segments"]:
            if segment in segments:
                raise ValueError(f"Segment belongs to multiple physical groups: {segment}")
            segments[segment] = name
        for field in ["site_pins", "leaf_pins"]:
            # Vivado may repeat the same physical pin when querying all hierarchy
            # segments together. Coalesce only identical records, never conflicts.
            unique = {}
            for pin in net[field]:
                if pin["pin"] in unique:
                    if unique[pin["pin"]] != pin:
                        raise ValueError(f"Conflicting {field}: {name}/{pin['pin']}")
                    duplicates[field] += 1
                unique[pin["pin"]] = pin
            net[field] = list(unique.values())
    result["coalesced_identical_endpoint_records"] = dict(duplicates)
    return result


def terminals(net):
    sources = sorted({p["node"] for p in net["site_pins"] if p["used"] and p["direction"] == "OUT"})
    sinks = sorted({p["node"] for p in net["site_pins"] if p["used"] and p["direction"] == "IN"})
    return sources, sinks


def routing_queries(snapshot):
    queries = []
    for name, net in sorted(snapshot["nets"].items()):
        sources, sinks = terminals(net)
        if net["type"] == "SIGNAL" and net["status"] == "ROUTED" and not net["fixed"] and len(sources) == 1 and sinks and net["pips"]:
            queries.append({"net": name, "source": sources[0], "sinks": sinks,
                            "reference_pip_count": len(net["pips"]), "reference_node_count": len(net["nodes"])})
    return queries


def ownership(snapshot, excluded=()):
    """Complete protected occupancy, with hierarchy segments already coalesced."""
    excluded = set(excluded)
    nodes, pips = defaultdict(set), defaultdict(set)
    for name, net in snapshot["nets"].items():
        if name in excluded:
            continue
        sources, sinks = terminals(net)
        for n in set(net["nodes"]) | set(sources) | set(sinks):
            nodes[n].add(name)
        for p in net["pips"]:
            pips[p].add(name)
    return nodes, pips
