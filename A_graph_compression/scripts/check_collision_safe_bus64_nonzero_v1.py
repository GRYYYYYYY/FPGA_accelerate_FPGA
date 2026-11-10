#!/usr/bin/env python3
"""Recheck every fresh RTL input, all30 guards and all44 relocated pointer files."""
import json
import argparse
from pathlib import Path
import re
import shlex
from check_vitis_kernel import digest,require
from check_compact_nonzero_axi_models_v1 import audit_model

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--mode',type=int,choices=[0,1],required=True)
    mode=parser.parse_args().mode
    BUNDLE=BASE/'collision_safe_bus64_nonzero_preparation_v1'/f'mode_{mode}'
    REPORT=ROOT/f'results/collision_safe_bus64_nonzero_mode_{mode}_audit_20261030_v1.json'
    require((BUNDLE/'preparation.json').is_file(),'Fresh bus64 nonzero preparation missing')
    require(not REPORT.exists(),'Refuse overwrite')
    path=BUNDLE/'preparation.json';p=json.loads(path.read_text())
    require(p['status']=='collision_safe_bus64_full44_nonzero_inputs_prepared_not_executed' and p['graph_mode']==mode and
            p['transactions']==4 and p['pointers']==44 and len(p['models'])==30 and len(p['vectors'])==44,
            'Wrong/incomplete preparation')
    files=dict(p['files'])
    for n,h in files.items():require(digest(n)==h,'Changed preparation input '+n)
    setup_path=Path(p['setup']);setup=json.loads(setup_path.read_text())
    require(setup['status']=='collision_safe_bus64_full44_four_transaction_csim_and_fresh_setup_verified_rtl_pending' and setup['graph_mode']==mode,
            'Wrong new setup gate')
    for n,h in setup['files'].items():require(digest(n)==h,'Changed new setup '+n)
    independent=ROOT/f'results/collision_safe_bus64_cosim_mode_{mode}_audit_20261030_v1.json'
    gate=json.loads(independent.read_text())
    require(gate['status']=='collision_safe_bus64_mode_full44_fresh_setup_independently_verified_RTL_pending' and gate['graph_mode']==mode,'Wrong independent full setup gate')
    for n,h in gate['files'].items():require(digest(n)==h,'Changed independent full setup '+n)
    files.update(gate['files']);files[str(independent)]=digest(independent)
    source=Path(setup['project'])/'solution/sim';dest=BUNDLE/'sim'
    require((dest/'tv/rtldatafile').is_dir() and not list((dest/'tv/rtldatafile').iterdir()),'Empty runtime output directory not preserved')
    old=ROOT/('results/compressed_batch_bus64_cosim_allocations_20261025_v1.json' if mode==0 else 'results/compressed_batch_compact_bus64_cosim_allocations_20261025_v1.json')
    old_alloc=json.loads(old.read_text())['allocations']
    require(p['allocations']==old_alloc,'Different original allocation layout')
    inv=ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json'
    ports={r['name']:r for r in json.loads(inv.read_text())['ports']}
    regions={r['name']:r for g in old_alloc for r in g['regions']}
    require(set(regions)==set(ports) and len(regions)==44,'Incomplete original allocation')
    expected=set()
    for q in source.rglob('*'):
        if not q.is_file():continue
        rel=q.relative_to(source)
        if (rel.parts[0]=='wrapc_pc' or rel.parts[:2]==('tv','cdatafile') or
                (len(rel.parts)==2 and rel.parts[0]=='verilog' and q.suffix in
                 ('.v','.sv','.svh','.vh','.dat','.prj','.ini','.sh','.tcl'))):expected.add(rel)
    actual={q.relative_to(dest) for q in dest.rglob('*') if q.is_file()}
    guard_rel=Path('verilog/axi_model_rebase_guard_v1.sv')
    require(actual==expected|{guard_rel},'Extra/missing full simulation input')
    changed=set();vectors=[]
    require({r['name'] for r in p['vectors']}==set(ports),'Duplicate/missing vector mapping')
    for r in p['vectors']:
        name=r['name'];canonical=name+'_r' if name in ('image','config') else name
        rel=Path('tv/cdatafile')/f'c.search_batch_trace_top_v2.autotvin_{canonical}.dat'
        original=(source/rel).read_text();new=(dest/rel).read_text()
        old_values=re.findall(r'\[\[transaction\]\]\s+(\d+)\s+(0x[0-9a-fA-F]+)\s+\[\[/transaction\]\]',original)
        new_values=re.findall(r'\[\[transaction\]\]\s+(\d+)\s+(0x[0-9a-fA-F]+)\s+\[\[/transaction\]\]',new)
        require([int(i) for i,v in old_values]==[int(i) for i,v in new_values]==[0,1,2,3],'Wrong vector transactions')
        require([int(v,16) for i,v in old_values]==[regions[name]['start']]*4 and
                [int(v,16) for i,v in new_values]==[regions[name]['start']+4096]*4,'Wrong pointer addresses')
        restored=re.sub(r'0x[0-9a-fA-F]+',lambda m:'0x'+format(int(m[0],16)-4096,'0'+str(len(m[0])-2)+'x'),new)
        require(restored==original,'Pointer framing/non-address data changed')
        require(r['path']==str(dest/rel) and r['sha256']==digest(dest/rel),'Manifest pointer mismatch')
        changed.add(rel);vectors.append(dict(name=name,old_address=regions[name]['start'],new_address=regions[name]['start']+4096))
    models=[];marker='\n// Independent conservative read-only AXI burst guard.\n'
    expected_bundles={r['bundle'] for r in ports.values()}
    require({r['bundle'] for r in p['models']}==expected_bundles and len(expected_bundles)==30,'Incomplete model set')
    for row in p['models']:
        bundle=row['bundle'];rel=Path('verilog')/f'AESL_axi_master_{bundle}.v'
        raw=(source/rel).read_text();guarded=raw
        readonly=[r for g in old_alloc for r in g['regions'] if ports[r['name']]['bundle']==bundle and r['readonly']]
        require(row['readonly']==readonly,'Wrong RO coverage')
        if readonly:
            original_model=BASE/'compact_native_stack_recovery_v3/sim/verilog'/rel.name
            old_body=original_model.read_text();require(old_body.count(marker)==1,'Missing original guard')
            ro=old_body.split(marker)[1].rsplit('endmodule',1)[0]
            require(raw.count('endmodule')==1,'Fresh model module count differs')
            guarded=raw.replace('endmodule',marker+ro+'endmodule')
        proof=audit_model(guarded,(dest/rel).read_text(),bundle)
        require(digest(source/rel)==row['raw_sha256'] and digest(dest/rel)==row['wrapped_sha256'],'Model hash mismatch')
        require(proof==row['structural'],'Different structural proof')
        models.append(dict(bundle=bundle,readonly=readonly,structural=proof));changed.add(rel)
    prj=Path('verilog/search_batch_trace_top_v2.prj')
    require((dest/prj).read_text()==(source/prj).read_text()+'sv xil_defaultlib "axi_model_rebase_guard_v1.sv"\n',
            'Project changed beyond original guard inclusion');changed.add(prj)
    require(digest(dest/guard_rel)==digest(ROOT/'hardware/vitis/axi_model_rebase_guard_v1.sv'),'Original guard changed')
    for rel in expected-changed:require(digest(source/rel)==digest(dest/rel),'Other generated input/DUT/ROM changed '+str(rel))
    require(set(p['changes'])=={str(dest/r) for r in changed},'Change set mismatch')
    raw_command=shlex.split((source/'verilog/run_xsim.sh').read_text().strip().splitlines()[0])
    prefix=['prlimit','--as=206158430208:206158430208','--stack=268435456:268435456','--core=0:0','--','/usr/bin/time','-v']
    expected_command=prefix+raw_command+['-mt','off','--O0','--stats','--timescale','1ns/1ps']
    require(p['compile_command']==expected_command and p['compile_cwd']==str(dest/'verilog'),'Different native compiler command')
    require((p['runtime_as_bytes'],p['compiler_as_bytes'],p['stack_bytes'],p['core_bytes'])==
            (96*1024**3,192*1024**3,256*1024**2,0),'Changed finite limits')
    for q in [path,setup_path,old,inv,Path(__file__).resolve(),ROOT/'scripts/check_compact_nonzero_axi_models_v1.py']:
        files[str(q)]=digest(q)
    result=dict(status='collision_safe_bus64_full44_inputs_all30_guards_all44_relocations_independently_verified',graph_mode=mode,
                files=files,models=models,vectors=vectors,unchanged_input_files=len(expected-changed),
                transactions=4,pointers=44,compile_command=p['compile_command'],rtl_executed=False,
                limits=['Input preparation/guard structure only. No compiled or simulated RTL acceptance.',
                        'Fresh complete4tx original postcheck and full44 snapshots remain mandatory.'])
    REPORT.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])


if __name__=='__main__':main()
