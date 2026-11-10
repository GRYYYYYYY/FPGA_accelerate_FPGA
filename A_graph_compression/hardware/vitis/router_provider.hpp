#pragma once
// Host-side adjacency interface for the unchanged site-aware router.
// KernelCall may execute the audited C model or an explicitly supplied transport.
#include "host_contract.hpp"
#include "packed_graph.hpp"
#include <functional>
#include <memory>

namespace kernel_router {
using KernelCall=std::function<void(const uint32_t*,const uint32_t*,const uint32_t*,
    uint32_t*,uint32_t*,uint32_t*,uint32_t,uint32_t)>;
struct Row {bool known=false;std::vector<Edge> edges;};

class Provider {
    std::vector<uint32_t> image,config;
    KernelCall invoke;
    struct Entry {std::vector<Edge> edges;std::list<uint32_t>::iterator position;};
    std::unordered_map<uint32_t,Entry> cache;
    std::list<uint32_t> lru;
    size_t capacity;
    bool materialized=false;
    std::vector<uint64_t> offsets;
    std::vector<Edge> stored;
    static constexpr uint32_t guard=8,max_degree=1024,max_batch=128;
    std::vector<uint32_t> output,result;
    int32_t source_row(uint32_t n) const {
        board_graph::require(n<node_count(),"Invalid canonical node request");
        auto row=int32_t(image[config[1]+4*n+3]);
        board_graph::require(row>=-1,"Invalid source row metadata");return row;
    }
public:
    uint64_t hits=0,misses=0,kernel_calls=0,kernel_requests=0,kernel_records=0;
    uint64_t kernel_payload_bytes=0;
    Provider(const std::string& graph,const std::string& descriptor,size_t rows,KernelCall call):
        image(board_graph::words(graph,board_graph::image_words)),config(board_graph::words(descriptor,32)),
        invoke(std::move(call)),capacity(rows) {
        board_graph::require(bool(invoke),"Missing explicit kernel transport");
        board_graph::require(config.size()==32&&config[0]<=1,"Invalid kernel configuration");
        board_graph::descriptor(image,config,config[0]);
    }
    size_t node_count() const {return config[2];}
    std::vector<Row> decode_batch(const std::vector<uint32_t>& nodes) {
        using board_graph::require;
        require(!nodes.empty()&&nodes.size()<=max_batch,"Kernel router batch bounds");
        for (auto n:nodes) source_row(n);
        uint32_t words=uint32_t(nodes.size())*max_degree*8;
        output.assign(words+guard,board_graph::sentinel);
        result.assign(nodes.size()*3+guard,board_graph::sentinel);
        std::array<uint32_t,2+guard> counts;counts.fill(board_graph::sentinel);
        invoke(image.data(),config.data(),nodes.data(),output.data(),result.data(),counts.data(),
               uint32_t(nodes.size()),words);
        ++kernel_calls;kernel_requests+=nodes.size();
        require(counts[0]<=words/8&&counts[1]<=nodes.size(),"Kernel counter bounds");
        std::vector<Row> decoded(nodes.size());uint32_t cursor=0,failed=0;
        for (size_t i=0;i<nodes.size();++i) {
            uint32_t start=result[3*i],degree=result[3*i+1],status=result[3*i+2];
            require(start==cursor&&degree<=max_degree&&degree<=counts[0]-cursor,"Kernel row offsets/bounds");
            // Capacity, invalid mapping and invalid request are fatal, never no_path.
            require(status<=1,"Kernel decoder error: capacity/mapping/configuration");
            require((status==1)==(source_row(nodes[i])==-1),"Kernel known/unknown status differs");
            if (status) {require(degree==0,"Unknown row contains edges");++failed;}
            else {
                decoded[i].known=true;auto& edges=decoded[i].edges;edges.reserve(degree);
                for (uint32_t j=0;j<degree;++j) {
                    const uint32_t* p=output.data()+8*(cursor+j);
                    require(p[0]==nodes[i],"Kernel canonical source differs");
                    Edge e{p[1],p[2],p[3],p[4],p[5],p[6],p[7]};
                    require(e.dst<node_count()&&e.tile<config[4]&&e.pip<config[25]&&e.up<config[25]
                        &&e.down<config[25]&&e.attr<config[26]&&e.dir<=1,"Kernel edge identity bounds");
                    edges.push_back(e);
                }
                require(std::is_sorted(edges.begin(),edges.end()),"Kernel numeric edge order differs");
            }
            cursor+=degree;
        }
        require(cursor==counts[0]&&failed==counts[1],"Kernel counters disagree with rows");
        auto sentinel=[](uint32_t x){return x==board_graph::sentinel;};
        require(std::all_of(output.begin()+8*cursor,output.end(),sentinel),"Kernel output tail overwritten");
        require(std::all_of(result.begin()+3*nodes.size(),result.end(),sentinel),"Kernel result guard overwritten");
        require(std::all_of(counts.begin()+2,counts.end(),sentinel),"Kernel counter guard overwritten");
        kernel_records+=cursor;
        // ABI payload accounting only; excludes transport guards, graph upload and hardware memory accesses.
        kernel_payload_bytes+=4*(nodes.size()+3*nodes.size()+8*uint64_t(cursor)+2);
        return decoded;
    }
    bool neighbors(uint32_t node,std::vector<Edge>& out) {
        out.clear();if(source_row(node)==-1)return false;
        if(materialized) {
            ++misses;out.assign(stored.begin()+offsets[node],stored.begin()+offsets[node+1]);return true;
        }
        if(capacity) {
            auto it=cache.find(node);
            if(it!=cache.end()) {++hits;lru.splice(lru.begin(),lru,it->second.position);out=it->second.edges;return true;}
        }
        ++misses;auto rows=decode_batch({node});out=std::move(rows[0].edges);
        if(capacity) {
            if(cache.size()==capacity) {cache.erase(lru.back());lru.pop_back();}
            lru.push_front(node);cache.emplace(node,Entry{out,lru.begin()});
        }
        return true;
    }
    void materialize_all() {
        board_graph::require(!materialized,"Kernel graph already materialized");
        offsets.push_back(0);
        for(uint32_t begin=0;begin<node_count();begin+=max_batch) {
            std::vector<uint32_t> requests;
            for(uint32_t node=begin;node<node_count()&&node<begin+max_batch;++node)requests.push_back(node);
            auto rows=decode_batch(requests);
            for(const auto& row:rows) {stored.insert(stored.end(),row.edges.begin(),row.edges.end());offsets.push_back(stored.size());}
        }
        cache.clear();lru.clear();hits=misses=0;materialized=true;
    }
};
}
