#define main original_router_main
#include "router.cpp"
#undef main

static void require(bool value,const char* message) { if (!value) throw std::runtime_error(message); }
int main() {
    setenv("B_RESIDENT_PAGES","2",1);
    Router::SparseLabels labels; labels.initPaged(1024,6);
    std::vector<Router::NodeDyn> global(1024, Router::NodeDyn{0,0,3.5f,-1,0,0});
    Router::tl_sparse = &labels; Router::tl_dyn = global.data();
    bvalues::init();
    {
        bvalues::Attempt scope(1,0,0,0); labels.reset();
        uint32_t raw = 0x7fc12345; float nan; std::memcpy(&nan,&raw,4);
        Router::bWriteLabel(0,&Router::NodeDyn::lb,0,1) = nan;
        Router::bWriteLabel(0,&Router::NodeDyn::upstream,1,2) = -0.0f;
        Router::bWriteLabel(0,&Router::NodeDyn::prev,2,3) = -1;
        Router::bWriteLabel(0,&Router::NodeDyn::visited,3,4) = INT32_MAX;
        Router::bWriteLabel(0,&Router::NodeDyn::target,4,5) = uint8_t(255);
        for (int node : {64,128,192}) Router::bWriteLabel(node,&Router::NodeDyn::prev,2,6) = node-1;
        require(labels.writebacks != 0,"Native trace did not exercise dirty eviction");
        require(bvalues::bits(Router::bReadLabel(0,&Router::NodeDyn::lb,0,7)) == raw,"Float bits changed");
        require(bvalues::bits(Router::bReadLabel(0,&Router::NodeDyn::upstream,1,8)) == 0x80000000,"Signed zero changed");
        require(Router::bReadLabel(0,&Router::NodeDyn::prev,2,9) == -1,"Predecessor lost");
        require(Router::bReadLabel(0,&Router::NodeDyn::visited,3,10) == INT32_MAX,"Visit stamp lost");
        require(Router::bReadLabel(0,&Router::NodeDyn::target,4,11) == 255,"Target lost");
        for (const auto& frame : labels.frames) require(frame.pins == 0,"Proxy leaked lease");
    }
    {
        bvalues::Attempt scope(2,1,1,0); labels.reset();
        require(Router::bReadLabel(0,&Router::NodeDyn::prev,2,12) == 0,"Query scratch not reset");
        require(Router::bReadLabel(0,&Router::NodeDyn::visited,3,13) == 0,"Old visit stamp visible");
        require(global[0].hist == 3.5f,"Global history was reset with scratch");
    }
    bvalues::finish();
    std::puts("{\"status\":\"passed\",\"native_generated_proxies\":true}");
}
