#!/usr/bin/env python3
"""Bounded XSim2022.2 test of installed clock primitives with full transcript audit."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from check_source_to_route import digest
from real_experiment import write_new
ROOT = Path(__file__).resolve().parents[1]
VIVADO = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2')


def audit_trace(text):
    if len(re.findall(r'^TEST_PASS clock_primitive_semantics cases=16 samples=192$', text, re.M)) != 1:
        raise ValueError('Missing/duplicate terminal PASS')
    if re.search(r'(?im)\b(?:fatal|error|CLOCK_FAIL|CLOCK_TIMEOUT)\b', text): raise ValueError('Simulation error/fatal')
    cases = re.findall(r'^CLOCK_CASE_PASS id=(\d+) leaf=(\d+) async=(\d+) inv_ce=(\d+) inv_i=(\d+) checks=(\d+)$', text, re.M)
    expected_cases = {(leaf*8+mode*4+ce*2+i,leaf,mode,ce,i,12) for leaf in range(2) for mode in range(2) for ce in range(2) for i in range(2)}
    if len(cases) != 16 or set(tuple(map(int,c)) for c in cases) != expected_cases: raise ValueError('Incomplete primitive parameter cross')
    samples = re.findall(r'^CLOCK_SAMPLE id=(\d+) phase=(\d+) i=([01xz]) ce=([01xz]) expected=([01xz]) actual=([01xz])$', text, re.M)
    keys = set()
    for case,phase,raw_i,raw_ce,expected,actual in samples:
        case,phase = int(case),int(phase); key=(case,phase)
        if key in keys or not 0 <= case < 16 or not 0 <= phase < 12: raise ValueError('Duplicate/invalid sample')
        keys.add(key); mode=(case//4)%2; ci=(case//2)%2; ii=case%2
        effective_i = [0,0,1,1,0,1,1,0,1,0,0,1][phase]
        effective_ce = [0,1,1,0,0,0,1,1,1,0,None,None][phase]
        wanted = [0,0,1,0 if mode else 1,0,0,1 if mode else 0,0,1,0,0,1][phase]
        if raw_i != str(effective_i^ii) or raw_ce != ('z' if effective_ce is None else str(effective_ce^ci)):
            raise ValueError('Stimulus differs from contract')
        if expected != str(wanted) or actual != str(wanted): raise ValueError('Independent behavioral expectation differs')
    if keys != {(c,p) for c in range(16) for p in range(12)}: raise ValueError('Missing behavioral samples')
    return {'parameter_cases':len(cases),'behavioral_samples':len(samples)}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    primitives=[VIVADO/'data/verilog/src/unisims'/name for name in ('BUFCE_ROW.v','BUFCE_LEAF.v')]
    glbl=VIVADO/'data/verilog/src/glbl.v';tb=ROOT/'tests/rtl/tb_clock_primitive_semantics.sv'
    for p in [*primitives,glbl,tb]:
        if not p.is_file():raise ValueError('Missing source: '+str(p))
    env=dict(os.environ);env['LD_PRELOAD']='/lib/x86_64-linux-gnu/libudev.so.1'
    commands=[['xvlog','--sv','-d','XIL_TIMING',*[str(p) for p in primitives],str(glbl),str(tb)],
              ['xelab','work.tb_clock_primitive_semantics','work.glbl','--debug','typical','--mt','off','-s','clock_semantics'],
              ['xsim','clock_semantics','-runall']]
    files={str(p):digest(p) for p in [Path(__file__),tb,*primitives,glbl]}
    write_new(out/'plan.json',{'backend':'XSim','vivado_version':'2022.2','owner_pid':os.getpid(),
        'sources':files,'commands':commands,'mode':'Installed timing-capable primitives with zero specified delays and no SDF; behavioral contract only.',
        'watchdog_ns':1000,'normal_finish_ns':210,'parameter_cases':16,'expected_samples':192})
    receipts=[]
    for index,command in enumerate(commands):
        command=[str(VIVADO/'bin'/command[0]),*command[1:]]
        with (out/f'stage_{index}.log').open('x') as log:
            proc=subprocess.run(command,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        receipts.append({'command':command,'exit_code':proc.returncode})
        write_new(out/f'stage_{index}.receipt.json',receipts[-1])
        if proc.returncode:raise RuntimeError('XSim stage failed: '+str(index))
        if re.search(r'(?im)^\s*(?:ERROR|FATAL)\b',(out/f'stage_{index}.log').read_text()):raise ValueError('Errors in stage transcript')
    trace=(out/'stage_2.log').read_text();counts=audit_trace(trace)
    for path,value in files.items():
        if digest(path)!=value:raise ValueError('Simulation source changed')
    artifacts={str(p):digest(p) for p in out.glob('*.log')}
    write_new(out/'report.json',{'status':'clock_primitive_behavior_contract_passed','counts':counts,
        'plan_sha256':digest(out/'plan.json'),'artifacts':artifacts,'receipts':receipts,
        'limitations':['No SDF annotation, routed-design simulation or timing signoff.',
            'Primitive Boolean/enable behavior does not establish physical site tie-offs, inversion selection, or ownership.',
            'Z-to-enabled behavior is the simulation model default, not proof that an unconnected physical CE is high.',
            'HARDSYNC is outside this test; observed BUFCE_ROW_FSR configuration offers SYNC/ASYNC only.']})
    print(json.dumps({'status':'clock_primitive_behavior_contract_passed',**counts}))


if __name__=='__main__':main()
