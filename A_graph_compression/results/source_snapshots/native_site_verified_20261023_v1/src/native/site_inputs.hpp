#pragma once
#include "site_search.hpp"
#include <charconv>
#include <fstream>

namespace site_native {
// Decimal tokens only: formatted unsigned extraction otherwise accepts '-1'.
class SiteTokens {
    std::ifstream input;
public:
    explicit SiteTokens(const std::string& path):input(path) {
        if (!input) throw std::invalid_argument("cannot open site fixture");
        std::string magic;input>>magic;
        if (magic!="NATIVE_SITES_V1") throw std::invalid_argument("invalid site schema");
    }
    uint64_t integer() {
        std::string token;input>>token;uint64_t value=0;
        if (!input || token.empty() || token.front()<'0' || token.front()>'9') throw std::invalid_argument("invalid site integer");
        auto result=std::from_chars(token.data(),token.data()+token.size(),value);
        if (result.ec!=std::errc{} || result.ptr!=token.data()+token.size()) throw std::invalid_argument("invalid site integer");
        return value;
    }
    Id id() {auto n=integer();if (n>UINT32_MAX) throw std::invalid_argument("site ID overflow");return Id(n);}
    Id bounded(Id limit) {auto n=id();if (n>=limit) throw std::invalid_argument("site ID outside domain");return n;}
    void end() {std::string trailing;if (input>>trailing) throw std::invalid_argument("trailing site data");}
};
struct SiteInputs {
    Id resources,values,attributes;
    Demands fixed{true,false,{},{},{}};
    std::vector<std::pair<Id,Id>> fixed_signals;
    std::map<std::pair<Id,Id>,Demands> requirements;
    std::set<Id> pseudo_attributes;
    explicit SiteInputs(const std::string& path) {
        SiteTokens in(path);resources=in.id();values=in.id();attributes=in.id();
        if (!resources || !attributes) throw std::invalid_argument("empty site domain");
        auto bits=[&](Demands& d) {
            auto count=in.id();
            for (Id i=0;i<count;++i) {auto field=in.bounded(resources);auto mask=in.integer();auto value=in.integer();d.bits.emplace_back(field,mask,value);}
        };
        auto categorical=[&](Demands& d) {
            auto count=in.id();std::set<Id> seen;
            for (Id i=0;i<count;++i) {auto field=in.bounded(resources);auto value=in.bounded(values);
                if (!seen.insert(field).second) throw std::invalid_argument("duplicate categorical resource");
                d.values.emplace_back(field,value);}
        };
        bits(fixed);auto count=in.id();std::set<Id> fixed_seen;
        for (Id i=0;i<count;++i) {auto field=in.bounded(resources);auto owner=in.id();
            if (!fixed_seen.insert(field).second) throw std::invalid_argument("duplicate fixed signal");
            fixed_signals.emplace_back(field,owner);}
        categorical(fixed);normalize(fixed);count=in.id();
        for (Id i=0;i<count;++i) {
            auto tile=in.id();auto pip=in.id();Demands d;d.verified=true;
            auto signals=in.id();std::set<Id> seen;
            for (Id j=0;j<signals;++j) {auto field=in.bounded(resources);
                if (!seen.insert(field).second) throw std::invalid_argument("duplicate signal resource");
                d.signals.push_back(field);}
            bits(d);categorical(d);normalize(d);
            if (!requirements.emplace(std::make_pair(tile,pip),std::move(d)).second) throw std::invalid_argument("duplicate site PIP");
        }
        count=in.id();
        for (Id i=0;i<count;++i) if (!pseudo_attributes.insert(in.bounded(attributes)).second) throw std::invalid_argument("duplicate pseudo attribute");
        in.end();
    }
    EdgeSemantics semantics(const Edge& e) const {
        if (e.attr>=attributes) throw std::invalid_argument("edge attribute outside site domain");
        EdgeSemantics result;result.pseudo=pseudo_attributes.count(e.attr);
        auto found=requirements.find({e.tile,e.pip});
        if (found!=requirements.end()) {
            if (!result.pseudo || e.dir!=0) throw std::invalid_argument("tested site PIP kind/direction differs");
            result.demands=found->second;
        }
        return result;
    }
};
} // namespace site_native
