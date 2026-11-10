#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
namespace board_graph {
constexpr size_t image_words=33554432, request_words=65536, output_words=1048576, result_words=196608;
constexpr uint32_t sentinel=0xdecafbad;
inline void require(bool condition,const char* message) {if(!condition)throw std::runtime_error(message);}
inline std::vector<uint32_t> words(const std::string& path,size_t maximum) {
    std::ifstream input(path,std::ios::binary|std::ios::ate);require(bool(input),"Cannot open input");
    auto length=input.tellg();require(length>=0&&uint64_t(length)%4==0&&uint64_t(length)/4<=maximum,"Input length outside contract");
    std::vector<uint32_t> data(size_t(length)/4);input.seekg(0);
    if(length)input.read(reinterpret_cast<char*>(data.data()),length);
    require(bool(input),"Truncated input");return data;
}
struct Section {uint64_t offset,size;uint32_t count,width;};
inline void descriptor(const std::vector<uint32_t>& image,const std::vector<uint32_t>& config,uint32_t mode) {
    uint32_t endian=1;require(*reinterpret_cast<uint8_t*>(&endian)==1,"Little-endian host required");
    require(image.size()>=6&&image.size()<=image_words&&config.size()==32,"Image/config length");
    auto bytes=reinterpret_cast<const uint8_t*>(image.data());
    require(std::memcmp(bytes,"AGRAPH01",8)==0&&image[2]==1&&image[3]==mode&&image[4]==0x01020304,"Image schema/mode mismatch");
    uint32_t sections=image[5];require(sections<=64&&24ull+40ull*sections<=image.size()*4,"Bad directory");
    std::map<std::string,Section> layout;std::vector<std::pair<uint64_t,uint64_t>> spans;
    for(uint32_t i=0;i<sections;++i){
        auto entry=bytes+24+40*i;size_t n=0;while(n<16&&entry[n])++n;
        require(n>0&&n<16,"Bad section name");Section s;
        std::memcpy(&s.offset,entry+16,8);std::memcpy(&s.size,entry+24,8);
        std::memcpy(&s.count,entry+32,4);std::memcpy(&s.width,entry+36,4);
        require(s.width&&s.size==uint64_t(s.count)*s.width&&s.offset%64==0&&s.offset>=24ull+40ull*sections&&s.offset<=image.size()*4&&s.size<=image.size()*4-s.offset,"Bad section bounds");
        require(layout.emplace(std::string(reinterpret_cast<const char*>(entry),n),s).second,"Duplicate section");
        if(s.size)spans.push_back({s.offset,s.offset+s.size});
    }
    std::sort(spans.begin(),spans.end());
    for(size_t i=1;i<spans.size();++i)require(spans[i-1].second<=spans[i].first,"Overlapping sections");
    const char* names[]={"NODE","TILE","GRID","ALIAS","INSTANCE","TPL_OFF","RULE","REMOVE","ADD","PATCH","CSR_OFF","CSR_EDGE"};
    const uint32_t widths[]={16,24,12,12,28,8,28,4,28,8,8,28};
    std::array<uint32_t,32> expected{};expected[0]=mode;
    for(unsigned i=0;i<12;++i){
        auto found=layout.find(names[i]);bool required=i<4||(mode?i>=4&&i<10:i>=10);
        require((found!=layout.end())==required,"Wrong representation section set");
        if(required){auto s=found->second;require(s.width==widths[i],"Wrong hardware section width");expected[1+2*i]=uint32_t(s.offset/4);expected[2+2*i]=s.count;}
    }
    require(layout.count("STR_OFF")&&layout.count("ATTR_OFF"),"Missing identity pools");
    require(layout.at("STR_OFF").count>0&&layout.at("ATTR_OFF").count>0,"Empty pool offsets");
    expected[25]=layout.at("STR_OFF").count-1;expected[26]=layout.at("ATTR_OFF").count-1;expected[27]=uint32_t(image.size());
    require(std::equal(expected.begin(),expected.end(),config.begin()),"Descriptor does not match exact image layout");
}
struct Case {
    uint32_t count,capacity,written,failed;
    std::vector<uint32_t> requests,results,output;
};
inline Case fixture(const std::string& path) {
    auto data=words(path,4+4*request_words+output_words);require(data.size()>=4,"Short fixture");
    Case c{data[0],data[1],data[2],data[3],{},{},{}};
    require(c.count>0&&c.count<=request_words&&c.capacity<=output_words&&c.written<=c.capacity/8&&c.failed<=c.count,"Fixture exceeds kernel bounds");
    require(data.size()==4ull+4ull*c.count+8ull*c.written,"Truncated or extra fixture data");
    auto it=data.begin()+4;c.requests.assign(it,it+c.count);it+=c.count;
    c.results.assign(it,it+3*c.count);it+=3*c.count;c.output.assign(it,data.end());
    uint32_t next=0,failed=0;
    for(uint32_t i=0;i<c.count;++i){
        auto start=c.results[3*i],degree=c.results[3*i+1],status=c.results[3*i+2];
        require(start==next&&degree<=1024&&status<=4,"Invalid per-request result contract");
        if(status){require(degree==0,"Failure contains partial adjacency");++failed;}
        else {require(degree<=c.written-next,"Expected records overflow");next+=degree;}
    }
    require(next==c.written&&failed==c.failed,"Fixture counters disagree");return c;
}
struct Workload {std::string image,config;std::vector<std::string> cases;};
inline Workload manifest(const std::string& path) {
    std::ifstream file(path);require(bool(file),"Missing manifest");Workload result;
    std::string line;
    while(std::getline(file,line)){
        std::istringstream row(line);std::string image,config,stimulus,extra;
        require(bool(row>>image>>config>>stimulus)&&!(row>>extra),"Malformed manifest row");
        if(result.cases.empty()){result.image=image;result.config=config;}
        require(image==result.image&&config==result.config,"Resident workload changes image/config");
        result.cases.push_back(stimulus);
    }
    require(!result.cases.empty(),"Empty manifest");return result;
}
inline void compare(const Case& c,const std::vector<uint32_t>& result,const std::vector<uint32_t>& output,const uint32_t* counts){
    require(result.size()==result_words&&output.size()==output_words,"Readback buffer length differs");
    require(counts[0]==c.written&&counts[1]==c.failed,"Device output counters differ");
    require(std::equal(c.results.begin(),c.results.end(),result.begin()),"Device request statuses/degrees differ");
    require(std::equal(c.output.begin(),c.output.end(),output.begin()),"Device edge identity/direction/attributes differ");
    require(std::all_of(result.begin()+c.results.size(),result.end(),[](uint32_t x){return x==sentinel;}),"Result guard changed");
    require(std::all_of(output.begin()+c.output.size(),output.end(),[](uint32_t x){return x==sentinel;}),"Output guard changed");
}
}
