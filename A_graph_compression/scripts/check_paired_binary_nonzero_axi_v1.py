#!/usr/bin/env python3
"""Independently inspect both relocated encoded-candidate environments."""
import json
from pathlib import Path
import re
from check_vitis_kernel import digest,require
from check_compact_nonzero_axi_models_v1 import audit_model

ROOT=Path(__file__).resolve().parents[1]


def main():
    source=ROOT/'results/paired_binary_nonzero_axi_preparation_20261029_v1.json';proof=json.loads(source.read_text())
    target=ROOT/'results/paired_binary_nonzero_axi_structure_audit_20261029_v1.json';require(not target.exists(),'Refuse overwrite')
    require(proof['status']=='paired_encoded_candidates_all44_pointers_and30_models_nonzero_environment_prepared_only' and proof['address_offset']==4096,'Different preparation')
    require([m['graph_mode'] for m in proof['modes']]==[0,1] and [m['encoded_fsm_modules'] for m in proof['modes']]==[43,45],'Different original encoded modes')
    files=dict(proof['files']);files[str(source)]=digest(source);records=[]
    inventory=json.loads((ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json').read_text());names={p['name'] for p in inventory['ports']}
    paired=json.loads((ROOT/'results/paired_binary_fsm_candidates_preparation_audit_20261025_v1.json').read_text())
    for mode in proof['modes']:
        require(set(mode['pointer_vectors'])==names and len(names)==44 and len(mode['models'])==30,'Partial scope')
        require({m['bundle']:m['width_depth_pages'] for m in mode['models']}==paired['shared_bus_width_depth_pages'],'Asymmetric capacities')
        candidate_plan=json.loads(Path(mode['candidate_plan']).read_text());candidate_dir=Path(mode['candidate_plan']).parent/'verilog'
        old_models={p.name for p in candidate_dir.glob('AESL_axi_master_*.v')}
        require({Path(m['source']).name for m in mode['models']}==old_models and len(old_models)==30,'Missing original model')
        for m in mode['models']:
            original=Path(m['source']);candidate=Path(m['target'])
            require(original==candidate_dir/candidate.name,'Different model source')
            require(digest(original)==candidate_plan['files'][str(original)],'Original DPI model changed')
            require(audit_model(original.read_text(),candidate.read_text(),m['bundle'])==m['structure'],'Changed wrapper structure')
        for name,row in mode['pointer_vectors'].items():
            original=Path(row['source']).read_text();translated=Path(row['target']).read_text()
            for text,address in [(original,row['original_address']),(translated,row['original_address']+4096)]:
                tx=re.findall(r'\[\[transaction\]\]\s+(\d+)\s+(0x[0-9a-fA-F]+)\s+\[\[/transaction\]\]',text)
                require([int(i) for i,v in tx]==list(range(4)) and [int(v,16) for i,v in tx]==[address]*4 and len(re.findall(r'0x[0-9a-fA-F]+',text))==4,'Incomplete four-address transaction stream')
            require(re.sub(r'0x[0-9a-fA-F]+',lambda m:'0x'+format(int(m[0],16)-4096,'0'+str(len(m[0])-2)+'x'),translated)==original,'Changed non-address vector text')
        expected_retained={str(p):candidate_plan['files'][str(p)] for p in candidate_dir.iterdir() if p.is_file() and not p.name.startswith('AESL_axi_master_')}
        require(mode['unchanged_candidate_dut_and_rom']==expected_retained,'Missing encoded DUT/ROM preservation')
        records.append(dict(graph_mode=mode['graph_mode'],models=30,pointers=44,transactions=4,encoded_dut_files_preserved=len(expected_retained)))
    for p,h in files.items():require(digest(p)==h,'Changed paired address evidence '+p)
    files[str(Path(__file__).resolve())]=digest(__file__)
    report=dict(status='both_encoded_modes_complete_nonzero_address_environment_structure_independently_verified',files=files,modes=records,
                rtl_executed=False,full_kernel_verified=False,
                limits=['No new encoding transformation; existing43/45-module DUT and full ROM/file sets preserved.',
                        'Address wrappers structurally checked against original DPI model bodies; integrated DPI behavioral regression and full44 RTL remain required.',
                        'Existing failed chain is not resumed or passed by this preparation.'])
    with target.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],len(files))


if __name__=='__main__':main()
