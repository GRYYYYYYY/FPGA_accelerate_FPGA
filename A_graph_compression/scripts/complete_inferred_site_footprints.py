#!/usr/bin/env python3
"""Complete inferred LUT/MUX footprints without promoting unverified instances."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from lut_equation import truth_table, MASK
from import_vivado import sha256
from real_experiment import write_new


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,default=ROOT/'data/derived/region_all_nets_cap8_20261022_v1/site_requirements_v2.json')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    parent=json.loads(a.input.read_text());result=deepcopy(parent);changed=0
    for pip,record in result['pips'].items():
        if record.get('kind')!='lut_o6_route_through':continue
        match=re.search(r'_([A-H])([1-6])->>.*_([A-H])(MUX|_O)$',pip)
        if not match or match.group(1)!=match.group(3):raise ValueError('Unsupported LUT footprint shape')
        if match.group(4)!='MUX':continue
        if record['status']!='inferred_requires_adapter_validation':raise ValueError('Unexpected inference status')
        mux=record['site']+'/OUTMUX'+match.group(3)
        signals=set(record['signal_resources']);signals.add(mux+'/OUT');record['signal_resources']=sorted(signals)
        values={tuple(v) for v in record['configuration_values']};values.add((mux,'D6'))
        record['configuration_values']=[list(v) for v in sorted(values)];changed+=1
    evidence=[];proofs=[]
    for version in (1,2):
        path=ROOT/f'data/netlist/lut_route_probes_20261023_v{version}/verification.json'
        proof=json.loads(path.read_text());proofs.append(proof);evidence.append(path)
        for name,digest in proof['files'].items():
            if sha256(path.parent/name)!=digest:raise ValueError('Probe evidence changed')
    equations={r['pip']:r for r in proofs[0]['checks']};checked=0
    for probe in proofs[1]['checks']:
        equation=equations[probe['pip']];record=result['pips'][probe['pip']]
        signals=[equation['bel']+'/O6'];values=[]
        if probe['output_mux']:
            mux,setting=probe['output_mux'].split(':');signals.append(mux+'/OUT');values.append([mux,setting])
        expected_bits=[[equation['bel']+'/INIT',MASK,truth_table(equation['expected_equation'])]]
        if (sorted(record['signal_resources'])!=sorted(signals) or
            sorted(record['configuration_values'])!=sorted(values) or record['configuration_bits']!=expected_bits):
            raise ValueError('Completed footprint differs from physical probe: '+probe['pip'])
        checked+=1
    if set(result['pips'])!=set(parent['pips']):raise ValueError('PIP domain changed')
    if any(r['status']!=parent['pips'][pip]['status'] for pip,r in result['pips'].items()):
        raise ValueError('Unverified instance status promoted')
    result['status']='requirements_partial_not_legality_certificate'
    result['footprint_completion']={'changed_inferred_mux_records':changed,'known_physical_probe_payloads_matched':checked,
        'all_instance_verification_statuses_preserved':True,
        'files':{str(path):sha256(path) for path in [a.input,*evidence,Path(__file__)]}}
    result['limitations'].append('MUX footprints include output exclusivity and D6 selection; untested instances remain inferred, not authorized search requirements.')
    write_new(a.output,result)
    print(json.dumps({'output':str(a.output),'pips':len(result['pips']),'footprint_completion':result['footprint_completion']},indent=2))


if __name__=='__main__':main()
