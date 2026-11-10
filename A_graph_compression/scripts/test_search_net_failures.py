#!/usr/bin/env python3
"""Exercise real partial-commit boundaries, without claiming cross-stage rollback."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def main():
    prior=ROOT/'data/derived/search_net_cpu_20261025_v1';plan=json.loads((prior/'plan.json').read_text())
    for p,h in {**plan['files'],**plan['generated']}.items():require(digest(p)==h,'Changed net CPU baseline')
    out=ROOT/'data/derived/search_net_failures_20261025_v1';out.mkdir(exist_ok=False);source=out/'source';shutil.copytree(prior/'source',source)
    tb=source/'test_search_net.cpp';text=tb.read_text();at=text.index('    std::printf("SEARCH_NET_PASS')
    checks='''    for(unsigned scenario=0;scenario<6;++scenario){
        assert(Node::reset(4,node_meta,node_counts.data(),node_history.data(),node_flags.data())==fpga_search::OccupancyStatus::ok);
        assert(Site::reset(site_meta)==fpga_search::SiteOccupancyStatus::ok);
        assert(fpga_search::RetainedNodes<>::reset(4,retained_meta)==fpga_search::RetainedStatus::ok);
        assert(fpga_search::RetainedEdges<>::reset(4,edge_meta)==fpga_search::RetainedEdgeStatus::ok);
        meta[0]=meta[1]=0;
        std::fill(static_image.begin(),static_image.end(),0);static_image[0]=UINT64_C(0x41534e4150535431);static_image[1]=89;static_image[2]=4;static_image[3]=2;static_image[5]=1;static_image[6]=1;static_image[17]=0x100;static_image[19]=3;
        assert(W::store(static_image.data()+20,0,requirement_key));std::copy(fixed,fixed+4,static_image.begin()+85);
        net_control[0]=7;net_control[1]=0;net_control[4]=89;net_control[5]=3;net_control[7]=0;sinks[0]=1;sinks[1]=sinks[2]=2;
        invoke();assert(!net_result[0] && node_meta[2]==3 && site_meta[2]==3 && edge_meta[2]==2);
        const uint64_t search_epoch=meta[0];
        if(scenario==0)site_meta[5]=UINT64_MAX;
        if(scenario==1)edge_meta[5]=UINT64_MAX;
        if(scenario==2)static_image[0]=0;
        if(scenario==3)meta[0]=UINT64_MAX;
        if(scenario==4)retained_meta[5]=UINT64_MAX;
        if(scenario==5)site_meta[5]=UINT64_MAX-1;
        invoke();const unsigned expected_stage[6]={3,4,5,6,8,9};
        assert(net_result[0]==2 && net_result[1]==expected_stage[scenario]);
        if(scenario<4){assert(node_meta[2]==0 && node_counts[0]==0 && node_counts[1]==0 && node_counts[2]==0);}
        else {assert(node_meta[2]==3 && node_counts[0]==1 && node_counts[1]==1 && node_counts[2]==1);}
        assert(site_meta[2]==(scenario==0?3:0));
        if(scenario<3)assert(meta[0]==search_epoch);
        if(scenario==3)assert(meta[0]==UINT64_MAX && result[0]==6);
        if(scenario==1)assert(tree_meta[3]==1 && edge_meta[2]==2 && edge_meta[5]==UINT64_MAX);
        if(scenario==2 || scenario==3)assert(tree_meta[3]==1 && edge_meta[2]==0);
        if(scenario==4 || scenario==5)assert(tree_meta[3]==3 && edge_meta[2]==2 && retained_meta[2]==3);
        if(scenario==4)assert(retained_meta[5]==UINT64_MAX);
        if(scenario==5)assert(site_meta[5]==UINT64_MAX && retained_meta[5]==3);
        std::printf("SEARCH_NET_FAILURE_PASS mode=%u scenario=%u stage=%llu\\n",SEARCH_GRAPH_MODE,scenario,(unsigned long long)net_result[1]);
    }
'''
    tb.write_text(text[:at]+checks+text[at:]);files={**plan['files'],**plan['generated'],str(Path(__file__).resolve()):digest(__file__)};generated={str(p):digest(p) for p in source.iterdir()}
    (out/'plan.json').write_text(json.dumps(dict(files=files,generated=generated),indent=2)+'\n');state=dict(owner_pid=os.getpid(),status='running',completed=[])
    def save():
        q=out/'state.tmp';q.write_text(json.dumps(state,indent=2)+'\n');q.replace(out/'state.json')
    save()
    try:
        for mode in [0,1]:
            binary=out/('mode_'+str(mode))
            commands=[('compile',['taskset','-c','123','g++','-std=c++14','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Wno-unknown-pragmas','-DSEARCH_GRAPH_MODE='+str(mode),str(tb),str(source/'search_net_top.cpp'),'-o',str(binary)]),('run',['prlimit','--stack=67108864:67108864','--','taskset','-c','123',str(binary)])]
            for phase,command in commands:
                name=phase+'_'+str(mode);state['stage']=name;save();env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'};env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
                with (out/(name+'.log')).open('x') as f:
                    child=subprocess.Popen(command,env=env,stdout=f,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
                (out/(name+'.receipt.json')).write_text(json.dumps(dict(command=command,exit_code=code,log_sha256=digest(out/(name+'.log'))),indent=2)+'\n');require(code==0,'Partial-commit test failed '+name)
            text=(out/('run_'+str(mode)+'.log')).read_text();require(text.count('SEARCH_NET_FAILURE_PASS')==6,'Missing rejected-stage coverage');state['completed'].append(mode);save()
        for p,h in {**files,**generated}.items():require(digest(p)==h,'Changed partial-commit input')
        state.update(status='complete',stage='six_failure_stages_both_modes_sanitizer_verified');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
