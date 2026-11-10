"""Independent metadata transaction/lease/journal oracle and native AXI replay."""
from pathlib import Path
from collections import Counter,defaultdict
import json,sys,struct,importlib.util
from run_checkpoint_authority import ROOT,sha
from verify_rtl_bundle import verify
from audit_route_fault_axi import replay

def main():
 p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
 for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256']
 ns={'__file__':str(ROOT/'hardware/variants/checkpoint_stage_v1/build.py'),'__name__':'frozen_stage'};exec(compile((p/'sources/build.py').read_text(),'stage_build.py','exec'),ns)
 ns['BASE']=Path('/tmp/B_state_residency_offer_20261025/cold_axi_fixed_v1/sources')
 for n,s in ns['make']().items():assert s==(p/'sources'/n).read_text()
 ns={'__file__':str(p/'sources/build_tb.py'),'__name__':'frozen_joint_tb'};exec(compile((p/'sources/build_tb.py').read_text(),'joint_tb.py','exec'),ns);ns['HERE']=p/'sources';assert ns['make']()==(p/'sources/tb_joint.sv').read_text()
 ref=Path('/tmp/B_state_residency_offer_20261025/authority_rotate_v6/sources')
 for n in ['checkpoint_authority_reader.sv','owner_state_store.sv','checkpoint_authority_rotator.sv','axi_file_memory.sv']:assert sha(p/'sources'/n)==sha(ref/n)
 assert sha(p/'sources/checkpoint_lease_guard.sv')==sha(Path('/tmp/B_state_residency_offer_20261025/cold_axi_fixed_v1/sources/checkpoint_lease_guard.sv'))
 bundle=Path(m['bundle']);mf=verify(bundle);assert sha(bundle/'manifest.json')==m['bundle_manifest_sha256'];initial=Path(m['initial']);old=(initial/'owners.bin').read_bytes()+(initial/'owner_allocator.bin').read_bytes();warm=(bundle/'owner_primary.bin').read_bytes()+(bundle/'owner_allocator.bin').read_bytes()
 assert (p/'old.bin').read_bytes()==old and (p/'warm.bin').read_bytes()==warm and sha(p/'old.bin')==m['old_sha256']and sha(p/'warm.bin')==m['warm_sha256']
 delta=set(struct.iter_unpack('<2I',(bundle/'journal_absorbed.u32').read_bytes()));expected=bytearray(old)
 for n,net in delta:assert struct.unpack_from('<4I',old,n*16)==(0,0,0,0);struct.pack_into('<4I',expected,n*16,net+1,65537,0,0)
 assert expected==warm
 physical=replay(p/'snapshot_axi.txt',[(0x1000000000,p/'old.bin'),(0x2000000000,p/'warm.bin')]);assert physical['error_read_beats']==physical['write_beats']==physical['write_replies']==0
 ts=[l.split()for l in(p/'events.txt').read_text().splitlines()];by=defaultdict(list)
 for t in ts:
  if t[0]!='JOINT_DONE':by[int(t[1])].append(t)
 D=mf['design'];G1=0x100000001;G2=mf['generation'];OLD=0x1000000000;WARM=0x2000000000
 a=None;ka=None;ca=None;journal=set();sa=sk=sc=None;pa=pk=pc=None;query=None;lease=False;tx=False;decision=None;ending=[];ars=[];floor=0;kr=None;counts=Counter(t[0]for t in ts)
 for cycle,group in by.items():
  join=None;drop=0;native_pub=False;native_discard=False
  for t in sorted(group,key=lambda x:0 if x[0]=='COMMIT'else 1):
   kind=t[0]
   if kind=='C':
    assert pa is None;stage=int(t[2]);desc=(int(t[3],16),int(t[4],16),int(t[5]),int(t[6],16));assert desc[0]==D
    if stage:assert lease and tx and a and desc[1]>a[1]and desc[2]>a[2]
    else:assert a is None
    pa=[stage,desc,False,False]
   elif kind=='K':assert pa and not pa[2]and int(t[3],16)==pa[1][1]and int(t[4])==pa[1][2];pa[2]=True
   elif kind=='L':assert pa and pa[2]and t[3:]==['0','0'];pa[3]=True
   elif kind=='F':
    assert pa and pa[3]and t[2:4]==['0','0']and t[5]=='0'
    if pa[0]:sa=pa[1]
    else:a=pa[1]
    assert int(t[4],16)==a[1];pa=None
   elif kind=='KC':
    assert pk is None;stage,cp,v=map(int,t[2:]);status=1 if (not stage and ka is not None)or(stage and(not lease or not tx or v!=ka[1]or cp<=ka[0]or sk is not None))else 0;pk=(stage,cp,v,status)
   elif kind=='KF':
    assert pk;stage,cp,v,status=pk;assert int(t[2])==status
    if status==0:
     if stage:sk=(cp,v)
     else:ka=(cp,v);floor=v
    assert int(t[3])==ka[0]and int(t[4])==len(journal);pk=None
   elif kind=='CC':
    assert pc is None;stage,cp,v=map(int,t[2:]);status=1 if (not stage and ca is not None)or(stage and(not lease or not tx or v!=ca[1]or cp<=ca[0]or sc is not None))else 0;pc=(stage,cp,v,status)
   elif kind=='CF':
    assert pc;stage,cp,v,status=pc;assert int(t[2])==status
    if status==0:
     if stage:sc=(cp,v)
     else:ca=(cp,v)
    assert tuple(map(int,t[3:]))==ca;pc=None
   elif kind=='J':assert not tx and (int(t[2]),int(t[3]))in delta;journal.add((int(t[2]),int(t[3])))
   elif kind=='LEASE':
    if t[2]=='A':assert not lease and not tx;lease=True
    else:assert lease and not tx and sa is sk is sc is None;lease=False
   elif kind=='START':assert lease and not tx and sa is sk is sc is None and ka==ca==(17,4)and len(journal)==6 and a[1:3]==(G1,17);assert [int(t[2]),int(t[3]),int(t[4],16)]==[17,6,G1];tx=True;decision=None
   elif kind=='COMMIT':
    assert lease and tx and sa and sk and sc and query is None and pa is pk is pc is None
    good=sa[:3]==(D,G2,18)and sk==sc==(18,4);assert int(t[2],2)==(7 if good else 0);decision=0 if good else 1
   elif kind=='CANCEL':assert lease and tx and decision is None;decision=2
   elif kind=='JOIN':
    assert decision==0 and lease and tx and sa and sk and sc and query is None;assert t[2]=='111'and [int(t[3]),int(t[4]),int(t[5]),int(t[6],16)]==[ka[0],ca[0],len(journal),a[1]];join=True
   elif kind=='P':assert decision==0 and sa and [int(t[2],16),int(t[3],16),int(t[4])]==[a[1],sa[1],sa[2]];native_pub=True
   elif kind=='DROP':
    mask=int(t[2],2);expected_mask=int(sa is not None)+2*int(sk is not None)+4*int(sc is not None);assert decision in [1,2]and lease and tx and mask==expected_mask and mask!=0;drop=mask
   elif kind=='X':assert decision in [1,2]and int(t[2],16)==a[1];native_discard=True
   elif kind=='END':
    assert lease and tx and sa is sk is sc is None and int(t[2])==decision;assert [int(t[3]),int(t[4]),int(t[5]),int(t[6],16)]==[ka[0],ca[0],len(journal),a[1]];ending.append(decision);tx=False;decision=None
   elif kind=='ABORT_CF':assert lease and tx and sc and tuple(map(int,t[2:]))==ca;sc=None
   elif kind=='KRQ':assert not tx and not lease and kr is None;cp,v,q=map(int,t[2:]);assert cp==ka[0]and v==floor and q==3;kr=(1,77)
   elif kind=='KRR':assert kr and tuple(map(int,t[2:]))==kr;kr=None
   elif kind=='Q':
    assert query is None and a;d,g,cp,node,net,cookie,inject=int(t[2],16),int(t[3],16),*map(int,t[4:]);assert not inject
    status=1 if(d,g,cp)!=a[:3]else 0;refs=occ=0
    if status==0:
     data=old if a[3]==OLD else warm;row=struct.unpack_from('<4I',data,node*16);refs=(row[1]&65535)if row[0]==net+1 else 0;occ=row[1]>>16;ars += [a[3]+len(old)-64,(a[3]+node*16)&~63]
    query=(cookie,status,refs,occ)
   elif kind=='R':assert query and [int(t[2],16),int(t[3],16),int(t[4])]==list(a[:3])and tuple(map(int,t[5:]))==query;query=None
   elif kind=='JOINT_DONE':assert not lease and not tx and not journal and ka==ca==(18,4)and a[:3]==(D,G2,18)and int(t[2])==8 and t[3:]==['0','18']
   else:raise AssertionError(t)
  if join:
   assert native_pub and not drop;a=sa;ka=sk;ca=sc;journal.clear();sa=sk=sc=None
  else:assert not native_pub
  if drop:
   assert bool(drop&1)==native_discard
   if drop&1:sa=None
   if drop&2:sk=None
   if drop&4:sc=None
  else:assert not native_discard
 actual=(p/'snapshot_axi.txt').read_text().splitlines();assert [int(l.split()[1],16)for l in actual if l.startswith('A ')]==ars
 assert ending==[1,2,2,0]and counts['LEASE']==8 and counts['START']==4 and counts['JOIN']==counts['P']==1 and counts['DROP']==counts['X']==3 and counts['ABORT_CF']==1 and counts['KRQ']==counts['KRR']==1 and counts['Q']==counts['R']==5 and len(ars)==8
 done=[t for t in ts if t[0]=='JOINT_DONE'];assert len(done)==1 and done[0][1:]==['205','8','0','18']
 log=(p/'simulate.log').read_text();assert 'CHECKPOINT_JOINT_PASS checks=205 reads=8'in log and 'Fatal:'not in log
 result={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'replay_sha256':sha(ROOT/'scripts/audit_route_fault_axi.py'),'checks':205,'transactions':ending,'joint_publications':1,'journal_keys':sorted(delta),'physical':physical,'limits':['Metadata slice, not full query-system integration. Journal interface is driven from verified six-key snapshot delta, not newly executed working-owner writes.','Native lease guard instantiated; route_retired tied1 because slice contains no route engine. Manifest-ready is a TB input backed by host bundle verification.','No native configuration provider callbacks or real recovery executed; only same-version recovery rejection checks attempt-floor retention. Path/query/label checkpoint and warm recovery still pending.','No synthesis/timing/board or durable atomic-publication proof.']}
 (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','checks':205,'transactions':ending,'joint_publications':1,'read_beats':8}))
if __name__=='__main__':main()
