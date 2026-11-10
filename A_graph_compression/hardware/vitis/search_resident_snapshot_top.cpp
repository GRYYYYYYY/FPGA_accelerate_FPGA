#include "search_resident_snapshot.hpp"
extern "C" void search_resident_snapshot_top(const uint64_t* control,const uint64_t* stat,const uint64_t* initial,
    const uint64_t* node_meta,const uint32_t* node_counts,const uint64_t* node_history,const uint64_t* node_keys,
    const uint32_t* node_flags,const uint64_t* site_meta,const uint64_t* site_owners,const uint64_t* site_history,
    uint64_t* packet,uint64_t* result) {
#pragma HLS INTERFACE m_axi port=control offset=slave bundle=control_mem depth=16
#pragma HLS INTERFACE m_axi port=stat offset=slave bundle=static_mem depth=4194304
#pragma HLS INTERFACE m_axi port=initial offset=slave bundle=control_mem depth=65
#pragma HLS INTERFACE m_axi port=node_meta offset=slave bundle=meta_mem depth=4
#pragma HLS INTERFACE m_axi port=node_counts offset=slave bundle=count_mem depth=1048576
#pragma HLS INTERFACE m_axi port=node_history offset=slave bundle=node_history_mem depth=1048576
#pragma HLS INTERFACE m_axi port=node_keys offset=slave bundle=node_table_mem depth=2097152
#pragma HLS INTERFACE m_axi port=node_flags offset=slave bundle=node_table_mem depth=2097152
#pragma HLS INTERFACE m_axi port=site_meta offset=slave bundle=meta_mem depth=6
#pragma HLS INTERFACE m_axi port=site_owners offset=slave bundle=site_table_mem depth=524288
#pragma HLS INTERFACE m_axi port=site_history offset=slave bundle=site_history_mem depth=262144
#pragma HLS INTERFACE m_axi port=packet offset=slave bundle=packet_mem depth=4194304
#pragma HLS INTERFACE m_axi port=result offset=slave bundle=result_mem depth=8
#pragma HLS INTERFACE s_axilite port=control bundle=control
#pragma HLS INTERFACE s_axilite port=stat bundle=control
#pragma HLS INTERFACE s_axilite port=initial bundle=control
#pragma HLS INTERFACE s_axilite port=node_meta bundle=control
#pragma HLS INTERFACE s_axilite port=node_counts bundle=control
#pragma HLS INTERFACE s_axilite port=node_history bundle=control
#pragma HLS INTERFACE s_axilite port=node_keys bundle=control
#pragma HLS INTERFACE s_axilite port=node_flags bundle=control
#pragma HLS INTERFACE s_axilite port=site_meta bundle=control
#pragma HLS INTERFACE s_axilite port=site_owners bundle=control
#pragma HLS INTERFACE s_axilite port=site_history bundle=control
#pragma HLS INTERFACE s_axilite port=packet bundle=control
#pragma HLS INTERFACE s_axilite port=result bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    fpga_search::ProductionResidentSnapshot::run(control,stat,initial,node_meta,node_counts,node_history,node_keys,node_flags,
                                               site_meta,site_owners,site_history,packet,result);
}
