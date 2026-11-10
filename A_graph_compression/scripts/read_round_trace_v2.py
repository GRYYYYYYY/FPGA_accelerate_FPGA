#!/usr/bin/env python3
"""Independent round snapshots and exact history transition validation."""
import argparse
import json
from pathlib import Path
import struct
from read_search_trace import MAGIC, U32, U64, require

def decode_words(w):
    require(len(w)>=8, 'Missing metadata')
    m=w[:8]
    require(m[0]==MAGIC and 0<m[1]<=16777216 and m[2]<=m[1] and len(w)==8+m[2] and m[4]==0 and m[5]==m[3]+1 and m[6:]==[0,0], 'Invalid metadata')
    at=8; records=[]; pending=None
    while at<len(w):
        start=at; h=w[at:at+16]
        require(len(h)==16 and h[0]==3 and h[9:]==[0]*7, 'Invalid round header')
        _,size,iteration,phase,nodes,nets,ns,nh,ng=h[:9]
        require(phase<=1 and 0<nodes<=1048576 and 0<nets<=65536 and max(ns,nh,ng)<=65536, 'Invalid domain/counts')
        require(size==42+2*nodes+(nets+1)//2+4*ns+2*nh+2*ng and start+size<=len(w), 'Invalid frame size')
        at+=16
        def take(n):
            nonlocal at
            v=w[at:at+n];at+=n;return v
        c=take(8);r=take(8);nm=take(4);sm=take(6)
        require(c[0]==nodes and c[1]==nets and c[2]==iteration and iteration<c[3]<=U32 and 0<c[4] and c[5]==ng and c[6:]==[0,0], 'Invalid control')
        require(nm[0]==0x414e4f44454f5731 and nm[1]==nodes and nm[2]<=2097152 and nm[3]>0, 'Invalid node metadata')
        require(sm[0]==0x41534954454f5731 and sm[1]<2 and sm[2]==ns and sm[3]<2 and sm[4]==nh and sm[5]>0, 'Invalid site metadata')
        pairs=[take(2) for _ in range(nodes)];counts=[p[0] for p in pairs];history=[p[1] for p in pairs]
        require(all(v<=U32 for v in counts) and sum(counts)==nm[2], 'Invalid owner counts')
        packed=take((nets+1)//2);flags=[(packed[i//2]>>(32*(i%2)))&U32 for i in range(nets)]
        require(all(v<=1 for v in flags) and (nets%2==0 or packed[-1]>>32==0), 'Invalid completion flags')
        owners=[take(4) for _ in range(ns)];sh=[take(2) for _ in range(nh)];summaries=[take(2) for _ in range(ng)]
        require([(v[0],v[1]) for v in owners]==sorted(set((v[0],v[1]) for v in owners)), 'Unordered owners')
        grouped={}
        for key,net,mask,value in owners:
            kind=key>>32
            require(kind<=2 and net<=U32 and (kind==1 or mask==0) and (kind!=0 or value==0) and (kind!=1 or not value&~mask), 'Invalid site owner')
            grouped.setdefault(key,[]).append((mask,value))
        expected=[]
        for key,rows in grouped.items():
            kind=key>>32
            if kind==0:bad=len(rows) if len(rows)>1 else 0
            elif kind==2:bad=len(rows) if len(set(v for _,v in rows))>1 else 0
            else:
                ones=zeros=0
                for mask,value in rows:ones|=value;zeros|=mask&~value
                bad=sum(bool((value&zeros)|((mask&~value)&ones)) for mask,value in rows)
            if bad:expected.append([key,bad])
        require(summaries==expected, 'Wrong site conflicts')
        require([k for k,_ in sh]==sorted(set(k for k,_ in sh)) and all(k>>32<=2 for k,_ in sh), 'Invalid site history')
        groups=sum(v>1 for v in counts);incomplete=flags.count(0);conflict=bool(groups or ng)
        present=min(1<<min(iteration,20),c[4]);next_round=conflict and iteration+1<c[3]
        want=[0,groups,incomplete,2 if next_round else int(conflict or incomplete>0),iteration+1 if next_round else 0,min(1<<min(iteration+1,20),c[4]) if next_round else 0,int(conflict),present]
        require(r==want, 'Wrong round decision')
        record=dict(iteration=iteration,phase=phase,control=c,result=r,node_meta=nm,site_meta=sm,counts=counts,node_history=history,complete=flags,owners=owners,site_history=sh,summaries=summaries)
        if phase==0:
            require(pending is None, 'Missing post-advance record')
            if records:require(iteration==records[-1]['iteration']+1 and records[-1]['result'][3]==2, 'Invalid round sequence')
            if conflict:pending=record
        else:
            require(pending is not None, 'Post-advance without pre-state')
            p=pending
            for key in ['iteration','control','result','counts','complete','owners','summaries']:
                require(record[key]==p[key], 'Changed round invariant '+key)
            require(nm[:3]==p['node_meta'][:3] and nm[3]==p['node_meta'][3]+1, 'Wrong node version')
            require(history==[v+max(0,count-1) for v,count in zip(p['node_history'],counts)] and all(v<=U64 for v in history), 'Wrong node history advance')
            want_sh=dict(p['site_history'])
            for key,bad in summaries:want_sh[key]=want_sh.get(key,0)+bad-1
            require(sh==[[k,v] for k,v in sorted(want_sh.items())] and all(v<=U64 for _,v in sh), 'Wrong site history advance')
            require(sm[1:3]==p['site_meta'][1:3] and sm[3]==1-p['site_meta'][3] and sm[5]==p['site_meta'][5]+1, 'Wrong site bank/version')
            pending=None
        require(at==start+size, 'Boundary mismatch');records.append(record)
    require(len(records)==m[3] and pending is None, 'Incomplete round sequence')
    return dict(status='round_snapshots_and_history_transitions_validated',records=records,complete_batch=False,requires_terminal_record=True)

def decode_file(path):
    raw=Path(path).read_bytes();require(len(raw)%8==0,'Unaligned bytes')
    return decode_words(list(struct.unpack('<%dQ'%(len(raw)//8),raw)))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('path',type=Path);a=p.parse_args();print(json.dumps(decode_file(a.path),indent=2))
