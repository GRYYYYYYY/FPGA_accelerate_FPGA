#include "frontier_api.hpp"
#include "frontier_bounded.hpp"
#include "frontier_reference.hpp"
#include <cstdio>
#include <cstdlib>
#include <vector>
static std::vector<golden::DaryPQ::E> storage;
static golden::DaryPQ oracle(storage,8);
static std::uint64_t checks=0,comparisons=0;
static void require(bool ok,const char* text) {if(!ok){std::fprintf(stderr,"FAIL %s check=%llu\n",text,(unsigned long long)checks);std::exit(1);}}
static void command(std::uint32_t op,std::uint32_t bits=0,std::uint32_t id=0) {
    std::uint32_t expected_status=frontier::OK,expected_bits=0,expected_id=0;
    if(op==frontier::CLEAR)oracle.clear();
    else if(op==frontier::OFFER){if(oracle.sz==(int)frontier::capacity)expected_status=frontier::FULL;else oracle.offer(golden::as_float(bits),(int)id);}
    else if(op==frontier::POLL){if(oracle.empty())expected_status=frontier::EMPTY;else{expected_bits=golden::as_bits(oracle.h[0].lb);expected_id=(std::uint32_t)oracle.poll();}}
    else if(op!=frontier::SIZE)expected_status=frontier::BAD;
    std::uint32_t status=99,result_bits=1,result_id=1,size=0;
    frontier_step(op,bits,id,status,result_bits,result_id,size);
    require(status==expected_status && result_bits==expected_bits && result_id==expected_id && size==(std::uint32_t)oracle.sz,"command vs frozen native D8");++checks;
}
static std::uint32_t rng_state=0x291u;
static std::uint32_t next_random(){rng_state^=rng_state<<13;rng_state^=rng_state>>17;rng_state^=rng_state<<5;return rng_state;}
int main() {
    // Direct bit comparator test is C++ validation; heap commands below also
    // exercise comparison in the actual synthesized/co-simulated component.
    const std::uint32_t corners[]={0u,0x80000000u,1u,0x80000001u,0x007fffffu,0x00800000u,0x3f800000u,0xbf800000u,0x7f800000u,0xff800000u,0x7fc12345u,0xffc12345u,0x7f800001u};
    for(auto a:corners)for(auto b:corners){const float x=golden::as_float(a),y=golden::as_float(b);require(frontier::less(a,b)==(x<y) && frontier::less_equal(a,b)==(x<=y),"corner compare");++comparisons;}
    for(unsigned i=0;i<1000000;++i){auto a=next_random(),b=next_random();float x=golden::as_float(a),y=golden::as_float(b);require(frontier::less(a,b)==(x<y) && frontier::less_equal(a,b)==(x<=y),"random compare");++comparisons;}
    command(frontier::CLEAR);command(frontier::POLL);command(99);command(frontier::SIZE);
    for(unsigned i=0;i<13;++i)command(frontier::OFFER,corners[i],i);
    for(unsigned i=0;i<13;++i)command(frontier::POLL);
    for(unsigned i=0;i<10;++i)command(frontier::OFFER,0,i);
    for(unsigned i=0;i<10;++i)command(frontier::POLL);
    // Exercise every address, six sift levels, full rejection and drain order.
    for(unsigned i=0;i<frontier::capacity;++i)command(frontier::OFFER,golden::as_bits((float)(frontier::capacity-i)),i);
    command(frontier::OFFER,0,0xffffffffu);command(99);command(frontier::SIZE);
    for(unsigned i=0;i<frontier::capacity;++i)command(frontier::POLL);
    command(frontier::POLL);
    for(unsigned i=0;i<4096;++i){if((next_random()&3u)!=0)command(frontier::OFFER,next_random(),i);else command(frontier::POLL);}
    // Nonempty reset must hide stale entries without sweeping payload RAM.
    command(frontier::CLEAR);command(frontier::POLL);command(frontier::OFFER,0x80000000u,9);command(frontier::POLL);
    command(frontier::CLEAR);command(frontier::SIZE);
    std::printf("FRONTIER_TEST_PASS capacity=%u checks=%llu comparisons=%llu\n",frontier::capacity,(unsigned long long)checks,(unsigned long long)comparisons);
    return 0;
}
