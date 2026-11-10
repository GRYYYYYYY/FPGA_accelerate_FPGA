"""Actual snapshot/live AXI replay and independent CPU owner-map equivalence."""
from pathlib import Path
import json,sys,struct
from audit_checkpoint_authority import common,oracle,regions,sha,ROOT
from audit_route_fault_axi import replay

def decode(primary,pool,n,capacity):
 key,packed,head,rsv=struct.unpack_from('<4I',primary,n*16);assert rsv==0
 owners={key-1:packed&65535}if key else {};seen=set()
 while head:
  idx=head-1;assert idx<capacity and idx not in seen;seen.add(idx)
  net,refs,head,pad=struct.unpack_from('<4I',pool,idx*16);assert net and refs and not pad and net-1 not in owners;owners[net-1]=refs
 assert len(owners)==packed>>16 and all(0<r<=65535 for r in owners.values());return owners,seen

def unchanged_except(a,b,indices,width=16):
 assert len(a)==len(b);start=0
 for idx in sorted(indices):
  off=idx*width;assert a[start:off]==b[start:off];start=off+width
 assert a[start:]==b[start:]

def main():
 out=Path(sys.argv[1]).resolve();m=common(out);cases={}
 assert sha(out/'sources/recovery_coordinator.sv')==sha(ROOT/'results/recovery_retry_normal_v1/sources/recovery_coordinator.sv')
 for name,cm in m['cases'].items():
  d=out/name;f=cm['fixture'];mut=cm['mutations'];dirty=len(mut);owners,extra=oracle(f,{x['node']for x in mut})
  expected=[]
  for x in mut:
   o=owners[x['node']];before=o.get(x['net'],0);after=before+(1 if x['op']==1 else -1);occ=len(o);ao=occ+int(before==0 and x['op']==1)-int(before==1 and x['op']==2)
   assert [x[k]for k in ['before_refs','before_occupancy','after_refs','after_occupancy']]==[before,occ,after,ao]
   expected.append((x['op'],x['node'],x['net'],after,ao))
  rows=[t.split()for t in(d/'events.txt').read_text().splitlines()];js=[t for t in rows if t[0]=='J'];hs=[t for t in rows if t[0]=='H'];hbs=[t for t in rows if t[0]=='HB']
  assert len(js)==dirty and len(hs)==len(hbs)==2*dirty
  for j,h,b,e in zip(js,hs[:dirty],hbs[:dirty],expected):
   op,n,t,r,o=e;assert list(map(int,j[2:]))==[n,t,op]and list(map(int,h[2:]))==[op,n,t]and int(j[1])<int(h[1])<int(b[1]);assert list(map(int,b[2:]))==[0,r,o]
  for h,b,x in zip(hs[dirty:],hbs[dirty:],mut):assert list(map(int,h[2:]))==[0,x['node'],x['net']]and list(map(int,b[2:]))==[0,x['before_refs'],x['before_occupancy']]
  kd=[list(map(int,t[2:]))for t in rows if t[0]=='KD'];assert kd==[[0,6,0,dirty],[1,0,dirty,0]]
  reset=[t for t in rows if t[0]=='RESET'];soft=[t for t in rows if t[0]=='SOFT'];assert len(reset)==2 and len(soft)==1 and all(int(t[2])==dirty and int(t[3],16)==f['generation']for t in reset+soft)
  first_done=next(int(t[1])for t in rows if t[0]=='KD');assert first_done<int(soft[0][1])<int(reset[1][1]);assert len([t for t in rows if t[0]=='LABELS_MOCK'])==1
  aa=[t for t in rows if t[0]=='AK'];ab=[t for t in rows if t[0]=='AB'];assert len(aa)==len(ab)==1+2*dirty
  for i,(a,b)in enumerate(zip(aa,ab)):
   n,t=int(a[3]),int(a[4]);assert int(a[1])<int(b[1])and int(a[6],16)==int(b[5],16)==f['generation']
   assert int(a[2])==(1 if i>dirty else 0)
   assert list(map(int,b[2:5]))==([9,0,0]if i==0 else[0,owners[n].get(t,0),len(owners[n])])
  assert [(int(a[3]),int(a[4]))for a in aa[1:dirty+1]]==[(x['node'],x['net'])for x in mut]
  assert [(int(a[3]),int(a[4]))for a in aa[dirty+1:]]==[(x['node'],x['net'])for x in mut]
  snap=replay(d/'snapshot_axi.txt',regions(d,f));assert snap['error_read_beats']==1 and snap['read_transactions']==1+2*sum(2+len(extra.get(x['node'],{}))*(len(extra.get(x['node'],{}))+1)//2 for x in mut)
  p=(d/'primary.bin').read_bytes();pool=(d/'pool.bin').read_bytes();allocator=(d/'allocator.bin').read_bytes();initial=p+pool+allocator;live=(d/'live.bin').read_bytes();assert len(live)==len(initial)
  ax=replay(d/'live_axi.txt',[(0xa1fffff000,initial)],d/'live.bin');assert ax['error_read_beats']==ax['error_write_replies']==0
  fp=live[:len(p)];fpool=live[len(p):len(p)+len(pool)];fa=live[-64:];assert fa==allocator
  used=set()
  for n in owners:
   old,os=decode(p,pool,n,f['capacity']);new,ns=decode(fp,fpool,n,f['capacity']);assert old==new==owners[n];assert not used&ns;used|=ns|os
  unchanged_except(p,fp,set(owners));unchanged_except(pool,fpool,used)
  assert all(t[0]in ['J','H','HB','AK','AB','O','OB','RESET','SOFT','LABELS_MOCK','KD']for t in rows)
  cases[name]={'dirty_keys':dirty,'failed_attempt_status':6,'journal_retained':dirty,'retry_corrected':dirty,'journal_final':0,'authority_queries':len(aa),'snapshot_axi':snap,'live_axi':ax,'complete_owner_semantics_restored':True,'untouched_primary_pool_bytes_identical':True,'allocator_identical':True,'live_byte_identical':live==initial,'generation':f['generation'],'labels_completion':'mock','result':cm['result']}
 audit={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'sources':{n:sha(out/'sources'/n)for n in m['sources']},'cases':cases,'scope':m['scope'],'auditor_sha256':sha(Path(__file__))}
 (out/'source_bound_audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
if __name__=='__main__':main()
