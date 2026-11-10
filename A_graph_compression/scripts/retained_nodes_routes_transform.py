"""Read old nodes from bounded retention, commit sorted tree roots in bulk."""
from derive_search_flat_controller import replace_once as one


def routes(text):
    text=one(text,'#include "search_kernel_route_adapter.hpp"','#include "search_kernel_route_adapter.hpp"\n#include "retained_nodes_adapter.hpp"')
    text=one(text,'    route_tree_host::Tree tree(unsigned(graph.node_count()));','    route_tree_host::Tree tree(unsigned(graph.node_count()));\n    retained_nodes_host::Store retained(unsigned(graph.node_count()));')
    text=one(text,'''            auto old=result.routes.find(q.net);
            if (old!=result.routes.end()) for (auto node:old->second.nodes) {
                if (owners[node].erase(q.net)!=1) throw std::invalid_argument("missing old occupancy");
            }''','''            const unsigned old_count=retained.get(q.net);
            if(old_count)owners.erase_nodes(q.net,retained.output(),old_count);''')
    return one(text,'            for (auto node:route.nodes) owners[node].insert(q.net);',
        '''            owners.insert_nodes(q.net,tree.roots(),nroots);
            retained.replace(q.net,tree.roots(),nroots);''')
