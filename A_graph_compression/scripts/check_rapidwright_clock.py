#!/usr/bin/env python3
"""Compare read-only RapidWright target routes against existing Vivado snapshots."""
import argparse
from collections import Counter
import json
from pathlib import Path
from check_vitis_kernel import digest,require
from real_experiment import write_new
ROOT=Path(__file__).resolve().parents[1]
TARGET='original_cost/genblk1[3].h_val_y_reg[55]_i_2_n_0'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    directory=ROOT/'data/derived/rapidwright_clock_20261023_v2'
    plan_path=directory/'plan.json';state_path=directory/'state.json';plan=json.loads(plan_path.read_text());state=json.loads(state_path.read_text())
    require(state['status']=='complete' and state['exit_code']==0,'Reader failed')
    require(digest(directory/'read.log')==state['log_sha256'],'Reader log changed')
    for name,h in plan['files'].items():require(digest(name)==h,'Reader dependency changed: '+name)
    previous=ROOT/'data/derived/rapidwright_clock_20261023_v1/plan.json';original=json.loads(previous.read_text())
    for name,h in original['files'].items():require(digest(name)==h,'Original copy/source changed: '+name)
    paths=[plan_path,state_path,directory/'read.log',previous,Path(__file__).resolve()]
    stages={}
    proof_path=ROOT/'results/clock_row_probe_input_20261023_v1.json';proof=json.loads(proof_path.read_text());paths.append(proof_path)
    for stage,folder,expected in [('baseline','site_full_applied_20261023_v1',6),('probe','clock_row_route_probe_full_20261023_v2',11)]:
        raw=directory/(stage+'.tsv');snapshot=ROOT/'data/netlist'/folder/'snapshot.tsv';dcp=ROOT/'data/netlist'/folder/'routed.dcp'
        copy=ROOT/'data/derived/rapidwright_clock_20261023_v1'/(stage+'.dcp')
        require(digest(copy)==digest(dcp),'Copied DCP differs')
        rows=[l.split('\t') for l in raw.read_text().splitlines()]
        require(rows[-1]==['complete',str(copy)],'Incomplete/wrong checkpoint')
        require(Counter(r[0] for r in rows)=={'meta':3,'design_counts':1,'target_net':1,'target_pip':expected,'site':2,'complete':1},'Unexpected capture coverage')
        meta={r[1]:r[2] for r in rows if r[0]=='meta'}
        require(meta=={'schema':'rapidwright_clock_observation_v2','checkpoint':str(copy),'part':'xcu280-fsvh2892-2L-e'},'Wrong metadata')
        require([r[1:] for r in rows if r[0]=='target_net']==[[TARGET,'WIRE',str(expected)]],'Target mismatch')
        require({tuple(r[1:]) for r in rows if r[0]=='site'}=={('BUFCE_ROW_FSR_X21Y6','BUFCE_ROW_FSR','absent'),('BUFCE_LEAF_X110Y26','BUFCE_LEAF','absent')},'New site evidence requires review')
        physical=[r for r in rows if r[0]=='target_pip'];names=[r[6] for r in physical]
        require(len(names)==len(set(names)) and all(r[4]=='false' for r in physical),'Duplicate/reversed route')
        vivado=[l.split('\t') for l in snapshot.read_text().splitlines()]
        expected_names=[r[2] for r in vivado if r[:2]==['pip',TARGET]]
        require(Counter(names)==Counter(expected_names),'Physical PIP identities differ from Vivado')
        route_through=[r[6] for r in physical if r[5]=='true']
        require(set(route_through)==(set(proof['pseudo_pips']) if stage=='probe' else set()),'Pseudo-route identity differs')
        primitives=[r for r in vivado if r[0]=='cell'];constants=sum(r[2] in ['VCC','GND'] for r in primitives)
        counts=next(r[1:] for r in rows if r[0]=='design_counts')
        require(list(map(int,counts))==[1824,2632,203],'Reader design count changed')
        stages[stage]={'exact_target_pips':expected,'route_through_pips':route_through,'implicit_clock_site_instances_present':0,
            'reader_design_counts':list(map(int,counts)),'vivado_primitive_count':len(primitives),'vivado_constant_primitives':constants,
            'count_interpretation':'The9-cell difference is consistent with5GND+4VCC cells; full cell-by-cell equivalence was not checked.'}
        paths += [raw,snapshot,dcp,copy]
    report={'status':'target_routes_match_reader_omits_implicit_clock_sites','stages':stages,
        'files':{str(p):digest(p) for p in paths},'reader_plan_dependencies':plan['files'],
        'limitations':['RapidWright2022.2.3 preserves the11-PIP probe route including both clock route-through PIPs, but does not reconstruct these two SiteInsts or their BEL attributes.',
            'Empty site objects are not evidence of free resources, constant values or inversion polarity.',
            'Only this target route and declared capture coverage were compared; no full RapidWright/Vivado design-equivalence claim.',
            'No instance added to the14-instance validated site model.'],
        'reference':'https://www.rapidwright.io/javadoc/com/xilinx/rapidwright/design/SiteInst.html'}
    write_new(a.output,report);print(json.dumps({'status':report['status'],'stages':stages}))

if __name__=='__main__':main()
