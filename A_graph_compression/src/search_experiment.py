"""Same unit-hop BFS over real-device CSR or lazy templates; no netlist routing claims."""
from array import array
from collections import deque, defaultdict
from statistics import median
from time import perf_counter_ns

from template_codec import DirectDecoder, PreparedDecoder


class IncompleteDomain(Exception):
    pass


def edge_order(pair):
    edge, _ = pair
    return edge["dst"], edge["pip"], edge["direction"], edge["src_wire"], edge["dst_wire"]


class ExplicitCSR:
    def __init__(self, graph):
        self.nodes = sorted(graph["nodes"])
        self.node_id = {n: i for i, n in enumerate(self.nodes)}
        self.known_sources = set(graph["roots"])
        self.edges = graph["edges"]
        self.pips = graph["pips"]
        adjacency = defaultdict(list)
        for index, edge in enumerate(self.edges):
            adjacency[edge["src"]].append(index)
        self.offsets = array("Q", [0])
        self.edge_ids = array("I")
        for node in self.nodes:
            ids = sorted(adjacency[node], key=lambda i: edge_order((self.edges[i], None)))
            self.edge_ids.extend(ids)
            self.offsets.append(len(self.edge_ids))

    def neighbors(self, node):
        if node not in self.known_sources:
            raise IncompleteDomain(node)
        index = self.node_id[node]
        return [(self.edges[self.edge_ids[j]], self.pips[self.edges[self.edge_ids[j]]["pip"]])
                for j in range(self.offsets[index], self.offsets[index+1])]


class LazyTemplates:
    def __init__(self, compact, decoder_type=DirectDecoder):
        self.decoder = decoder_type(compact)
        self.known_sources = set(compact["context"]["roots"])

    def neighbors(self, node):
        if node not in self.known_sources:
            raise IncompleteDomain(node)
        # Match CSR neighbor ordering; all sorting/decoding is included in query timing.
        return sorted(self.decoder.neighbors(node), key=edge_order)


def search(provider, source, target, max_expansions, trace=False):
    """FIFO BFS: one cost per PIP traversal; preserve parallel edge visits and path identity."""
    if max_expansions < 0:
        raise ValueError("Negative expansion budget")
    queue = deque([source])
    distance = {source: 0}
    parent = {}
    expanded = 0
    examined = 0
    fetched = 0
    visits = []
    status = "no_path"
    incomplete_at = None
    while queue:
        node = queue.popleft()
        if node == target:
            status = "found"
            break
        if expanded >= max_expansions:
            status = "budget_exhausted"
            break
        try:
            edges = provider.neighbors(node)
        except IncompleteDomain:
            status, incomplete_at = "incomplete_domain", node
            break
        expanded += 1
        fetched += len(edges)
        examined_before = examined
        if trace:
            visits.append({"source": node, "distance": distance[node],
                           "fetched_edges": [[e["pip"], e["direction"], e["dst"]] for e, _ in edges]})
        for edge, _ in edges:
            examined += 1
            child = edge["dst"]
            if child not in distance:
                distance[child] = distance[node] + 1
                parent[child] = edge
                queue.append(child)
                # Unit-cost BFS can finish on first discovery; it need not expand
                # unknown frontier nodes at the target's distance.
                if child == target:
                    status = "found"
                    break
        if trace:
            visits[-1]["examined_edges"] = examined-examined_before
        if status == "found":
            break
    path = []
    if status == "found":
        cur = target
        while cur != source:
            edge = parent[cur]
            path.append(dict(edge))
            cur = edge["src"]
        path.reverse()
    return {"status": status, "distance": len(path) if status == "found" else None,
            "path": path, "expanded_sources": expanded, "examined_edges": examined,
            "fetched_edge_records": fetched,
            "discovered_nodes": len(distance), "incomplete_at": incomplete_at,
            **({"trace": visits} if trace else {})}


def make_queries(graph, seeds, depth, budget):
    """Construct queries from real resource reachability, not a real-net workload."""
    provider = ExplicitCSR(graph)
    queries = []
    for seed in seeds:
        levels = {seed: 0}
        queue = deque([seed])
        while queue:
            node = queue.popleft()
            if levels[node] >= depth:
                continue
            try:
                edges = provider.neighbors(node)
            except IncompleteDomain:
                continue
            for edge, _ in edges:
                dst = edge["dst"]
                if dst not in levels:
                    levels[dst] = levels[node]+1
                    queue.append(dst)
        for distance in range(1, depth+1):
            candidates = sorted(n for n, d in levels.items() if d == distance)
            if candidates:
                queries.append({"id": f"q{len(queries):02d}", "source": seed,
                                "target": candidates[len(candidates)//2], "max_expansions": budget,
                                "kind": "reachable_by_exported_edges", "discovery_distance": distance})
    far = next(q for q in queries if q["discovery_distance"] >= 3)
    queries.append({**far, "id": f"q{len(queries):02d}", "max_expansions": 1, "kind": "budget_probe"})
    unknown = next(n for n in sorted(graph["nodes"]) if n not in graph["roots"])
    queries.append({"id": f"q{len(queries):02d}", "source": unknown, "target": seeds[0],
                    "max_expansions": budget, "kind": "unknown_adjacency_probe"})
    sink = next(n for n in sorted(graph["roots"]) if graph["roots"][n]["pip_count"] == 0 and n != seeds[0])
    queries.append({"id": f"q{len(queries):02d}", "source": sink, "target": seeds[0],
                    "max_expansions": budget, "kind": "confirmed_sink_no_path_probe"})
    queries.append({"id": f"q{len(queries):02d}", "source": seeds[0], "target": seeds[0],
                    "max_expansions": 0, "kind": "zero_hop_probe"})
    return queries


def validate_path(graph, query, result):
    if query["source"] not in graph["nodes"] or query["target"] not in graph["nodes"]:
        return False
    if result["status"] != "found":
        return not result["path"] and result["distance"] is None
    available = {(e["src"], e["pip"], e["direction"]): e for e in graph["edges"]}
    cur = query["source"]
    for edge in result["path"]:
        if edge["src"] != cur or available.get((cur, edge["pip"], edge["direction"])) != edge:
            return False
        cur = edge["dst"]
    return cur == query["target"] and len(result["path"]) == result["distance"]


def compare_search(graph, compact, queries, repetitions):
    if repetitions < 1:
        raise ValueError("At least one timing repetition is required")
    factories = {"python_explicit_csr": lambda: ExplicitCSR(graph),
                 "python_lazy_templates": lambda: LazyTemplates(compact),
                 "python_prepared_templates": lambda: LazyTemplates(compact, PreparedDecoder)}
    providers, preparation_ms = {}, {}
    for name, factory in factories.items():
        t0 = perf_counter_ns()
        providers[name] = factory()
        preparation_ms[name] = (perf_counter_ns()-t0)/1e6
    outcomes, checks = [], []
    for query in queries:
        args = (query["source"], query["target"], query["max_expansions"])
        results = {n: search(p, *args, trace=True) for n, p in providers.items()}
        left = results["python_explicit_csr"]
        equal = all(left == r for r in results.values())
        valid = all(validate_path(graph, query, r) for r in results.values())
        checks.append(equal and valid)
        outcomes.append({"query": query, "equal_including_trace": equal, "paths_valid": valid,
                         "result": left, "candidate_results": None if equal else results})
    # Diagnostic comparison above also serves as one warm-up per provider/query.
    references = {o["query"]["id"]: o["result"] for o in outcomes}
    timed_queries = [q for q in queries if q["kind"] == "reachable_by_exported_edges"]
    if not timed_queries:
        raise ValueError("No timed resource queries")
    batches = {name: [] for name in providers}
    per_query = {name: {q["id"]: [] for q in timed_queries} for name in providers}
    for repeat in range(repetitions):
        names = list(providers)
        offset = repeat % len(names)
        order = names[offset:] + names[:offset]
        for name in order:
            total = 0
            for query in timed_queries:
                t0 = perf_counter_ns()
                actual = search(providers[name], query["source"], query["target"], query["max_expansions"])
                elapsed = perf_counter_ns()-t0
                total += elapsed
                per_query[name][query["id"]].append(elapsed/1e6)
                # Stable semantic fields are checked against the untimed trace result below.
                reference = references[query["id"]]
                if actual != {k: v for k, v in reference.items() if k != "trace"}:
                    checks.append(False)
            batches[name].append(total/1e6)
    return {"all_equal_and_valid": all(checks), "outcomes": outcomes,
            "measurements": {"scope": "Resident Python CPU unit-hop BFS on constructed real-device resource queries; no netlist constraints/timing. Parsing, fitting, exception generation and trace recording excluded from timed query batches.",
                             "warmup_per_query_per_provider": 1, "repetitions": repetitions,
                             "provider_order": "rotate each repetition", "clock": "time.perf_counter_ns",
                             "trace_recording_timed": False,
                             "timed_query_ids": [q["id"] for q in timed_queries],
                             "provider_construction_ms": preparation_ms,
                             "query_batch_ms": batches,
                             "median_query_batch_ms": {n: median(v) for n, v in batches.items()},
                             "per_query_ms": per_query,
                             "whole_router_speedup": None, "hardware_speedup": None}}
