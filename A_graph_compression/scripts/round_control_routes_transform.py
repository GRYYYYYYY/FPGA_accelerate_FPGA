"""Use actual read-only round decision top; host maps become checks/observations."""
from derive_search_flat_controller import replace_once as one


def routes(text):
    text=one(text,'#include "retained_nodes_adapter.hpp"','#include "retained_nodes_adapter.hpp"\n#include "round_control_adapter.hpp"')
    text=one(text,'    for (unsigned iteration=0;iteration<max_iterations;++iteration) {','    round_control_host::Context control;uint64_t present=1;\n    for (unsigned iteration=0;iteration<max_iterations;++iteration) {')
    text=one(text,'        uint64_t present=std::min<uint64_t>(uint64_t(1)<<std::min(iteration,20u),present_cap);SiteRound round;','        SiteRound round;')
    text=one(text,'            result.routes.insert_or_assign(q.net,std::move(route));round.outcomes.push_back(std::move(connections));','            control.mark(round.outcomes.size(),route.complete);\n            result.routes.insert_or_assign(q.net,std::move(route));round.outcomes.push_back(std::move(connections));')
    start=text.index('        if (last.conflicts.empty() && last.site_conflicts.empty()) {')
    end=text.index('        ledger.advance(last.site_conflicts.size());',start)+len('        ledger.advance(last.site_conflicts.size());')
    return text[:start]+'''        const unsigned site_groups=ledger.analyze_groups();
        const auto decision=control.finish(unsigned(graph.node_count()),queries.size(),iteration,max_iterations,present_cap,site_groups,owners.buffers().counts);
        if(decision[1]!=last.conflicts.size() || decision[2]!=last.incomplete.size() || site_groups!=last.site_conflicts.size() || decision[7]!=present)
            throw std::logic_error("round control/native observation differs");
        if(decision[6]){owners.advance(decision[1]);ledger.advance(site_groups);}
        if(decision[3]==0)result.status="routed";
        if(decision[3]!=2)break;
        present=decision[5];'''+text[end:]
