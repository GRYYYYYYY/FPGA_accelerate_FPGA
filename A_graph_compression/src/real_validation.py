"""Coverage, exception ablation, occupancy checks and real-sample corruption probes."""
from collections import Counter, defaultdict
from copy import deepcopy

from canonical_graph import NodeState, compare, signature, split_name, validate
from template_codec import DirectDecoder


def coverage(graph, compact):
    adjacency = validate(graph)
    aliases_by_node = defaultdict(list)
    for wire, node in graph["aliases"].items():
        aliases_by_node[node].append(wire)
    parallel = Counter((e["src"], e["dst"]) for e in graph["edges"])
    physical = graph["pips"].values()
    instances = compact["instances"]
    return {
        "seed_tiles": len(graph["seed_tiles"]), "canonical_nodes": len(graph["nodes"]),
        "complete_sources": len(graph["roots"]), "unexpanded_targets": len(graph["nodes"])-len(graph["roots"]),
        "complete_sources_without_edges": sum(not adjacency[r] for r in graph["roots"]),
        "wire_aliases": len(graph["aliases"]), "physical_pips": len(graph["pips"]),
        "directed_edges": len(graph["edges"]),
        "cross_tile_nodes": sum(len({split_name(w)[0] for w in ws}) > 1 for ws in aliases_by_node.values()),
        "parallel_endpoint_pairs": sum(v > 1 for v in parallel.values()),
        "parallel_edges_beyond_first": sum(v-1 for v in parallel.values()),
        "bidirectional_pips": sum(p["attributes"]["IS_DIRECTIONAL"] == "0" for p in physical),
        "pseudo_pips": sum(p["attributes"]["IS_PSEUDO"] == "1" for p in physical),
        "excluded_pips": sum(p["attributes"]["IS_EXCLUDED_PIP"] == "1" for p in physical),
        "invertible_pips": sum(p["attributes"]["CAN_INVERT"] == "1" for p in physical),
        "templates": len(compact["templates"]),
        "templates_reused_by_multiple_sources": sum(n > 1 for n in Counter(i["template"] for i in instances.values()).values()),
        "template_rule_records": sum(len(t["rules"]) for t in compact["templates"].values()),
        "exception_sources": sum(bool(i["add"] or i["remove"]) for i in instances.values()),
        "exception_add_records": sum(len(i["add"]) for i in instances.values()),
        "exception_remove_records": sum(len(i["remove"]) for i in instances.values()),
        "node_intents": dict(sorted(Counter(n["INTENT_CODE_NAME"] for n in graph["nodes"].values()).items())),
        "seed_tile_types": dict(sorted(Counter(graph["tiles"][t]["TYPE"] for t in graph["seed_tiles"]).items())),
    }


def ablate_exceptions(graph, compact):
    decoder = DirectDecoder(compact)
    rows = []
    totals = Counter()
    changed_attributes = Counter()
    topology_key = lambda rule: signature({k: v for k, v in rule.items() if k != "attributes"})
    for root in sorted(compact["instances"]):
        full, base = decoder.rules(root), decoder.rules(root, False)
        if Counter(map(signature, full)) == Counter(map(signature, base)):
            continue
        topology_differs = Counter(map(topology_key, full)) != Counter(map(topology_key, base))
        kind = "connection_rule_difference" if topology_differs else "attributes_only"
        totals[kind] += 1
        base_by_key = {topology_key(r): r for r in base}
        for rule in full:
            other = base_by_key.get(topology_key(rule))
            if other:
                for attr in set(rule["attributes"]) | set(other["attributes"]):
                    if rule["attributes"].get(attr) != other["attributes"].get(attr):
                        changed_attributes[attr] += 1
        try:
            list(decoder.neighbors(root, False))
            resolution = "resolves_but_differs"
        except (KeyError, ValueError):
            resolution = "cannot_resolve_in_exported_domain"
        totals[resolution] += 1
        rows.append({"source": root, "kind": kind, "resolution": resolution,
                     "removed_rules": len(compact["instances"][root]["remove"]),
                     "added_rules": len(compact["instances"][root]["add"])})
    return {"mismatched_sources": len(rows), "counts": dict(totals),
            "changed_attribute_counts_on_matching_rules": dict(changed_attributes), "sources": rows,
            "scope": "Remove all per-instance exceptions; compare normalized rules including attributes. Unresolvable rules are failures, never silently dropped."}


def occupancy_checks(graph, compact):
    state = NodeState(graph)
    by_node = defaultdict(list)
    for wire, node in graph["aliases"].items():
        by_node[node].append(wire)
    cross = next((node for node, ws in by_node.items()
                  if len({split_name(w)[0] for w in ws}) > 1), None)
    if cross is None:
        raise ValueError("No cross-tile alias coverage")
    state.add(cross, 1)
    aliases_share_state = all(state.get(w) == 1 for w in by_node[cross])
    state.add(cross, -1)
    by_template = defaultdict(list)
    for node, instance in compact["instances"].items():
        by_template[instance["template"]].append(node)
    pair = next((ns[:2] for ns in by_template.values() if len(ns) > 1), None)
    if pair is None:
        raise ValueError("No shared-template coverage")
    state.add(pair[0], 1)
    independent = state.get(pair[0]) == 1 and state.get(pair[1]) == 0
    return {"cross_tile_aliases_share_occupancy": aliases_share_state,
            "different_nodes_sharing_template_have_independent_occupancy": independent}


def fault_injections(graph, compact):
    """Each mutation touches a real record; required coverage absence is an error."""
    outcomes = []

    def graph_fault(name, mutate):
        candidate = deepcopy(graph)
        mutate(candidate)
        try:
            outcome = compare(graph, candidate)
            detected = not outcome["equal"]
            reason = signature(outcome["differences"])
        except (ValueError, KeyError) as exc:
            detected, reason = True, str(exc)
        outcomes.append({"fault": name, "detected": detected, "reason": reason[:500]})

    def compact_fault(name, mutate):
        candidate = deepcopy(compact)
        mutate(candidate)
        try:
            outcome = compare(graph, DirectDecoder(candidate).materialize())
            detected = not outcome["equal"]
            reason = signature(outcome["differences"])
        except (ValueError, KeyError) as exc:
            detected, reason = True, str(exc)
        outcomes.append({"fault": name, "detected": detected, "reason": reason[:500]})

    parallel = Counter((e["src"], e["dst"]) for e in graph["edges"])
    parallel_index = next(i for i, e in enumerate(graph["edges"]) if parallel[e["src"], e["dst"]] > 1)
    reverse_index = next(i for i, e in enumerate(graph["edges"]) if e["direction"] == "reverse")
    pseudo = next(p for p, v in graph["pips"].items() if v["attributes"]["IS_PSEUDO"] == "1")
    alias = next(w for w, n in graph["aliases"].items() if split_name(w)[0] != split_name(n)[0])
    another_node = next(n for n in graph["nodes"] if n != graph["aliases"][alias])
    node = next(iter(graph["nodes"]))
    pip = graph["edges"][0]["pip"]
    exception = next(r for r, i in compact["instances"].items() if i["add"] or i["remove"])
    graph_fault("drop_one_parallel_edge", lambda c: c["edges"].pop(parallel_index))
    graph_fault("reverse_bidirectional_traversal_incorrectly", lambda c: c["edges"][reverse_index].update(direction="forward"))
    graph_fault("alter_pip_speed_index", lambda c: c["pips"][pip]["attributes"].update(SPEED_INDEX="-999"))
    graph_fault("erase_pseudo_flag", lambda c: c["pips"][pseudo]["attributes"].update(IS_PSEUDO="0"))
    graph_fault("change_node_intent", lambda c: c["nodes"][node].update(INTENT_CODE_NAME="FAULT"))
    graph_fault("duplicate_directed_pip", lambda c: c["edges"].append(deepcopy(c["edges"][0])))
    # A same-size valid graph still must fail exact identity comparison.
    def rename_pip(c):
        new = pip + "_FAULT"
        c["pips"][new] = c["pips"].pop(pip)
        for edge in c["edges"]:
            if edge["pip"] == pip:
                edge["pip"] = new
    graph_fault("change_pip_identity_keep_counts", rename_pip)
    graph_fault("alter_independent_oracle", lambda c: c["oracle_children"][c["edges"][0]["src"]].clear())
    compact_fault("mismerge_cross_tile_alias", lambda c: c["context"]["aliases"].__setitem__(alias, another_node))
    compact_fault("omit_real_exception", lambda c: c["instances"][exception].update(add=[], remove=[]))
    def bad_removal(c):
        c["instances"][exception]["remove"].append({"nonexistent_rule": True})
    compact_fault("remove_nonexistent_template_rule", bad_removal)
    return outcomes
