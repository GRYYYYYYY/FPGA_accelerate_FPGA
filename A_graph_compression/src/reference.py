"""Toy template expansion checker; no device database compressor is implemented."""
from research_common import validate_graph


def run(case):
    graph, compact = case["graph"], case["compact"]
    validate_graph(graph)
    decoded = []
    for instance in compact["instances"]:
        mapping = instance["node_map"]
        for edge in compact["templates"][instance["template"]]:
            decoded.append({"id": f"{instance['id']}:{edge['id']}",
                            "src": mapping[str(edge["src"])], "dst": mapping[str(edge["dst"])],
                            "switch": edge["switch"], "cost": edge["cost"]})
    removed = set(compact.get("remove_edges", []))
    if not removed <= {edge["id"] for edge in decoded}:
        raise ValueError("Exception removes an unknown edge")
    decoded = [edge for edge in decoded if edge["id"] not in removed]
    decoded.extend(compact.get("add_edges", []))
    validate_graph({"nodes": graph["nodes"], "edges": decoded})

    def signatures(edges):
        return sorted((e["id"], e["src"], e["dst"], e["switch"], e["cost"]) for e in edges)

    return {"checks": {"canonical_edges_and_attributes_equal": signatures(decoded) == signatures(graph["edges"])},
            "observations": {"canonical_nodes": len(graph["nodes"]), "edges": len(decoded),
                             "template_count": len(compact["templates"]),
                             "scope": "handwritten toy templates; compression ratio and device coverage unmeasured"},
            "outputs": {"decoded_edges": decoded}}
