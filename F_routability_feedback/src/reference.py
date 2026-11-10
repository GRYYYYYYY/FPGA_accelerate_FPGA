"""Budgeted local path queries under fixed external reservations."""
from research_common import shortest_path, verify_path


def run(case):
    outputs, checks = [], {}
    for candidate in case["candidates"]:
        route = shortest_path(case["local_graph"], candidate["source"], candidate["targets"],
                              blocked=case["fixed_reserved_nodes"], max_expansions=candidate["budget"])
        status = {"found": "local_path_found", "no_path": "no_path_in_fixed_local_model",
                  "budget_exhausted": "unknown_budget_exhausted"}[route["status"]]
        outputs.append({"id": candidate["id"], "local_status": status,
                        "global_routable": None, "route": route})
        checks[f"status_{candidate['id']}"] = status == case["expected_status"][candidate["id"]]
        if route["status"] == "found":
            checks[f"path_{candidate['id']}"] = verify_path(case["local_graph"], route, candidate["source"], candidate["targets"])
            checks[f"reserved_{candidate['id']}"] = not set(route["nodes"]) & set(case["fixed_reserved_nodes"])
    if len({row["id"] for row in outputs}) != len(outputs):
        raise ValueError("Duplicate candidate ID")
    return {"checks": checks,
            "observations": {"candidate_count": len(outputs), "scope": "independent local queries, frozen hard reservations; no whole-design feasibility claim"},
            "outputs": {"candidates": outputs}}
