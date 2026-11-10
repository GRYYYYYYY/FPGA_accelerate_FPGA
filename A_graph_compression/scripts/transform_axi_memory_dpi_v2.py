#!/usr/bin/env python3
"""Change only generated HLS AXI backing storage; preserve protocol and NBA timing."""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def transform(text):
    match=re.search(r'module AESL_axi_master_(\w+)\s*\(',text);assert match,'Not an HLS AXI model'
    b=match[1];pages=int(re.search(r'parameter\s+mem_page_num\s*=\s*32\x27d\s*(\d+)',text)[1])
    depth=b+'_mem_depth';width=b+'_DATA_BITWIDTH'
    declarations=r"(?m)^[ \t]*reg\s*\[\s*"+re.escape(width)+r"\s*-\s*1\s*:\s*0\s*\]\s*"+re.escape(b)+r"_mem_(\d+)\s*\[\s*0\s*:\s*"+re.escape(depth)+r"\s*-\s*1\s*\]\s*=\s*'\{\s*default\s*:\s*'h0\s*\};[ \t]*$"
    found=re.findall(declarations,text);assert sorted(map(int,found))==list(range(pages)),'Unexpected native memory declarations'
    helper='''// A_DPI_STORAGE_ONLY: protocol, depths and transaction pages unchanged.
import "DPI-C" function int a_model_register(input string name,input int bits,input longint depth,input int pages);
import "DPI-C" function void a_model_read(input int id,input int page,input longint index,output logic[511:0] value);
import "DPI-C" function void a_model_write(input int id,input int page,input longint index,input logic[511:0] value);
import "DPI-C" function void a_model_enqueue(input int id,input int page,input longint index,input logic[511:0] value);
import "DPI-C" function void a_model_commit(input int id);
integer a_storage_id=-1;
reg a_storage_commit=0;
function integer a_storage_ensure();
 if(a_storage_id<0)a_storage_id=a_model_register($sformatf("%m"),WIDTH,DEPTH,mem_page_num);
 if(a_storage_id<0)$fatal(1,"A_DPI_STORAGE_ALLOCATION_FAILED");
 return a_storage_id;
endfunction
function [WIDTH-1:0] a_storage_read(input integer page,input logic[63:0] index);
 logic[511:0] value;
 if(^index===1'bx)return 'x;
 a_model_read(a_storage_ensure(),page,index,value);return value[WIDTH-1:0];
endfunction
function [15:0] a_storage_read_low16(input integer page,input logic[63:0] index);
 reg[WIDTH-1:0] value;
 value=a_storage_read(page,index);return value[15:0];
endfunction
function a_storage_read_bit(input integer page,input logic[63:0] index,input integer bit_index);
 reg[WIDTH-1:0] value;
 if((^bit_index===1'bx)||bit_index<0||bit_index>=WIDTH)return 1'bx;
 value=a_storage_read(page,index);return value[bit_index];
endfunction
task a_storage_write_blk(input integer page,input logic[63:0] index,input logic[WIDTH-1:0] value);
 if(^index!==1'bx)a_model_write(a_storage_ensure(),page,index,value);
endtask
task a_storage_write_nba(input integer page,input logic[63:0] index,input logic[WIDTH-1:0] value);
 if(^index!==1'bx)begin a_model_enqueue(a_storage_ensure(),page,index,value);a_storage_commit<=~a_storage_commit;end
endtask
always @(a_storage_commit)if(a_storage_id>=0)a_model_commit(a_storage_id);
initial if(mem_page_num!=PAGES || WIDTH<32 || WIDTH>512 || WIDTH%32)$fatal(1,"A_DPI_STORAGE_UNSUPPORTED_PARAMETERS");
'''.replace('WIDTH',width).replace('DEPTH',depth).replace('PAGES',str(pages))
    phases=[]
    def phase(kind,pattern,callback):
        nonlocal text
        before=text;edits=[]
        def convert(m):
            new=callback(m);edits.append(dict(start=m.start(),end=m.end(),old=m[0],new=new));return new
        text=re.sub(pattern,convert,text)
        rebuilt=before
        for e in reversed(edits):assert rebuilt[e['start']:e['end']]==e['old'];rebuilt=rebuilt[:e['start']]+e['new']+rebuilt[e['end']:]
        assert rebuilt==text
        phases.append(dict(kind=kind,before_sha256=sha(before),after_sha256=sha(text),edits=edits))
    phase('storage_declarations',declarations,lambda m:helper if int(m[1])==0 else '')
    ref=re.escape(b)+r'_mem_(\d+)\s*\[([^\[\]\n]+)\]'
    def write(m):
        assert m[4].strip() in ['WDATA_tmp','mem_tmp'],'Unsupported write RHS; do not transform protocol expressions'
        return 'a_storage_write_'+('nba' if m[3]=='<=' else 'blk')+'('+m[1]+',('+m[2]+'),('+m[4]+'));'
    phase('procedural_memory_writes',ref+r'\s*(<=|=(?!=))\s*([^;\n]+);',write)
    phase('low16_reads',ref+r'\s*\[\s*15\s*:\s*0\s*\]',lambda m:'a_storage_read_low16('+m[1]+',('+m[2]+'))')
    phase('packed_bit_reads',ref+r'\s*\[([^\[\]\n:]+)\]',lambda m:'a_storage_read_bit('+m[1]+',('+m[2]+'),('+m[3]+'))')
    phase('whole_word_reads',ref,lambda m:'a_storage_read('+m[1]+',('+m[2]+'))')
    assert not re.search(re.escape(b)+r'_mem_\d+\s*\[',text),'Unsupported memory access remains'
    assert not re.search(r'\ba_storage_read(?:_bit)?\([^;\n]*\)\s*\[',text),'Unsupported function-result part select'
    # Replay the edit ledger independently to prove every changed byte is listed.
    original=text
    for ph in reversed(phases):
        shift=0;positions=[]
        for e in ph['edits']:positions.append((e['start']+shift,e));shift+=len(e['new'])-len(e['old'])
        for start,e in reversed(positions):assert original[start:start+len(e['new'])]==e['new'];original=original[:start]+e['old']+original[start+len(e['new']):]
        assert sha(original)==ph['before_sha256']
    return text,dict(bundle=b,pages=pages,input_sha256=sha(original),output_sha256=sha(text),phases=phases,storage_only=True)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('--ledger',type=Path,required=True);a=p.parse_args();assert not a.output.exists() and not a.ledger.exists()
    text,ledger=transform(a.source.read_text());a.output.write_text(text);a.ledger.write_text(json.dumps(ledger,indent=2)+'\n');print(ledger['bundle'],ledger['pages'],[len(p['edits']) for p in ledger['phases']])
if __name__=='__main__':main()
