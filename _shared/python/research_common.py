"""Small, dependency-free reference utilities; no FPGA/GPU execution here."""
import heapq
import itertools
import math


def validate_graph(graph):
    nodes = [node["id"] for node in graph["nodes"]]
    if len(nodes) != len(set(nodes)):
        raise ValueError("Duplicate canonical node ID")
    node_set = set(nodes)
    edge_ids = set()
    for edge in graph["edges"]:
        if edge["id"] in edge_ids:
            raise ValueError("Duplicate edge ID")
        edge_ids.add(edge["id"])
        if edge["src"] not in node_set or edge["dst"] not in node_set:
            raise ValueError("Edge references an unknown node")
        cost = edge["cost"]
        if not math.isfinite(cost) or cost < 0:
            raise ValueError("Reference solver needs finite nonnegative edge costs")
    return node_set


def shortest_path(graph, source, targets, *, blocked=(), allowed_edges=None,
                  node_penalty=None, max_expansions=None):
    """Directed Dijkstra baseline with explicit budget and edge-preserving traceback."""
    nodes = validate_graph(graph)
    targets = set(targets)
    if source not in nodes or not targets or not targets <= nodes:
        raise ValueError("Unknown source/target or empty target set")
    if max_expansions is not None and max_expansions < 0:
        raise ValueError("Negative expansion budget")
    blocked = set(blocked)
    if not blocked <= nodes:
        raise ValueError("Unknown blocked node")
    edge_ids = {edge["id"] for edge in graph["edges"]}
    if allowed_edges is not None and not set(allowed_edges) <= edge_ids:
        raise ValueError("Unknown allowed edge")
    penalty = node_penalty or {}
    if any(not math.isfinite(v) or v < 0 for v in penalty.values()):
        raise ValueError("Reference solver needs nonnegative node penalties")
    adjacency = {node: [] for node in nodes}
    for edge in graph["edges"]:
        if allowed_edges is None or edge["id"] in allowed_edges:
            adjacency[edge["src"]].append(edge)
    counts = {"expanded_nodes": 0, "examined_edges": 0, "successful_relaxations": 0,
              "stale_pops": 0, "peak_queue_entries": 0}

    def result(status, path=None, edges=None, cost=None):
        return {"status": status, "nodes": path or [], "edges": edges or [],
                "cost": cost, "logical_counts": counts.copy()}

    if source in blocked:
        return result("no_path")
    sequence = itertools.count()
    queue = [(0.0, next(sequence), source)]
    distances, parents = {source: 0.0}, {}
    counts["peak_queue_entries"] = 1
    while queue:
        distance, _, node = heapq.heappop(queue)
        if distance != distances[node]:
            counts["stale_pops"] += 1
            continue
        if max_expansions is not None and counts["expanded_nodes"] >= max_expansions:
            return result("budget_exhausted")
        counts["expanded_nodes"] += 1
        if node in targets:
            path, path_edges = [node], []
            while node != source:
                node, edge_id = parents[node]
                path.append(node)
                path_edges.append(edge_id)
            return result("found", list(reversed(path)), list(reversed(path_edges)), distance)
        for edge in adjacency[node]:
            counts["examined_edges"] += 1
            dst = edge["dst"]
            if dst in blocked:
                continue
            candidate = distance + edge["cost"] + penalty.get(dst, 0)
            if candidate < distances.get(dst, math.inf):
                distances[dst] = candidate
                parents[dst] = node, edge["id"]
                heapq.heappush(queue, (candidate, next(sequence), dst))
                counts["successful_relaxations"] += 1
                counts["peak_queue_entries"] = max(counts["peak_queue_entries"], len(queue))
    return result("no_path")


def verify_path(graph, result, source, targets):
    """Validate the returned path under the unmodified edge-cost model."""
    if result["status"] != "found":
        return False
    nodes, edges = result["nodes"], result["edges"]
    if not nodes or nodes[0] != source or nodes[-1] not in set(targets):
        return False
    if len(edges) != len(nodes) - 1:
        return False
    by_id = {edge["id"]: edge for edge in graph["edges"]}
    total = 0
    for src, dst, edge_id in zip(nodes, nodes[1:], edges):
        edge = by_id.get(edge_id)
        if edge is None or (edge["src"], edge["dst"]) != (src, dst):
            return False
        total += edge["cost"]
    return math.isclose(total, result["cost"], rel_tol=1e-10, abs_tol=1e-10)
