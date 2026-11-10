// Self-checking RTL stimulus: every pointer remains allocated at its production
// interface depth for every call, including invalid and empty-list operations.
// Oracle uses canonical-node sets; it never calls the production hash helper.
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <set>
#include <vector>

extern "C" void search_node_occupancy_top(const uint64_t*,uint64_t*,uint32_t*,uint64_t*,uint64_t*,uint32_t*,
                                         const uint32_t*,const uint32_t*,uint64_t*,uint64_t*);
constexpr unsigned Nodes=1048576,Slots=2097152;
constexpr uint32_t Guard32=0xa5a5f00d;
constexpr uint64_t Guard64=0x1122334455667788ULL,Magic=0x414e4f44454f5731ULL;

struct Buffers {
    std::array<uint64_t,5> meta{{Guard64,Guard64,Guard64,Guard64,Guard64}};
    std::vector<uint32_t> counts=std::vector<uint32_t>(Nodes+1,Guard32);
    std::vector<uint64_t> history=std::vector<uint64_t>(Nodes+1,Guard64);
    std::vector<uint64_t> keys=std::vector<uint64_t>(Slots+1,Guard64);
    std::vector<uint32_t> flags=std::vector<uint32_t>(Slots+1,Guard32);
    std::vector<uint64_t> output=std::vector<uint64_t>(2*Nodes+1,Guard64);
    bool operator==(const Buffers& b)const {
        return meta==b.meta && counts==b.counts && history==b.history && keys==b.keys && flags==b.flags && output==b.output;
    }
};

struct Bench {
    Buffers actual;
    std::array<uint64_t,5> expected_meta=actual.meta;
    std::vector<uint32_t> expected_counts=actual.counts;
    std::vector<uint64_t> expected_history=actual.history,expected_output=actual.output;
    std::map<uint32_t,std::set<uint32_t>> owners;
    std::vector<uint32_t> old_nodes=std::vector<uint32_t>(Nodes+1,Guard32);
    std::vector<uint32_t> new_nodes=std::vector<uint32_t>(Nodes+1,Guard32);
    unsigned transaction=0;
    void verify()const {
        assert(actual.meta==expected_meta && actual.counts==expected_counts && actual.history==expected_history && actual.output==expected_output);
        std::map<uint32_t,std::set<uint32_t>> observed;uint64_t pairs=0;
        for(unsigned i=0;i<Slots;++i) {
            assert(actual.flags[i]<=2);
            if(actual.flags[i]==1) {
                uint32_t node=uint32_t(actual.keys[i]),net=uint32_t(actual.keys[i]>>32);
                assert(node<actual.meta[1] && observed[node].insert(net).second);++pairs;
            }
        }
        assert(observed==owners && pairs==actual.meta[2]);
        assert(actual.keys.back()==Guard64 && actual.flags.back()==Guard32 && old_nodes.back()==Guard32 && new_nodes.back()==Guard32);
    }
    void call(unsigned opcode,uint32_t net,const std::vector<uint32_t>& old_list,
              const std::vector<uint32_t>& next_list,unsigned status,unsigned reset_nodes=0,
              bool too_many=false,bool reserved=false) {
        std::array<uint64_t,9> config{{opcode,net,reset_nodes,old_list.size(),next_list.size(),0,0,0,Guard64}};
        std::array<uint64_t,5> result{{Guard64,Guard64,Guard64,Guard64,Guard64}};
        if(too_many)config[4]=Nodes+1;
        if(reserved)config[5]=1;
        for(unsigned i=0;i<old_list.size();++i)old_nodes[i]=old_list[i];
        for(unsigned i=0;i<next_list.size();++i)new_nodes[i]=next_list[i];
        // Reject paths must preserve ALL persistent words, including unused
        // slots and output tails, rather than only the active logical entries.
        std::vector<Buffers> before;if(status)before.push_back(actual);
        const auto input_config=config;
        search_node_occupancy_top(config.data(),actual.meta.data(),actual.counts.data(),actual.history.data(),
            actual.keys.data(),actual.flags.data(),old_nodes.data(),new_nodes.data(),actual.output.data(),result.data());
        assert(result[0]==status && config==input_config && result.back()==Guard64);
        uint64_t conflicts=0;
        if(status) {
            assert(actual==before[0] && result[1]==0 && result[2]==0 && result[3]==0);
        } else {
            if(opcode==0) {
                owners.clear();expected_meta={{Magic,reset_nodes,0,1,Guard64}};
                for(unsigned n=0;n<reset_nodes;++n){expected_counts[n]=0;expected_history[n]=0;}
            } else if(opcode==1) {
                for(auto n:old_list){assert(owners[n].erase(net)==1);if(owners[n].empty())owners.erase(n);}
                for(auto n:next_list)owners[n].insert(net);
                for(auto n:old_list){auto p=owners.find(n);expected_counts[n]=p==owners.end()?0:unsigned(p->second.size());}
                for(auto n:next_list)expected_counts[n]=unsigned(owners.at(n).size());
                expected_meta[2]=0;for(const auto& item:owners)expected_meta[2]+=item.second.size();++expected_meta[3];
            } else if(opcode==2) {
                for(const auto& item:owners)if(item.second.size()>1){expected_history[item.first]+=item.second.size()-1;++conflicts;}
                ++expected_meta[3];
            } else {
                for(unsigned n=0;n<expected_meta[1];++n) {
                    auto p=owners.find(n);expected_output[2*n]=p==owners.end()?0:p->second.size()-p->second.count(net);
                    expected_output[2*n+1]=expected_history[n];
                }
            }
            assert(result[1]==expected_meta[2] && result[2]==expected_meta[3] && result[3]==conflicts);
        }
        verify();
        std::cout<<"NODE_OCCUPANCY_RTL_CASE_PASS transaction="<<transaction++<<" status="<<status
                 <<" nodes="<<actual.meta[1]<<" pairs="<<actual.meta[2]<<" version="<<actual.meta[3]
                 <<" full_depth=1 all_state=1 guards=1\n";
    }
};

int main() {
    Bench t;
    t.call(0,0,{}, {},0,Nodes);                                      // 0: complete production domain reset
    t.call(1,UINT32_MAX,{}, {0,Nodes-1},0);                           // 1: highest node and net IDs
    t.call(1,0,{}, {Nodes-1},0);                                     // 2: shared highest node
    t.call(0,0,{}, {},0,64);                                        // 3: reset and reuse; inactive tails remain untouched
    const uint32_t A=820,B=3227;
    t.call(1,A,{}, {0,3,63},0);                                     // 4
    // These two literal keys independently hash to slot625610 in the 2^21
    // table. Check actual collision handling; no production hash call in TB.
    assert(t.actual.flags[625610]==1 && t.actual.keys[625610]==((uint64_t(A)<<32)|3));
    t.call(1,B,{}, {0,3,8},0);                                      // 5
    assert(t.actual.flags[625611]==1 && t.actual.keys[625611]==((uint64_t(B)<<32)|3));
    t.call(1,A,{}, {3},0);                                          // 6: idempotent acquisition
    t.call(3,A,{}, {},0);                                           // 7: self ownership excluded once
    // Seed reachable valid history values to exercise uint64 saturation.
    // The early conflict at node0 must not change when node3 overflows.
    t.actual.history[3]=UINT64_MAX;t.expected_history[3]=UINT64_MAX;
    t.call(2,0,{}, {},4);                                           // 8: atomic overflow rejection
    t.actual.history[3]=UINT64_MAX-1;t.expected_history[3]=UINT64_MAX-1;
    t.call(2,0,{}, {},0);                                           // 9: exact max accepted
    t.call(3,B,{}, {},0);                                           //10
    t.call(1,A,{0,3,63}, {8},0);                                    //11: tombstone before B's colliding key
    assert(t.actual.flags[625610]==2);
    t.call(1,A,{63}, {},3);                                         //12: missing owner
    t.call(1,A,{}, {8,8},1);                                        //13: duplicate IDs
    t.call(1,A,{}, {},2,0,true);                                    //14: declared count overflow; no out-of-bounds read
    t.call(1,A,{}, {},1,0,false,true);                              //15: reserved control bits
    t.call(3,A,{}, {},0);                                           //16: recover and read across tombstone
    t.call(2,0,{}, {},0);                                           //17: history for newly shared node8
    t.call(1,B,{0,3,8}, {},0);                                      //18
    t.call(1,0,{}, {0},0);                                          //19: real pair key0 is valid
    t.call(3,0,{}, {},0);                                           //20
    const uint64_t version=t.actual.meta[3];
    t.actual.meta[3]=UINT64_MAX;t.expected_meta[3]=UINT64_MAX;
    t.call(1,0,{0}, {3},4);                                         //21: version overflow is atomic
    t.actual.meta[3]=version;t.expected_meta[3]=version;
    t.call(1,0,{0}, {3},0);                                         //22: recovery after rejected update
    t.call(3,0,{}, {},0);                                           //23
    t.call(0,0,{}, {},0,64);                                        //24: reset removes stale ownership/history
    t.call(3,UINT32_MAX,{}, {},0);                                  //25
    t.call(0,0,{}, {},1,0);                                         //26: invalid empty domain
    t.call(0,0,{}, {},2,Nodes+1);                                   //27: domain capacity rejection
    assert(t.transaction==28);
    std::cout<<"NODE_OCCUPANCY_RTL_ALL_PASS transactions=28 production_nodes=1048576 production_slots=2097152 full_depth=1\n";
}
