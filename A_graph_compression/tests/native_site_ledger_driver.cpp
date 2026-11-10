#include "../src/native/site_ledger.hpp"
#include <iostream>
static site_native::Normalized normalized(std::vector<uint32_t> signals,
    std::vector<std::tuple<uint32_t,uint64_t,uint64_t>> bits,
    std::vector<std::pair<uint32_t,uint32_t>> values) {
    return site_native::normalize(site_native::Demands{true,false,signals,bits,values});
}
int main() {
    using namespace site_native;
    DemandLedger ledger;Normalized empty;
    SiteHistory history={{{0,1},3},{{1,0},5},{{2,0},7}};
    auto probe=normalized({1},{{0,3,1}},{{0,8}});
    auto before=normalized({1},{{0,1,1}},{});
    std::vector<std::tuple<bool,Id,Normalized>> actions={
        {false,1,normalized({1},{{0,1,0}},{{0,7}})},
        {false,2,normalized({1},{{0,1,0}},{{0,7}})},
        {false,2,normalized({2},{{0,1,1}},{{0,8}})},
        {false,3,normalized({},{{0,0,0}},{{0,7}})},
        {false,1,normalized({1},{{0,3,0}},{{0,7}})},
        {true,2,empty},{true,1,empty},{true,3,empty}};
    std::cout<<'[';bool first=true;
    for (const auto& action:actions) {
        if (std::get<0>(action)) ledger.release(std::get<1>(action));
        else ledger.replace(std::get<1>(action),std::get<2>(action));
        if (!first) {std::cout<<',';} first=false;
        std::cout<<"{\"conflicts\":[";bool cf=true;
        for (const auto& conflict:ledger.conflicts()) {
            if (!cf) {std::cout<<',';} cf=false;
            std::cout<<'['<<conflict.first.first<<','<<conflict.first.second<<",[";bool of=true;
            for (auto owner:conflict.second) {if (!of) {std::cout<<',';} of=false;std::cout<<owner;}
            std::cout<<"]]";
        }
        std::cout<<"],\"penalties\":["<<ledger.penalty(4,empty,probe,2,history)<<','
            <<ledger.penalty(4,before,probe,2,history)<<','<<ledger.penalty(4,probe,probe,2,history)<<','
            <<ledger.penalty(1,empty,probe,2,history)<<"]}";
    }
    std::cout<<"]\n";
}
