#!/usr/bin/env python3
"""Read-only 500ms RSS observations; whole-process time -v remains authoritative."""
import argparse
import json
import os
from pathlib import Path
import time


def children(pid):
    try: return [int(p) for p in Path(f"/proc/{pid}/task/{pid}/children").read_text().split()]
    except (FileNotFoundError, ProcessLookupError): return []


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path)
    parser.add_argument("pid",type=int,help="existing benchmark runner PID")
    args=parser.parse_args();directory=args.directory.resolve()
    runner=Path(f"/proc/{args.pid}")
    if not runner.exists(): raise ValueError("Runner is not alive")
    birth=(runner/"stat").read_text().split()[21]
    summaries={};output=directory/"memory_observations.jsonl"
    with output.open("x") as out:
        while runner.exists():
            try:
                if (runner/"stat").read_text().split()[21]!=birth: break
                manifest=json.loads((directory/"manifest.json").read_text())
                if manifest["status"]!="running": break
                rows=manifest["runs"]
                if not rows or "exit_code" in rows[-1]: time.sleep(.5);continue
                row=rows[-1];name=row["name"]
                candidates=children(args.pid)
                for parent in list(candidates): candidates.extend(children(parent))
                for pid in candidates:
                    path=Path(f"/proc/{pid}")
                    executable=Path(os.readlink(path/"exe")).name
                    if executable not in ("router","router_original"): continue
                    status={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in (path/"status").read_text().splitlines()}
                    rss=int(status["VmRSS"].split()[0]);anon=int(status.get("RssAnon","0 kB").split()[0])
                    text=(directory/(name+".log")).read_text()
                    after_load="[prolog]" in text
                    sample={"name":name,"pid":pid,"time_ns":time.time_ns(),"rss_kib":rss,"anon_kib":anon,"after_load":after_load}
                    out.write(json.dumps(sample)+"\n");out.flush()
                    summary=summaries.setdefault(name,{"samples":0,"after_load_samples":0,"observed_peak_rss_kib":0,"observed_after_load_peak_rss_kib":0,"first_observation_after_load":after_load})
                    summary["samples"]+=1;summary["observed_peak_rss_kib"]=max(summary["observed_peak_rss_kib"],rss)
                    if after_load:
                        summary["after_load_samples"]+=1
                        summary["observed_after_load_peak_rss_kib"]=max(summary["observed_after_load_peak_rss_kib"],rss)
            except (FileNotFoundError,ProcessLookupError,KeyError,json.JSONDecodeError): pass
            time.sleep(.5)
    (directory/"memory_observation_summary.json").write_text(json.dumps({"interval_seconds":.5,"runner_pid":args.pid,
        "scope":"Observed RSS after prolog includes routing and write-out; may miss transient peaks. Late attachment is explicit.",
        "runs":summaries},indent=2)+"\n")
    print("Memory observer completed",flush=True)


if __name__=="__main__":main()
