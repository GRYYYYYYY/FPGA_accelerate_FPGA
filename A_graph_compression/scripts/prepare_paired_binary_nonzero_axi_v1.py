#!/usr/bin/env python3
"""Prepare checked address relocation for both frozen full44 encoded candidates."""
import json
from pathlib import Path
import re
from check_vitis_kernel import digest,require
from prepare_compact_nonzero_axi_models_v1 import wrap,interface
from check_compact_nonzero_axi_models_v1 import audit_model

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')


def main():
    out=ROOT/'data/derived/paired_binary_nonzero_axi_20261029_v1'
    target=ROOT/'results/paired_binary_nonzero_axi_preparation_20261029_v1.json'
    require(not out.exists() and not target.exists(),'Refuse overwrite')
    paired=ROOT/'results/paired_binary_fsm_candidates_preparation_audit_20261025_v1.json';proof=json.loads(paired.read_text())
    require(proof['status']=='both_graph_modes_matched_binary_fsm_candidate_preparations_verified_full_rtl_pending' and proof['shared_pointer_ports']==44 and proof['shared_axi_models']==30 and proof['transactions_per_mode']==4,'Incomplete paired preparation')
    files={str(paired):digest(paired)}
    for p,h in proof['files'].items():require(digest(p)==h,'Changed original paired proof');files[p]=h
    invp=ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json';inv=json.loads(invp.read_text());ports={p['name']:p for p in inv['ports']};require(len(ports)==44,'Partial inventory');files[str(invp)]=digest(invp)
    guard=ROOT/'hardware/vitis/axi_model_rebase_guard_v1.sv';files[str(guard)]=digest(guard)
    out.mkdir();modes=[]
    for mode,label,original_name,parent_name,allocation_name in [
        (0,'csr','hls_binary_fsm_candidate_20261025_v1','compressed_batch_bus64_rtl_guarded_v1','compressed_batch_bus64_cosim_allocations_20261025_v1.json'),
        (1,'compact','hls_compact_binary_fsm_candidate_20261025_v1','compressed_batch_compact_bus64_rtl_guarded_v1','compressed_batch_compact_bus64_cosim_allocations_20261025_v1.json')]:
        candidate=ROOT/'data/derived'/original_name;candidate_plan=json.loads((candidate/'plan.json').read_text());parent=BASE/parent_name
        setup=json.loads((parent/'plan.json').read_text());ap=ROOT/'results'/allocation_name;allocation=json.loads(ap.read_text())
        require(setup['graph_mode']==mode and setup['transactions']==4 and len(allocation['allocations'])==30,'Mode/scope mismatch')
        require(setup['allocation_sha256']==digest(ap),'Changed allocation report')
        for p,h in allocation['files'].items():require(digest(p)==h,'Changed original allocation evidence');files[p]=h
        files[str(ap)]=digest(ap);files[str(parent/'plan.json')]=digest(parent/'plan.json');files[str(candidate/'plan.json')]=digest(candidate/'plan.json')
        dest=out/label;(dest/'verilog').mkdir(parents=True);(dest/'cdatafile').mkdir()
        models=[];vectors={}
        for group in allocation['allocations']:
            bundles={ports[r['name']]['bundle'] for r in group['regions']};require(len(bundles)==1,'Mixed bundles');bundle=next(iter(bundles))
            original=candidate/'verilog'/('AESL_axi_master_'+bundle+'.v');require(digest(original)==candidate_plan['files'][str(original)],'Candidate model changed')
            text=original.read_text();new=wrap(text,bundle);details=audit_model(text,new,bundle)
            params=dict(interface(text,bundle)[2]);number=lambda v:int(re.fullmatch(r"32'd\s*(\d+)",v.strip())[1])
            dimensions=[number(params[bundle+'_DATA_BITWIDTH']),number(params[bundle+'_mem_depth']),number(params['mem_page_num'])]
            require(dimensions==proof['shared_bus_width_depth_pages'][bundle],'Changed width/depth/pages')
            p=dest/'verilog'/original.name;p.write_text(new);files[str(original)]=digest(original);files[str(p)]=digest(p)
            models.append(dict(bundle=bundle,source=str(original),target=str(p),width_depth_pages=dimensions,structure=details))
            for region in group['regions']:
                name=region['name'];require(name not in vectors,'Repeated pointer');vname=name+'_r' if name in ['image','config'] else name
                src=parent/'sim/tv/cdatafile'/('c.search_batch_trace_top_v2.autotvin_'+vname+'.dat')
                require(digest(src)==setup['copied_files'][str(src)],'Changed original pointer fixture')
                original_text=src.read_text();values=re.findall(r'\[\[transaction\]\]\s+(\d+)\s+(0x[0-9a-fA-F]+)\s+\[\[/transaction\]\]',original_text)
                require([int(i) for i,v in values]==list(range(4)) and [int(v,16) for i,v in values]==[region['start']]*4,'Wrong actual allocation addresses')
                require(region['end']<=2**64-4096 and region['end']-region['start']>=ports[name]['payload_bytes'],'Address overflow/reduced capacity')
                shifted=re.sub(r'0x[0-9a-fA-F]+',lambda m:'0x'+format(int(m[0],16)+4096,'0'+str(len(m[0])-2)+'x'),original_text)
                restored=re.sub(r'0x[0-9a-fA-F]+',lambda m:'0x'+format(int(m[0],16)-4096,'0'+str(len(m[0])-2)+'x'),shifted)
                require(restored==original_text,'Different pointer framing');dst=dest/'cdatafile'/src.name;dst.write_text(shifted)
                files[str(src)]=digest(src);files[str(dst)]=digest(dst)
                vectors[name]=dict(source=str(src),target=str(dst),original_address=region['start'],relocated_address=region['start']+4096,bundle=bundle,depth=ports[name]['depth'])
        require(set(vectors)==set(ports) and len(models)==30,'Partial relocation')
        # All candidate DUT and ROM files remain the existing frozen files. Only
        # the30 verification models above are new; no state encoding is changed.
        retained={}
        for p in (candidate/'verilog').iterdir():
            if p.is_file() and not p.name.startswith('AESL_axi_master_'):
                require(digest(p)==candidate_plan['files'][str(p)],'Frozen encoded DUT/ROM changed');retained[str(p)]=digest(p);files[str(p)]=digest(p)
        sink=candidate/'verilog/search_batch_trace_top_v2_sink_loop_worker.v'
        comparisons=[line.strip() for line in sink.read_text().splitlines() if "64'd0" in line and '==' in line and any(re.search(r'\b'+name+r'\b',line) for name in ['heap','slots','records','keys','unknown_nodes'])]
        require(len(comparisons)==5,'Unexpected encoded null-check cone')
        zeros=sorted(name for name,row in vectors.items() if row['original_address']==0)
        require(all(name in zeros for name in ['heap','slots','records','keys','unknown_nodes']),'Different original zero-address conflict')
        modes.append(dict(graph_mode=mode,label=label,candidate_plan=str(candidate/'plan.json'),models=models,pointer_vectors=vectors,
                          original_zero_base_pointers=zeros,unchanged_candidate_dut_and_rom=retained,
                          encoded_null_comparison_lines=comparisons,encoded_fsm_modules=len(candidate_plan['modules'])))
    require({m['bundle']:m['width_depth_pages'] for m in modes[0]['models']}=={m['bundle']:m['width_depth_pages'] for m in modes[1]['models']},'Asymmetric model dimensions')
    for name in ['prepare_paired_binary_nonzero_axi_v1.py','prepare_compact_nonzero_axi_models_v1.py','check_compact_nonzero_axi_models_v1.py']:
        p=ROOT/'scripts'/name;files[str(p)]=digest(p)
    for p,h in files.items():require(digest(p)==h,'Changed preparation evidence')
    report=dict(status='paired_encoded_candidates_all44_pointers_and30_models_nonzero_environment_prepared_only',files=files,modes=modes,
                address_offset=4096,transactions_per_mode=4,pointers_per_mode=44,models_per_mode=30,guard_source=str(guard),
                candidate_dut_changed_by_this_preparation=False,execution_entry_prepared=False,rtl_executed=False,
                prerequisites_remaining=['Independent re-read of both complete wrappers/pointer transforms and their frozen original DPI model proofs.',
                                         'Real DPI model-plus-address-wrapper behavior check; native model regression alone is not DPI integration execution.',
                                         'New typed full44 drivers/checkers must require actually accepted nonzero native baseline; preserve original C full snapshots.',
                                         'No concurrent large compilation while current native compiler/runtime is active.'])
    with target.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],[(m['label'],len(m['original_zero_base_pointers'])) for m in modes],len(files))


if __name__=='__main__':main()
