#include "../hardware/vitis/search_xrt_v1/topology.hpp"
#include <cassert>
#include <functional>
#include <iostream>
using namespace search_xrt;
template<class T>std::vector<char> packed(const std::vector<T>& rows,size_t offset) {
    std::vector<char> bytes(offset+rows.size()*sizeof(T));int32_t count=int32_t(rows.size());
    std::memcpy(bytes.data(),&count,sizeof(count));
    if(!rows.empty())std::memcpy(bytes.data()+offset,rows.data(),rows.size()*sizeof(T));
    return bytes;
}
struct Fixture {
    std::vector<mem_data> banks,groups;
    std::vector<connection> connections,group_connections;
    std::vector<ip_data> ips;
    explicit Fixture(const std::string& layout):banks(34),groups(64),ips(1) {
        for(unsigned i=0;i<34;++i) {
            auto& m=banks[i];m.m_used=1;m.m_type=i<32?MEM_HBM:MEM_DDR4;
            m.m_size=i<32?256ull*1024:16ull*1024*1024;
            m.m_base_address=i<32?i*256ull*1024*1024:0x800000000ull+(i-32)*16ull*1024*1024*1024;
            const std::string name=i<32?"HBM["+std::to_string(i)+"]":"DDR["+std::to_string(i-32)+"]";
            std::memcpy(m.m_tag,name.c_str(),name.size()+1);
        }
        ips[0].m_type=IP_KERNEL;ips[0].properties=AP_CTRL_CHAIN<<IP_CONTROL_SHIFT;
        std::strcpy(reinterpret_cast<char*>(ips[0].m_name),"search_kernel_top:search_kernel_top_1");
        std::map<std::set<std::string>,int> assigned;
        for(unsigned id=0;id<15;++id)if(arguments[id].bytes) {
            auto tags=expected_banks(layout,id);
            if(!assigned.count(tags))assigned[tags]=40+int(assigned.size());
            int group=assigned.at(tags);auto& combined=groups[size_t(group)];combined={};
            combined.m_base_address=UINT64_MAX;combined.m_used=1;combined.m_type=layout=="ddr_shared"?MEM_DDR4:MEM_HBM;
            for(unsigned i=0;i<banks.size();++i)if(tags.count(tag(banks[i].m_tag,16))) {
                connections.push_back({int(id),0,int(i)});combined.m_size+=banks[i].m_size;
                combined.m_base_address=std::min(combined.m_base_address,banks[i].m_base_address);
            }
            group_connections.push_back({int(id),0,group});
        }
    }
    std::vector<char> raw()const {
        std::vector<std::pair<unsigned,std::vector<char>>> sections={
            {MEM_TOPOLOGY,packed(banks,offsetof(mem_topology,m_mem_data))},
            {ASK_GROUP_TOPOLOGY,packed(groups,offsetof(mem_topology,m_mem_data))},
            {CONNECTIVITY,packed(connections,offsetof(connectivity,m_connection))},
            {ASK_GROUP_CONNECTIVITY,packed(group_connections,offsetof(connectivity,m_connection))},
            {IP_LAYOUT,packed(ips,offsetof(ip_layout,m_ip_data))}};
        const size_t directory=offsetof(axlf,m_sections)+sections.size()*sizeof(axlf_section_header);
        size_t total=directory;for(const auto& s:sections)total+=s.second.size();
        std::vector<char> data(total);std::memcpy(data.data(),"xclbin2",7);
        axlf_header header{};header.m_length=total;header.m_numSections=unsigned(sections.size());
        std::memcpy(data.data()+offsetof(axlf,m_header),&header,sizeof(header));
        size_t offset=directory;
        for(size_t i=0;i<sections.size();++i) {
            axlf_section_header s{};s.m_sectionKind=sections[i].first;s.m_sectionOffset=offset;s.m_sectionSize=sections[i].second.size();
            std::memcpy(data.data()+offsetof(axlf,m_sections)+i*sizeof(s),&s,sizeof(s));
            std::memcpy(data.data()+offset,sections[i].second.data(),sections[i].second.size());offset+=sections[i].second.size();
        }
        return data;
    }
};
int main(){
    for(const std::string layout:{"ddr_shared","hbm_shared","hbm_split"}) {
        Fixture fixture(layout);Topology actual(fixture.raw(),layout);
        uint64_t total=0;for(const auto& g:actual.groups)total+=g.second.requested;
        assert(total==523800576 && actual.argument_groups[2]==-1 && actual.argument_groups[5]==-1);
        for(unsigned i=0;i<15;++i)if(arguments[i].bytes)assert(actual.argument_groups[i]>=40);
        assert(actual.groups.size()==(layout=="hbm_split"?7:1));
    }
    std::vector<std::function<void(Fixture&)>> faults={
        [](auto& f){f.groups[40].m_size--;},
        [](auto& f){f.banks[0].m_base_address++;},
        [](auto& f){f.banks[0].m_used=0;},
        [](auto& f){f.banks[0].m_type=MEM_DDR4;},
        [](auto& f){std::strcpy(reinterpret_cast<char*>(f.banks[0].m_tag),"HBM[31]");},
        [](auto& f){f.group_connections.push_back(f.group_connections.front());},
        [](auto& f){f.connections.push_back({2,0,0});},
        [](auto& f){f.connections.push_back({15,0,0});},
        [](auto& f){f.connections[0].mem_data_index=1000;},
        [](auto& f){f.group_connections[0].mem_data_index=1000;},
        [](auto& f){f.groups[40].m_used=0;},
        [](auto& f){f.ips.push_back(f.ips.front());},
        [](auto& f){std::memset(f.ips[0].m_name,'a',sizeof(f.ips[0].m_name));},
        [](auto& f){f.ips[0].properties=0;},
        [](auto& f){f.group_connections.erase(f.group_connections.begin());},
        [](auto& f){f.groups[41]=f.groups[40];f.group_connections[1].mem_data_index=41;},
    };
    for(size_t i=0;i<faults.size();++i) {
        Fixture fixture("hbm_shared");faults[i](fixture);bool rejected=false;
        try{Topology bad(fixture.raw(),"hbm_shared");}catch(const std::runtime_error&){rejected=true;}
        if(!rejected)std::cerr<<"accepted fault "<<i<<'\n';
        assert(rejected);
    }
    Fixture fixture("hbm_shared");auto bytes=fixture.raw();
    for(size_t length:{size_t(0),size_t(7),offsetof(axlf,m_sections)-1,bytes.size()-1}) {
        bool rejected=false;try{Topology bad(std::vector<char>(bytes.begin(),bytes.begin()+length),"hbm_shared");}catch(const std::runtime_error&){rejected=true;}assert(rejected);
    }
    std::cout<<"SEARCH_TOPOLOGY_PASS layouts=3 corruptions="<<faults.size()<<" truncations=4 group_ids_distinct_from_physical=1 hardware_executed=false\n";
}
