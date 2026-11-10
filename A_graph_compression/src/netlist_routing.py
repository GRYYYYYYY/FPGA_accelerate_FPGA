"""Canonical-resource negotiated-congestion router shared by graph providers.

Clock/constants/unselected nets stay protected. Unknown rows are recorded as
unknown, not sinks; successful paths in a partial domain have no global
optimality claim. The cost is hop/congestion based, not a calibrated delay model.
"""
from collections import Counter, defaultdict
import heapq
from time import perf_counter

from canonical_graph import signature
from netlist import ownership
from search_experiment import IncompleteDomain


def connect(provider, tree, target, net, protected, protected_pips, reserved,
            owners, history, present, max_expansions):
    if target in tree:
        return {"status": "found", "path": [], "cost": 0, "expanded": 0,
                "examined": 0, "fetched": 0, "unknown_sources": [], "blocked_edges": 0}
    if target in protected or any(n in protected for n in tree):
        raise ValueError("Terminals or tree intersect protected ownership")
    distance = dict.fromkeys(tree, 0)
    parent = {}
    queue = [(0, node) for node in tree]
    heapq.heapify(queue)
    expanded = examined = fetched = blocked = 0
    unknown = set()
    status = "no_path"
    while queue:
        cost, node = heapq.heappop(queue)
        if cost != distance[node]:
            continue
        if node == target:
            status = "found"
            break
        if expanded >= max_expansions:
            status = "budget_exhausted"
            break
        try:
            edges = provider.neighbors(node)
        except IncompleteDomain:
            unknown.add(node)
            continue
        expanded += 1
        fetched += len(edges)
        for edge, pip in edges:
            examined += 1
            dst = edge["dst"]
            if (dst in tree or dst in protected or edge["pip"] in protected_pips
                    or (dst in reserved and reserved[dst] != net)
                    or pip["attributes"].get("IS_EXCLUDED_PIP") == "1"
                    or pip["attributes"].get("IS_TEST_PIP") == "1"):
                blocked += 1
                continue
            occupancy = len(owners.get(dst, set()) - {net})
            new = cost + 1 + present * occupancy + history.get(dst, 0)
            if new < distance.get(dst, float("inf")):
                distance[dst] = new
                parent[dst] = edge
                heapq.heappush(queue, (new, dst))
    if status == "no_path" and unknown:
        status = "incomplete_domain"
    path = []
    if status == "found":
        node = target
        while node not in tree:
            edge = parent[node]
            path.append(edge)
            node = edge["src"]
        path.reverse()
    return {"status": status, "path": path, "cost": distance[target] if status == "found" else None,
            "expanded": expanded, "examined": examined, "fetched": fetched,
            "unknown_sources": sorted(unknown), "blocked_edges": blocked}


def route_batch(provider, snapshot, queries, max_iterations=20, max_expansions=200000,
                full_trace=True, progress=None, present_cap=1048576):
    if max_iterations < 1 or max_expansions < 1 or present_cap < 1:
        raise ValueError("Positive iteration/expansion budgets required")
    names = [q["net"] for q in queries]
    if not names or len(names) != len(set(names)) or any(n not in snapshot["nets"] for n in names):
        raise ValueError("Empty, duplicate or unknown routing queries")
    protected, protected_pips = ownership(snapshot, names)
    reserved = {}
    for q in queries:
        for node in [q["source"], *q["sinks"]]:
            if node in protected or (node in reserved and reserved[node] != q["net"]):
                raise ValueError(f"Conflicting reserved terminal: {node}")
            reserved[node] = q["net"]
    owners = defaultdict(set)
    history = Counter()
    routes = {}
    iterations = []
    started = perf_counter()
    for iteration in range(max_iterations):
        # A finite present-cost ceiling lets accumulated conflict history break
        # alternating routes instead of becoming negligible beside 2**iteration.
        present = min(2 ** min(iteration, 20), present_cap)
        outcomes = []
        iteration_unknown = set()
        # Fixed reproducible order; no dependence on reference route geometry.
        for q in queries:
            name = q["net"]
            old = routes.get(name)
            if old:
                for node in old["nodes"]:
                    owners[node].remove(name)
            tree, edges, connections = {q["source"]}, [], []
            for target in sorted(q["sinks"]):
                result = connect(provider, tree, target, name, protected, protected_pips,
                                 reserved, owners, history, present, max_expansions)
                iteration_unknown.update(result["unknown_sources"])
                if full_trace:
                    connections.append({"target": target, **result})
                else:
                    connections.append({"target": target, **{k:v for k,v in result.items()
                        if k not in {"path", "unknown_sources"}},
                        "unknown_count": len(result["unknown_sources"]), "path_length": len(result["path"])})
                if result["status"] != "found":
                    continue
                edges.extend(result["path"])
                tree.update(e["dst"] for e in result["path"])
            for node in tree:
                owners[node].add(name)
            routes[name] = {"source": q["source"], "sinks": list(q["sinks"]),
                            "nodes": sorted(tree), "edges": edges,
                            "complete": set(q["sinks"]).issubset(tree)}
            outcomes.append({"net": name, "connections": connections})
            if progress and len(outcomes) % 50 == 0:
                progress(iteration, len(outcomes), len(queries))
        conflicts = {n: sorted(o) for n, o in owners.items() if len(o) > 1}
        incomplete = sorted(n for n, r in routes.items() if not r["complete"])
        iterations.append({"iteration": iteration, "present_factor": present, "conflicts": conflicts,
                           "incomplete_nets": incomplete, "outcomes": outcomes,
                           "unknown_sources": sorted(iteration_unknown)})
        if progress:
            progress(iteration, len(queries), len(queries), len(conflicts), len(incomplete))
        if not conflicts and not incomplete:
            break
        for node, users in conflicts.items():
            history[node] += len(users)-1
        # A missing graph row or fixed budget cannot improve without graph expansion.
        if not conflicts and incomplete:
            break
    return {"status": "routed" if not conflicts and not incomplete else "incomplete",
            "routes": routes, "iterations": iterations, "wall_ms": (perf_counter()-started)*1000,
            "protected_nodes": len(protected), "protected_pips": len(protected_pips),
            "reserved_terminals": len(reserved), "history": dict(history)}


def validate_routes(graph, snapshot, queries, result):
    """Independent tree reachability, directed-PIP legality, ownership and coverage."""
    expected = {q["net"]: q for q in queries}
    if set(result["routes"]) != set(expected):
        raise ValueError("Routing result net domain differs")
    protected, protected_pips = ownership(snapshot, expected)
    legal = {signature(e) for e in graph["edges"]}
    reserved = {}
    for name, query in expected.items():
        for node in [query['source'], *query['sinks']]:
            if node in reserved and reserved[node] != name:
                raise ValueError('Conflicting query terminal owners')
            reserved[node] = name
    users = defaultdict(set)
    pip_users = defaultdict(set)
    for name, route in result["routes"].items():
        query = expected[name]
        if route["source"] != query["source"] or route["sinks"] != query["sinks"]:
            raise ValueError("Query terminals changed")
        parents, children = {}, defaultdict(set)
        for edge in route["edges"]:
            if signature(edge) not in legal:
                raise ValueError("Nonexistent or altered directed PIP")
            if edge["dst"] in parents or edge["dst"] == route["source"]:
                raise ValueError("Multiple parents or cycle into source")
            attrs = graph["pips"][edge["pip"]]["attributes"]
            if attrs.get("IS_EXCLUDED_PIP") == "1" or attrs.get("IS_TEST_PIP") == "1":
                raise ValueError("Excluded/test PIP in route")
            parents[edge["dst"]] = edge["src"]
            children[edge["src"]].add(edge["dst"])
            pip_users[edge["pip"]].add(name)
        reached, todo = {route["source"]}, [route["source"]]
        while todo:
            for dst in children[todo.pop()]:
                if dst in reached:
                    raise ValueError("Cycle in route")
                reached.add(dst)
                todo.append(dst)
        if reached != set(route["nodes"]) or set(parents) != reached-{route["source"]}:
            raise ValueError("Unreachable or inconsistent route nodes")
        if route["complete"] != set(query["sinks"]).issubset(reached):
            raise ValueError("False sink-completion claim")
        if reached & set(protected):
            raise ValueError("Protected canonical node used")
        if any(node in reserved and reserved[node] != name for node in reached):
            raise ValueError('Other net reserved terminal used')
        if any(e["pip"] in protected_pips for e in route["edges"]):
            raise ValueError("Protected PIP used")
        for node in reached:
            users[node].add(name)
    conflicts = {n: sorted(o) for n, o in users.items() if len(o) > 1}
    pip_conflicts = {p: sorted(o) for p, o in pip_users.items() if len(o) > 1}
    completed = sum(r["complete"] for r in result["routes"].values())
    if result["status"] == "routed" and (conflicts or pip_conflicts or completed != len(expected)):
        raise ValueError("False globally legal routing claim")
    return {"legal_individual_trees": True, "completed_nets": completed,
            "conflicts": conflicts, "pip_conflicts": pip_conflicts,
            "total_pips": sum(len(r["edges"]) for r in result["routes"].values()),
            "all_nets_routed_without_conflicts": completed == len(expected) and not conflicts and not pip_conflicts}
