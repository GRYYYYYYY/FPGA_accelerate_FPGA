#!/usr/bin/env python3
"""Prepare per-mode bus64 full44/4tx nonzero RTL inputs from independently audited fresh setups."""
import json
import argparse
from pathlib import Path
import re
import shlex
import shutil
from check_vitis_kernel import digest, require
from prepare_compact_nonzero_axi_models_v1 import wrap
from check_compact_nonzero_axi_models_v1 import audit_model
from owned_sim_resource_policy_v1 import observe, abort_reason, POLICY
from run_compact_native_stack_recovery_v3 import atomic

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
RO_MARKER='\n// Independent conservative read-only AXI burst guard.\n'


def allocations(sim,ports):
    text=(sim/'wrapc_pc/apatb_search_batch_trace_top_v2.cpp').read_text()
    offsets={name:(int(a)*int(b),int(b)) for name,a,b in
             re.findall(r'(__xlx_offset_byte_param_\w+)\s*=\s*(\d+)\*(\d+);',text)}
    seen=set();groups=[]
    for match in re.finditer(r'port(\d+)\.param = \{ ([^}]+) \};\s*port\1\.depth = \{ ([^}]+) \};',text):
        names=[x.strip().removeprefix('__xlx_apatb_param_') for x in match[2].split(',')]
        depths=[int(x.strip()) for x in match[3].split(',')]
        require(len(names)==len(depths),'Malformed wrapper allocation')
        regions=[];bundles=set()
        for name,depth in zip(names,depths):
            canonical={'image_r':'image','config_r':'config'}.get(name,name)
            require(canonical in ports and canonical not in seen,'Duplicate/unknown pointer')
            seen.add(canonical);port=ports[canonical];bundle=port['bundle'];bundles.add(bundle)
            model=(sim/'verilog'/f'AESL_axi_master_{bundle}.v').read_text()
            width=re.search(re.escape(bundle)+r"_DATA_BITWIDTH\s*=\s*32'd\s*(\d+)",model)
            require(width is not None,'Missing model width')
            if '__xlx_offset_byte_param_'+name in offsets:
                start,unit=offsets['__xlx_offset_byte_param_'+name]
            else:
                require(len(names)==1 and re.search(r'port'+match[1]+r'\.offset = \{\s*\};',text),'Unexplained address')
                start,unit=0,int(width[1])//8
            size=depth*unit;require(size>=port['payload_bytes'],'Allocation shrank')
            regions.append(dict(name=canonical,start=start,end=start+size,allocated_bytes=size,
                                declared_bytes=port['payload_bytes'],readonly=port['const']))
        require(len(bundles)==1,'Mixed AXI bundle')
        ordered=sorted(regions,key=lambda r:r['start'])
        require(all(a['end']<=b['start'] for a,b in zip(ordered,ordered[1:])),'Overlapping allocation')
        groups.append(dict(wrapper_port=int(match[1]),regions=regions))
    require(seen==set(ports) and len(groups)==30,'Not the full44/30 interface')
    return groups


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--mode',type=int,choices=[0,1],required=True)
    mode=parser.parse_args().mode
    SETUP=BASE/'collision_safe_bus64_cosim_setup_v1'/f'mode_{mode}'
    OUT=BASE/'collision_safe_bus64_nonzero_preparation_v1'/f'mode_{mode}'
    audit_path=ROOT/f'results/collision_safe_bus64_cosim_mode_{mode}_audit_20261030_v1.json'
    require(audit_path.is_file(),'Independent fresh bus64 setup audit missing')
    audited=json.loads(audit_path.read_text())
    require(audited['status']=='collision_safe_bus64_mode_full44_fresh_setup_independently_verified_RTL_pending' and audited['graph_mode']==mode,'Wrong independent setup gate')
    for name,checksum in audited['files'].items():require(digest(name)==checksum,'Changed independently audited setup '+name)
    require(not OUT.exists(),'Refuse overwrite')
    setup_path=SETUP/'setup.json';setup=json.loads(setup_path.read_text())
    require(setup['status']=='collision_safe_bus64_full44_four_transaction_csim_and_fresh_setup_verified_rtl_pending',
            'Fresh full setup is not verified')
    require((setup['ports'],setup['transactions'],setup['models'],setup['graph_mode'])==(44,4,30,mode),'Scope changed')
    for n,h in setup['files'].items():require(digest(n)==h,'Changed fresh setup evidence '+n)
    initial=observe();source=Path(setup['project'])/'solution/sim'
    inventory_path=ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json'
    inventory=json.loads(inventory_path.read_text());ports={p['name']:p for p in inventory['ports']}
    groups=allocations(source,ports)
    old_alloc_path=ROOT/('results/compressed_batch_bus64_cosim_allocations_20261025_v1.json' if mode==0 else 'results/compressed_batch_compact_bus64_cosim_allocations_20261025_v1.json')
    old_alloc=json.loads(old_alloc_path.read_text())
    require(groups==old_alloc['allocations'],'New allocation layout differs; guard reuse needs fresh review')
    regression_path=ROOT/'results/axi_rebase_regressions_independent_audit_20261029_v1.json'
    regression=json.loads(regression_path.read_text())
    require(regression['status']=='all30_structure_1300_positive20_negative_six_full_depth_models_evidence_independently_rechecked',
            'Missing unchanged guard/model regression')
    for name,checksum in regression['files'].items():require(digest(name)==checksum,'Changed guard regression evidence '+name)
    OUT.mkdir(parents=True);destination=OUT/'sim';manifest=dict(regression['files']);changes={};models=[];vectors=[]
    def bind(p):manifest[str(p)]=digest(p)
    for p in source.rglob('*'):
        if not p.is_file():continue
        relative=p.relative_to(source)
        selected=(relative.parts[0]=='wrapc_pc' or relative.parts[:2]==('tv','cdatafile') or
                  (len(relative.parts)==2 and relative.parts[0]=='verilog' and p.suffix in
                   ('.v','.sv','.svh','.vh','.dat','.prj','.ini','.sh','.tcl')))
        if not selected:continue
        require(abort_reason(initial,observe()) is None,'New OOM during input copy')
        target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        require(digest(target)==digest(p),'Copy changed input '+str(relative));bind(p)
    (destination/'tv/rtldatafile').mkdir(parents=True)
    for group in groups:
        bundle=ports[group['regions'][0]['name']]['bundle']
        raw=source/'verilog'/f'AESL_axi_master_{bundle}.v'
        original=raw.read_text();guarded=original
        readonly=[r for r in group['regions'] if r['readonly']]
        if readonly:
            old_model=BASE/'compact_native_stack_recovery_v3/sim/verilog'/raw.name
            oldtext=old_model.read_text()
            require(oldtext.count(RO_MARKER)==1 and oldtext.count('endmodule')==1,'Unexpected original RO guard')
            guard_body=oldtext.split(RO_MARKER)[1].rsplit('endmodule',1)[0]
            require(original.count('endmodule')==1 and RO_MARKER not in original,'Fresh model is not unmodified')
            actual_spans=re.findall(r"if \(a_ro_first < 65'd(\d+) && a_ro_last >= 65'd(\d+)\) \$fatal\(1,\"A_RO_WRITE_VIOLATION "+bundle+r' (\w+)"\);',guard_body)
            require([(int(end),int(start),name) for end,start,name in actual_spans]==
                    [(r['end'],r['start'],r['name']) for r in readonly],'RO guard range mismatch')
            guarded=original.replace('endmodule',RO_MARKER+guard_body+'endmodule');bind(old_model)
        candidate=wrap(guarded,bundle)
        structural=audit_model(guarded,candidate,bundle)
        target=destination/'verilog'/raw.name;target.write_text(candidate)
        changes[str(target)]=dict(kind='original_generated_model_plus_original_RO_guard_and_checked_rebase',source=str(raw))
        models.append(dict(bundle=bundle,raw_sha256=digest(raw),readonly=readonly,
                           wrapped_sha256=digest(target),structural=structural))
        for region in group['regions']:
            canonical=region['name'];name=canonical+'_r' if canonical in ('image','config') else canonical
            p=destination/'tv/cdatafile'/f'c.search_batch_trace_top_v2.autotvin_{name}.dat'
            original=p.read_text();tokens=re.findall(r'\[\[transaction\]\]\s+(\d+)\s+(0x[0-9a-fA-F]+)\s+\[\[/transaction\]\]',original)
            require([int(i) for i,v in tokens]==list(range(4)) and
                    all(int(v,16)==region['start'] for i,v in tokens) and len(re.findall(r'0x[0-9a-fA-F]+',original))==4,
                    'Wrong actual pointer vectors '+canonical)
            shifted=re.sub(r'0x[0-9a-fA-F]+',lambda m:'0x'+format(int(m[0],16)+4096,'0'+str(len(m[0])-2)+'x'),original)
            restored=re.sub(r'0x[0-9a-fA-F]+',lambda m:'0x'+format(int(m[0],16)-4096,'0'+str(len(m[0])-2)+'x'),shifted)
            require(restored==original,'Pointer framing changed');p.write_text(shifted)
            vectors.append(dict(name=canonical,bundle=bundle,original_address=region['start'],
                                relocated_address=region['start']+4096,path=str(p),sha256=digest(p)))
            changes[str(p)]=dict(kind='all4_pointer_addresses_plus4096',original_address=region['start'])
    guard_source=ROOT/'hardware/vitis/axi_model_rebase_guard_v1.sv'
    guard_target=destination/'verilog'/guard_source.name;shutil.copy2(guard_source,guard_target);bind(guard_source)
    prj=destination/'verilog/search_batch_trace_top_v2.prj';prj.write_text(prj.read_text()+'sv xil_defaultlib "'+guard_target.name+'"\n')
    changes[str(prj)]=dict(kind='append_original_guard_compilation_unit')
    require(len(models)==30 and len(vectors)==44,'Partial preparation')
    for p in destination.rglob('*'):
        if not p.is_file():continue
        relative=p.relative_to(destination)
        if str(p) not in changes and p!=guard_target:
            require(digest(p)==digest(source/relative),'Unapproved simulation input change '+str(relative))
        bind(p)
    for p in [audit_path,setup_path,inventory_path,old_alloc_path,regression_path,Path(__file__).resolve(),
              ROOT/'scripts/prepare_compact_nonzero_axi_models_v1.py',ROOT/'scripts/check_compact_nonzero_axi_models_v1.py']:
        bind(p)
    command_lines=(destination/'verilog/run_xsim.sh').read_text().strip().splitlines()
    original_command=shlex.split(command_lines[0])
    require(Path(original_command[0]).name=='xelab' and '-R' not in original_command,'Unexpected generated flow')
    compile_command=['prlimit','--as=206158430208:206158430208','--stack=268435456:268435456','--core=0:0','--',
                     '/usr/bin/time','-v',str(BIN/'xelab'),*original_command[1:],'-mt','off','--O0','--stats','--timescale','1ns/1ps']
    report=dict(status='collision_safe_bus64_full44_nonzero_inputs_prepared_not_executed',graph_mode=mode,files=manifest,changes=changes,
                setup=str(setup_path),allocations=groups,models=models,vectors=vectors,transactions=4,pointers=44,
                compile_command=compile_command,compile_cwd=str(destination/'verilog'),resource_policy=POLICY,
                runtime_as_bytes=96*1024**3,compiler_as_bytes=192*1024**3,stack_bytes=256*1024**2,core_bytes=0,
                rtl_executed=False,limits=['Preparation only; independent input/guard/vector review must precede compilation.',
                'No DUT or ROM edits; only memory-model guards/address adapters and pointer input relocation.',
                'Four full transactions, original C postcheck and complete full44 snapshot comparisons remain mandatory.'])
    atomic(OUT/'preparation.json',report)
    print(report['status'])


if __name__=='__main__':main()
