from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def derive():
    s=(ROOT/'hardware/vitis/search_batch_trace_top.cpp').read_text()
    assert s.count('fpga_search::SearchTraceV2<>::search(')==1
    return '#include "search_trace_v3.hpp"\n'+s.replace('#define SEARCH_TOP_NAME search_batch_trace_top','#define SEARCH_TOP_NAME search_batch_trace_top_v2').replace('fpga_search::SearchTraceV2<>::search(','fpga_search::SearchTraceV3<>::search(')
if __name__=='__main__':
    text=derive()
    with (ROOT/'hardware/vitis/search_batch_trace_top_v2.cpp').open('x') as f:f.write(text)
