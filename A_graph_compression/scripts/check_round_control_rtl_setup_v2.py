#!/usr/bin/env python3
"""Verify actual Csim/setup and every transaction's full AXI memory stimulus depth."""
import argparse
import hashlib
import json
import mmap
from pathlib import Path
import re
from check_vitis_kernel import digest,require
from round_control_rtl_contract import golden

# Derived from declared pointer depths, packed widths and bundle alignment.
BUS={'input_mem':(32776,64),'count_mem':(1048576,32),'output_mem':(1,512)}
POINTERS=['control','counts','complete','result']


def vector_file(path,depth,count,hex_digits):
    with path.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        # Actual generated wrapc Output::begin/from and AESL_axi_master read_binary
        # use BE uint64 depth, depth fixed-width words, and this 8-byte EOF mark.
        if data[:13]!=b'[[[runtime]]]':
            word_bytes=(hex_digits+1)//2;stride=8+depth*word_bytes
            require(len(data)==count*stride+8,'Truncated/extra binary vector data '+str(path))
            require(data[-8:]==bytes.fromhex('5a5aa5a50f0ff0f0'),'Wrong binary vector EOF')
            for index in range(count):
                at=index*stride
                require(int.from_bytes(data[at:at+8],'big')==depth,'Wrong binary vector depth at transaction '+str(index))
            return dict(sha256=hashlib.sha256(data).hexdigest(),transactions=count,words_per_transaction=depth,
                        packed_word_bits=4*hex_digits,bytes=len(data),format='binary_be_depth_records')
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
                    packed_word_bits=4*hex_digits,bytes=len(data),format='text_runtime_records')


def verify_single_owner_frame(path, depth=1048576):
    """Inspect every actual packed count in the first generated transaction."""
    with path.open('rb') as stream:
        require(int.from_bytes(stream.read(8),'big')==depth,'Wrong one-owner frame depth')
        words=stream.read(depth*4)
    require(len(words)==depth*4 and words==bytes.fromhex('00000001')*depth,
            'First transaction must give every node exactly one owner')
    return dict(transaction=0,nodes=depth,owners_per_node=1,expected_conflict_groups=0)


def audit(bundle,output):
    require(not output.exists(),'Refusing existing setup audit')
    plan_path=bundle/'plan.json';setup_path=bundle/'setup.json';execution_path=bundle/'execution_plan.json'
    plan=json.loads(plan_path.read_text());setup=json.loads(setup_path.read_text());execution=json.loads(execution_path.read_text())
    require(plan['transactions']==37 and plan['simulation_bound_ns']==10000000000 and plan['stack_bytes']==67108864,
            'Changed RTL execution scope')
    require(setup['status']=='full_depth_37_transaction_setup_verified_rtl_pending' and setup['production_synthesis']=='unchanged',
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
            require('ROUND_CONTROL_COSIM_SETUP_COMPLETE' in text and 'CSim done with 0 errors.' in before,'Csim/setup incomplete')
        for p in [log,rp,sp]:files[str(p)]=digest(p)
    solution=Path(plan['project'])/'solution';cdata=solution/'sim/tv/cdatafile';ref=cdata/'ref.tcl'
    depths={name:int(n) for name,n in re.findall(r'\{(\w+) (\d+)\}',ref.read_text())}
    require(depths=={**{name:1 for name in POINTERS},**{k:v[0] for k,v in BUS.items()}}
            and re.search(r'^set trans_num 37$',ref.read_text(),re.M),'Wrong packed memory depths')
    vectors={}
    for direction in ['in','out']:
        for name,(depth,bits) in BUS.items():
            if direction=='out' and name!='output_mem':continue # Read-only bundle.
            path=cdata/('c.search_round_control_top.autotv'+direction+'_'+name+'.dat')
            checked=vector_file(path,depth,37,bits//4)
            require(checked['sha256']==setup['files'][str(path)],'Changed stimulus during full-depth check')
            vectors[str(path)]=checked
    for p in [plan_path,setup_path,execution_path,Path(__file__).resolve(),
              solution/'sim/wrapc/apatb_search_round_control_top.cpp',solution/'sim/verilog/AESL_axi_master_input_mem.v']:files[str(p)]=digest(p)
    threshold=verify_single_owner_frame(cdata/'c.search_round_control_top.autotvin_count_mem.dat')
    result=dict(single_owner_threshold_stimulus=threshold,status='production_round_control_full_capacity_37_transaction_setup_independently_verified_rtl_pending',
        files=files,memory_vectors=vectors,production_synthesis='unchanged',transactions=37,
        capacities=dict(nodes=1048576,nets=65536),rtl_verified=False,
        limitations=['Actual CPU/Csim/stimulus-generation evidence only; no RTL completion claim.',
                     'All37 transactions have full packed AXI memory depths; golden outputs are C-model expectations, not RTL output.',
                     'Inputs are synthetic round observations, not full-ledger histories; final conflicting round still requests advancement.'])
    with output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(result['status'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();audit(a.bundle.resolve(),a.output.resolve())
