#include "../hardware/vitis/search_xrt_v1/transport.hpp"
#include <iostream>
// Force compilation/linkage of the production XRT API path without opening a
// device during a compile-only run. Board execution requires a bound xclbin.
void instantiate_search_xrt(const std::vector<char>& binary,const std::string& device,
                            const std::string& layout,const std::vector<uint32_t>& image,
                            const std::vector<uint32_t>& config,const std::vector<uint64_t>& packet) {
    search_xrt::Transport backend(binary,device,layout,image,config,config.at(0));
    search_xrt::Session<search_xrt::Transport> session(backend,image.data(),unsigned(image.size()),config.data());
    uint32_t root=0;
    (void)session.search(&root,1,packet.data(),packet.size());
}
int main(){std::cout<<"SEARCH_XRT_LINK_PASS hardware_executed=false\n";}
