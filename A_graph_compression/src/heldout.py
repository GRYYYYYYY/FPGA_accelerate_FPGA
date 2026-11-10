"""Fit only on training sources; encode unseen sources with audited exceptions/fallback."""
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json

from canonical_graph import signature, split_name, validate
from template_codec import DirectDecoder, encode, family, normalize


def object_digest(value):
    return hashlib.sha256(signature(value).encode()).hexdigest()


def source_slr(graph, root):
    return int(graph["tiles"][split_name(root)[0]]["SLR_REGION_ID"])


def select_sources(graph, roots):
    """Keep complete selected rows and all endpoint aliases, never clip their edges."""
    selected = set(roots)
    if not selected or not selected <= graph["roots"].keys():
        raise ValueError("Unknown/empty source selection")
    edges = [deepcopy(e) for e in graph["edges"] if e["src"] in selected]
    nodes = selected | {e["dst"] for e in edges}
    aliases = {w: n for w, n in graph["aliases"].items() if n in nodes}
    tile_ids = {split_name(w)[0] for w in aliases}
    result = deepcopy({k: v for k, v in graph.items() if k not in {
        "nodes", "tiles", "aliases", "pips", "roots", "edges", "oracle_children", "selections", "seed_tiles"}})
    result.update(nodes={n: deepcopy(graph["nodes"][n]) for n in sorted(nodes)},
                  tiles={t: deepcopy(graph["tiles"][t]) for t in sorted(tile_ids)}, aliases=aliases,
                  pips={p: deepcopy(graph["pips"][p]) for p in sorted({e["pip"] for e in edges})},
                  roots={r: deepcopy(graph["roots"][r]) for r in sorted(selected)}, edges=edges,
                  oracle_children={r: list(graph["oracle_children"][r]) for r in sorted(selected)},
                  selections=[deepcopy(s) for s in graph["selections"] if s["node"] in selected],
                  seed_tiles=[t for t in graph["seed_tiles"] if t in tile_ids])
    validate(result)
    return result


def fit_bank(training):
    templates = encode(training)["templates"]
    return {"schema": "frozen_bank_v1", "templates": templates,
            "training_sources": sorted(training["roots"]),
            "training_source_slrs": sorted({source_slr(training, r) for r in training["roots"]}),
            "training_graph_sha256": object_digest(training)}


def encode_frozen(graph, bank):
    if bank.get("schema") != "frozen_bank_v1":
        raise ValueError("Unsupported frozen bank")
    adjacency = validate(graph)
    if set(graph["roots"]) & set(bank["training_sources"]):
        raise ValueError("Training and evaluation canonical sources overlap")
    by_family = {}
    for tid, template in bank["templates"].items():
        f = tuple(template["family"])
        if f in by_family:
            raise ValueError("Duplicate template family in bank")
        by_family[f] = tid
    result = {"schema": "frozen_adjacency_v1", "bank_sha256": object_digest(bank),
              "templates": deepcopy(bank["templates"]), "instances": {},
              "context": deepcopy({k: v for k, v in graph.items() if k not in {"edges", "pips"}})}
    for root in sorted(graph["roots"]):
        rules = sorted((normalize(graph, e) for e in adjacency[root]), key=signature)
        tid = by_family.get(family(graph, root))
        if tid is None:
            # Explicit per-source fallback; never learn a new template from held-out rows.
            instance = {"template": None, "fallback_rules": rules}
        else:
            actual = Counter(map(signature, rules))
            base = Counter(map(signature, bank["templates"][tid]["rules"]))
            instance = {"template": tid,
                        "remove": [json.loads(s) for s in sorted((base - actual).elements())],
                        "add": [json.loads(s) for s in sorted((actual - base).elements())]}
        result["instances"][root] = instance
    return result


def heldout_stats(graph, compact):
    decoder = DirectDecoder(compact)
    stats = Counter()
    strata = defaultdict(Counter)
    rows = []
    topology = lambda rs: Counter(signature({k: v for k, v in r.items() if k != "attributes"}) for r in rs)
    for root, instance in compact["instances"].items():
        stats["sources"] += 1
        if instance["template"] is None:
            category = "unseen_family_fallback"
            stats["fallback_rule_records"] += len(instance["fallback_rules"])
        else:
            stats["known_family_sources"] += 1
            actual, base = decoder.rules(root), decoder.rules(root, False)
            if not instance["add"] and not instance["remove"]:
                category = "exact_without_exceptions"
            elif topology(actual) == topology(base):
                category = "attributes_only_exception"
            else:
                category = "connection_rule_exception"
            stats["exception_add_records"] += len(instance["add"])
            stats["exception_remove_records"] += len(instance["remove"])
        stats[category] += 1
        slr = source_slr(graph, root)
        ty = family(graph, root)[0]
        strata[f"SLR{slr}/{ty}"][category] += 1
        rows.append({"source": root, "slr": slr, "tile_type": ty, "category": category})
    keys = ["known_family_sources", "unseen_family_fallback", "exact_without_exceptions",
            "attributes_only_exception", "connection_rule_exception", "fallback_rule_records",
            "exception_add_records", "exception_remove_records"]
    for key in keys:
        stats.setdefault(key, 0)
    stats["known_family_exact_fraction"] = stats["exact_without_exceptions"] / max(1, stats["known_family_sources"])
    stats["all_source_exact_fraction"] = stats["exact_without_exceptions"] / stats["sources"]
    return {"counts": dict(stats), "strata": {k: dict(v) for k, v in sorted(strata.items())}, "sources": rows,
            "scope": "Templates frozen on SLR0; exact recovery uses evaluation-derived per-instance exceptions or explicit fallback. This is not prediction without access to the device database."}
