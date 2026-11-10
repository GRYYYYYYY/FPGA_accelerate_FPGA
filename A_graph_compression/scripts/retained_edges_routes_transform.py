"""Raw search paths drive edge storage; decoded paths remain observations."""
from derive_search_flat_controller import replace_once as one

def routes(text):
    text=one(text,'#include "retained_nodes_adapter.hpp"','#include "retained_nodes_adapter.hpp"\n#include "retained_edges_adapter.hpp"')
    text=one(text,'    retained_nodes_host::Store retained(unsigned(graph.node_count()));','    retained_nodes_host::Store retained(unsigned(graph.node_count()));\n    retained_edges_host::Store retained_edges(unsigned(graph.node_count()));')
    text=one(text,'            ledger.release(q.net);tree.reset(q.source);','            ledger.release(q.net);tree.reset(q.source);retained_edges.clear(q.net);')
    text=one(text,'snapshot.search(tree,target,budget)','snapshot.search(tree,target,budget,retained_edges,q.net)')
    text=one(text,'''                if (connection.status=="found") {
                    route.edges.insert(route.edges.end(),connection.path.begin(),connection.path.end());
                }
''','')
    return one(text,'            route.complete=tree.complete(q.sinks);','''            const unsigned edge_count=retained_edges.get(q.net);
            for(unsigned i=0;i<edge_count;++i){const uint32_t* p=retained_edges.output()+8*i;
                route.edges.emplace_back(p[0],Edge{p[1],p[2],p[3],p[4],p[5],p[6],p[7]});}
            route.complete=tree.complete(q.sinks);''')

def search(text):
    text=one(text,'#pragma once','#pragma once\n#include "retained_edges_adapter.hpp"')
    text=one(text,'search(route_tree_host::Tree& tree,uint32_t target,uint64_t budget)',
             'search(route_tree_host::Tree& tree,uint32_t target,uint64_t budget,retained_edges_host::Store& retained_edges,uint32_t net)')
    return one(text,'        tree.accept(target,result,w.path);','        tree.accept(target,result,w.path);\n        if(result[0]==0)retained_edges.append(net,w.path,unsigned(result[7]));')
