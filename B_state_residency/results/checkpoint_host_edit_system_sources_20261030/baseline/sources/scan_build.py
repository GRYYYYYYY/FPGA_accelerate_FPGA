from pathlib import Path
import re
HERE=Path(__file__).resolve().parent
BASE=Path('/tmp/B_state_residency_offer_20261025/iter2_runtime_owner_full_v4/sources')
CHAIN=['expansion_20261024/pager/backend/backing_frame_directory_small.sv','expansion_20261024/pager/backend/backing_page_service_small.sv','expansion_20261024/pager/backend/record_backing_service_small_staticcodec.sv','expansion_20261024/pager/backend/memory_scratch_endpoint_small_staticcodec.sv','expansion_20261024/pager/pager/paged_exclusion_engine.sv','priced/candidate_recursive_query_core.sv','priced/candidate_recursive_engine.sv','residency_system.sv','search_residency_system.sv','query_residency_system.sv']
MANAGER='expansion_20261024/pager/pager/resident_page_manager.sv'
FILES=CHAIN+[MANAGER]
PORTS='''
 input wire scan_valid,output wire scan_ready,input wire scan_permit,input wire[INDEX_BITS-1:0]scan_frame,
 output wire scan_rsp_valid,input wire scan_rsp_ready,output wire[2:0]scan_status,
 output wire[INDEX_BITS-1:0]scan_result_frame,output wire[26:0]scan_owner,output wire scan_published'''
CONNECT='.scan_valid(scan_valid),.scan_ready(scan_ready),.scan_permit(scan_permit),.scan_frame(scan_frame),.scan_rsp_valid(scan_rsp_valid),.scan_rsp_ready(scan_rsp_ready),.scan_status(scan_status),.scan_result_frame(scan_result_frame),.scan_owner(scan_owner),.scan_published(scan_published),'
def make():
 child=None
 for n in CHAIN:
  s=(BASE/n).read_text();name=re.search(r'\bmodule\s+(\w+)',s)[1]
  at=s.index('#(',s.index('module'))+2;s=s[:at]+'parameter integer ENABLE_FRAME_SCAN=0,'+s[at:]
  end=s.index(');',s.index('input wire'));s=s[:end].rstrip()+','+PORTS+'\n'+s[end:]
  if child:
   start=re.search(r'\b'+child+r'\s*#\s*\(',s).end();s=s[:start]+'.ENABLE_FRAME_SCAN(ENABLE_FRAME_SCAN),'+s[start:]
   depth=1;pos=start
   while depth:
    depth+=(s[pos]=='(')-(s[pos]==')');pos+=1
   inst=re.match(r'\s*\w+\s*\(',s[pos:]);assert inst,(n,child)
   pos+=inst.end();connect=CONNECT.replace('.scan_permit(scan_permit)', '.scan_permit(scan_permit&&pc_owned&&pc_safe&&!wm_owned&&!jp_owned)')if name=='query_residency_system'else CONNECT.replace('.scan_permit(scan_permit)', '.scan_permit(scan_permit&&snapshot_clean)')if name=='paged_exclusion_engine'else CONNECT
   s=s[:pos]+connect+s[pos:]
  else:
   s=s.replace('output reg rsp_valid','output wire rsp_valid')
   start=s.index('    localparam');end=s.index('`ifdef BUNDLE_TRACE')
   body=s[start:end].replace('    reg [3:0] state;','');body=re.sub(r'\brsp_valid\b','reply_valid',body)
   body=body.replace('&& !reply_valid;','&& !reply_valid && !want_scan;')
   body=body.replace('if(reply_valid && rsp_ready)','if(reply_valid && reply_ready)')
   body=body.replace('OWNER_CHECK:begin\n                    if(','''OWNER_CHECK:begin
                    if(inspecting)begin reply_valid<=1;rsp_frame<=indexed_frame;rsp_published<=read_word[27];inspected_owner<=read_word[26:0];state<=IDLE;end
                    else if(''')
   body=body.replace('tx_used<=0;last_tx<=0;lookup_only<=0;','inspecting<=0;inspected_owner<=0;tx_used<=0;last_tx<=0;lookup_only<=0;',1)
   body=body.replace('if(accept)begin\n', 'if(accept)begin\n                inspecting<=0;\n')
   marker='            if(accept)begin'
   body=body.replace(marker,'''            if(want_scan && scan_ready)begin
                inspecting<=1;reply_valid<=1;rsp_status<=OK;rsp_frame<=scan_frame;rsp_published<=0;inspected_owner<=0;
                if(!scan_permit || leased!=0 || any_fault)rsp_status<=BUSY;
                else if({1'b0,scan_frame}>=allocated)rsp_status<=UNREADY;
                else begin indexed_frame<=scan_frame;reply_valid<=0;state<=OWNER_READ;end
            end
'''+marker)
   extra='''    reg[3:0]state;reg reply_valid,inspecting;reg[26:0]inspected_owner;
    wire want_scan=(ENABLE_FRAME_SCAN!=0)&&scan_valid;
    wire reply_ready=inspecting?scan_rsp_ready:rsp_ready;
    assign rsp_valid=reply_valid&&!inspecting;
    assign scan_ready=(ENABLE_FRAME_SCAN!=0)&&!rst&&state==4'd0&&!reply_valid;
    assign scan_rsp_valid=reply_valid&&inspecting;
    assign scan_status=rsp_status;assign scan_result_frame=rsp_frame;
    assign scan_owner=inspected_owner;assign scan_published=rsp_published;
'''
   s=s[:start]+extra+body+s[end:]
  if name=='paged_exclusion_engine':s=s.replace('    wire client_quiescent=engine_ready;','    wire snapshot_clean;\n    wire client_quiescent=engine_ready;')
  p=HERE/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s);child=name
 s=(BASE/MANAGER).read_text();end=s.index(');',s.index('input wire'));s=s[:end].rstrip()+',output wire snapshot_clean\n'+s[end:]
 s=s.replace('endmodule','assign snapshot_clean=!rst&&state==IDLE&&active&&valid_slots==0&&dirty_slots==0;\nendmodule')
 p=HERE/MANAGER;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
if __name__=='__main__':make()
