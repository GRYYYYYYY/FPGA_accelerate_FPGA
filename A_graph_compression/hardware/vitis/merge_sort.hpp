// Alternative sorting stage only; preserve the original seven-word comparator.
static void sort_edges_merge(EdgeRecord buffer[MAX_DEGREE], uint32_t degree) {
    EdgeRecord scratch[MAX_DEGREE];
#pragma HLS BIND_STORAGE variable=scratch type=ram_2p impl=bram
    for (uint32_t width=1; width<degree; width*=2) {
        for (uint32_t begin=0; begin<degree; begin+=2*width) {
            uint32_t middle=begin+width;
            if (middle>degree) middle=degree;
            uint32_t end=begin+2*width;
            if (end>degree) end=degree;
            uint32_t left=begin, right=middle;
            for (uint32_t k=begin; k<end; ++k) {
                if (left<middle && (right>=end || !less_edge(buffer[right],buffer[left])))
                    scratch[k]=buffer[left++];
                else
                    scratch[k]=buffer[right++];
            }
        }
        for (uint32_t i=0; i<degree; ++i) buffer[i]=scratch[i];
    }
}
