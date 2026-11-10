#include "frontier_api.hpp"
#include "frontier_reference.hpp"
void frontier_step(std::uint32_t op,std::uint32_t key_bits,std::uint32_t id,
                   std::uint32_t& status,std::uint32_t& result_bits,
                   std::uint32_t& result_id,std::uint32_t& size) {
    static std::vector<golden::DaryPQ::E> storage;
    static golden::DaryPQ heap(storage,8);
    status=frontier::OK;result_bits=0;result_id=0;
    if(op==frontier::CLEAR)heap.clear();
    else if(op==frontier::OFFER) {
        if(heap.sz==(int)frontier::capacity)status=frontier::FULL;
        else heap.offer(golden::as_float(key_bits),(int)id);
    } else if(op==frontier::POLL) {
        if(heap.empty())status=frontier::EMPTY;
        else {result_bits=golden::as_bits(heap.h[0].lb);result_id=(std::uint32_t)heap.poll();}
    } else if(op!=frontier::SIZE)status=frontier::BAD;
    size=(std::uint32_t)heap.sz;
}
