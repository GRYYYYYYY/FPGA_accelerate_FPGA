"""Actual-trace LRU demand versus resident capacity; no cycle/speedup claim."""
from pathlib import Path
from collections import OrderedDict,Counter
import hashlib,json,os,struct,sys
ROOT=Path(__file__).resolve().parents[1]
RECORD=struct.Struct('<IIIBBHI')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
class Cache:
 def __init__(self,capacity):self.capacity=capacity;self.live=OrderedDict();self.backing=set();self.counts=Counter()
 def release(self,page,dirty):
  if dirty:self.counts['writebacks']+=1;self.backing.add(page)
 def access(self,page,write):
  if page in self.live:
   self.counts['hits']+=1;self.live.move_to_end(page)
   if write:self.live[page]=True
  else:
   if len(self.live)==self.capacity:self.release(*self.live.popitem(last=False))
   if page in self.backing:self.counts['refills']+=1
   self.live[page]=bool(write);self.counts['bindings']+=1
 def finish(self):
  for page,dirty in self.live.items():self.release(page,dirty)
  self.counts['transfers']=self.counts['writebacks']+self.counts['refills']
  self.counts['page_bytes']=self.counts['transfers']*1344
  return dict(self.counts)
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir()
 capture=ROOT/'results/real_field_values_20261023T024250Z';cp=capture/'manifest.json'
 assert sha(cp)=='e6eaa58c27c56125f727d01f1d9189c71e943de2e9343912ea71a38f5f374aac'
 c=json.loads(cp.read_text());data=capture/'trace.values';queries=capture/'trace.queries.jsonl'
 for p in [data,queries]:assert sha(p)==c['artifacts'][str(p)]
 dp=ROOT/'results/large_query_demand_20261023/manifest.json';assert sha(dp)=='cbc1340cf62b89ea6b00e3f1a62a8476857a5ac3c36bc0a0ca78243a16c6fbda'
 baseline=json.loads(dp.read_text());qpath=dp.parent/'queries.json';assert sha(qpath)==baseline['artifacts']['queries.json']
 reference={q['attempt']:q for q in json.loads(qpath.read_text())}
 capacities=[4,8,16,32,64,128,256,512]
 m={'status':'running','pid':os.getpid(),'capacities':capacities,'queries':[],'inputs':{str(p):sha(p) for p in [cp,data,queries,dp,qpath]},'source_sha256':sha(Path(__file__)),'scope':'LRU page demand with unbounded transaction/generation counting and no checkpoint; traces and final dirty flush preserved. Address/write census only, not field-value or RTL correctness and not measured timing. Larger capacities not implemented in RTL.'}
 (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
 def save():
  temp=out/'manifest.tmp';temp.write_text(json.dumps(m,indent=2)+'\n');temp.replace(out/'manifest.json')
 save()
 try:
  with data.open('rb') as stream:
   for line in queries.read_text().splitlines():
    q=json.loads(line);assert stream.tell()==q['byte_offset'];raw=stream.read(q['count']*20);assert len(raw)==q['count']*20
    caches=[Cache(n) for n in capacities];accesses=reads=writes=0
    for node,site,bits,field,write,reserved,hist in RECORD.iter_unpack(raw):
     assert field<5 and write in (0,1) and reserved==0
     page=node//64
     for cache in caches:cache.access(page,write)
     accesses+=1;writes+=write;reads+=1-write
    assert (accesses,reads,writes)==(q['count'],q['reads'],q['writes'])
    counts={str(cache.capacity):cache.finish() for cache in caches}
    for key in ['bindings','hits','writebacks','refills','transfers']:assert counts['4'].get(key,0)==reference[q['attempt']].get(key,0),(q['attempt'],key)
    for cache in caches:
     assert len(cache.backing)==reference[q['attempt']]['unique_backing_pages']
     counts[str(cache.capacity)]['public_commands_without_checkpoint']=accesses+2*cache.counts['bindings']+cache.counts['transfers']+3
    m['queries'].append({'attempt':q['attempt'],'accesses':accesses,'reads':reads,'writes':writes,'capacities':counts});save();print(q['attempt'],'passed',flush=True)
   assert not stream.read(1)
  assert len(m['queries'])==38 and sum(q['accesses'] for q in m['queries'])==14047736
  totals={str(n):dict(sum((Counter(q['capacities'][str(n)]) for q in m['queries']),Counter())) for n in capacities}
  for key in ['bindings','hits','writebacks','refills','transfers']:assert totals['4'].get(key,0)==baseline['totals_without_checkpoints'][key]
  assert sha(Path(__file__))==m['source_sha256']
  m.update(status='passed',totals=totals,resident_payload_bits_only={str(n):n*(64*136+64) for n in capacities});save()
  (out/'completion_audit.json').write_text(json.dumps({'status':'passed','manifest_sha256':sha(out/'manifest.json')},indent=2)+'\n');print(json.dumps(totals,indent=2))
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
