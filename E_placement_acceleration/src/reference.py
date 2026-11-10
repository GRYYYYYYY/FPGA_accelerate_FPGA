"""Toy placement candidate legality and weighted HPWL; not a full placer."""


def run(case):
    sites = {s["id"]: s for s in case["sites"]}
    cells = {c["id"]: c for c in case["cells"]}
    if len(sites) != len(case["sites"]) or len(cells) != len(case["cells"]):
        raise ValueError("Duplicate site/cell ID")
    baseline = {c["id"]: c["site"] for c in case["cells"]}
    if any(s not in sites for s in baseline.values()):
        raise ValueError("Unknown initial site")
    for net in case["nets"]:
        if not net["cells"] or not set(net["cells"]) <= cells.keys() or net.get("weight", 1) < 0:
            raise ValueError("Invalid net")
    rows = []
    for candidate in case["candidates"]:
        placement = dict(baseline)
        for cell_id, site_id in candidate["moves"].items():
            if cell_id not in cells or site_id not in sites:
                raise ValueError("Candidate refers to unknown cell/site")
            placement[cell_id] = site_id
        violations, occupied = [], {}
        for cell_id, site_id in placement.items():
            cell, site = cells[cell_id], sites[site_id]
            if site_id in occupied:
                violations.append(f"site_conflict:{site_id}")
            occupied[site_id] = cell_id
            if cell["type"] != site["type"]:
                violations.append(f"resource_type:{cell_id}")
            if cell.get("fixed", False) and site_id != cell["site"]:
                violations.append(f"fixed_cell:{cell_id}")
            if "region" in cell:
                x0, y0, x1, y1 = cell["region"]
                if not (x0 <= site["x"] <= x1 and y0 <= site["y"] <= y1):
                    violations.append(f"region:{cell_id}")
        for rule in case.get("cascades", []):
            a, b = sites[placement[rule["first"]]], sites[placement[rule["second"]]]
            if (b["x"] - a["x"], b["y"] - a["y"]) != (rule["dx"], rule["dy"]):
                violations.append(f"cascade:{rule['first']}:{rule['second']}")
        hpwl = 0
        for net in case["nets"]:
            points = [sites[placement[cell]] for cell in net["cells"]]
            hpwl += net.get("weight", 1) * (max(p["x"] for p in points) - min(p["x"] for p in points)
                                          + max(p["y"] for p in points) - min(p["y"] for p in points))
        rows.append({"id": candidate["id"], "legal_in_toy_model": not violations,
                     "violations": violations, "weighted_hpwl": hpwl})
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate candidate ID")
    feasible = [row for row in rows if row["legal_in_toy_model"]]
    best = min(feasible, key=lambda r: (r["weighted_hpwl"], r["id"]))["id"] if feasible else None
    checks = {"expected_best_candidate": best == case["expected"]["best_candidate"]}
    by_id = {row["id"]: row for row in rows}
    for key, value in case["expected"]["legal"].items():
        checks[f"legality_{key}"] = by_id[key]["legal_in_toy_model"] == value
    return {"checks": checks,
            "observations": {"candidate_count": len(rows), "scope": "site coordinates, resource type, region and simple cascades only; no timing/site-pin model"},
            "outputs": {"candidates": rows, "best_candidate": best}}
