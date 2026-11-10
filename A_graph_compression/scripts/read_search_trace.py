#!/usr/bin/env python3
"""Decode exact little-endian search records; a fragment never proves batch completion."""
import argparse
import json
from pathlib import Path
import struct
MAGIC=0x4154524143453031
U32=(1<<32)-1
U64=(1<<64)-1
def require(ok,message):
    if not ok:raise ValueError(message)
def state(words,target):
    h=words[0];s=(h>>32)&255;b=(h>>40)&255;v=(h>>48)&255
    require(not h>>56 and s<=32 and b<=16 and v<=8 and (h&U32)==target,'Invalid demand header')
    signals=[(words[1+i//2]>>(32*(i%2)))&U32 for i in range(s)]
    bits=[[(words[17+i//2]>>(32*(i%2)))&U32,words[25+i],words[41+i]] for i in range(b)]
    values=[[words[57+i]&U32,words[57+i]>>32] for i in range(v)]
    require(signals==sorted(set(signals)),'Unordered/duplicate signal demands')
    for entries in [bits,values]:require([r[0] for r in entries]==sorted(set(r[0] for r in entries)),'Unordered/duplicate demand fields')
    require(all(not value&~mask for _,mask,value in bits),'Bits outside demand mask')
    return dict(node=target,signals=signals,bits=bits,values=values)
def decode_words(words,nodes):
    require(1<=nodes<=1048576 and len(words)>=8 and all(isinstance(w,int) and 0<=w<=U64 for w in words),'Invalid word stream/domain')
    m=words[:8];magic,capacity,used,count,status,version,z0,z1=m
    require(magic==MAGIC and 1<=capacity<=16777216 and used<=capacity and count<=used and status==0 and version==count+1 and z0==z1==0,'Invalid/incomplete trace metadata')
    require(len(words)==8+used,'Truncated/extra committed trace words')
    data=words[8:];cursor=0;records=[];previous=None
    while cursor<used:
        require(used-cursor>=89,'Truncated record header/result')
        h=data[cursor:cursor+8];kind,size,iteration,query,target,nroots,nunknown,npips=h
        require(kind==1 and target<nodes and nroots<=1048576 and nunknown<=nodes and npips<=1100754,'Unsupported/malformed search frame')
        r=data[cursor+8:cursor+89];path_count=r[7]
        require(r[0]<=6 and r[15]==1 and path_count<=524288 and r[8]==nunknown and r[9]==npips,'Invalid search result ABI/counts')
        expected=89+(nroots+1)//2+4*path_count+nunknown+npips
        require(size==expected and size<=used-cursor,'Wrong/truncated search payload')
        ordinal=(iteration,query);require(previous is None or ordinal>previous,'Duplicated/reordered query frame');previous=ordinal
        at=cursor+89;packed=data[at:at+(nroots+1)//2];at+=(nroots+1)//2
        roots=[(packed[i//2]>>(32*(i%2)))&U32 for i in range(nroots)]
        require(roots==sorted(set(roots)) and all(n<nodes for n in roots),'Invalid roots')
        if nroots%2:require(packed[-1]>>32==0,'Nonzero root padding')
        packed_path=data[at:at+4*path_count];at+=4*path_count
        raw_path=[lane for word in packed_path for lane in [word&U32,word>>32]]
        path=[raw_path[i:i+8] for i in range(0,len(raw_path),8)]
        require(all(p[0]<nodes and p[1]<nodes and p[7]<=1 for p in path),'Invalid path fields')
        if r[0]==0:
            require((not path and target in roots) or (path and path[0][0] in roots and path[-1][1]==target and all(a[1]==b[0] for a,b in zip(path,path[1:]))),'Discontinuous found path')
            demands=state(r[16:81],target)
        else:
            require(not path and not any(r[16:81]),'Non-found result has path/demands');demands=None
        unknown=data[at:at+nunknown];at+=nunknown;pips=data[at:at+npips];at+=npips
        require(unknown==sorted(set(unknown)) and all(n<nodes for n in unknown),'Invalid unknown-node set')
        require(pips==sorted(set(pips)),'Invalid unknown-PIP set')
        require(at==cursor+size,'Payload boundary mismatch')
        records.append(dict(iteration=iteration,query=query,target=target,result=r,roots=roots,path=path,unknown_nodes=unknown,unknown_pips=pips,demands=demands));cursor=at
    require(len(records)==count,'Wrong committed record count')
    return dict(status='search_fragment_validated',metadata=m,records=records,complete_batch=False,requires_terminal_record=True)
def decode_file(path,nodes):
    with Path(path).open('rb') as stream:
        header=stream.read(64);require(len(header)==64,'Truncated metadata')
        m=list(struct.unpack('<8Q',header));require(m[2]<=16777216 and Path(path).stat().st_size==64+8*m[2],'Invalid binary length')
        payload=stream.read();words=m+[w[0] for w in struct.iter_unpack('<Q',payload)]
    return decode_words(words,nodes)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('path',type=Path);p.add_argument('--nodes',type=int,required=True);a=p.parse_args();print(json.dumps(decode_file(a.path,a.nodes),indent=2))
