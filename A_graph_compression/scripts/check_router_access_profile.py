#!/usr/bin/env python3
"""Independently verify full routing and canonical-node access counters."""
import argparse
import json
import mmap
from pathlib import Path
import struct
from check_vitis_kernel import digest,require
from check_native_site_runtime import METRICS


def image_degrees(path):
    with Path(path).open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        require(data[:8]==b'AGRAPH01' and struct.unpack_from('<III',data,8)==(1,1,0x01020304),'Expected compact AGRAPH01')
        count=struct.unpack_from('<I',data,20)[0];sections={}
        for i in range(count):
            name,offset,size,n,width=struct.unpack_from('<16sQQII',data,24+40*i)
            require(offset+size<=len(data) and size==n*width,'Bad section bounds')
            name=name.rstrip(b'\0').decode();require(name not in sections,'Duplicate section');sections[name]=(offset,n,width)
        def record(name,index,fmt):
            offset,n,width=sections[name]
            require(0<=index<n and struct.calcsize(fmt)==width,'Bad degree record access')
            return struct.unpack_from(fmt,data,offset+index*width)
        result=[]
        for node in range(sections['NODE'][1]):
            row=record('NODE',node,'<IIIi')[3]
            if row==-1:result.append(-1);continue
            require(row>=0,'Invalid known row')
            tid,rs,rc,add_start,add_count,ps,pc=record('INSTANCE',row,'<iIIIIII')
            require(rs+rc<=sections['REMOVE'][1] and add_start+add_count<=sections['ADD'][1]
                    and ps+pc<=sections['PATCH'][1],'Invalid instance span')
            if tid>=0:
                start=record('TPL_OFF',tid,'<Q')[0];end=record('TPL_OFF',tid+1,'<Q')[0]
                require(start<=end<=sections['RULE'][1] and rc<=end-start,'Invalid template span')
                result.append(end-start-rc+add_count)
            else:
                require(tid==-1 and rc==0 and pc==0,'Invalid fallback instance');result.append(add_count)
        return result


def read_profile(path,degrees,batch,hits,misses,expanded):
    totals={'visits':0,'hits':0,'misses':0,'unknown':0,'visited_nodes':0,
            'edges_returned':0,'edges_decoded_on_misses':0}
    strata={};rows=[]
    with Path(path).open() as f:
        require(f.readline().rstrip('\n')==f'ROUTER_ACCESS_V1\t{len(degrees)}\t{batch}','Invalid access header')
        for node,degree in enumerate(degrees):
            line=f.readline();require(bool(line),'Missing canonical node row')
            fields=line.rstrip('\n').split('\t');require(len(fields)==6,'Wrong access field count')
            values=[int(value) for value in fields];n,visits,hit,miss,unknown,observed=values
            require(n==node and all(0<=x<=2**64-1 for x in values[1:5]),'Invalid node/count')
            require(visits==hit+miss+unknown,'Access count conservation failed')
            require(observed==(degree if visits else -2),'Degree differs from packed image')
            if degree<0:require(hit==miss==0,'Unknown adjacency entered cache')
            else:require(unknown==0,'Known adjacency reported unknown')
            label='unknown' if degree<0 else ('empty' if degree==0 else next(label for lo,hi,label in
                [(1,2,'degree_1_2'),(3,4,'degree_3_4'),(5,8,'degree_5_8'),(9,63,'degree_9_63'),
                 (64,127,'degree_64_127'),(128,255,'degree_128_255'),(256,511,'degree_256_511'),
                 (512,1024,'degree_512_1024'),(1025,2**64-1,'degree_above1024')] if lo<=degree<=hi))
            s=strata.setdefault(label,{'population_nodes':0,'visited_nodes':0,'visits':0,'hits':0,'misses':0,'unknown':0,'edges_returned':0,'edges_decoded_on_misses':0})
            s['population_nodes']+=1
            local={'visits':visits,'hits':hit,'misses':miss,'unknown':unknown,'visited_nodes':int(visits>0),
                   'edges_returned':max(degree,0)*(hit+miss),'edges_decoded_on_misses':max(degree,0)*miss}
            for key,value in local.items():totals[key]+=value;s[key]+=value
            if visits:rows.append({'node':node,'degree':degree,'visits':visits,'hits':hit,'misses':miss,'unknown':unknown})
        require(f.read()=='','Trailing access data')
    require(totals['hits']==hits and totals['misses']==misses,'Access counts differ from native counters')
    require(hits+misses==expanded,'Known visits differ from all recorded search expansions')
    return {'totals':totals,'strata':strata,
            'top_nodes_by_visits':sorted(rows,key=lambda r:(-r['visits'],r['node']))[:32],
            'top_nodes_by_misses':sorted(rows,key=lambda r:(-r['misses'],r['node']))[:32]}


def audit(bundle):
    pp=bundle/'plan.json';plan=json.loads(pp.read_text())
    for path,sha in plan['files'].items():require(digest(path)==sha,'Frozen access input changed: '+path)
    rp=bundle/'receipt.json';receipt=json.loads(rp.read_text())
    raw_path=bundle/'router.raw.json';log=bundle/'router.log';submission_path=bundle/'submission.json'
    submission=json.loads(submission_path.read_text());inp=plan['inputs']
    command=[plan['binary'],inp['image'],inp['fixture'],inp['sites'],'4096','80','200000','8','direct',str(bundle/'access')]
    require(submission['command']==command and submission['cpu']==123 and submission['owner_pid']==plan['owner_pid'],'Access submission changed')
    require(receipt['exit_code']==0 and receipt['raw_sha256']==digest(raw_path) and receipt['log_sha256']==digest(log),'Access execution failed or evidence changed')
    reference=json.loads(Path(plan['reference']).read_text());expected={k:v for k,v in reference.items() if k not in METRICS}
    require(reference['status']=='routed' and len(reference['routes'])==1062,'Incomplete reference')
    raw=json.loads(raw_path.read_text());require(raw['execution']=='direct' and len(raw['batches'])==2,'Incomplete access workload')
    degrees=image_degrees(inp['image']);require(len(degrees)==274732,'Unexpected canonical node domain')
    profiles=[];files={str(p):digest(p) for p in [pp,rp,raw_path,log,submission_path,Path(__file__).resolve()]}
    for index,batch in enumerate(raw['batches']):
        require({k:v for k,v in batch.items() if k not in METRICS}==expected,'Full route/search/site semantics differ')
        expanded=sum(c['expanded'] for round in batch['iterations'] for connections in round['connections'] for c in connections)
        path=bundle/f'access.batch_{index}.tsv'
        require(digest(path)==receipt['profiles'][str(index)],'Access profile hash mismatch')
        profiles.append(read_profile(path,degrees,index,batch['cache_hits'],batch['cache_misses'],expanded));files[str(path)]=digest(path)
    return {'status':'two_full_router_batches_and_canonical_access_profiles_independently_verified',
            'files':files,'profiles':profiles,'node_count':len(degrees),'limitations':plan['limitations']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();report=audit(a.bundle.resolve())
    with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'profiles':report['profiles']}))


if __name__=='__main__':main()
