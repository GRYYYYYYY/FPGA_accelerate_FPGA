"""Derive a complete router with bounded node AND site mutable ledgers."""
from derive_search_flat_controller import replace_once as one


def routes(text):
    text = one(text, '#include "node_occupancy_adapter.hpp"',
               '#include "node_occupancy_adapter.hpp"\n#include "site_occupancy_adapter.hpp"')
    text = one(text, 'SiteBatch result;DemandLedger ledger;', 'SiteBatch result;site_occupancy_host::Ledger ledger;')
    text = one(text, '    SiteHistory site_history;\n', '')
    text = one(text, 'snapshot.bind(q.net,present,owners,result.site_demands,site_history,forbidden);',
               'snapshot.bind(q.net,present,owners,ledger,forbidden);')
    old = '''        for (const auto& c:last.site_conflicts) {
            uint64_t delta=c.second.size()-1;auto& h=site_history[c.first];
            if (h>std::numeric_limits<uint64_t>::max()-delta) throw std::invalid_argument("site history overflow");
            h+=delta;
        }'''
    return one(text, old, '        ledger.advance(last.site_conflicts.size());')


def adapter(text):
    text = one(text, '#include "node_occupancy_adapter.hpp"',
               '#include "node_occupancy_adapter.hpp"\n#include "site_occupancy_adapter.hpp"')
    text = one(text, '''    // Called after releasing the old route. by_net may still contain this net's
    // old demands; explicitly exclude it. Other nets retain current demands.''',
               '    // Called after releasing this net; snapshot still explicitly excludes self.')
    text = one(text, '''const std::map<uint32_t,site_native::Normalized>& by_net,
              const site_native::SiteHistory& site_history,const std::set<uint32_t>& forbidden''',
               'const site_occupancy_host::Ledger& site_ledger,const std::set<uint32_t>& forbidden')
    start = text.index('        using Row=std::array<uint64_t,4>;std::vector<Row> rows;')
    end = text.index('        if(sites_.pseudo_attributes.size()', start)
    text = text[:start] + '''        site_ledger.snapshot(net,owners_,history_);
        const unsigned owner_count=unsigned(owners_.size()/4),history_count=unsigned(history_.size()/2);
        if(owner_count>Limits::config_owners || history_count>Limits::config_history)
            fail(true,"site ledger snapshot exceeds search capacity");
''' + text[end:]
    text = text.replace('unsigned(rows.size())', 'owner_count').replace('unsigned(site_history.size())', 'history_count')
    return text.replace('!rows.empty()', '(owner_count!=0)').replace('!site_history.empty()', '(history_count!=0)')
