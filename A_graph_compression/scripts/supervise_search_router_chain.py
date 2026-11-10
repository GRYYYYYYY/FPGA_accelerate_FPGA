#!/usr/bin/env python3
"""One downstream owner: wait for existing controller, then snapshot and word."""
import json
import os
from pathlib import Path
import subprocess
import time
from prepare_search_heap_router import ROOT,digest
OUT=ROOT/'data/derived/search_router_chain_20261024_v1'
STAGES=[('controller','controller_router_pipeline.py','controller_router_20261024_v1','controller_router_audit_20261024_v1.json','four_full_router_controller_conditions_independently_verified'),
    ('snapshot','snapshot_router_pipeline.py','snapshot_router_20261024_v1','snapshot_router_audit_20261024_v1.json','four_full_router_snapshot_conditions_independently_verified'),
    ('word_snapshot','word_snapshot_router_pipeline.py','word_snapshot_router_20261024_v1','word_snapshot_router_audit_20261024_v1.json','four_full_router_word_snapshot_conditions_independently_verified')]

def save(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def live_owner(pid,script):
    try:cmd=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode()
    except FileNotFoundError:return False
    return script in cmd

def verified_gate(bundle,report,status):
    state=json.loads((bundle/'state.json').read_text())
    if state['status']!='complete':raise RuntimeError('Predecessor not complete')
    receipt_path=bundle/'audit_receipt.json';receipt=json.loads(receipt_path.read_text())
    if receipt['exit_code']!=0 or receipt['log_sha256']!=digest(bundle/'audit.log'):raise RuntimeError('Invalid predecessor audit receipt')
    result=json.loads(report.read_text())
    if result['status']!=status:raise RuntimeError('Wrong predecessor audit status')
    # The independent auditor already reread every raw result. At handoff bind
    # its receipt/log and every small artifact, without re-reading large raws.
    checked=0
    for p,h in result['files'].items():
        if p.endswith('.raw.json'):continue
        if digest(p)!=h:raise RuntimeError('Changed predecessor binding '+p)
        checked+=1
    return {'path':str(report),'sha256':digest(report),'audit_receipt_sha256':digest(receipt_path),'nonraw_bindings_checked':checked,'status':status}

def main():
    OUT.mkdir(exist_ok=False)
    files={str(Path(__file__).resolve()):digest(__file__)}
    for _,script,bundle,_,_ in STAGES:
        for p in [ROOT/'scripts'/script,ROOT/'data/derived'/bundle/'plan.json']:files[str(p)]=digest(p)
    save(OUT/'plan.json',{'files':files,'stages':STAGES,'policy':'Observe original controller owner; launch each not-yet-started successor once after verified audit. No automatic restart/recovery.'})
    state={'owner_pid':os.getpid(),'status':'running','stage':'await_controller','completed':[]}
    def update():
        p=OUT/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(OUT/'state.json')
    update()
    try:
        _,script,name,report,status=STAGES[0];bundle=ROOT/'data/derived'/name
        while True:
            original=json.loads((bundle/'state.json').read_text())
            if original['status']=='complete':break
            if original['status']!='running':raise RuntimeError('Original controller failed; no automatic relaunch')
            if not live_owner(original['owner_pid'],script):
                # Recheck state after the PID check to avoid a terminal-write race.
                original=json.loads((bundle/'state.json').read_text())
                if original['status']=='complete':break
                raise RuntimeError('Original controller owner missing; reconciliation required')
            if state.get('observed_stage')!=original['stage']:
                state.update(observed_owner=original['owner_pid'],observed_stage=original['stage']);update()
            time.sleep(15)
        gate=verified_gate(bundle,ROOT/'results'/report,status);save(OUT/'controller_gate.json',gate)
        state['completed'].append('controller');update()
        for stage,script,name,report,status in STAGES[1:]:
            for p,h in files.items():
                if digest(p)!=h:raise RuntimeError('Changed queue definition '+p)
            bundle=ROOT/'data/derived'/name
            if (bundle/'state.json').exists():raise RuntimeError('Successor already has an owner; no duplicate launch '+stage)
            command=['python3',str(ROOT/'scripts'/script)];log=OUT/(stage+'.log')
            with log.open('x') as stream:
                child=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
                save(OUT/(stage+'.submission.json'),{'command':command,'pid':child.pid,'plan_sha256':digest(OUT/'plan.json')})
                state.update(stage=stage,child_pid=child.pid);update();code=child.wait()
            save(OUT/(stage+'.receipt.json'),{'exit_code':code,'command':command,'log_sha256':digest(log)})
            if code:raise RuntimeError('Successor failed '+stage)
            gate=verified_gate(bundle,ROOT/'results'/report,status);save(OUT/(stage+'_gate.json'),gate)
            state['completed'].append(stage);update()
        state.update(status='complete',stage='all_three_independently_audited');update()
    except BaseException as e:
        state.update(status='failed',error=str(e));update();raise

if __name__=='__main__':main()
