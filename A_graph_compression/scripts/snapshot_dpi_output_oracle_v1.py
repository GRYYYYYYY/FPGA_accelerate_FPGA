"""Compare every snapshot output word against the original prepared C oracle."""
import re
from pathlib import Path
from check_vitis_kernel import require

def binary_records(expected,actual,depth,count,word_bytes):
    stride=8+depth*word_bytes;size=count*stride;marker=bytes.fromhex('5a5aa5a50f0ff0f0')
    require(expected.stat().st_size==size+8,'Wrong complete C binary oracle size')
    require(actual.stat().st_size in [size,size+8],'Wrong complete RTL binary output size')
    with expected.open('rb') as a,actual.open('rb') as b:
        for transaction in range(count):
            header=a.read(8);other=b.read(8)
            require(header==other and int.from_bytes(header,'big')==depth,'Different binary depth/header at '+str(transaction))
            remaining=depth*word_bytes
            while remaining:
                amount=min(4*1024*1024,remaining);x=a.read(amount);y=b.read(amount)
                require(len(x)==amount and x==y,'Full binary output differs at transaction '+str(transaction))
                remaining-=amount
        require(a.read()==marker,'Wrong C binary EOF')
        require(b.read() in [b'',marker],'Wrong RTL binary EOF')

def text_records(path,depth,count,bits):
    lines=path.read_text().splitlines();require(lines and lines[0]=='[[[runtime]]]' and lines[-1]=='[[[/runtime]]]','Invalid runtime framing')
    at=1;result=[]
    for transaction in range(count):
        match=re.fullmatch(r'\[\[transaction\]\][ \t]+(\d+)',lines[at]) if at<len(lines) else None
        require(match is not None and int(match[1])==transaction,'Missing/reordered output transaction')
        at+=1;words=[]
        for i in range(depth):
            require(at<len(lines) and re.fullmatch(r'0x[0-9a-fA-F]+',lines[at]),'Malformed/unknown output word')
            value=int(lines[at],16);require(value.bit_length()<=bits,'Output word too wide');words.append(value);at+=1
        require(at<len(lines) and lines[at]=='[[/transaction]]','Invalid transaction boundary');at+=1;result.append(words)
    require(at==len(lines)-1,'Extra complete output data');return result

def verify(original_sim,actual_sim):
    source=original_sim/'tv/cdatafile';target=actual_sim/'tv/rtldatafile'
    packet_source=source/'c.search_resident_snapshot_top.autotvout_packet_mem.dat'
    packet_target=target/'rtl.search_resident_snapshot_top.autotvout_packet_mem.dat'
    result_source=source/'c.search_resident_snapshot_top.autotvout_result_mem.dat'
    result_target=target/'rtl.search_resident_snapshot_top.autotvout_result_mem.dat'
    expected_names={packet_target.name,result_target.name}
    require({p.name for p in target.glob('rtl.*.autotvout_*.dat')}==expected_names,'Missing/extra snapshot output bundles')
    require(packet_target.stat().st_size==packet_source.stat().st_size,'Missing complete snapshot runtime EOF')
    binary_records(packet_source,packet_target,524288,30,64)
    require(text_records(result_source,1,30,512)==text_records(result_target,1,30,512),'Complete result words differ')
    return [packet_source,packet_target,result_source,result_target]
