"""Rebuild oracle from CPU records and replay each actual AXI byte."""
from pathlib import Path
import json,sys,mmap,struct
from run_checkpoint_authority import sha,ROOT
from audit_route_fault_axi import replay

def oracle(f,nodes):
 extra={}
 for n,t,r in struct.iter_unpack('<III',(Path(f['cpu'])/'initial_overflow.u32').read_bytes()):
  if n in nodes:extra.setdefault(n,{})[t]=r
 result={}
 with(Path(f['cpu'])/'initial_nodes.u32').open('rb')as fp,mmap.mmap(fp.fileno(),0,access=mmap.ACCESS_READ)as mm:
  for n in nodes:
   row=struct.unpack_from('<11I',mm,n*44);o=dict(extra.get(n,{}))
   if row[6]!=0xffffffff:o[row[6]]=row[7]
   assert len(o)==row[8];result[n]=o
 return result,extra

def common(out):
 m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h['sha256']
 base=ROOT/'results/route_checkpoint_normal_v2/sources'
 assert sha(out/'sources/owner_state_store.sv')==sha(base/'access_owner_v3_20261024/owners/owner_state_store.sv')
 assert sha(out/'sources/axi_file_memory.sv')==sha(base/'axi_file_memory.sv')
 assert all(c['exit_code']==0 for c in m['build'])
 for name,cm in m['cases'].items():
  d=out/name;f=cm['fixture'];assert cm['status']=='passed' and all(c['exit_code']==0 for c in cm['commands'])
  for n,h in cm['artifacts'].items():assert sha(d/n)==h
  for n,h in f['artifacts'].items():assert sha(d/n)==h
  assert sha(Path(f['codec'])/'source_bound_audit.json')==f['codec_audit_sha256']
  assert sha(Path(f['cpu'])/'source_bound_audit.json')==f['cpu_audit_sha256']
  for a,b in [('primary.bin','owners.bin'),('pool.bin','owner_pool.bin'),('allocator.bin','owner_allocator.bin')]:assert sha(d/a)==sha(Path(f['codec'])/b)
  log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log
 return m

def regions(d,f):return [(f[k],d/n)for k,n in [('primary_base','primary.bin'),('pool_base','pool.bin'),('allocator_base','allocator.bin')]]

def main():
 out=Path(sys.argv[1]).resolve();m=common(out);cases={}
 for name,cm in m['cases'].items():
  d=out/name;f=cm['fixture'];v=[t.split()for t in(d/'vectors.txt').read_text().splitlines()];nodes={int(t[1])for t in v if int(t[1])<f['nodes']};owners,extra=oracle(f,nodes)
  expected=[]
  for t in v:
   i,n,net=map(int,t[:3]);design=int(t[3],16);cp=int(t[4]);g=int(t[5],16)
   st=1 if (design,cp,g)!=(f['design'],f['checkpoint'],f['generation'])else 2 if n>=f['nodes']or net>=f['nets']else 0
   refs=owners[n].get(net,0)if not st else 0;occ=len(owners[n])if not st else 0;k=len(extra.get(n,{}));reads=2+k*(k+1)//2 if not st else 0
   assert list(map(int,t[6:]))==[st,refs,occ,reads];expected.append([i,st,refs,occ,reads])
  refs=owners[0].get(0,0);occ=len(owners[0]);k=len(extra.get(0,{}));r=2+k*(k+1)//2
  expected += [[0x70000000,9,0,0,1],[0x70000001,0,refs,occ,r],[0x70000002,12,0,0,1],[0x70000003,0,refs,occ,r]]
  rows=[t.split()for t in(d/'events.txt').read_text().splitlines()];accepted=[t for t in rows if t[0]=='A'];assert len(accepted)==len(expected)
  for a,t in zip(accepted,v):assert [int(a[2]),int(a[3]),int(a[4]),int(a[5],16),int(a[6]),int(a[7],16)]==[int(t[0]),int(t[1]),int(t[2]),int(t[3],16),int(t[4]),int(t[5],16)]
  for a,cookie in zip(accepted[len(v):],range(0x70000000,0x70000004)):assert [int(a[2]),int(a[3]),int(a[4]),int(a[5],16),int(a[6]),int(a[7],16)]==[cookie,0,0,f['design'],f['checkpoint'],f['generation']]
  replies=[t for t in rows if t[0]=='R'];assert len(replies)==len(expected)
  for t,e in zip(replies,expected):
   assert list(map(int,t[2:7]))==e
   assert (int(t[7],16),int(t[8]),int(t[9],16))==(f['design'],f['checkpoint'],f['generation'])
  cfg=[t for t in rows if t[0]=='CFG'];assert [int(t[3])for t in cfg]==[1,2,3,0,1,0,0]and [int(t[4])for t in cfg]==[0,0,0,0,0,1,1]
  arm=[t for t in rows if t[0]=='ARM'];reset=[t for t in rows if t[0]=='RESET'];assert len(arm)==2 and len(reset)==5
  for a,cookie in zip(arm,[0x70000000,0x70000002]):
   reply=next(t for t in replies if int(t[2])==cookie);assert int(a[1])>int(reply[1])and int(a[2],16)==f['generation']
  axi=replay(d/'snapshot_axi.txt',regions(d,f));assert axi['error_read_beats']==1 and axi['read_transactions']==sum(e[4]for e in expected)
  cases[name]={'cpu_oracle_replies':len(expected),'vector_requests':len(v),'overflow_queries':f['overflow_queries'],'cfg_checks':7,'private_resets':5,'safe_rearms':2,'axi':axi,'result':cm['result']}
 audit={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'sources':{n:sha(out/'sources'/n)for n in m['sources']},'cases':cases,'scope':m['scope'],'auditor_sha256':sha(Path(__file__))}
 (out/'source_bound_audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
if __name__=='__main__':main()
