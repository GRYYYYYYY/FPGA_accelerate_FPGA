#!/usr/bin/env python3
"""Audit complete public-property observations without inventing missing pin state."""
import argparse
from collections import Counter
import json
from pathlib import Path
from check_template_scope import digest
from real_experiment import write_new
ROOT=Path(__file__).resolve().parents[1]
COUNTS={'site':2,'bel':8,'bel_pin':33,'site_pin':13,'site_pip':4}


def parse(text, stage):
    metadata={};objects=set();properties={};completed=False
    for line in text.splitlines():
        r=line.split('\t');tag=r[0]
        if completed:raise ValueError('Records after completion')
        if tag=='meta':
            if len(r)!=3 or r[1] in metadata:raise ValueError('Invalid metadata')
            metadata[r[1]]=r[2]
        elif tag=='object':
            if len(r)!=3 or tuple(r[1:]) in objects:raise ValueError('Duplicate/invalid object')
            objects.add(tuple(r[1:]))
        elif tag=='property':
            if len(r)!=5 or tuple(r[1:3]) not in objects or tuple(r[1:4]) in properties:
                raise ValueError('Duplicate/outside-object property')
            properties[tuple(r[1:4])]=r[4]
        elif tag=='complete':
            if r!=['complete',stage,str(len(objects)),str(len(properties)),'0']:
                raise ValueError('Incomplete property collection')
            completed=True
        else:raise ValueError('Unsupported record or property read error')
    if not completed or metadata.get('stage')!=stage or metadata.get('part')!='xcu280-fsvh2892-2L-e':
        raise ValueError('Wrong stage/device or missing completion')
    if Counter(kind for kind,name in objects)!=COUNTS:raise ValueError('Incomplete physical object domain')
    for kind,name in objects:
        if properties.get((kind,name,'NAME'))!=name:raise ValueError('Object identity property differs')
    return metadata,objects,properties


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args();directory=ROOT/'data/netlist/clock_property_observation_20261023_v1'
    prior_dir=ROOT/'data/netlist/clock_semantics_capture_20261023_v3'
    prior_report=ROOT/'results/clock_semantics_capture_20261023_v1.json'
    proof=json.loads(prior_report.read_text())
    for path,value in proof['files'].items():
        if digest(path)!=value:raise ValueError('Original physical observation evidence changed')
    captures={};files=[Path(__file__),ROOT/'adapters/capture_clock_properties_20261023_v1.tcl',prior_report]
    for stage in ('baseline','probe'):
        path=directory/(stage+'.tsv');metadata,objects,properties=parse(path.read_text(),stage)
        expected={tuple(r[:2]) for line in (prior_dir/(stage+'.tsv')).read_text().splitlines()
                  if (r:=line.split('\t'))[0] in COUNTS}
        if objects!=expected:raise ValueError('Object domain differs from previously audited physical capture')
        checkpoint=ROOT/('data/netlist/site_full_applied_20261023_v1/routed.dcp' if stage=='baseline'
                         else 'data/netlist/clock_row_route_probe_full_20261023_v2/routed.dcp')
        if metadata['checkpoint']!=str(checkpoint) or metadata['get_site_wires_available']!='0':
            raise ValueError('Unexpected checkpoint or command surface')
        captures[stage]=properties;files.extend([path,prior_dir/(stage+'.tsv'),checkpoint])
    left,right=captures['baseline'],captures['probe']
    if set(left)!=set(right) or len(left)!=1132:raise ValueError('Property coverage differs')
    differences={k:(left[k],right[k]) for k in left if left[k]!=right[k]}
    expected={('bel','BUFCE_ROW_FSR_X21Y6/BUFCE','CONFIG.CE_TYPE'):('NOT CONFIGURED','ASYNC'),
        ('bel','BUFCE_LEAF_X110Y26/LCLK_TEST_DELAY','CONFIG.DELAY'):('NOT CONFIGURED','VAL0'),
        ('site_pip','BUFCE_ROW_FSR_X21Y6/CEINV:CE_PREINV','IS_USED'):('0','1'),
        ('site_pip','BUFCE_LEAF_X110Y26/IINV:I_PREINV','IS_USED'):('0','1')}
    if differences!=expected:raise ValueError('Unexpected physical property differences')
    inversion=[{'kind':k[0],'object':k[1],'value':v} for k,v in sorted(right.items()) if k[2]=='IS_INVERTED']
    if len(inversion)!=4 or any(r['value']!='' for r in inversion):raise ValueError('Inversion observability changed; investigate')
    restore=ROOT/'results/clock_property_restore_20261023_v1.json'
    receipt=json.loads(restore.read_text());payload=json.loads(receipt['content'][0]['text'])
    if payload['exit_code']!=0 or 'CAPTURE_STATUS 0 RESTORE_STATUS 0 CHECKPOINT '+str(ROOT/'data/netlist/site_full_applied_20261023_v1/routed.dcp') not in payload['output']:
        raise ValueError('No successful baseline restoration receipt')
    files.append(restore)
    write_new(a.output,{'status':'complete_public_property_surface_audited_physical_gap_retained',
        'objects_per_stage':COUNTS,'properties_per_stage':len(left),'property_read_errors':0,
        'differences':[{'kind':k[0],'object':k[1],'property':k[2],'baseline':v[0],'probe':v[1]} for k,v in sorted(differences.items())],
        'inversion_properties':inversion,'files':{str(p):digest(p) for p in files},
        'limitations':['All four exposed IS_INVERTED BEL properties are empty in both checkpoints; empty is not a demonstrated noninverted selection.',
            'Public pin properties expose optional inversion capability, not physical constant bindings. get_site_wires is unavailable in this session.',
            'Only four properties change, agreeing with previously audited observation; no new implicit clock-instance model authorization.',
            'Baseline design restored; no synthesis, routing, configuration edits or bitstream operations were performed.']})
    print('CLOCK_PROPERTY_SURFACE_AUDITED',len(left))


if __name__=='__main__':main()
