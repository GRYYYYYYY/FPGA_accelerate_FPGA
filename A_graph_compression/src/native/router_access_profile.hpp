#pragma once
// Diagnostic counters only. No changes to adjacency, caching or occupancy.
#include <cstdint>
#include <fstream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
struct RouterAccessProfile {
    struct Row { uint64_t visits=0,hits=0,misses=0,unknown=0; int64_t degree=-2; };
    std::vector<Row> rows;
    explicit RouterAccessProfile(size_t nodes):rows(nodes) {}
    static void check(bool value,const char* message) {
        if(!value)throw std::runtime_error(message);
    }
    void reset() {for(auto& row:rows)row=Row();}
    void observe(uint32_t node,bool known,size_t degree,uint64_t hits,uint64_t misses) {
        check(node<rows.size(),"access node out of range");
        check(known ? ((hits==1&&misses==0)||(hits==0&&misses==1)) : (hits==0&&misses==0),
              "access cache counters inconsistent");
        check(!known||degree<=uint64_t(std::numeric_limits<int64_t>::max()),"access degree overflow");
        auto& row=rows[node];int64_t value=known?int64_t(degree):-1;
        check(row.degree==-2||row.degree==value,"static adjacency changed during access profile");
        check(row.visits<std::numeric_limits<uint64_t>::max(),"access count overflow");
        row.degree=value;++row.visits;row.hits+=hits;row.misses+=misses;row.unknown+=!known;
    }
    void write(const std::string& prefix,unsigned batch) const {
        std::string path=prefix+".batch_"+std::to_string(batch)+".tsv";
        std::ifstream existing(path);check(!existing.good(),"refusing existing access profile");
        std::ofstream out(path);check(bool(out),"open access profile");
        out<<"ROUTER_ACCESS_V1\t"<<rows.size()<<'\t'<<batch<<'\n';
        for(size_t node=0;node<rows.size();++node) {
            const auto& row=rows[node];
            out<<node<<'\t'<<row.visits<<'\t'<<row.hits<<'\t'<<row.misses<<'\t'<<row.unknown<<'\t'<<row.degree<<'\n';
        }
        out.close();check(bool(out),"write access profile");
    }
};
