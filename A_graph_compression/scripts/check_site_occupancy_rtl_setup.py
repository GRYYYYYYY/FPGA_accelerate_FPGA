#!/usr/bin/env python3
"""Verify actual Csim/setup and every transaction's full AXI memory stimulus depth."""
import argparse
import hashlib
import json
import mmap
from pathlib import Path
import re
from check_vitis_kernel import digest,require
from site_occupancy_rtl_contract import golden

# Derived from declared pointer depths, packed widths and bundle alignment.
BUS={ 'input_mem':(196616,64), 'meta_mem':(1,512), 'owner_mem':(131072,256),
      'history_mem':(131072,128), 'scratch_mem':(81920,128), 'output_mem':(49153,512) }
POINTERS=['config_r','meta','owners','history','request','flags','summaries','out_owners','out_history','result']


def vector_file(path,depth,count,hex_digits):
    with path.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        header=b'[[[runtime]]]\n';footer=b'[[[/runtime]]]\n';end=b'[[/transaction]]\n'
        require(data[:len(header)]==header,'Wrong vector header '+str(path));position=len(header)
        marker=re.compile(rb'\[\[transaction\]\][ \t]+(\d+)\n')
        bad_width=re.compile(rb'0x[0-9a-fA-FxX]{'+str(hex_digits+1).encode()+rb'}')
        for index in range(count):
            match=marker.match(data,position)
            require(match is not None and int(match[1])==index,'Missing/reordered vector transaction '+str(path))
            stop=data.find(end,match.end());require(stop>=0,'Unterminated vector transaction')
            body=data[match.end():stop]
            require(body.startswith(b'0x') and body.endswith(b'\n') and body.count(b'\n')==depth
                    and body.count(b'\n0x')==depth-1,'Wrong full vector depth '+str(path)+' transaction '+str(index))
            require(not re.search(rb'[^0-9a-fA-FxX\n]',body) and b'0x\n' not in body and not bad_width.search(body),
                    'Malformed/wide vector word '+str(path))
            position=stop+len(end)
        require(data[position:]==footer,'Unexpected additional vector data '+str(path))
        return dict(sha256=hashlib.sha256(data).hexdigest(),transactions=count,words_per_transaction=depth,
                    packed_word_bits=4*hex_digits,bytes=len(data))


def audit(bundle,output):
    require(not output.exists(),'Refusing existing setup audit')
    plan_path=bundle/'plan.json';setup_path=bundle/'setup.json';execution_path=bundle/'execution_plan.json'
    plan=json.loads(plan_path.read_text());setup=json.loads(setup_path.read_text());execution=json.loads(execution_path.read_text())
    require(plan['transactions']==52 and plan['simulation_bound_ns']==10000000000 and plan['stack_bytes']==67108864,
            'Changed RTL execution scope')
    require(setup['status']=='full_depth_52_transaction_setup_verified_rtl_pending' and setup['production_synthesis']=='unchanged',
            'Incomplete RTL setup')
    require(execution['plan_sha256']==digest(plan_path) and execution['setup_sha256']==digest(setup_path),'Changed setup plan')
    files={**plan['files'],**plan['synthesis'],**setup['files'],**execution['files']}
    for p,h in files.items():require(digest(p)==h,'Changed prepared RTL input '+p)
    for phase in ['compile_cpu','cpu','prepare']:
        log=bundle/(phase+'.log');rp=bundle/(phase+'.receipt.json');sp=bundle/(phase+'.submission.json')
        receipt=json.loads(rp.read_text());submission=json.loads(sp.read_text());text=log.read_text()
        require(receipt['exit_code']==0 and receipt['log_sha256']==digest(log)
                and receipt['command']==submission['command']==plan['commands'][phase]['command']
                and submission['cwd']==plan['commands'][phase]['cwd'] and submission['plan_sha256']==digest(plan_path),
                'Failed/different setup phase '+phase)
        require(not any(s in text for s in ['ERROR:','FATAL_ERROR','runtime error:']),'Setup error')
        if phase=='cpu':golden(text)
        if phase=='prepare':
            before,after=text.split('Running: cosim_design',1);golden(before);golden(after)
            require('SITE_OCCUPANCY_COSIM_SETUP_COMPLETE' in text and 'CSim done with 0 errors.' in before,'Csim/setup incomplete')
        for p in [log,rp,sp]:files[str(p)]=digest(p)
    solution=Path(plan['project'])/'solution';cdata=solution/'sim/tv/cdatafile';ref=cdata/'ref.tcl'
    depths={name:int(n) for name,n in re.findall(r'\{(\w+) (\d+)\}',ref.read_text())}
    require(depths=={**{name:1 for name in POINTERS},**{k:v[0] for k,v in BUS.items()}}
            and re.search(r'^set trans_num 52$',ref.read_text(),re.M),'Wrong packed memory depths')
    vectors={}
    for direction in ['in','out']:
        for name,(depth,bits) in BUS.items():
            if direction=='out' and name=='input_mem':continue # Read-only bundle.
            path=cdata/('c.search_site_occupancy_top.autotv'+direction+'_'+name+'.dat')
            checked=vector_file(path,depth,52,bits//4)
            require(checked['sha256']==setup['files'][str(path)],'Changed stimulus during full-depth check')
            vectors[str(path)]=checked
    for p in [plan_path,setup_path,execution_path,Path(__file__).resolve()]:files[str(p)]=digest(p)
    result=dict(status='production_site_occupancy_full_capacity_52_transaction_setup_independently_verified_rtl_pending',
        files=files,memory_vectors=vectors,production_synthesis='unchanged',transactions=52,
        capacities=dict(owners=65536,history=65536,requests=65536),rtl_verified=False,
        limitations=['Actual CPU/Csim/stimulus-generation evidence only; no RTL completion claim.',
                     'All52 transactions have full packed AXI memory depths; golden outputs are C-model expectations, not RTL output.',
                     'Saturated history/version are explicitly seeded; full owner/request/history capacities are reached through actual operations.'])
    with output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(result['status'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();audit(a.bundle.resolve(),a.output.resolve())
