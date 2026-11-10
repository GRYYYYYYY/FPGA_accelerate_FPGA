"""CPU shortest-path reference for future queue/dataflow implementations."""
from research_common import shortest_path, verify_path


def run(case):
    output = shortest_path(case["graph"], case["source"], case["targets"])
    expected = case["expected"]
    checks = {"expected_status": output["status"] == expected["status"]}
    if output["status"] == "found":
        checks["traceback_valid"] = verify_path(case["graph"], output, case["source"], case["targets"])
        checks["expected_cost"] = output["cost"] == expected["cost"]
    return {"checks": checks,
            "observations": {**output["logical_counts"], "scope": "CPU Dijkstra on frozen nonnegative costs; no congestion negotiation"},
            "outputs": {"route": output}}
