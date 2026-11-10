#!/usr/bin/env python3
"""Frozen scope and evidence contract for a new full native compact trial."""
import json
from pathlib import Path
import re
from check_vitis_kernel import digest, require
from check_compact_nonzero_axi_models_v1 import audit_model

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')
OLD = BASE/'compact_native_stack_recovery_v3'
ORIGINAL = BASE/'compressed_batch_compact_rtl_guarded_v1'
OUT = BASE/'compact_nonzero_native_rtl_v1'
PREP = ROOT/'data/derived/compact_nonzero_native_entry_20261029_v1'
PREPORT = ROOT/'results/compact_nonzero_native_entry_preparation_20261029_v1.json'
ACCEPTED = ROOT/'results/compact_nonzero_native_rtl_audit_20261029_v1.json'
BIN = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
GIB = 1024**3
RUNTIME_AS = 96*GIB
STACK = 256*1024**2
GUARD_FREE = 16*GIB
ERRORS = ['ERROR:', 'Fatal:', 'FATAL_ERROR', 'runtime error:', 'LLVM ERROR', 'A_RO_WRITE_VIOLATION',
          'A_RO_UNKNOWN_ADDRESS', 'A_RO_UNSUPPORTED_BURST', 'Simulator command interrupted',
          'engine not responding', 'unexpected manner']


def selected(relative):
    p=Path(relative)
    return ((len(p.parts)==2 and p.parts[0]=='verilog' and p.suffix in ['.v','.sv','.svh','.vh','.dat','.prj','.ini'])
            or p.parts[:2]==('tv','cdatafile') or p.parts[0]=='wrapc_pc')


def evidence():
    files={}
    def bind_report(name,status=None):
        p=ROOT/'results'/name; r=json.loads(p.read_text())
        if status: require(r['status']==status,'Wrong prerequisite '+name)
        files[str(p)]=digest(p)
        for n,h in r.get('files',{}).items():
            require(n not in files or files[n]==h,'Conflicting prerequisite evidence'); files[n]=h
        return r
    proof=bind_report('axi_rebase_regressions_independent_audit_20261029_v1.json',
                     'all30_structure_1300_positive20_negative_six_full_depth_models_evidence_independently_rechecked')
    require((proof['models'],proof['pointers'],proof['transactions'],proof['guard_requests'],proof['negative_guard_cases'],proof['representative_models'])==(30,44,4,1300,20,6),'Partial regression evidence')
    vectors=bind_report('compact_nonzero_axi_vectors_preparation_20261029_v1.json','full44_nonzero_pointer_vectors_prepared_only')
    models=bind_report('compact_nonzero_axi_models_preparation_20261029_v1.json','all30_full_depth_axi_models_wrapped_for_nonzero_addresses_prepared_only')
    require(vectors['offset_bytes']==4096 and len(vectors['pointer_vectors'])==44 and len(models['models'])==30,'Partial relocation')
    for name in ['plan.json','state.json','rtl.receipt.json','postcheck.receipt.json']:
        files[str(OLD/name)]=digest(OLD/name)
    oldstate=json.loads((OLD/'state.json').read_text())
    require(oldstate['status']=='failed' and oldstate['stage']=='postcheck','Different original failure')
    require(json.loads((OLD/'rtl.receipt.json').read_text())['exit_code']==0 and json.loads((OLD/'postcheck.receipt.json').read_text())['exit_code']==-6,'Different failure receipts')
    setup=BASE/'compressed_batch_compact_cosim_setup/setup.json'; s=json.loads(setup.read_text())
    require(s['mode']=='compact' and s['transactions']==4,'Wrong C/setup provenance')
    files[str(setup)]=digest(setup)
    for n,h in s['files'].items():
        require(n not in files or files[n]==h,'Conflicting setup provenance');files[n]=h
    for i in range(4):
        p=BASE/f'compressed_batch_compact_cosim_setup/hls_1_{i}.bin'
        require(p.stat().st_size==946498280,'Original full44 golden missing'); files[str(p)]=digest(p)
    for p in [ORIGINAL/'plan.json',ORIGINAL/'elaborate.receipt.json',ORIGINAL/'elaborate.log']:
        files[str(p)]=digest(p)
    for n,h in files.items(): require(digest(n)==h,'Changed prerequisite '+n)
    for m in models['models']: audit_model(Path(m['source']).read_text(),Path(m['target']).read_text(),m['bundle'])
    for row in vectors['pointer_vectors'].values():
        original=Path(row['source']).read_text(); relocated=Path(row['relocated']).read_text()
        tokens=re.findall(r'0x[0-9a-fA-F]+',relocated)
        require(len(tokens)==4 and all(int(x,16)==row['original_address']+4096 for x in tokens),'Different four relocated pointers')
        restored=re.sub(r'0x[0-9a-fA-F]+',lambda m:'0x'+format(int(m[0],16)-4096,'0'+str(len(m[0])-2)+'x'),relocated)
        require(restored==original,'Pointer relocation changed framing')
    return files,vectors,models


def commands():
    original=json.loads((ORIGINAL/'plan.json').read_text())['command']
    require(original[:2]==['/usr/bin/time','-v'] and original[2]==str(BIN/'xelab') and original[-4:]==['-mt','off','--O0','--stats'],'Different original compiler')
    # The successful original compilation had unlimited AS, unlike the96GiB runtime.
    # Retain that compiler policy; apply the16GiB live cgroup guard to all stages.
    prefix=['prlimit','--stack='+str(STACK)+':'+str(STACK),'--core=0:0']
    runtime=prefix+['--as='+str(RUNTIME_AS)+':'+str(RUNTIME_AS),'--']
    return [dict(phase='elaborate',command=prefix+['--']+original+['--timescale','1ns/1ps'],cwd=str(OUT/'sim/verilog')),
            dict(phase='rtl',command=runtime+[str(BIN/'xsim'),'--noieeewarnings','search_batch_trace_top_v2','-tclbatch',str(OUT/'bounded.tcl')],cwd=str(OUT/'sim/verilog')),
            dict(phase='postcheck',command=runtime+[str(OUT/'sim/wrapc_pc/cosim.pc.exe')],cwd=str(OUT/'sim/wrapc_pc'))]


def verify_preparation():
    r=json.loads(PREPORT.read_text())
    require(r['status']=='nonzero_native_full4tx44pointers30models_entry_prepared' and r['commands']==commands(),'Different prepared scope/commands')
    require((r['transactions'],r['pointers'],r['models'])==(4,44,30) and r['dut_unchanged'] and r['startup_gate_removed_by_user'],'Different full scope')
    require(r['runtime_as_bytes']==RUNTIME_AS and r['runtime_guard_free_bytes']==GUARD_FREE and r['compiler_as']=='original_unlimited','Different resource contract')
    for n,h in r['files'].items(): require(digest(n)==h,'Changed prepared input '+n)
    old=json.loads((OLD/'plan.json').read_text())['copied']
    expected={str(Path(p).relative_to(OLD/'sim')) for p in old if selected(Path(p).relative_to(OLD/'sim'))}
    require(set(r['manifest'])==expected|{'verilog/axi_model_rebase_guard_v1.sv'},'Changed complete input set')
    for relative,record in r['manifest'].items():
        require(digest(record['source'])==record['sha256'],'Changed planned source')
        if record['kind']=='unchanged':
            require(record['sha256']==old[str(OLD/'sim'/relative)]['sha256'],'Non-model/vector input changed')
    require(sum(m['kind']=='model' for m in r['manifest'].values())==30 and sum(m['kind']=='pointer' for m in r['manifest'].values())==44,'Partial mapped manifest')
    return r
