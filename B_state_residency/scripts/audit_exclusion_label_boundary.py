"""Source-backed integration contract review, not a hardware integration test."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha

def main():
 out=ROOT/'results/exclusion_label_boundary_20261024';out.mkdir()
 names=['hardware/variants/sparse_records/memory_scratch_endpoint_small_staticcodec.sv','hardware/rtl/scratch_frame_store_bram.sv','adapters/build_real_value_trace.py','adapters/build_resident_zero_router.py','hardware/hls/exclusion/rearchitect/v1/src/exclusion_port.hpp','hardware/hls/exclusion/ARCHITECTURE.md']
 text={name:(ROOT/name).read_text() for name in names}
 native=text[names[0]];store=text[names[1]]
 assert 'input wire [20:0] cmd_page' in native and 'input wire [2:0] cmd_offset' in native
 assert 'TX_BITS=16,GENERATION_BITS=16' in native
 assert '2: merged[95:64] = access_value;' in store and '3: merged[127:96] = access_value;' in store
 assert "rsp_payload <= read_present ? {24'b0,read_word} : 160'b0;" in store
 assert "fields = {'lb': 0, 'upstream': 1, 'prev': 2, 'visited': 3, 'target': 4}" in text[names[2]]
 assert 'static NodeDyn zero{};' in text[names[3]]
 graph=ROOT/'results/graph_image_20261024/source_bound_audit.json';g=json.loads(graph.read_text());assert g['status']=='passed' and g['nodes']<=1<<24
 hls=ROOT/'results/exclusion_hls_20261024/source_bound_audit.json';assert json.loads(hls.read_text())['status']=='passed'
 result={'status':'source_reviewed','script_sha256':sha(Path(__file__)),'files':{name:sha(ROOT/name) for name in names},'gates':{'graph_image':sha(graph),'exclusion_hls':sha(hls)},'mapping':{'phase1_child_prev':{'field':2,'payload_bits':[95,64]},'phase2_child_visited':{'field':3,'payload_bits':[127,96]},'phase3_parent_visited':{'field':3,'payload_bits':[127,96]},'phase4_arc_prev':{'field':2,'payload_bits':[95,64]}},'native_node_capacity':1<<24,'observed_graph_nodes':g['nodes'],'node_mapping':{'page':'node >> 3','offset':'node & 7','require_before_truncation':'node < 2^24'},'empty_record_value':0,'generation_domains':{'edge_context':32,'page_binding':16,'same_identifier':False},'scope':'Static source contract only; no adapter/label-service or paging integration run.'}
 (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
