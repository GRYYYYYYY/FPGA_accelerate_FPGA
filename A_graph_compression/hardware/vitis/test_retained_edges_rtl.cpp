// Independent ordered-vector/map oracle, full declared pointers and tail guards.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <vector>
extern "C" void search_retained_edges_top(const uint64_t*,uint64_t*,uint32_t*,const uint32_t*,uint32_t*,uint64_t*);
constexpr unsigned E=2097152,N=1048576;constexpr uint32_t G=0xdeadbeef;
constexpr uint64_t M=UINT64_C(0x4152455445444731),G64=UINT64_C(0xdeadbeef01234567);
struct Bench {
    std::vector<uint64_t> c=std::vector<uint64_t>(9),m=std::vector<uint64_t>(7),r=std::vector<uint64_t>(6);
    std::vector<uint32_t> rows=std::vector<uint32_t>(18*E+1,G),path=std::vector<uint32_t>(8*E+1,G),out=std::vector<uint32_t>(8*E+1,G);
    std::map<uint32_t,std::vector<uint32_t>> ref;unsigned tx=0;
    Bench(){c.back()=m.back()=r.back()=G64;}
    void config(unsigned op,uint32_t net=0,unsigned count=0,unsigned domain=0){for(unsigned i=0;i<8;++i)c[i]=0;c[0]=op;c[1]=net;c[2]=domain;c[3]=count;}
    void edge(unsigned i,unsigned variant=0){uint32_t a[8]={N-1,0,UINT32_MAX,variant%2,17,19,0xfedcba98,variant%2};for(unsigned j=0;j<8;++j)path[8*i+j]=a[j];}
    void call(unsigned status){
        const auto oldc=c,oldm=m;const auto input=path;auto wantrows=rows;auto wantout=out;auto wantm=m;
        unsigned returned=0;
        if(!status){
            if(c[0]==0){ref.clear();wantm[0]=M;wantm[1]=c[2];wantm[2]=0;wantm[3]=0;wantm[4]=0;wantm[5]=1;}
            else if(c[0]==2){auto it=ref.find(uint32_t(c[1]));if(it!=ref.end()){returned=it->second.size()/8;std::copy(it->second.begin(),it->second.end(),wantout.begin());}}
            else {
                auto &v=ref[uint32_t(c[1])];if(c[0]==1)v.clear();v.insert(v.end(),path.begin(),path.begin()+8*c[3]);if(v.empty())ref.erase(uint32_t(c[1]));
                unsigned at=(1-unsigned(m[3]))*E*9,total=0;
                for(const auto &entry:ref)for(unsigned i=0;i<entry.second.size()/8;++i){wantrows[at++]=entry.first;for(unsigned j=0;j<8;++j)wantrows[at++]=entry.second[8*i+j];++total;}
                wantm[2]=total;wantm[3]=1-m[3];wantm[4]=ref.size();++wantm[5];
            }
        }
        search_retained_edges_top(c.data(),m.data(),rows.data(),path.data(),out.data(),r.data());
        assert(c==oldc && path==input && m==wantm && rows==wantrows && out==wantout && r.back()==G64);
        assert(r[0]==status && r[1]==(status?0:m[2]) && r[2]==(status?0:m[4]) && r[3]==(status?0:m[5]) && r[4]==returned);
        if(status)assert(m==oldm);
        std::cout<<"EDGE_RTL_TX "<<tx++<<' '<<c[0]<<' '<<r[0]<<' '<<r[1]<<' '<<r[2]<<' '<<r[3]<<' '<<r[4]<<'\n';
    }
    void seed_nets(){
        ref.clear();m[0]=M;m[1]=N;m[2]=65536;m[3]=0;m[4]=65536;m[5]=1;
        edge(0);for(unsigned i=0;i<65536;++i){ref[i]=std::vector<uint32_t>(path.begin(),path.begin()+8);rows[9*i]=i;for(unsigned j=0;j<8;++j)rows[9*i+1+j]=path[j];}
    }
};
int main(){
    Bench b;b.config(0,0,0,N);b.call(0); //0
    for(unsigned i=0;i<E;++i)b.edge(i,i);
    b.config(1,0,E);b.call(0); //1 actual maximum
    b.config(2);b.call(0); //2 all fields
    b.config(3,0,1);b.call(2); //3 full append
    b.config(1,UINT32_MAX,1);b.call(2); //4 full distinct net
    b.config(2,UINT32_MAX);b.call(0); //5 absent
    b.config(1);b.call(0); //6 delete
    b.config(3,UINT32_MAX,2);b.call(0); //7
    b.call(0); //8 duplicates, stable append
    b.config(2,UINT32_MAX);b.call(0); //9
    b.config(1,0,1);b.call(0); //10 sorted net insert
    b.config(2,0);b.call(0); //11
    b.config(2,UINT32_MAX);b.call(0); //12
    b.path[15]=2;b.config(3,UINT32_MAX,2);b.call(1);b.path[15]=1; //13 late dir
    b.path[9]=N;b.call(1);b.path[9]=0; //14 late dst
    b.path[0]=N;b.call(1);b.path[0]=N-1; //15 src
    b.m[5]=UINT64_MAX;b.call(3); //16 saturated
    b.config(2,UINT32_MAX);b.call(0); //17 readable at maxversion
    b.config(0,0,0,N);b.call(0); //18
    b.config(0);b.call(1); //19 zero domain
    b.config(0,0,0,N+1);b.call(2); //20 oversized
    b.config(2);b.c[7]=1;b.call(1); //21 reserved
    b.config(2);b.c[1]=UINT64_C(1)<<32;b.call(1); //22 width
    b.config(3);b.c[3]=UINT64_C(1)<<32;b.call(1); //23 width
    b.config(4);b.call(1); //24 invalid op
    b.config(2);b.m[0]=0;b.call(1); //25 invalid state
    b.config(0,0,0,N);b.call(0); //26 recovery
    b.seed_nets();b.config(3,UINT32_MAX,1);b.call(2); //27 actual netcap
    b.config(1,0,2);b.call(0); //28 replace existing at cap
    b.config(2);b.call(0); //29
    b.config(1);b.call(0); //30 delete 2
    b.config(3,UINT32_MAX,2);b.call(0); //31 regain cap
    b.config(2,UINT32_MAX);b.call(0); //32
    b.config(0,0,0,N);b.call(0); //33
    for(unsigned i=0;i<4;++i)b.edge(i,i%2);
    b.config(3,0,4);b.call(0); //34 repeated sequence
    b.config(2);b.call(0); //35
    b.config(1);b.call(0); //36
    assert(b.tx==37);
    std::cout<<"EDGE_RTL_GOLDEN_PASS transactions=37 edges=2097152 seeded_nets=65536 full_depths=1\n";
}
