"""Decode type6 exact search frames through independent set and search readers."""
from read_search_trace import MAGIC,require,decode_words as plain
from read_trace_set_codec import decode as set_decode

def decode_words(words,nodes):
    require(len(words)>=16,'Truncated frame')
    if words[8]==1:return plain(words,nodes)
    m=words[:8]
    require(m[0]==MAGIC and 0<m[1]<=16777216 and m[2]<=m[1] and m[3:]==[1,0,2,0,0] and len(words)==8+m[2],'Invalid compressed metadata')
    f=words[8:];require(len(f)>=93 and f[0]==6 and f[1]==len(f),'Invalid compressed search header')
    _,size,iteration,query,target,nroots,nn,np,ne,nb,pe,pb=f[:12]
    result=f[12:93];path_count=result[7]
    require(nroots<=1048576 and nn<=nodes and np<=1100754 and path_count<=524288,'Invalid compressed counts')
    prefix=93+(nroots+1)//2+4*path_count;nw=(nb+7)//8;pw=(pb+7)//8
    require(size==prefix+nw+pw,'Compressed payload boundary mismatch')
    unknown=set_decode(f[prefix:prefix+nw],ne,nb,nn)
    pips=set_decode(f[prefix+nw:],pe,pb,np)
    payload=f[12:prefix]+unknown+pips
    frame=[1,8+len(payload),iteration,query,target,nroots,nn,np]+payload
    return plain([MAGIC,16777216,len(frame),1,0,2,0,0]+frame,nodes)
