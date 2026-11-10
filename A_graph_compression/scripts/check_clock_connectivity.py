#!/usr/bin/env python3
"""Check exact capture coverage, bidirectional net associations, and context restoration."""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_template_scope import digest
from real_experiment import write_new

SITES={'BUFCE_ROW_FSR_X21Y6':'BUFCE_ROW_FSR','BUFCE_LEAF_X110Y26':'BUFCE_LEAF'}
TARGET='original_cost/genblk1[3].h_val_y_reg[55]_i_2_n_0'

def require(x,message):
    if not x:raise ValueError(message)

def parse(path,stage):
    rows=[s.split('\t') for s in Path(path).read_text().splitlines()]
    require(rows and rows[-1]==['complete',stage],'Incomplete capture')
    counts=Counter(r[0] for r in rows)
    require(counts==Counter({'meta':4,'site':2,'net_count':59,'pin_node':13,'node_property':317,
        'context':6,'context_property':375,'inversion_getter':12,'complete':1,**({'net':8} if stage=='probe' else {})}),'Capture coverage differs')
    meta={r[1]:r[2] for r in rows if r[0]=='meta'}
    require(meta['schema']=='clock_connectivity_v1' and meta['stage']==stage and meta['part']=='xcu280-fsvh2892-2L-e','Wrong metadata')
    require({r[1]:r[2] for r in rows if r[0]=='site'}==SITES,'Wrong sites')
    declared={};nets=defaultdict(list);nodes={};properties={};context={};cp={};inverters={}
    for r in rows:
        if r[0]=='net_count':
            k=tuple(r[1:3]);require(k not in declared,'Duplicate net query');declared[k]=int(r[3])
        elif r[0]=='net':nets[tuple(r[1:3])].append(tuple(r[3:]))
        elif r[0]=='pin_node':require(r[1] not in nodes,'Duplicate site pin');nodes[r[1]]=r[2]
        elif r[0]=='node_property':
            k=tuple(r[1:3]);require(k not in properties,'Duplicate node property');properties[k]=r[3]
        elif r[0]=='context':
            k=tuple(r[1:3]);require(k not in context,'Duplicate context');context[k]=tuple(r[3:])
        elif r[0]=='context_property':
            k=tuple(r[1:5]);require(k not in cp,'Duplicate context property');cp[k]=r[5]
        elif r[0]=='inversion_getter':
            k=tuple(r[1:4]);require(k not in inverters,'Duplicate inversion query');inverters[k]=r[4]
    require(set(nets)<=set(declared),'Undeclared net association')
    require(Counter(k[0] for k in declared)=={'bel_pin':33,'site_pin':13,'node':13},'Missing physical object queries')
    for k,n in declared.items():require(n==len(nets[k]),'Net count mismatch')
    for site,typ in SITES.items():
        for c in ['default','manual','restored']:
            require(context[(site,c)]==(typ if c=='manual' else '', ''),'Unexpected context/SITE_PIPS value')
            for bel in ['CEINV','IINV']:require(inverters[(site,c,site+'/'+bel)]=='','Unexpected inversion evidence; review required')
        base={(b,p):v for (s,c,b,p),v in cp.items() if s==site and c=='default'}
        for c in ['manual','restored']:
            require({(b,p):v for (s,x,b,p),v in cp.items() if s==site and x==c}==base,'Context changed BEL properties')
    for pin,node in nodes.items():
        require(('site_pin',pin) in declared and ('node',node) in declared,'Pin/node query missing')
        require(nets[('site_pin',pin)]==nets[('node',node)],'Site pin and canonical node owners differ')
        require(properties[(node,'IS_GND')]=='0' and properties[(node,'IS_VCC')]=='0','New constant-node evidence requires review')
    expected={'BUFCE_ROW_FSR_X21Y6/CE_PRE_OPTINV','BUFCE_ROW_FSR_X21Y6/CLK_OUT','BUFCE_LEAF_X110Y26/CLK_IN','BUFCE_LEAF_X110Y26/CLK_LEAF'} if stage=='probe' else set()
    observed={pin for (kind,pin),owners in nets.items() if kind=='site_pin' and owners}
    require(observed==expected,'Signal pin set differs')
    require(all(owners==[(TARGET,'SIGNAL')] for owners in nets.values() if owners),'Unexpected net/type')
    require(all(n==0 for (kind,name),n in declared.items() if kind=='bel_pin'),'New internal connectivity requires review')
    return {'metadata':meta,'row_counts':dict(counts),'site_pin_nodes':nodes,'observed_signal_pins':sorted(observed),
            'empty_bel_pin_queries':33,'external_constant_node_flags':0,'manual_context_revealed_inversion_or_pips':False}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    folder=ROOT/'data/netlist/clock_connectivity_observation_20261023_v1'
    stages={s:parse(folder/(s+'.tsv'),s) for s in ['baseline','probe']}
    old=ROOT/'data/netlist/clock_semantics_capture_20261023_v3'
    for stage,d in stages.items():
        previous=[l.split('\t') for l in (old/(stage+'.tsv')).read_text().splitlines()]
        require({r[2]:r[3] for r in previous if r[:2]==['node_link','site_pin']}==d['site_pin_nodes'],'Mapping differs from prior capture')
    receipt=ROOT/'results/clock_connectivity_capture_receipt_20261023_v1.json'
    raw=json.loads(receipt.read_text());tool=json.loads(next(c['text'] for c in raw['content'] if c['type']=='text'))
    require(tool['exit_code']==0 and tool['error_count']==0 and 'CLOCK_CONNECTIVITY_CAPTURED_AND_BASELINE_RESTORED' in tool['output'],'Capture/restore failed')
    paths=[Path(__file__).resolve(),ROOT/'adapters/capture_clock_connectivity_20261023_v1.tcl',receipt]
    paths += [folder/(s+'.tsv') for s in stages]+[old/(s+'.tsv') for s in stages]
    paths += [Path(d['metadata']['checkpoint']) for d in stages.values()]
    report={'status':'connectivity_observation_verified_constants_and_inversion_unresolved','stages':stages,
        'capture_warning_count':tool['warning_count'],'files':{str(p):digest(p) for p in paths},
        'interpretation':['Four probe site pins and their canonical nodes expose the expected signal owner; all33 internal BEL-pin net queries return empty.',
            'All13 external nodes have IS_GND=IS_VCC=0; this does not determine internal tie values.',
            'MANUAL_ROUTING context is entered and restored; SITE_PIPS and inversion getters remain empty, with identical BEL properties in all contexts.',
            'No clock instance is added to the validated14-instance model.'],
        'remaining':'Need internal constant/inversion/delay/test and physical ownership evidence beyond these public Vivado queries.'}
    write_new(a.output,report);print(json.dumps({'status':report['status'],'output':str(a.output)}))

if __name__=='__main__':main()
