#!/usr/bin/env python3
"""Freeze an isolated post-route optimization trial; never launch it implicitly."""
import hashlib
import json
import os
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def publish(path,value):
    temp=path.with_suffix(path.suffix+'.tmp')
    with temp.open('x') as f:
        json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temp,path)
def main():
    audit=ROOT/'results/search_packet_width64_physical_audit_20261025_v2.json'
    bindings=json.loads(audit.read_text())['files']
    source=ROOT/'data/derived/search_packet_width64_physical_20261025_v1/csr/routed.dcp'
    assert bindings[str(source)]==digest(source),'Baseline checkpoint differs'
    with zipfile.ZipFile(source) as z:assert z.testzip() is None
    template=ROOT/'data/derived/search_kernel_csr_physopt_20261024_v1/run_flow.tcl'
    help_file=template.parent/'local_help_mcp_history.json'
    help_text=help_file.read_text()
    assert 'AggressiveFanoutOpt' in help_text and '-tns_cleanup' in help_text
    out=ROOT/'data/derived/search_packet64_physopt_20261025_v1'
    out.mkdir(exist_ok=False)
    frozen=out/'baseline_routed.dcp';shutil.copyfile(source,frozen)
    assert digest(frozen)==digest(source)
    flow=template.read_text()
    old=str(ROOT/'data/derived/search_kernel_physical_20261024_v1/csr/routed.dcp')
    assert flow.count(old)==1 and flow.count('(-1.389)')==1
    flow=flow.replace(old,str(frozen)).replace('(-1.389)','(-0.382)')
    flow=flow.replace('CSR_PHYSOPT','PACKET64_PHYSOPT')
    (out/'run_flow.tcl').write_text(flow)
    inputs=[source,frozen,audit,template,help_file,out/'run_flow.tcl',Path(__file__).resolve()]
    current=int(Path('/sys/fs/cgroup/memory.current').read_text())
    limit=int(Path('/sys/fs/cgroup/memory.max').read_text())
    publish(out/'plan.json',dict(status='prepared_not_started',
        scope='Isolated packet64 routed-checkpoint physical optimization; unchanged DUT and timing constraints',
        expected_input_setup_slack_ns=-.382,part='xcu280-fsvh2892-2L-e',clock_period_ns=5,
        operations=['phys_opt_design -directive AggressiveFanoutOpt','route_design -directive Explore -tns_cleanup'],
        admission=dict(minimum_raw_free_bytes=64*1024**3,observed_current_bytes=current,limit_bytes=limit,
                       admitted=limit-current>=64*1024**3),
        acceptance=['Successful terminal command and independent artifact audit',
                    'Reopened baseline WNS matches -0.382 ns within 0.0011 ns',
                    'Unchanged timing constraints; complete legal route; setup, hold, DRC and methodology reported independently'],
        files={str(p):digest(p) for p in inputs}))
    print(out/'plan.json')
if __name__=='__main__':main()
