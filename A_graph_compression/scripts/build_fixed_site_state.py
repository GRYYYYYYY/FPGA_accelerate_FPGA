#!/usr/bin/env python3
"""Separate fixed functional LUT bits from inferred tool-default programming."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'src'),str(Path(__file__).resolve().parents[1]/'adapters')]
from lut_equation import truth_table, MASK
from netlist import read_snapshot


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw',type=Path,required=True);p.add_argument('--snapshot',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    snapshot=read_snapshot(a.snapshot);equations={};carry_pins={};constant_inputs={}
    for line in (a.raw/'baseline_site_ownership.tsv').read_text().splitlines():
        x=line.split('\t')
        if x[0]=='bel_pin' and x[4] in ('GLOBAL_LOGIC0','GLOBAL_LOGIC1') and x[3] in ('A1','A2','A3','A4','A5','A6'):
            constant_inputs.setdefault(x[1]+'/'+x[2],{})[int(x[3][1])]=int(x[4][-1])
    for line in (a.raw/'bel_config.tsv').read_text().splitlines():
        x=line.split('\t')
        if x[0]=='config' and x[2]=='CONFIG.EQN':equations[x[1]]=x[3]
    for line in (a.raw/'cell_pin_ownership.tsv').read_text().splitlines():
        x=line.split('\t')
        if x[0]=='pin' and x[3]=='CARRY8':carry_pins[(x[2],x[4])]=x[6]
    fixed=[];unresolved=[];defaults=[];occupied=set()
    for name,c in snapshot['cells'].items():
        bel=c['bel'].split('.')[-1];physical=c['loc']+'/'+bel;occupied.add(physical)
        if not bel.endswith(('5LUT','6LUT')):continue
        output='O5' if bel.endswith('5LUT') else 'O6'
        equation=equations.get(physical)
        try:value=truth_table(equation or '',output=output)
        except ValueError:
            unresolved.append({'cell':name,'bel':physical,'equation':equation});continue
        field=c['loc']+'/'+bel[0]+'6LUT/INIT'
        mask=0xffffffff if output=='O5' else MASK
        bindings=constant_inputs.get(physical,{})
        for index,bit in bindings.items():
            if output=='O5' and index==6:continue
            reachable=sum(1 << assignment for assignment in range(64)
                          if ((assignment >> (index-1)) & 1)==bit)
            mask &= reachable
        fixed.append({'cell':name,'bel':physical,'equation':equation,'constant_input_bindings':bindings,
                      'configuration_bits':[field,mask,value & mask]})
    for physical,equation in equations.items():
        if physical in occupied or not physical.endswith('6LUT') or equation not in ('O6=0','O6=1'):continue
        site,bel=physical.split('/');pin='S'+str(ord(bel[0])-ord('A'))
        kind=carry_pins.get((site,pin))
        defaults.append({'bel':physical,'equation':equation,'carry_pin':pin,'logical_pin_kind':kind,
            'status':'isolated_vivado_conflict_verified' if physical=='SLICE_X22Y411/G6LUT' else 'inferred_not_yet_enforced',
            'configuration_bits':[physical+'/INIT',MASK,truth_table(equation)]})
    r={'status':'partial_fixed_state','fixed_functional_luts':fixed,'unresolved_functional_luts':unresolved,
       'unoccupied_constant_configurations':defaults,'limitations':['Functional LUT bit constraints require pin/configuration mapping validation before complete router integration.',
       'Unoccupied constant equations are distinguished from functional ownership; inferred defaults are not blanket fixed constraints.'],
       'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in (a.snapshot,a.raw/'bel_config.tsv',a.raw/'cell_pin_ownership.tsv',a.raw/'baseline_site_ownership.tsv',Path(__file__))}}
    with a.output.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps({'functional_luts':len(fixed),'unresolved':len(unresolved),'defaults':len(defaults),
        'default_logical_pin_kinds':dict(Counter(x['logical_pin_kind'] for x in defaults))}))


if __name__=='__main__':main()
