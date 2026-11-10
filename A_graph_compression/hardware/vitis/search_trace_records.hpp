#pragma once
#include "search_trace_v2.hpp"
#include "search_node_occupancy.hpp"
#include "search_retained_nodes.hpp"
#include "search_retained_edges.hpp"
#include "search_site_occupancy.hpp"
#include "search_route_tree.hpp"
namespace fpga_search {
// Exact net records extend the frozen search-frame writer without altering it.
template<unsigned Words=16777216,unsigned Nodes=1048576,unsigned Pairs=2097152,unsigned Owners=65536,unsigned Nets=65536>
struct SearchTraceRecords {
    using Base=SearchTraceV2<Words>;using Node=NodeOccupancy<Nodes,Pairs>;
    using Retained=RetainedNodes<Nodes,Pairs,Nets>;using Edges=RetainedEdges<Nodes,Pairs,Nets>;
    using Site=SiteOccupancy<Owners,Owners,Owners>;using Tree=RouteTree<Nodes>;
    static unsigned net(uint64_t iteration,unsigned query,uint32_t net_id,const uint32_t* roots,unsigned root_count,
        const uint64_t* result,const uint64_t* demands,const uint64_t* tree_meta,
        const uint64_t* node_meta,const uint32_t* counts,const uint64_t* history,const uint64_t* node_keys,const uint32_t* flags,
        const uint64_t* retained_meta,const uint64_t* retained_rows,const uint64_t* edge_meta,const uint32_t* edge_rows,
        const uint64_t* site_meta,const uint64_t* owners,uint64_t* m,uint64_t* out){
        unsigned status=Base::reserve(0,m);if(status)return status;
        if(!Node::valid_meta(node_meta) || !Retained::valid(retained_meta) || !Edges::valid(edge_meta) || !Site::valid(site_meta) || !Tree::valid(tree_meta) ||
           retained_meta[1]!=node_meta[1] || edge_meta[1]!=node_meta[1] || tree_meta[1]!=node_meta[1] || root_count>Nodes || result[0] || result[1]!=10)return Base::reject(m,1);
        for(unsigned i=0;i<root_count;++i)if(roots[i]>=node_meta[1] || (i && roots[i]<=roots[i-1]))return Base::reject(m,1);
        const unsigned rb=unsigned(retained_meta[3])*Pairs,rn=unsigned(retained_meta[2]);
        const unsigned rf=Retained::bound(retained_rows,rb,rn,net_id,false),rl=Retained::bound(retained_rows,rb,rn,net_id,true),retained_count=rl-rf;
        const unsigned eb=unsigned(edge_meta[3])*Pairs*9,en=unsigned(edge_meta[2]);
        const unsigned ef=Edges::bound(edge_rows,eb,en,net_id,false),el=Edges::bound(edge_rows,eb,en,net_id,true),edge_count=el-ef;
        unsigned owned_count=0,site_count=0;
        for(unsigned i=0;i<Pairs;++i)if(flags[i]==1 && uint32_t(node_keys[i]>>32)==net_id)++owned_count;
        const unsigned sb=unsigned(site_meta[1])*Owners*4;
        for(unsigned i=0;i<unsigned(site_meta[2]);++i)if(owners[sb+4*i+1]==net_id)++site_count;
        const uint64_t size=116+uint64_t((root_count+1)/2)+(retained_count+1)/2+owned_count+2*uint64_t(root_count)+4*uint64_t(edge_count)+4*uint64_t(site_count);
        status=Base::reserve(size,m);if(status)return status;
        unsigned at=unsigned(m[2]);const uint64_t h[16]={2,size,iteration,query,net_id,root_count,retained_count,owned_count,edge_count,site_count,0,0,0,0,0,0};
        for(unsigned i=0;i<16;++i)out[at++]=h[i];
        for(unsigned i=0;i<8;++i)out[at++]=result[i];
        for(unsigned i=0;i<65;++i)out[at++]=demands[i];
        for(unsigned i=0;i<5;++i)out[at++]=tree_meta[i];
        for(unsigned i=0;i<4;++i)out[at++]=node_meta[i];
        for(unsigned i=0;i<6;++i)out[at++]=retained_meta[i];
        for(unsigned i=0;i<6;++i)out[at++]=edge_meta[i];
        for(unsigned i=0;i<6;++i)out[at++]=site_meta[i];
        for(unsigned i=0;i<(root_count+1)/2;++i)out[at++]=uint64_t(roots[2*i])|(2*i+1<root_count?uint64_t(roots[2*i+1])<<32:0);
        for(unsigned i=0;i<(retained_count+1)/2;++i){uint64_t v=uint32_t(retained_rows[rb+rf+2*i]);if(2*i+1<retained_count)v|=uint64_t(uint32_t(retained_rows[rb+rf+2*i+1]))<<32;out[at++]=v;}
        for(unsigned i=0;i<Pairs;++i)if(flags[i]==1 && uint32_t(node_keys[i]>>32)==net_id)out[at++]=node_keys[i];
        for(unsigned i=0;i<root_count;++i){out[at++]=counts[roots[i]];out[at++]=history[roots[i]];}
        for(unsigned i=ef;i<el;++i)for(unsigned j=0;j<4;++j)out[at++]=uint64_t(edge_rows[eb+9*i+1+2*j])|(uint64_t(edge_rows[eb+9*i+2+2*j])<<32);
        for(unsigned i=0;i<unsigned(site_meta[2]);++i)if(owners[sb+4*i+1]==net_id)for(unsigned j=0;j<4;++j)out[at++]=owners[sb+4*i+j];
        Base::commit(unsigned(size),m);return 0;
    }
};
}
