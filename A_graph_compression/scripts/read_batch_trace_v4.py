#!/usr/bin/env python3
"""Validate mixed plain/compressed exact traces with strengthened inheritance checks.

Seeded ledgers require external initial-state proof and remain incomplete_batch.
Error terminals are retained for diagnosis, not accepted as validated routing.
"""
import argparse
import json
from pathlib import Path
import struct
from read_search_trace import MAGIC, U32, require
from read_compressed_search_trace import decode_words as search_decode
from read_batch_trace_v2 import strengthen
from read_net_trace import decode_words as net_decode
from read_round_trace_v2 import decode_words as round_decode

def fragment(frames):
    payload=[x for f in frames for x in f]
    return [MAGIC,16777216,len(payload),len(frames),0,len(frames)+1,0,0]+payload

def _decode_words(w,nodes):
    require(len(w)>=8 and 0<nodes<=1048576,'Invalid domain/metadata')
    m=w[:8]
    require(m[0]==MAGIC and 0<m[1]<=16777216 and m[2]<=m[1] and m[4]==0 and m[5]==m[3]+1 and m[6:]==[0,0] and len(w)==8+m[2],'Invalid/incomplete metadata')
    frames=[];at=8
    while at<len(w):
        require(at+2<=len(w),'Truncated header');size=w[at+1]
        require(size>=8 and at+size<=len(w),'Truncated frame')
        frames.append(w[at:at+size]);at+=size
    require(len(frames)==m[3] and len(frames)>=2,'Wrong frame count')
    begin=frames[0];terminal=frames[-1]
    require(begin[0]==4 and len(begin)>=24 and begin[2]==1 and begin[5:8]==[0]*3,'Missing/invalid begin')
    c=begin[8:24];nets,ns=begin[3:5]
    require(0<nets<=65536 and ns<=4194304 and c[2]==nets and c[3]==ns and c[6]<=1 and c[7:]==[0]*9,'Invalid schedule header')
    require(c[0]>0 and 0<c[1]<=U32 and 16<=c[4]<=4194304 and 0<c[5]<=200000,'Invalid batch control')
    require(len(begin)==24+4*nets+(ns+1)//2,'Wrong begin size')
    table=[begin[i:i+4] for i in range(24,24+4*nets,4)];packed=begin[24+4*nets:]
    sinks=[(packed[i//2]>>(32*(i%2)))&U32 for i in range(ns)]
    require(ns%2==0 or packed[-1]>>32==0,'Nonzero sink padding')
    require(len(set(q[0] for q in table))==nets,'Duplicate net IDs')
    for net,source,first,count in table:
        require(net<=U32 and source<nodes and first<=ns and count<=1048576 and count<=ns-first,'Invalid query')
        part=sinks[first:first+count]
        require(part==sorted(part) and all(v<nodes for v in part),'Invalid sink sequence')
    require(terminal[:8]==[5,20,1,0,0,0,0,0] and len(terminal)==20,'Missing/invalid terminal')
    tr=terminal[8:]
    # Early errors can occur before the immutable schedule itself is valid. They
    # need a separate failure-state protocol; this success reader rejects them.
    require(tr[0:3]==[0,7,0],'Routing error/unverified terminal')
    cursor=1;rounds=net_calls=searches=found=advances=0;previous_round=None
    net_records=[];search_records=[];round_records=[];routes={};site_routes={};history=[0]*nodes
    while cursor<len(frames)-1:
        iteration=rounds;flags=[]
        for q,(net,source,first,count) in enumerate(table):
            roots={source};paths=[];last_demands=[0]*65;net_found=0
            for sink_index,target in enumerate(sinks[first:first+count]):
                require(cursor<len(frames)-1 and frames[cursor][0] in [1,6],'Missing scheduled search')
                r=search_decode(fragment([frames[cursor]]),nodes)['records'][0];cursor+=1
                require((r['iteration'],r['query'],r['target'])==(iteration,(q<<32)|sink_index,target),'Search/schedule mismatch')
                require(r['roots']==sorted(roots),'Wrong search roots')
                require(r['result'][0]<5,'Failed search control')
                if r['result'][0]==0:
                    net_found+=1;paths+=r['path']
                    for p in r['path']:roots.update(p[:2])
                    last_demands=r['result'][16:81].copy();last_demands[0]&=~U32
                search_records.append(r)
            require(cursor<len(frames)-1 and frames[cursor][0]==2,'Missing net snapshot')
            nr=net_decode(fragment([frames[cursor]]),nodes)['records'][0];cursor+=1
            require((nr['iteration'],nr['query'],nr['net'])==(iteration,q,net),'Net/schedule mismatch')
            require(nr['roots']==sorted(roots) and nr['edges']==paths and nr['demand_words']==last_demands,'Net/search state mismatch')
            complete=int(all(v in roots for v in sinks[first:first+count]))
            require(nr['result'][3:7]==[count,net_found,complete,len(roots)],'Wrong net totals')
            routes[net]=roots;site_routes[net]=nr['site_owners']
            if c[6]:
                counts=[sum(n in route for route in routes.values()) for n in nr['roots']]
                require(nr['occupancy']==[[cnt,history[n]] for n,cnt in zip(nr['roots'],counts)],'Net occupancy/history mismatch')
            flags.append(complete);net_calls+=1;searches+=count;found+=net_found;net_records.append(nr)
        require(cursor<len(frames)-1 and frames[cursor][0]==3 and frames[cursor][3]==0,'Missing pre-round snapshot')
        pair=[frames[cursor]];cursor+=1
        if cursor<len(frames)-1 and frames[cursor][0]==3 and frames[cursor][3]==1:
            pair.append(frames[cursor]);cursor+=1
        rr=round_decode(fragment(pair))['records'];pre=rr[0];post=rr[-1]
        require(pre['iteration']==iteration and pre['control']==[nodes,nets,iteration,c[1],c[0],len(pre['summaries']),0,0] and pre['complete']==flags,'Round/schedule mismatch')
        if previous_round:
            require(previous_round['result'][3]==2,'Extra round after terminal decision')
            require(pre['node_history']==previous_round['node_history'] and pre['site_history']==previous_round['site_history'],'History changed during net transactions')
        if c[6]:
            require(pre['counts']==[sum(n in route for route in routes.values()) for n in range(nodes)],'Round node ledger mismatch')
            expected=sorted([row for rows in site_routes.values() for row in rows],key=lambda row:(row[0],row[1]))
            require(pre['owners']==expected,'Round site ledger mismatch')
            if iteration==0:require(pre['node_history']==[0]*nodes and not pre['site_history'],'Nonzero reset histories')
        rounds+=1;advances+=pre['result'][6];history=post['node_history'];previous_round=post;round_records+=rr
    require(cursor==len(frames)-1 and previous_round is not None and previous_round['result'][3]!=2,'Missing final round decision')
    r=previous_round['result']
    expected=[0,7,0,rounds,net_calls,searches,found,int(r[3]==0),r[2],r[1],len(previous_round['summaries']),advances]
    require(tr==expected,'Terminal totals mismatch')
    return dict(status='mixed_batch_trace_validated_initial_state_proof_required' if not c[6] else 'mixed_reset_batch_trace_validated',complete_batch=bool(c[6]),initial_state_verified=bool(c[6]),metadata=m,batch_control=c,terminal=tr,searches=search_records,nets=net_records,rounds=round_records)

def decode_words(words,nodes):return strengthen(_decode_words(words,nodes))

def decode_file(path,nodes):
    raw=Path(path).read_bytes();require(len(raw)%8==0,'Unaligned byte stream')
    return decode_words(list(struct.unpack('<%dQ'%(len(raw)//8),raw)),nodes)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('path',type=Path);p.add_argument('--nodes',type=int,required=True);a=p.parse_args();print(json.dumps(decode_file(a.path,a.nodes),indent=2))
