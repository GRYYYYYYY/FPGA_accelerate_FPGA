#!/usr/bin/env python3
"""Run the unchanged full workload with the independently verified trace entry."""
import json
import os
from pathlib import Path
import re
import subprocess
import time
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def main():
    prior=ROOT/'data/derived/batch_router_full_20261025_v1';original=json.loads((prior/'plan.json').read_text())
    gate=ROOT/'results/compressed_batch_trace_cases_20261025_v2.json';proof=json.loads(gate.read_text());require(proof['cases']==400 and proof['searches']==4938 and proof['net_snapshots']==3750 and proof['rounds']==1250,'Missing complete trace gate')
    for p,h in proof['files'].items():require(digest(p)==h,'Changed trace gate '+p)
    build=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_router');complete=json.loads((build/'regular_build_complete_v2.json').read_text());bp=build/'regular_build_plan_v2.json';plan_build=json.loads(bp.read_text())
    require(complete['status']=='compiled' and complete['plan_sha256']==digest(bp) and complete['binary_sha256']==digest(build/'router_v2'),'Missing verified optimized build')
    for p,h in {**plan_build['files'],**complete['objects']}.items():require(digest(p)==h,'Changed optimized input '+p)
    for phase,cmd in zip(['compile_csr_regular_v2','compile_compact_regular_v2','compile_router_v2'],plan_build['commands']):
        receipt=json.loads((build/(phase+'.receipt.json')).read_text());text=(build/(phase+'.log')).read_text()
        require(receipt['exit_code']==0 and receipt['command']==cmd and receipt['log_sha256']==digest(build/(phase+'.log')),'Wrong/failed build')
        if 'regular' in phase:require(re.findall(r'warning: (.*)',text)==["unused parameter ‘trace_control’ [-Wunused-parameter]"],'Unreviewed compiler warning')
    old_proof=ROOT/'results/batch_router_audit_20261025_v1.json';old=json.loads(old_proof.read_text());require(old['status']=='batch_two_full_router_conditions_independently_verified','Missing full baseline')
    execution=json.loads((prior/'execution_plan.json').read_text())
    for paths in original['inputs'].values():
        for p in paths.values():require(digest(p)==execution['files'][p],'Changed real workload input '+p)
    out=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_real');out.mkdir(exist_ok=False)
    pointer=ROOT/'data/derived/compressed_batch_real_20261025_v1';pointer.mkdir(exist_ok=False);(pointer/'location.json').write_text(json.dumps(dict(bundle=str(out),owner_pid=os.getpid(),local_storage_ephemeral=True),indent=2)+'\n')
    files={str(p):digest(p) for p in [gate,old_proof,prior/'plan.json',prior/'execution_plan.json',bp,build/'regular_build_complete_v2.json',build/'router_v2',Path(__file__).resolve(),ROOT/'scripts/check_compressed_batch_real.py']}
    for p,h in execution['files'].items():
        if any(p in row.values() for row in original['inputs'].values()):files[p]=h
    jobs=original['jobs'];require(jobs==[dict(mode='csr',execution='kernel',cpu=116),dict(mode='compact',execution='kernel',cpu=117)],'Changed workload matrix')
    commands=[]
    for job in jobs:
        inp=original['inputs'][job['mode']]
        commands.append(['taskset','-c',str(job['cpu']),str(build/'router_v2'),inp['image'],inp['fixture'],inp['sites'],'4096','80','200000','8','kernel',inp['config']])
    plan=dict(files=files,trace_gate=str(gate),build_complete=str(build/'regular_build_complete_v2.json'),prior_bundle=str(prior),prior_audit=str(old_proof),inputs=original['inputs'],jobs=jobs,commands=commands,trace_prefix=str(out/'trace'),trace_capacity_words=16777216,scope='Each mode executes both complete original batches; exact compressed diagnostic trace alongside unchanged raw observations.')
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');state=dict(owner_pid=os.getpid(),status='running',stage='full_real',completed=[],workers={})
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    save();running={};handles=[]
    env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'};env['A_BATCH_TRACE_OUTPUT_PREFIX']=str(out/'trace')
    for index,(job,cmd) in enumerate(zip(jobs,commands)):
        prefix=out/f'worker_{index:03d}';raw=prefix.with_suffix('.raw.json').open('x');log=prefix.with_suffix('.log').open('x');handles.extend([raw,log])
        child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=raw,stderr=log);start=time.monotonic();running[index]=(child,start,raw,log);state['workers'][str(index)]=child.pid;save()
        prefix.with_suffix('.submission.json').write_text(json.dumps(dict(pid=child.pid,command=cmd,condition=job,trace_prefix=env['A_BATCH_TRACE_OUTPUT_PREFIX'],plan_sha256=digest(out/'plan.json')),indent=2)+'\n')
    failed=[]
    while running:
        for index,(child,start,raw,log) in list(running.items()):
            code=child.poll()
            if code is None:continue
            raw.close();log.close();prefix=out/f'worker_{index:03d}'
            prefix.with_suffix('.receipt.json').write_text(json.dumps(dict(command=commands[index],condition=jobs[index],exit_code=code,process_wall_ms=(time.monotonic()-start)*1000,log_sha256=digest(prefix.with_suffix('.log')),raw_sha256=digest(prefix.with_suffix('.raw.json'))),indent=2)+'\n')
            if code:failed.append(index)
            state['completed'].append(index);del running[index];save()
        if running:time.sleep(10)
    if failed:state.update(status='failed',stage='full_real',failed_workers=failed);save();raise RuntimeError('Full diagnostic workers failed; prefixes retained')
    state['stage']='independent_raw_and_trace_audit';save()
    cmd=['taskset','-c','115','python3',str(ROOT/'scripts/check_compressed_batch_real.py'),'--bundle',str(out),'--output',str(ROOT/'results/compressed_batch_real_audit_20261025_v1.json')]
    with (out/'audit.log').open('x') as log:code=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT).returncode
    (out/'audit.receipt.json').write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=digest(out/'audit.log')),indent=2)+'\n')
    state.update(status='complete' if code==0 else 'failed',stage='independently_audited' if code==0 else 'audit_failed');save();require(code==0,'Full diagnostic audit failed')
if __name__=='__main__':main()
