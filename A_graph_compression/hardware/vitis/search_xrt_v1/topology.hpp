#pragma once
// Bounded raw section reader. Physical bank indices and group IDs are distinct.
#include "exchange.hpp"
#include <xclbin.h>
#include <cstring>
#include <map>
#include <set>
#include <string>

namespace search_xrt {
struct Span {const char* data;size_t size;};
template<class T>T load(Span s,size_t at) {
    require(at<=s.size && sizeof(T)<=s.size-at,"truncated xclbin section");
    T value;std::memcpy(&value,s.data+at,sizeof(T));return value;
}
inline Span section(const std::vector<char>& raw,axlf_section_kind kind) {
    Span all{raw.data(),raw.size()};
    require(raw.size()>=offsetof(axlf,m_sections),"truncated xclbin header");
    require(std::memcmp(raw.data(),"xclbin2",7)==0,"invalid xclbin magic");
    const auto header=load<axlf_header>(all,offsetof(axlf,m_header));
    require(header.m_length==raw.size() && header.m_numSections<=
            (raw.size()-offsetof(axlf,m_sections))/sizeof(axlf_section_header),"invalid xclbin length/directory");
    Span found{};unsigned count=0;
    const size_t directory_end=offsetof(axlf,m_sections)+header.m_numSections*sizeof(axlf_section_header);
    for(unsigned i=0;i<header.m_numSections;++i) {
        auto entry=load<axlf_section_header>(all,offsetof(axlf,m_sections)+i*sizeof(axlf_section_header));
        require(entry.m_sectionOffset>=directory_end && entry.m_sectionOffset<=raw.size() &&
                entry.m_sectionSize<=raw.size()-entry.m_sectionOffset,"xclbin section out of file bounds");
        if(entry.m_sectionKind==unsigned(kind)){found={raw.data()+entry.m_sectionOffset,size_t(entry.m_sectionSize)};++count;}
    }
    require(count==1,"required xclbin section missing/duplicated");return found;
}
template<class T>std::vector<T> table(Span span,size_t offset) {
    auto count=load<int32_t>(span,0);
    require(count>=0 && offset<=span.size && uint64_t(count)<=(span.size-offset)/sizeof(T),"invalid xclbin table count");
    std::vector<T> out;out.reserve(size_t(count));
    for(int32_t i=0;i<count;++i)out.push_back(load<T>(span,offset+size_t(i)*sizeof(T)));
    return out;
}
inline std::string tag(const unsigned char* data,size_t size) {
    auto end=static_cast<const unsigned char*>(std::memchr(data,0,size));
    require(end!=nullptr,"unterminated xclbin name");return {reinterpret_cast<const char*>(data),size_t(end-data)};
}
inline std::set<std::string> expected_banks(const std::string& layout,unsigned id) {
    require(layout=="ddr_shared" || layout=="hbm_shared" || layout=="hbm_split","unknown memory layout");
    if(layout=="ddr_shared")return {"DDR[0]"};
    if(layout=="hbm_shared")return {"HBM[0]","HBM[1]","HBM[2]","HBM[3]"};
    if(id==9)return {"HBM[6]","HBM[7]"};
    unsigned pc=id==0?0:(id==1 || id==3 || id==4)?1:id==6?2:id==7?3:id==8?4:5;
    return {"HBM["+std::to_string(pc)+"]"};
}
struct Group {int id;uint64_t base,capacity,requested;std::set<std::string> banks;};
struct Topology {
    std::array<int,15> argument_groups{};
    std::map<int,Group> groups;
    Topology(const std::vector<char>& raw,const std::string& layout) {
        argument_groups.fill(-1);
        auto physical=table<mem_data>(section(raw,MEM_TOPOLOGY),offsetof(mem_topology,m_mem_data));
        auto grouped=table<mem_data>(section(raw,ASK_GROUP_TOPOLOGY),offsetof(mem_topology,m_mem_data));
        auto connections=table<connection>(section(raw,CONNECTIVITY),offsetof(connectivity,m_connection));
        auto group_connections=table<connection>(section(raw,ASK_GROUP_CONNECTIVITY),offsetof(connectivity,m_connection));
        auto ips=table<ip_data>(section(raw,IP_LAYOUT),offsetof(ip_layout,m_ip_data));
        int ip_index=-1;unsigned matches=0;
        for(size_t i=0;i<ips.size();++i)if(tag(ips[i].m_name,sizeof(ips[i].m_name))=="search_kernel_top:search_kernel_top_1") {
            require(ips[i].m_type==IP_KERNEL &&
                    ((ips[i].properties & IP_CONTROL_MASK)>>IP_CONTROL_SHIFT)==AP_CTRL_CHAIN,
                    "search IP is not an ap_ctrl_chain managed kernel");
            ip_index=int(i);++matches;
        }
        require(matches==1,"expected exactly one named search compute unit");
        for(const auto* list:{&connections,&group_connections})for(const auto& c:*list)
            if(c.m_ip_layout_index==ip_index)require(c.arg_index>=0 && c.arg_index<15 &&
                    arguments[unsigned(c.arg_index)].bytes,"connectivity references non-pointer argument");
        for(unsigned id=0;id<arguments.size();++id) {
            std::set<int> bank_indices,group_indices;
            unsigned physical_links=0,group_links=0;
            for(const auto& c:connections)if(c.m_ip_layout_index==ip_index && c.arg_index==int(id)){bank_indices.insert(c.mem_data_index);++physical_links;}
            for(const auto& c:group_connections)if(c.m_ip_layout_index==ip_index && c.arg_index==int(id)){group_indices.insert(c.mem_data_index);++group_links;}
            if(!arguments[id].bytes){require(bank_indices.empty() && group_indices.empty(),"scalar has memory connectivity");continue;}
            require(!bank_indices.empty() && physical_links==bank_indices.size() && group_links==1 && group_indices.size()==1,"missing/ambiguous memory connectivity");
            std::set<std::string> banks;std::vector<std::pair<uint64_t,uint64_t>> spans;
            const bool hbm=layout!="ddr_shared";
            for(int index:bank_indices) {
                require(index>=0 && size_t(index)<physical.size(),"physical bank index out of range");
                const auto& mem=physical[size_t(index)];
                require(mem.m_used && (hbm?mem.m_type==MEM_HBM:
                        (mem.m_type==MEM_DDR4 || mem.m_type==MEM_DDR3 || mem.m_type==MEM_DRAM)),"physical bank type/usage differs");
                require(mem.m_size==(hbm?256ull*1024:16ull*1024*1024),"physical bank capacity differs from selected U280 plan");
                const uint64_t bytes=mem.m_size*1024;
                require(mem.m_base_address<=UINT64_MAX-bytes,"physical bank span overflow");
                require(banks.insert(tag(mem.m_tag,sizeof(mem.m_tag))).second,"duplicate physical bank tag");
                spans.push_back({mem.m_base_address,mem.m_base_address+bytes});
            }
            require(banks==expected_banks(layout,id),"physical bank set differs from selected layout");
            std::sort(spans.begin(),spans.end());
            for(size_t i=1;i<spans.size();++i)require(spans[i-1].second==spans[i].first,"memory group is not contiguous");
            const int group=*group_indices.begin();
            require(group>=0 && size_t(group)<grouped.size(),"group index out of range");
            const auto& mem=grouped[size_t(group)];
            const uint64_t capacity=spans.back().second-spans.front().first;
            require(mem.m_used && (hbm?mem.m_type==MEM_HBM:
                    (mem.m_type==MEM_DDR4 || mem.m_type==MEM_DDR3 || mem.m_type==MEM_DRAM)) &&
                    mem.m_base_address==spans.front().first && mem.m_size==capacity/1024,"group topology does not match physical banks");
            auto it=groups.find(group);
            if(it==groups.end()) {
                for(const auto& old:groups)require(mem.m_base_address>=old.second.base+old.second.capacity ||
                        mem.m_base_address+capacity<=old.second.base,"overlapping independently identified groups");
                it=groups.emplace(group,Group{group,mem.m_base_address,capacity,0,banks}).first;
            }
            require(it->second.banks==banks,"group ID reused for different banks");
            it->second.requested+=allocation_size(id);argument_groups[id]=group;
        }
        for(const auto& g:groups)require(g.second.requested+16*1024*1024<=g.second.capacity,"aggregate BO requests plus reserve exceed group");
        for(unsigned a=0;a<15;++a)for(unsigned b=0;b<a;++b)if(arguments[a].bytes && arguments[b].bytes &&
                std::string(arguments[a].port)==arguments[b].port)
            require(argument_groups[a]==argument_groups[b],"shared AXI bundle has different group IDs");
    }
};
} // namespace search_xrt
