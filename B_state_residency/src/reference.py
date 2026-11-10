"""Dense reset versus epoch-tagged labels on a small bounded state array."""


def run(case):
    capacity, bits = case["capacity"], case["epoch_bits"]
    if capacity <= 0 or not 1 <= bits <= 32:
        raise ValueError("Invalid state capacity or epoch width")
    dense, values, tags = [None] * capacity, [None] * capacity, [0] * capacity
    epoch, search_count = 0, 0
    dense_clears, tag_clears, wraps = 0, 0, 0
    reads, equal = [], True
    for operation in case["operations"]:
        kind = operation["op"]
        if kind == "begin":
            dense = [None] * capacity
            dense_clears += capacity
            epoch += 1
            if epoch >= 1 << bits:
                tags = [0] * capacity
                tag_clears += capacity
                wraps += 1
                epoch = 1
            search_count += 1
            continue
        if not search_count:
            raise ValueError("State access before begin")
        node = operation["node"]
        if not 0 <= node < capacity:
            raise ValueError("Node outside state array")
        if kind == "write":
            dense[node] = values[node] = operation["value"]
            tags[node] = epoch
        elif kind == "read":
            actual = values[node] if tags[node] == epoch else None
            equal = equal and actual == dense[node]
            reads.append({"search": search_count, "node": node, "value": actual})
        else:
            raise ValueError(f"Unknown operation: {kind}")
    return {"checks": {"dense_and_epoch_reads_equal": equal, "at_least_one_search": search_count > 0},
            "observations": {"searches": search_count, "epoch_wraps": wraps,
                             "logical_dense_reset_slots": dense_clears,
                             "logical_epoch_wrap_clear_slots": tag_clears,
                             "scope": "logical operation counts; no memory latency or hardware throughput model"},
            "outputs": {"reads": reads}}
