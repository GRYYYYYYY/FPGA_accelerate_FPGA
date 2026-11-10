"""Probe actual frozen SparseLabels object/allocation capacities (not process RSS)."""
import json,subprocess,hashlib
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=ROOT/'results'/('resident_metadata_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'));out.mkdir()
    records=[]
    for mode,bd in [('list',ROOT/'build/resident_zero_v1'),('index',ROOT/'build/resident_index_lru_v1')]:
        b=json.loads((bd/'build.json').read_text());original=(bd/'router.cpp').read_text()
        if sha(bd/'router.cpp')!=b['source_sha256']:raise ValueError('Frozen source changed')
        begin=original.index('    struct SparseLabels {');end=original.index('    struct LabelLease {',begin);core=original[begin:end]
        nb=original.index('    struct NodeDyn {');ne=original.index('    };',nb)+7;node=original[nb:ne]
        prefix='''#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <list>
#include <malloc.h>
#include <stdexcept>
#include <unordered_map>
#include <vector>
int rwEnvI(const char* key,int fallback){auto* value=std::getenv(key);return value?std::atoi(value):fallback;}
struct Router {
'''
        tail='''};
int main(int argc,char** argv){
    Router::SparseLabels labels;labels.initPaged(std::stoull(argv[1]),6);
    size_t payload=0,usablePayload=0,listRequested=0,listUsable=0;
    for(const auto& f:labels.frames){payload+=f.values.capacity()*sizeof(Router::NodeDyn);usablePayload+=malloc_usable_size((void*)f.values.data());}
'''
        if mode=='list':tail+='    for(auto i=labels.lru.begin();i!=labels.lru.end();++i){listRequested+=sizeof(std::_List_node<size_t>);listUsable+=malloc_usable_size(i._M_node);}\n'
        tail+='''    size_t table=labels.pageEp.capacity()*sizeof(uint32_t)+labels.pageSlot.capacity()*sizeof(int32_t);
    size_t frameBytes=labels.frames.capacity()*sizeof(Router::SparseLabels::Frame);
    std::cout<<"{\\"object_bytes\\":"<<sizeof(labels)<<",\\"frame_size\\":"<<sizeof(Router::SparseLabels::Frame)<<",\\"frame_capacity_bytes\\":"<<frameBytes<<",\\"resident_payload_bytes\\":"<<payload<<",\\"page_table_bytes\\":"<<table<<",\\"list_node_requested_bytes\\":"<<listRequested<<",\\"list_node_usable_bytes\\":"<<listUsable<<",\\"known_requested_total_bytes\\":"<<sizeof(labels)+frameBytes+payload+table+listRequested<<",\\"known_usable_total_bytes\\":"<<sizeof(labels)+malloc_usable_size(labels.frames.data())+usablePayload+malloc_usable_size(labels.pageEp.data())+malloc_usable_size(labels.pageSlot.data())+listUsable<<"}\\n";
}
'''
        source=out/(mode+'.cpp');source.write_text(prefix+node+core+tail);binary=out/mode
        cmd=['taskset','-c','24','g++','-std=c++17','-O2',str(source),'-o',str(binary)]
        subprocess.run(cmd,check=True,capture_output=True,timeout=60)
        for ds,nodes,capacity in [('logicnets_jscl',9089009,256),('vtr_mcml',14991410,4096)]:
            import os
            env=dict(os.environ,B_RESIDENT_PAGES=str(capacity));r=subprocess.run(['taskset','-c','24',str(binary),str(nodes)],env=env,check=True,capture_output=True,text=True,timeout=20)
            records.append(dict(mode=mode,dataset=ds,physical_pages=capacity,measurements=json.loads(r.stdout),source_sha256=sha(source),binary_sha256=sha(binary),frozen_source_sha256=b['source_sha256'],class_sha256=hashlib.sha256(core.encode()).hexdigest()))
    (out/'manifest.json').write_text(json.dumps(dict(status='passed',tool_sha256=sha(__file__),scope='Exact extracted frozen SparseLabels and NodeDyn; init-only actual ABI and malloc_usable_size. Global dyn, populated backing, allocator headers/arenas, RSS, and other router structures excluded. GNU list node introspection is local ABI specific.',records=records),indent=2)+'\n')
    print(out);print(json.dumps(records,indent=2))
if __name__=='__main__':main()
