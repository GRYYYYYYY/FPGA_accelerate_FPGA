#include "../hardware/vitis/search_label_records.hpp"
#include <cassert>
#include <iostream>
#include <random>
#include <vector>
using fpga_search::LabelEdge;
using fpga_search::LabelRecord;
using Status=fpga_search::RecordStatus;
bool equal(const LabelRecord& a,const LabelRecord& b) {
    return a.cost==b.cost && a.parent==b.parent && a.root==b.root && a.edge.dst==b.edge.dst && a.edge.tile==b.edge.tile &&
        a.edge.pip==b.edge.pip && a.edge.up==b.edge.up && a.edge.down==b.edge.down && a.edge.attr==b.edge.attr && a.edge.dir==b.edge.dir;
}
template<unsigned Capacity> void random_cases() {
    using Store=fpga_search::LabelRecords<Capacity>;
    std::mt19937_64 rng(Capacity+20261024);const uint64_t guard=0xdeadbeef12345678ULL;
    std::vector<uint64_t> storage(10*Capacity+2,guard);auto words=storage.data()+1;
    std::vector<LabelRecord> oracle;unsigned count=0,insertions=0,improvements=0,rejections=0;
    for (unsigned op=0;op<20000;++op) {
        if (op%500==0) {count=0;oracle.clear();}
        auto before=storage;unsigned old_count=count,id=UINT32_MAX;
        auto edge=LabelEdge{uint32_t(rng()),uint32_t(rng()),uint32_t(rng()),uint32_t(rng()),uint32_t(rng()),uint32_t(rng()),uint32_t(rng()%2)};
        bool changed=false;
        if (oracle.empty() || op%17==0) {
            auto status=Store::append_root(words,count,id);
            if (oracle.size()==Capacity) {assert(status==Status::capacity_exhausted && id==UINT32_MAX);++rejections;}
            else {assert(status==Status::ok && id==oracle.size());oracle.push_back({0,0,true,{}});changed=true;++insertions;}
        } else if (op%3) {
            unsigned parent=unsigned(rng()%oracle.size());uint64_t cost=oracle[parent].cost+1+rng()%10000;
            auto status=Store::append_child(words,count,cost,parent,edge,id);
            if (oracle.size()==Capacity) {assert(status==Status::capacity_exhausted && id==UINT32_MAX);++rejections;}
            else {assert(status==Status::ok && id==oracle.size());oracle.push_back({cost,parent,false,edge});changed=true;++insertions;}
        } else {
            id=unsigned(rng()%oracle.size());unsigned parent=unsigned(rng()%oracle.size());uint64_t cost=1+rng()%10000;
            auto status=Store::improve(words,count,id,cost,parent,edge);
            if (oracle[id].root) assert(status==Status::invalid);
            else if (cost>=oracle[id].cost) assert(status==Status::not_improved);
            else if (parent==id || oracle[parent].cost>=cost) assert(status==Status::invalid);
            else {assert(status==Status::ok);oracle[id]={cost,parent,false,edge};changed=true;++improvements;}
            if (!changed) ++rejections;
        }
        assert(count==oracle.size());
        if (!changed) assert(storage==before && count==old_count);
        assert(storage.front()==guard && storage.back()==guard);
        for (unsigned j=0;j<count;++j) {LabelRecord r{};assert(Store::read(words,count,j,r)==Status::ok && equal(r,oracle[j]));}
        unsigned target=unsigned(rng()%count),n=UINT32_MAX,expected=0,cursor=target;
        while (!oracle[cursor].root) {cursor=oracle[cursor].parent;++expected;assert(expected<=count);}
        assert(Store::validate_path(words,count,target,n)==Status::ok && n==expected);
    }
    assert(insertions && rejections);
    if (Capacity>1) assert(improvements);
    std::cout<<"LABEL_RECORD_RANDOM_PASS capacity="<<Capacity<<" operations=20000 insertions="<<insertions<<" improvements="<<improvements<<" rejections="<<rejections<<'\n';
}
void boundaries() {
    using Store=fpga_search::LabelRecords<8>;std::vector<uint64_t> w(80,0);unsigned count=0,id;
    assert(Store::append_root(w.data(),count,id)==Status::ok && id==0);
    assert(Store::append_child(w.data(),count,100,0,{1,2,3,4,5,6,1},id)==Status::ok && id==1);
    assert(Store::append_child(w.data(),count,2,0,{UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX,1},id)==Status::ok && id==2);
    // Newer label 2 becomes predecessor of older label 1.
    assert(Store::improve(w.data(),count,1,3,2,{1,7,8,9,10,11,0})==Status::ok);
    unsigned steps=999;assert(Store::validate_path(w.data(),count,1,steps)==Status::ok && steps==2);
    assert(Store::append_child(w.data(),count,UINT64_MAX-1,0,{},id)==Status::ok);
    for (auto cost:{uint64_t(0),UINT64_MAX}) {
        auto before=w;auto old=count;id=999;
        assert(Store::append_child(w.data(),count,cost,0,{},id)==Status::invalid && count==old && id==999 && w==before);
    }
    for (unsigned parent:{1u,999u}) {
        auto before=w;assert(Store::improve(w.data(),count,1,1,parent,{})==Status::invalid && w==before);
    }
    auto valid=w;
    // A forged two-node cycle, malformed words, and invalid counts never leak output.
    for (unsigned kind=0;kind<6;++kind) {
        w=valid;unsigned c=count;
        if (kind==0) w[21]=1;
        if (kind==1) w[12]=2;
        if (kind==2) w[13]=uint64_t(UINT32_MAX)+1;
        if (kind==3) c=9;
        if (kind==4) w[11]=999;
        if (kind==5) w[10]=0;
        auto before=w;steps=999;
        assert(Store::validate_path(w.data(),c,1,steps)==Status::invalid && steps==999 && w==before);
    }
    LabelRecord r{17,19,true,{}};auto before=r;
    assert(Store::read(valid.data(),0,0,r)==Status::invalid && equal(r,before));
    std::cout<<"LABEL_RECORD_BOUNDARY_PASS\n";
}
int main(){random_cases<1>();random_cases<3>();random_cases<64>();boundaries();std::cout<<"LABEL_RECORD_ALL_PASS\n";}
