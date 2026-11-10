#include "router_access_profile.hpp"
#include <cassert>
#include <iostream>
int main() {
    RouterAccessProfile profile(4);
    profile.observe(0,true,0,0,1);profile.observe(0,true,0,1,0);
    profile.observe(1,true,642,0,1);profile.observe(1,true,642,1,0);
    profile.observe(1,true,642,0,1);
    profile.observe(2,false,999,0,0); // Stale output vector must not count as edges.
    assert(profile.rows[0].visits==2&&profile.rows[0].degree==0);
    assert(profile.rows[1].visits==3&&profile.rows[1].misses==2&&profile.rows[1].hits==1);
    assert(profile.rows[2].unknown==1&&profile.rows[2].degree==-1);
    assert(profile.rows[3].visits==0&&profile.rows[3].degree==-2);
    unsigned rejected=0;
    auto reject=[&](auto call){try{call();}catch(const std::runtime_error&){++rejected;}};
    reject([&]{profile.observe(4,true,0,0,1);});
    reject([&]{profile.observe(0,true,0,0,0);});
    reject([&]{profile.observe(0,true,0,1,1);});
    reject([&]{profile.observe(0,true,0,2,0);});
    reject([&]{profile.observe(2,false,0,0,1);});
    reject([&]{profile.observe(1,true,8,0,1);});
    reject([&]{profile.observe(2,true,0,0,1);});
    profile.rows[3].visits=UINT64_MAX;
    reject([&]{profile.observe(3,true,0,0,1);});
    assert(rejected==8);
    profile.reset();for(const auto& row:profile.rows)assert(row.visits==0&&row.degree==-2);
    profile.observe(1,true,8,0,1);assert(profile.rows[1].degree==8);
    std::cout<<"ROUTER_ACCESS_PROFILE_PASS rejected=8 reset=pass\n";
}
