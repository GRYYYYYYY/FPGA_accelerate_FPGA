"""CPU enumeration of existing vertical portals on a two-layer toy RRG."""
from research_common import shortest_path, verify_path, validate_graph


def run(case):
    graph = case["graph"]
    validate_graph(graph)
    layers = {n["id"]: n["layer"] for n in graph["nodes"]}
    vertical = {e["id"] for e in graph["edges"] if layers[e["src"]] != layers[e["dst"]]}
    portals = case["portal_edge_ids"]
    if len(portals) != len(set(portals)) or not set(portals) <= vertical:
        raise ValueError("Candidate portals must be unique existing vertical edges")
    if layers[case["source"]] == layers[case["target"]]:
        raise ValueError("This reference fixture requires an inter-layer connection")
    all_edges = {e["id"] for e in graph["edges"]}
    rows, checks = [], {}
    for portal in portals:
        allowed = all_edges - vertical | {portal}
        route = shortest_path(graph, case["source"], [case["target"]], allowed_edges=allowed)
        rows.append({"portal": portal, "route": route})
        if route["status"] == "found":
            checks[f"path_{portal}"] = verify_path(graph, route, case["source"], [case["target"]])
            checks[f"only_requested_portal_{portal}"] = set(route["edges"]) & vertical == {portal}
    feasible = [row for row in rows if row["route"]["status"] == "found"]
    best = min(feasible, key=lambda row: (row["route"]["cost"], row["portal"])) if feasible else None
    unrestricted = shortest_path(graph, case["source"], [case["target"]])
    checks["expected_portal"] = (best["portal"] if best else None) == case["expected"]["best_portal"]
    checks["expected_cost"] = (best["route"]["cost"] if best else None) == case["expected"]["cost"]
    return {"checks": checks,
            "observations": {"portal_candidates": len(portals), "scope": "existing directed portals, one crossing per candidate; no H3D DP/negotiation or physical 3D implementation"},
            "outputs": {"candidates": rows, "best": best, "unrestricted_reference": unrestricted}}
