"""Independent semantic replay, complete AXI bytes/B-order transcript and backing-file audit."""
from pathlib import Path
import hashlib,json,re,struct
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/design_store_v3_20261024';m=read(out/'manifest.json');assert m['status']=='passed'
 graph=Path(m['graph']);gm=read(graph/'manifest.json');gate=read(graph/'source_bound_audit.json')
 assert gate['status']=='passed'and gate['manifest_sha256']==m['graph_manifest_sha256']==sha(graph/'manifest.json')
 assert sha(graph/'source_bound_audit.json')==m['graph_gate_sha256']
 for name,digest in m['graph_artifacts'].items():assert sha(graph/name)==digest==gm['artifacts'][name]
 for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']==sha(Path(spec['path']))
 for name,digest in m['oracle'].items():assert sha(out/name)==digest
 assert all(x['exit_code']==0 for x in m['commands'])
 offsets=(graph/'offsets.u32le').read_bytes();n=len(offsets)//4-1;coverage=read(out/'coverage.json');assert n==coverage['nodes']
 def degree(node):a,b=struct.unpack_from('<II',offsets,node*4);return b-a
 rows=[list(map(int,line.split()))for line in (out/'vectors.txt').read_text().splitlines()]
 size=((n*16+63)//64)*64;assert size==coverage['backing_bytes'];zero_sha=hashlib.sha256(bytes(size)).hexdigest()
 results={}
 for case,cm in m['cases'].items():
  assert cm['status']=='passed'and all(x['exit_code']==0 for x in cm['commands'])
  assert cm['initial_memory_sha256']==zero_sha
  d=out/case
  for name,digest in cm['artifacts'].items():assert sha(d/name)==digest
  log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log and log.count(cm['result'])==1
  counts={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])}
  assert counts['AR']==counts['R']and counts['AW']==counts['W']==counts['B']
  assert counts['awfirst']>0 and counts['wfirst']>0 and counts['simultaneous']>0
  assert sum(counts[k]for k in ('awfirst','wfirst','simultaneous'))==counts['AW']
  mem=bytearray(size)
  if case=='faults':
   assert (counts['faults'],counts['checks'],counts['configurations'],counts['AR'],counts['AW'])==(17,35,24,31,5)
   # Model intentionally commits physical bytes even when returning an erroneous B.
   for node,record in {244:(1,0,0,0),245:(4,1,1,0),248:(1,0,0,0),249:(4,1,1,0),300:(4,0,0,0)}.items():struct.pack_into('<4I',mem,node*16,*record)
   assert (d/'axi_trace.txt').stat().st_size==0
  else:
   subset=rows[:200]if case=='pilot'else rows
   active=False;claim_owner=claim_node=claim_count=keep=0;last=-1;reads=writes=hits=publishes=empty=0;parents=set();all_lanes=set()
   with (d/'axi_trace.txt').open()as trace:
    for cookie,row in enumerate(subset,2):
     op,node,arg,owner=row[:4];status=0;reply=(0,0,0);ar=aw=0
     bad=op>6 or node>=n or (op==1 and arg>32)or(op not in(1,4)and arg!=0)
     denied=(op==1 and owner==0)or(op!=1 and owner!=(claim_owner if active else 0))or(op in(4,5)and(not active or node!=claim_node))or(op==6 and active)
     if bad:status=2
     elif op==1 and active:status=3
     elif denied:status=4
     elif op==4:
      if arg>=claim_count or arg<=last:status=2
      else:keep|=1<<arg;last=arg;reply=(0,claim_count,keep)
     else:
      ar=1;reads+=1;address=0x31fffff000+(node//4)*64;start=(node//4)*64
      pre=mem[start:start+64];assert trace.readline().strip()==f'A {cookie} {address:016x} {int.from_bytes(pre,"little"):0128x}'
      flags,raw_count,mask,reserved=struct.unpack_from('<4I',mem,node*16);assert reserved==0
      all_lanes.add(node%4)
      new=(flags,raw_count,mask)
      if op==1:
       if node==coverage['synthetic_degree32_parent']:assert arg==32
       else:assert arg==degree(node);parents.add(node)
       if flags&4:assert raw_count==arg;hits+=1
       else:active=True;claim_owner=owner;claim_node=node;claim_count=arg;keep=0;last=-1
      elif op in(2,3,6):
       bit={2:1,3:2,6:8}[op];new=(flags|bit,raw_count,mask);aw=int(new[0]!=flags)
      elif op==5:
       assert active and not flags&4;new=(flags|4,claim_count,keep);aw=1;publishes+=1;empty+=keep==0
      reply=new
      if aw:
       writes+=1;record=struct.pack('<4I',*new,0);payload=int.from_bytes(record,'little')<<((node%4)*128);strb=65535<<((node%4)*16)
       assert trace.readline().strip()==f'W {cookie} {address:016x} {strb:016x} {payload:0128x}'
       assert trace.readline().strip()==f'B {cookie} 0 0' # must precede retirement and claim release
       mem[node*16:node*16+16]=record
       if op==5:active=False;claim_owner=claim_node=claim_count=keep=0
     claims=(int(active),claim_owner,claim_node,claim_count,keep)
     expected=[status,*reply,*claims,ar,aw]
     assert row[4:]==expected,(cookie,row,expected)
     assert trace.readline().strip()=='R '+' '.join(map(str,[cookie,status,*reply,*claims]))
    assert trace.read()==''
   assert counts['commands']==len(subset)and counts['AR']==reads+(case=='full')and counts['AW']==writes
   assert counts['checks']==len(subset)+(2 if case=='full'else 1)and counts['faults']==0
   if case=='full':
    assert not active and all_lanes==set(range(4))
    assert (reads,writes,hits,empty,len(parents))==(coverage['reads'],coverage['writes'],coverage['cache_hits'],coverage['empty_published'],coverage['real_parents'])
    assert len(rows)==coverage['commands']and sha(out/'expected_memory.bin')==hashlib.sha256(mem).hexdigest()
   counts.update(audited_reads=reads,audited_writes=writes,cache_hits=hits,publishes=publishes,empty_published=empty)
  digest=hashlib.sha256(mem).hexdigest();assert sha(d/'memory.bin')==digest
  results[case]={**counts,'entire_backing_sha256':digest}
 # Preserve and bind the initial compile failure and both subsequent tested sources.
 old=ROOT/'results/design_store_20261024';v2=ROOT/'results/design_store_v2_20261024'
 assert read(old/'manifest.json')['status']=='failed'and "keyword 'config'"in (old/'pilot/compile.stdout.log').read_text()
 assert read(v2/'manifest.json')['status']=='passed'
 for name in ['design_state_store.sv','make_vectors.py']:assert sha(old/'sources'/name)==sha(v2/'sources'/name)==sha(out/'sources'/name)
 oldtb=(old/'sources/tb_design_state_store.sv').read_text();v2tb=(v2/'sources/tb_design_state_store.sv').read_text()
 assert re.sub(r'\bconfig\b','configure_store',oldtb)==v2tb
 expectedtb=v2tb.replace('if(m_bvalid&&m_bready)begin bp<=0;', 'if(m_bvalid&&m_bready)begin if(log_enabled)$fdisplay(fd_trace,"B %0d %0d %0d",req_cookie,m_bid,m_bresp);bp<=0;').replace('if(req_op==5&&claim_active&&bp&&!m_bvalid&&rsp_valid)','if(req_op==5&&(aw||wd||bp)&&!m_bvalid&&(!claim_active||rsp_valid))')
 assert expectedtb==(out/'sources/tb_design_state_store.sv').read_text()
 dependencies={str(p):sha(p)for p in [old/'manifest.json',old/'pilot/compile.stdout.log',v2/'manifest.json']}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'coverage':coverage,'cases':results,'prior_evidence':dependencies,'scope':m['scope'],'limitations':['Backing starts zero once per design, not per query. No device uploader yet.','32 raw positions maximum; larger degree rejected, exact real graph max18.','External exclusive writer and immutable raw graph required. Cold reset during failed claim cannot safely retry filtering in place.','No whole-route, graph/children/pager integration, or board performance result.']}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
