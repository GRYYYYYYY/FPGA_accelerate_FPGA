"""Deterministic list-scheduling example using explicit shared resource IDs."""


def run(case):
    workers, capacity = case["workers"], case["worker_state_capacity_bytes"]
    if workers < 1 or capacity < 1:
        raise ValueError("Invalid worker count/capacity")
    tasks = {task["id"]: task for task in case["tasks"]}
    if len(tasks) != len(case["tasks"]):
        raise ValueError("Duplicate task ID")
    for task in tasks.values():
        if not set(task["predecessors"]) <= tasks.keys():
            raise ValueError("Unknown dependency")
        if task["work_units"] <= 0 or not 0 <= task["state_bytes"] <= capacity:
            raise ValueError("Invalid work estimate or task exceeds worker capacity")
    remaining, completed = set(tasks), {}
    worker_free, resource_free, schedule = [0] * workers, {}, []
    while remaining:
        ready = sorted(t for t in remaining if set(tasks[t]["predecessors"]) <= completed.keys())
        if not ready:
            raise ValueError("Dependency cycle")
        task = tasks[ready[0]]
        dependency_end = max([completed[d] for d in task["predecessors"]] + [0])
        resource_end = max([resource_free.get(r, 0) for r in task["resource_ids"]] + [0])
        start, worker = min((max(free, dependency_end, resource_end), index)
                            for index, free in enumerate(worker_free))
        end = start + task["work_units"]
        worker_free[worker] = end
        for resource in task["resource_ids"]:
            resource_free[resource] = end
        completed[task["id"]] = end
        remaining.remove(task["id"])
        schedule.append({"task": task["id"], "worker": worker, "start_units": start, "end_units": end})
    by_id = {row["task"]: row for row in schedule}
    dependencies_ok = all(by_id[d]["end_units"] <= row["start_units"]
                          for row in schedule for d in tasks[row["task"]]["predecessors"])
    conflicts_ok = True
    for i, row in enumerate(schedule):
        for other in schedule[i + 1:]:
            overlap = max(row["start_units"], other["start_units"]) < min(row["end_units"], other["end_units"])
            shared = set(tasks[row["task"]]["resource_ids"]) & set(tasks[other["task"]]["resource_ids"])
            if overlap and (shared or row["worker"] == other["worker"]):
                conflicts_ok = False
    return {"checks": {"dependencies_respected": dependencies_ok, "resource_and_worker_conflicts_absent": conflicts_ok},
            "observations": {"estimated_makespan_units": max(worker_free),
                             "scope": "schedule estimate in abstract work units; no router executed"},
            "outputs": {"schedule": schedule}}
