#!/usr/bin/env python3
"""Require original production RTL, all37 actual transactions and full-state postcheck."""
import argparse
import json
from pathlib import Path
import re
from check_vitis_kernel import digest, require
from round_control_rtl_contract import golden, transactions


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);a=parser.parse_args();out=a.bundle.resolve()
    require(not a.output.exists(),'Refusing to overwrite RTL audit')
    plan_path=out/'plan.json';plan=json.loads(plan_path.read_text())
    state_path=out/'audit_owner_state.json';state=json.loads(state_path.read_text())
    live=json.loads((out/'state.json').read_text())
    require(live['owner_pid']==state['owner_pid'] and (live==state or live['status']=='complete' and live['stage']=='independently_audited'),'Different audit owner/state')
    require(state['status']=='running' and state['stage']=='independent_audit' or
            state['status']=='complete' and state['stage']=='independently_audited','RTL owner has not reached independent audit')
    setup_path=out/'setup.json';setup=json.loads(setup_path.read_text())
    execution_path=out/'execution_plan.json';execution=json.loads(execution_path.read_text())
    files={**plan['files'],**plan['synthesis'],**setup['files'],**execution['files']}
    for p,h in files.items():require(digest(p)==h,'Changed occupancy RTL input '+p)
    require(execution['plan_sha256']==digest(plan_path) and execution['setup_sha256']==digest(setup_path),'Different RTL preparation')
    for phase in ['compile_cpu','cpu','prepare','elaborate','rtl','postcheck']:
        log=out/(phase+'.log');rp=out/(phase+'.receipt.json');sp=out/(phase+'.submission.json')
        receipt=json.loads(rp.read_text());submission=json.loads(sp.read_text());text=log.read_text(errors='replace')
        require(receipt['exit_code']==0 and receipt['command']==submission['command'] and
                receipt['log_sha256']==digest(log) and submission['plan_sha256']==digest(plan_path),'Failed/different phase '+phase)
        if phase in execution['commands']:
            require(receipt['command']==execution['commands'][phase]['command'] and submission['cwd']==execution['commands'][phase]['cwd'],
                    'Different simulator execution '+phase)
        require(not any(x in text for x in ['ERROR:','FATAL_ERROR','runtime error:']),'Error in '+phase)
        if phase in ['cpu','postcheck']:golden(text)
        if phase=='rtl':
            require('ROUND_CONTROL_BOUNDED_RUN_RETURNED' in text and re.search(r'RTL Simulation :\s*37 / 37',text),'Incomplete RTL progress')
        for p in [log,rp,sp]:files[str(p)]=digest(p)
    solution=Path(plan['project'])/'solution'
    golden((solution/'csim/report/search_round_control_top_csim.log').read_text())
    perf=solution/'sim/verilog/search_round_control_top.performance.result.transaction.xml'
    cycles=transactions(perf.read_text())
    outputs=list((solution/'sim/tv/rtldatafile').glob('rtl.*.autotvout_*.dat'))
    require(outputs,'Missing actual RTL output vectors')
    for p in [plan_path,state_path,setup_path,execution_path,perf,*outputs,Path(__file__).resolve()]:files[str(p)]=digest(p)
    report=dict(status='production_round_control_full_depth_37_transactions_rtl_verified',files=files,
                transactions=37,cycles=cycles,capacities=dict(nodes=1048576,nets=65536),
                production_synthesis='unchanged',postcheck='all count/flag/control input words and result guards checked; all37 decisions match independent reference',
                limitations=['Synthetic transaction sequence in HLS AXI memory models; not a real XRT resident-device test.',
                             'All37 transactions retain full count/flag/result/control depths. Inputs are synthetic round observations, not generated full-ledger histories.',
                             'Final conflicting rounds still request history advancement; no-conflict termination does not.',
                             'No full real routing traffic in RTL, statistical peak-load performance, physical timing, board bandwidth or power claim.'])
    with a.output.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(status=report['status'],transactions=37,cycles=cycles)),flush=True)


if __name__=='__main__':main()
