#!/usr/bin/env python3
"""Build explicit, confidence-labelled site requirements without dropping PIPs."""
import argparse
from collections import defaultdict, Counter
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from lut_equation import truth_table, MASK


def build(raw):
    sites=defaultdict(list)
    for line in (raw/'pseudo_sites.tsv').read_text().splitlines():
        x=line.split('\t')
        if x[0]=='site':sites[x[1]].append((x[2],x[3]))
    clock=json.loads((raw/'clock_leaf_mapping.json').read_text())['clock_pseudo_pips']
    records={}
    for line in (raw/'pseudo_pips.tsv').read_text().splitlines():
        x=line.split('\t')
        if x[0]!='pip':continue
        _,pip,src,dst,tile=x
        record={'status':'unverified','signal_resources':[],'configuration_bits':[],
                'configuration_values':[]}
        a=re.fullmatch(r'CLE_CLE_[LM]_SITE_0_([A-H])([1-6])',src.split('/')[-1])
        b=re.fullmatch(r'CLE_CLE_[LM]_SITE_0_([A-H])(?:MUX|_O)',dst.split('/')[-1])
        candidates=[s for s,t in sites[tile] if t in ('SLICEL','SLICEM')]
        if a and b and a[1]==b[1] and len(candidates)==1:
            site=candidates[0];bel=site+'/'+a[1]+'6LUT'
            equation='O6=A'+a[2]
            record.update(kind='lut_o6_route_through',site=site,
                          status='inferred_requires_adapter_validation',equation=equation,
                          signal_resources=[bel+'/O6'],
                          configuration_bits=[[bel+'/INIT',MASK,truth_table(equation)]])
        elif pip in clock:
            mapping=clock[pip];site=mapping['site']
            record.update(kind='clock_leaf',site=site,endpoint_mapping=mapping)
            if mapping['source']['pin'].endswith('/CE_INT') and mapping['destination']['pin'].endswith('/CLK_LEAF'):
                record.update(status='family_rule_three_sites_probed_ownership_pending',
                    instance_configuration_probed=site in {'BUFCE_LEAF_X115Y26','BUFCE_LEAF_X118Y26','BUFCE_LEAF_X114Y26'},
                    signal_resources=[site+'/CLK_LEAF'],
                    configuration_values=[[site+'/BUFCE/CE_TYPE','ASYNC'],
                                          [site+'/LCLK_TEST_DELAY/DELAY','VAL0']],
                    additional_requirements=['Verify clock-input constant source and inversion programming.'])
        if pip in records:raise ValueError('Duplicate pseudo PIP')
        records[pip]=record
    return {'status':'requirements_partial_not_legality_certificate','pips':records,
            'counts':dict(Counter(r['status'] for r in records.values())),
            'limitations':['No graph edges removed; unverified requirements remain explicit.',
                           'Fixed internal ownership, LUT5 sharing, mux configuration and clock constant/inversion requirements are not complete.',
                           'Do not use inferred records as a complete physical legality oracle.']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raw',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=build(a.raw)
    names=['pseudo_sites.tsv','pseudo_pips.tsv','clock_leaf_mapping.json']
    r['input_sha256']={n:hashlib.sha256((a.raw/n).read_bytes()).hexdigest() for n in names}
    r['code_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with a.output.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps({'pips':len(r['pips']),'counts':r['counts']}))


if __name__=='__main__':main()
