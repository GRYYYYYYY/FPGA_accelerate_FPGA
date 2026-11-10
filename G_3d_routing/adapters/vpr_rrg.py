"""Stream native VPR XML into a directed, capacity-preserving SQLite graph.

This is a search projection, not a replacement VPR interchange file. Keep the
original XML for VPR. Capacities belong to RR nodes; incident CHANZ edges must
not receive separate capacity budgets. A spanning CHANZ has two layer bounds,
not a single layer. Edge IDs are zero-based XML encounter ordinals.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import sqlite3
import time
import xml.etree.ElementTree as ET

from adapters.common import sha256, write_new


SCHEMA = """
CREATE TABLE nodes (
 id INTEGER PRIMARY KEY, kind TEXT NOT NULL, capacity INTEGER NOT NULL CHECK(capacity>=0),
 direction TEXT NOT NULL, xlow INTEGER, ylow INTEGER, xhigh INTEGER, yhigh INTEGER,
 layer_low INTEGER, layer_high INTEGER, ptc TEXT, r_ohm REAL, c_farad REAL,
 segment_id INTEGER, raw_xml TEXT NOT NULL);
CREATE TABLE switches (
 id INTEGER PRIMARY KEY, kind TEXT NOT NULL, name TEXT,
 tdel_seconds REAL, r_ohm REAL, cin_farad REAL, cout_farad REAL, cinternal_farad REAL,
 raw_xml TEXT NOT NULL);
CREATE TABLE edges (
 id INTEGER PRIMARY KEY, src INTEGER NOT NULL REFERENCES nodes(id),
 dst INTEGER NOT NULL REFERENCES nodes(id), switch_id INTEGER NOT NULL REFERENCES switches(id),
 src_portal INTEGER REFERENCES nodes(id), dst_portal INTEGER REFERENCES nodes(id),
 direct_layer_change INTEGER NOT NULL, metadata_xml TEXT);
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE VIEW portals AS SELECT id, 'chanz:' || id AS resource_id, capacity,
 direction, xlow, ylow, xhigh, yhigh, layer_low, layer_high, r_ohm, c_farad
 FROM nodes WHERE kind='CHANZ';
CREATE VIEW vertical_edges AS SELECT e.*, s.tdel_seconds, s.r_ohm,
 s.cin_farad, s.cout_farad, s.cinternal_farad FROM edges e
 JOIN switches s ON s.id=e.switch_id
 WHERE src_portal IS NOT NULL OR dst_portal IS NOT NULL OR direct_layer_change=1;
"""


def number(attrs, key):
    # Missing optional timing fields remain NULL; no invented delay/capacitance.
    if key not in attrs:
        return None
    value = float(attrs[key])
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"Invalid nonnegative timing value {key}={attrs[key]}")
    return value


def export_graph(source, output, expected_sha256=None):
    source, output = Path(source).resolve(), Path(output).resolve()
    digest = sha256(source)
    if expected_sha256 and digest != expected_sha256:
        raise ValueError("RRG hash differs from pinned input")
    output.mkdir(parents=True, exist_ok=False)
    database = output / "rr_graph.sqlite"
    started = time.monotonic()
    connection = sqlite3.connect(database)
    connection.execute("PRAGMA foreign_keys=ON")
    connection.executescript(SCHEMA)
    # O(nodes) compact descriptors; XML elements are released after each record.
    nodes, switches, kinds = {}, set(), Counter()
    incoming, outgoing = Counter(), Counter()
    edge_batch, edge_count, vertical_count, direct_count = [], 0, 0, 0
    stack, root_attrs = [], {}
    try:
        for event, element in ET.iterparse(source, events=("start", "end")):
            if event == "start":
                stack.append(element)
                if len(stack) == 1:
                    if element.tag != "rr_graph":
                        raise ValueError("Expected rr_graph XML root")
                    root_attrs = dict(element.attrib)
                continue
            if len(stack) == 3:
                section, attrs = stack[1].tag, element.attrib
                if section == "rr_nodes" and element.tag == "node":
                    inode, kind = int(attrs["id"]), attrs["type"]
                    if inode < 0 or inode in nodes:
                        raise ValueError(f"Invalid/duplicate node ID {inode}")
                    loc = element.find("loc").attrib
                    low = int(loc.get("layer_low", loc.get("layer", "0")))
                    high = int(loc.get("layer_high", loc.get("layer", "0")))
                    if low < 0 or high < low or (kind == "CHANZ" and high == low):
                        raise ValueError(f"Invalid layer span at node {inode}")
                    if kind != "CHANZ" and high != low:
                        raise ValueError(f"Unsupported non-CHANZ spanning node {inode}")
                    timing = element.find("timing")
                    timing = timing.attrib if timing is not None else {}
                    segment = element.find("segment")
                    connection.execute("INSERT INTO nodes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                        inode, kind, int(attrs["capacity"]), attrs.get("direction", "NONE"),
                        *(int(loc[k]) for k in ("xlow", "ylow", "xhigh", "yhigh")),
                        low, high, loc["ptc"], number(timing, "R"), number(timing, "C"),
                        int(segment.get("segment_id")) if segment is not None else None,
                        ET.tostring(element, encoding="unicode")))
                    nodes[inode] = (kind, low, high)
                    kinds[kind] += 1
                elif section == "switches" and element.tag == "switch":
                    sid = int(attrs["id"])
                    if sid < 0 or sid in switches:
                        raise ValueError(f"Invalid/duplicate switch ID {sid}")
                    timing = element.find("timing")
                    timing = timing.attrib if timing is not None else {}
                    connection.execute("INSERT INTO switches VALUES (?,?,?,?,?,?,?,?,?)", (
                        sid, attrs["type"], attrs.get("name"),
                        *(number(timing, k) for k in ("Tdel", "R", "Cin", "Cout", "Cinternal")),
                        ET.tostring(element, encoding="unicode")))
                    switches.add(sid)
                elif section == "rr_edges" and element.tag == "edge":
                    src, dst, sid = (int(attrs[k]) for k in ("src_node", "sink_node", "switch_id"))
                    if src not in nodes or dst not in nodes or sid not in switches:
                        raise ValueError(f"Dangling or out-of-order edge {(src, dst, sid)}")
                    a, b = nodes[src], nodes[dst]
                    sp = src if a[0] == "CHANZ" else None
                    dp = dst if b[0] == "CHANZ" else None
                    direct = int(sp is None and dp is None and a[1] != b[1])
                    vertical_count += sp is not None or dp is not None or bool(direct)
                    direct_count += direct
                    if sp is not None:
                        outgoing[sp] += 1
                    if dp is not None:
                        incoming[dp] += 1
                    edge_batch.append((edge_count, src, dst, sid, sp, dp, direct,
                                       ET.tostring(element, encoding="unicode") if len(element) else None))
                    edge_count += 1
                    if len(edge_batch) >= 8192:
                        connection.executemany("INSERT INTO edges VALUES (?,?,?,?,?,?,?,?)", edge_batch)
                        edge_batch.clear()
                # Other sections are retained in the authoritative XML, not this projection.
                stack[1].remove(element)
            elif len(stack) == 2:
                stack[0].remove(element)
            stack.pop()
        connection.executemany("INSERT INTO edges VALUES (?,?,?,?,?,?,?,?)", edge_batch)
        if not nodes or not switches or not edge_count:
            raise ValueError("Empty/incomplete routing graph")
        connection.executescript("CREATE INDEX edge_src ON edges(src,dst,switch_id);\n"
                                 "CREATE INDEX edge_dst ON edges(dst,src);\n"
                                 "CREATE INDEX node_kind ON nodes(kind);")
        if connection.execute("PRAGMA foreign_key_check").fetchone():
            raise ValueError("Foreign key check failed")
        if sha256(source) != digest:
            raise ValueError("Source XML changed during export")
        summary = {
            "schema_version": 1, "status": "complete", "execution_kind": "model_rrg_export",
            "source": {"path": str(source), "sha256": digest, "root_attributes": root_attrs},
            "adapter_sha256": sha256(__file__),
            "nodes": len(nodes), "nodes_by_type": dict(kinds), "edges": edge_count,
            "switches": len(switches), "vertical_incident_or_direct_edges": vertical_count,
            "direct_layer_change_edges": direct_count,
            "portals_with_fanin_and_fanout": sum(incoming[n] > 0 and outgoing[n] > 0 for n in nodes if nodes[n][0] == "CHANZ"),
            "portals_without_fanin": sum(incoming[n] == 0 for n in nodes if nodes[n][0] == "CHANZ"),
            "portals_without_fanout": sum(outgoing[n] == 0 for n in nodes if nodes[n][0] == "CHANZ"),
            "capacity_semantics": "RR node capacity, per-net use; chanz:<node_id> is shared by all incident edges",
            "edge_identity": "zero-based XML edge ordinal plus directed (src,dst,switch_id); parallel edges retained",
            "timing_semantics": "R ohm; C farad; switch Tdel seconds, not path delay; absent fields NULL; full RC timing remains in VPR",
            "export_wall_seconds": time.monotonic() - started,
        }
        connection.execute("INSERT INTO metadata VALUES (?,?)", ("summary", json.dumps(summary)))
        connection.commit()
    except BaseException as exc:
        connection.rollback()
        write_new(output / "failure.json", {"status": "failed", "error": str(exc)})
        raise
    finally:
        connection.close()
    summary["database"] = {"path": str(database), "sha256": sha256(database), "bytes": database.stat().st_size}
    write_new(output / "summary.json", summary)
    return summary


def check_route_projection(database, route):
    """Check every used node/edge against the derived graph, including direction."""
    from adapters.route_audit import read_trace
    count = 0
    with sqlite3.connect(f"{Path(database).resolve().as_uri()}?mode=ro", uri=True) as db:
        for net in read_trace(route).values():
            trace = net["trace"]
            for node in trace:
                actual = db.execute("SELECT kind,xlow,ylow,layer_low,xhigh,yhigh,layer_high FROM nodes WHERE id=?", (node.inode,)).fetchone()
                if actual != (node.kind, *node.low, *node.high):
                    raise ValueError(f"Derived graph node mismatch: {node.inode}")
            for a, b in zip(trace, trace[1:]):
                if a.switch != -1:
                    if not db.execute("SELECT 1 FROM edges WHERE src=? AND dst=? AND switch_id=? LIMIT 1", (a.inode, b.inode, a.switch)).fetchone():
                        raise ValueError(f"Derived graph missing edge: {(a.inode, b.inode, a.switch)}")
                    count += 1
    return {"passed": True, "checked_trace_edges": count}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rr-graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sha256")
    args = parser.parse_args(argv)
    print(json.dumps(export_graph(args.rr_graph, args.output, args.sha256), indent=2))
    return 0
