#!/usr/bin/env python3
"""Re-read actual native/DPI comparison receipts and complete payload oracles."""
import json
from pathlib import Path
import re
from check_vitis_kernel import digest,require
from run_axi_rebase_model_regression_v3 import transactions

ROOT=Path(__file__).resolve().parents[1]


def main():
    source=ROOT/'results/paired_axi_rebase_dpi_regression_20261029_v3.json';r=json.loads(source.read_text())
    target=ROOT/'results/paired_axi_rebase_dpi_independent_audit_20261029_v1.json';require(not target.exists(),'Refuse overwrite')
    require(r['status']=='both_modes_six_full_depth_models_native_vs_dpi_rebase_all4pages_verified' and r['graph_modes']==[0,1],'Missing paired behavioral result')
    expected={'completion_mem':(32,65536),'state_mem':(64,65),'site_scratch_mem':(64,163840),'node_meta_mem':(64,4),'tree_meta_mem':(64,5),'batch_input_mem':(64,16)}
    require(len(r['models'])==12 and {(m['graph_mode'],m['bundle']):(m['data_bits'],m['depth']) for m in r['models']}=={(g,b):d for g in [0,1] for b,d in expected.items()},'Partial paired matrix')
    files=dict(r['files']);files[str(source)]=digest(source);out=ROOT/'data/derived/paired_axi_rebase_dpi_regression_20261029_v3'
    checks=[(out/'dpi','xsc',None,None)];words=0
    for m in r['models']:
        mode=m['graph_mode'];bundle=m['bundle'];width,depth=expected[bundle];directory=out/('csr' if mode==0 else 'compact')/bundle/'sim/verilog'
        require(m['pages']==4 and m['native_reference'] and m['dpi_registration_verified'] and m['response_cycles_compared'],'Incomplete comparison')
        checks += [(directory,'xvlog',None,None),(directory,'xelab',None,None),(directory,'positive',0,None)]
        log=(directory/'positive.log').read_text()
        matches=re.findall(r'A_DPI_REGISTER id=(\d+) name=(\S+) bits=(\d+) depth=(\d+) pages=(\d+)',log)
        require(matches==[('0','model_tb.candidate_model.original_model.a_storage_write_blk',str(width),str(depth),'4')],'Wrong actual DPI registration')
        terminal=re.findall(r'MODEL_REBASE_PASS bundle=(\w+) width=(\d+) depth=(\d+) pages=4 requests=(\d+) samples=(\d+)',log)
        require(len(terminal)==1 and terminal[0][:3]==(bundle,str(width),str(depth)) and int(terminal[0][3])==(4 if bundle=='batch_input_mem' else 24) and int(terminal[0][4])>=100,'Incomplete terminal checks')
        if bundle=='batch_input_mem':
            require(m['readonly_full_page_words_read']==depth*4 and m['readonly_write_and_zero_strobe_rejected'],'Incomplete readonly matrix')
            checks += [(directory,'readonly_'+str(i),i,'A_RO_WRITE_VIOLATION') for i in [1,2]]
            require((directory/'model_tb.sv').read_text().count('read_words(0,DEPTH-1);')==1,'Readonly full-page read omitted')
        else:
            c=directory.parent/'tv/cdatafile'/('c.search_batch_trace_top_v2.autotvin_'+bundle+'.dat')
            expected_rows=transactions(c,width,depth)
            for tx,row in enumerate(expected_rows):
                row[0]=sum((0xa0+tx)<<(8*lane) for lane in range(width//8))
                mask=sum(255<<(8*lane) for lane in range(0,width//8,2))
                value=sum((0x50+tx)<<(8*lane) for lane in range(0,width//8,2))
                row[-1]=(row[-1]&~mask)|value
            for prefix in ['ref','rtl']:
                p=directory.parent/'tv/rtldatafile'/(prefix+'.search_batch_trace_top_v2.autotvout_'+bundle+'.dat')
                require(str(p) in files and transactions(p,width,depth)==expected_rows,'Complete native/DPI payload differs')
            require(m['all_output_words_verified']==depth*4,'Partial output record');words+=depth*4
    for directory,phase,case,error in checks:
        rp=directory/(phase+'.receipt.json');lp=directory/(phase+'.log');receipt=json.loads(rp.read_text());log=lp.read_text()
        require(str(rp) in files and str(lp) in files and receipt['log_sha256']==digest(lp) and receipt['expected_failure']==error and receipt['elapsed_seconds']>0,'Unbound/changed phase evidence')
        if case is not None:
            require(receipt['command'][-2:]==['-testplusarg','CASE='+str(case)] and re.findall(r'^SELECTED_CASE=(\d+)$',log,re.M)==[str(case)],'Wrong selected test case')
        if error:require(receipt['exit_code'] in [0,1] and error in log and 'Fatal:' in log and 'MODEL_REBASE_PASS' not in log and 'UNEXPECTED_ACCEPTANCE' not in log,'Missing negative rejection')
        else:require(receipt['exit_code']==0 and not any(e in log for e in ['ERROR:','Fatal:','FATAL','UNEXPECTED_ACCEPTANCE']),'Failed phase')
        if phase=='xsc':require('Turned off multi-threading.' in log and receipt['command'][-3:-1]==['--mt','off'],'Changed bounded single-thread compiler policy')
    for p,h in files.items():require(digest(p)==h,'Changed regression evidence '+p)
    files[str(Path(__file__).resolve())]=digest(__file__)
    report=dict(status='both_modes_native_dpi_rebase_regression_receipts_and_full_payloads_independently_rechecked',files=files,
                graph_modes=[0,1],models=12,pages=4,execution_phases=len(checks),output_words_per_implementation=words,
                readonly_negative_cases=4,full_kernel_verified=False,
                limits=['Representative actual full-depth models; full4tx/44-pointer encoded DUT acceptance remains required.'])
    with target.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],len(files),words)


if __name__=='__main__':main()
