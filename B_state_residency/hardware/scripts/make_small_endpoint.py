"""Independent 32-slot/8-node endpoint chain. Original 64-node RTL stays frozen."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def common(s):
 s=s.replace('[1:0] cmd_slot, cmd_query','[4:0] cmd_slot, input wire [1:0] cmd_query')
 s=s.replace('[1:0] cmd_slot,cmd_query','[4:0] cmd_slot,input wire [1:0] cmd_query')
 s=s.replace('[17:0] cmd_page','[20:0] cmd_page').replace('[5:0] cmd_offset','[2:0] cmd_offset')
 return s

def controller(s):
 s=common(s).replace('module scratch_page_controller #','module scratch_page_controller_small #')
 s=s.replace('[0:3]','[0:31]').replace('reg [3:0] dirty, pristine, generation_used, query_used;','reg [31:0] dirty, pristine, generation_used;\n    reg [3:0] query_used;')
 s=s.replace('[17:0] page_tag','[20:0] page_tag').replace('[63:0] transferred','[7:0] transferred')
 a=s.index('    wire all_free =');b=s.index('\n    reg core_valid',a)
 s=s[:a]+'''    wire [31:0] slot_free,slot_dirty;
    genvar slot_index;
    generate for(slot_index=0;slot_index<32;slot_index=slot_index+1)begin: slot_flags
        assign slot_free[slot_index]=phase[slot_index]==FREE;
        assign slot_dirty[slot_index]=phase[slot_index]==LIVE && dirty[slot_index];
    end endgenerate
    wire all_free=&slot_free;
    wire unleased_dirty=|slot_dirty;
'''+s[b:]
 s=s.replace('reg [1:0] saved_slot, saved_query;','reg [4:0] saved_slot;reg [1:0] saved_query;').replace('[17:0] saved_page','[20:0] saved_page').replace('[5:0] saved_offset','[2:0] saved_offset')
 s=s.replace('scratch_frame_store #(.GENERATION_BITS(GENERATION_BITS))','scratch_frame_store #(.SLOTS(32),.SLOT_BITS(5),.OFFSET_BITS(3),.PAGE_BITS(21),.GENERATION_BITS(GENERATION_BITS))').replace('i<4;','i<32;')
 return s

def queued(s):
 s=common(s).replace('module queued_scratch_endpoint #','module queued_scratch_endpoint_small #')
 s=s.replace('[3:0] leases','[31:0] leases').replace('CMD_WIDTH=233+','CMD_WIDTH=236+')
 s=s.replace('wire [1:0] slot,query_id;','wire [4:0] slot;wire [1:0] query_id;').replace('[17:0] page','[20:0] page').replace('[5:0] offset','[2:0] offset').replace('[1:0] pending_slot','[4:0] pending_slot')
 s=s.replace('scratch_page_controller #','scratch_page_controller_small #')
 return s

def endpoint(s):
 s=common(s).replace('module memory_scratch_endpoint_retained #','module memory_scratch_endpoint_small #')
 s=s.replace('FRAMES=23405,INDEX_BITS=15,HASH_BITS=15','FRAMES=163840,INDEX_BITS=18,HASH_BITS=18')
 s=s.replace('[3:0] page_leases,memory_leases','[31:0] page_leases,memory_leases')
 s=s.replace('reg [3:0] retained_price,bound_mask;','reg [3:0] retained_price;reg [31:0] bound_mask;')
 s=s.replace('reg [1:0] slot,query_id;','reg [4:0] slot;reg [1:0] query_id;').replace('[17:0] page','[20:0] page').replace('[5:0] offset,position','[2:0] offset,position').replace('[23:0] owner','[26:0] owner')
 s=s.replace("wire [63:0] cookie={5'b0,kind", "wire [71:0] cookie={7'b0,kind")
 for n in ['q_offset','record_out_offset']:s=s.replace('[5:0] '+n,'[2:0] '+n)
 for n in ['m_cookie','m_command_cookie','m_expected_cookie']:s=s.replace('[63:0] '+n,'[71:0] '+n)
 s=s.replace("?64'b0:cookie","?72'b0:cookie").replace('position==63','position==7')
 s=s.replace('queued_scratch_endpoint #','queued_scratch_endpoint_small #').replace('record_backing_service_retained #','record_backing_service_small #')
 return s
if __name__=='__main__':
 for src,dst,fn in [('scratch_page_controller','scratch_page_controller_small',controller),('queued_scratch_endpoint','queued_scratch_endpoint_small',queued),('memory_scratch_endpoint_retained','memory_scratch_endpoint_small',endpoint)]:
  p=ROOT/'hardware/rtl'/f'{dst}.sv';s=fn((ROOT/'hardware/rtl'/f'{src}.sv').read_text())
  if p.exists():assert p.read_text()==s
  else:p.write_text(s)
