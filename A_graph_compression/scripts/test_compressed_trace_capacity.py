#!/usr/bin/env python3
"""Exercise real diagnostic entry capacity cuts at every actual frame boundary."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    proof=ROOT/'results/search_trace_v3_cpu_20261025_v1.json';d=json.loads(proof.read_text())
    for p,h in d['files'].items():assert sha(p)==h,p
    out=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_trace_capacity');out.mkdir(exist_ok=False)
    src=out/'source';shutil.copytree(Path('/tmp/A_graph_compression_recovery_20261025_v1/trace_v2_cpu/source'),src)
    fixture=Path('/tmp/A_graph_compression_recovery_20261025_v1/trace_v2_cpu/trace_mode_0_case_0.bin');raw=fixture.read_bytes();w=list(struct.unpack('<%dQ'%(len(raw)//8),raw))
    used=0;at=8;cuts={1}
    while at<len(w):
        size=w[at+1];used+=size;at+=size;cuts.update([used-1,used])
    cuts=sorted(cuts-{used})
    text=(src/'test_search_batch_trace.cpp').read_text();a=text.index('    auto invoke=');end=text.index('    invoke();',a)
    call=text[a:text.index(';',a)+1]
    text=text[:a]+call+'};\n'+text[end:]
    text=text[:text.index('    // Explicit trusted component-state seed')]
    text+='''    const std::vector<uint64_t> baseline(trace_data.begin(),trace_data.begin()+trace_meta[2]);
    const uint64_t baseline_start_epoch=meta[0]-3;
    auto expected_prefix=[&](uint64_t before){
        auto expected=baseline;
        for(unsigned at=0;at<expected.size();at+=unsigned(expected[at+1]))if(expected[at]==6)expected[at+25]+=before-baseline_start_epoch;
        return expected;
    };
    const std::vector<uint64_t> node_history_before=node_history;
    const std::vector<uint32_t> node_counts_before=node_counts;
    uint64_t expected_result[12];std::copy(batch_result,batch_result+12,expected_result);
    uint64_t expected_node_meta[4];std::copy(node_meta,node_meta+4,expected_node_meta);
    uint64_t expected_retained_meta[6];std::copy(retained_meta,retained_meta+6,expected_retained_meta);
    uint64_t expected_edge_meta[6];std::copy(edge_meta,edge_meta+6,expected_edge_meta);
    uint64_t expected_site_meta[6];std::copy(site_meta,site_meta+6,expected_site_meta);
    auto save_trace=[&](const std::string& label){
        std::ofstream out("mode_"+std::to_string(SEARCH_GRAPH_MODE)+"_"+label+".bin",std::ios::binary);
        auto put=[&](uint64_t word){for(unsigned b=0;b<8;++b)out.put(char(word>>(8*b)));};
        for(auto word:trace_meta)put(word);
        for(unsigned i=0;i<trace_meta[2];++i)put(trace_data[i]);
        out.close();assert(out);
    };
    const unsigned cuts[]={CUTS};
    for(unsigned capacity:cuts){
        trace_control[0]=capacity;std::fill(trace_data.begin(),trace_data.end(),UINT64_C(0xdeadbeef));
        auto expected=expected_prefix(meta[0]);invoke();assert(trace_meta[4]==2 && trace_meta[2]<=capacity && trace_meta[5]==trace_meta[3]+1);
        assert(std::equal(trace_data.begin(),trace_data.begin()+trace_meta[2],expected.begin()));
        assert(std::all_of(trace_data.begin()+trace_meta[2],trace_data.end(),[](uint64_t v){return v==UINT64_C(0xdeadbeef);}));
        if(capacity<34){assert(batch_result[0]==9 && trace_meta[2]==0);}
        else{
            assert(std::equal(batch_result,batch_result+12,expected_result));
            assert(node_counts==node_counts_before && node_history==node_history_before);
            assert(std::equal(node_meta,node_meta+4,expected_node_meta));
            assert(std::equal(retained_meta,retained_meta+6,expected_retained_meta));
            assert(std::equal(edge_meta,edge_meta+6,expected_edge_meta));
            assert(std::equal(site_meta,site_meta+6,expected_site_meta));
        }
        save_trace("capacity_"+std::to_string(capacity));
    }
    trace_control[0]=baseline.size();std::fill(trace_data.begin(),trace_data.end(),UINT64_C(0xdeadbeef));auto expected=expected_prefix(meta[0]);invoke();
    assert(!trace_meta[4] && trace_meta[2]==baseline.size() && std::equal(trace_data.begin(),trace_data.begin()+trace_meta[2],expected.begin()) && trace_data[trace_meta[2]]==UINT64_C(0xdeadbeef));
    save_trace("exact_fit");
    const uint64_t node_version=node_meta[3];
    trace_control[0]=0;std::fill(trace_meta,trace_meta+8,UINT64_C(0x1234));invoke();
    assert(batch_result[0]==9 && node_meta[3]==node_version && std::all_of(trace_meta,trace_meta+8,[](uint64_t v){return v==UINT64_C(0x1234);}));
    trace_control[0]=16777217;invoke();assert(batch_result[0]==9 && node_meta[3]==node_version);
    trace_control[0]=262144;trace_control[7]=1;invoke();assert(batch_result[0]==9 && trace_meta[4]==1 && !trace_meta[2] && node_meta[3]==node_version);
    std::printf("BATCH_TRACE_CAPACITY_PASS mode=%u cuts=%zu exact_fit=1 invalid_controls=3\\n",SEARCH_GRAPH_MODE,sizeof(cuts)/sizeof(cuts[0]));
}
'''.replace('CUTS',','.join(map(str,cuts)))
    tb=src/'test_batch_trace_capacity.cpp';tb.write_text(text)
    state=dict(owner_pid=os.getpid(),status='running',completed=[])
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    save()
    env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'};env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    for mode in [0,1]:
        binary=out/f'mode_{mode}'
        jobs=[('compile',['g++','-std=c++14','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Wno-unknown-pragmas',f'-DSEARCH_GRAPH_MODE={mode}',str(tb),str(src/'search_batch_trace_top_v2.cpp'),'-o',str(binary)]),('run',['prlimit','--stack=67108864:67108864','--',str(binary)])]
        for phase,cmd in jobs:
            state.update(stage=f'{phase}_{mode}');save()
            with (out/f'{phase}_{mode}.log').open('x') as f:
                child=subprocess.Popen(cmd,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
            (out/f'{phase}_{mode}.receipt.json').write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=sha(out/f'{phase}_{mode}.log')),indent=2)+'\n')
            if code:state.update(status='failed');save();raise RuntimeError(state)
        state['completed'].append(mode);save()
    state.update(status='complete',stage='all_capacity_cuts_cpu_verified_reader_pending');save()
    paths=[p for p in src.iterdir() if p.is_file()]+[p for p in out.iterdir() if p.is_file()]+[Path(__file__).resolve(),proof,fixture]
    (out/'files.json').write_text(json.dumps({str(p):sha(p) for p in paths},indent=2)+'\n')
if __name__=='__main__':main()
