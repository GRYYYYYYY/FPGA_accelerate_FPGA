"""Independent namespace/state oracle and physical AXI replay for dual authority slots."""
from pathlib import Path
import sys,json,struct
from collections import Counter,defaultdict
from run_checkpoint_authority import ROOT,sha
from verify_rtl_bundle import verify
from audit_route_fault_axi import replay

def main():
 p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
 for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256']
 ns={'__file__':str(ROOT/'hardware/variants/authority_rotate_v1/build.py'),'__name__':'frozen_rotate'};exec(compile((p/'sources/build.py').read_text(),'build.py','exec'),ns);ns['BASE']=p/'sources/checkpoint_authority_reader.sv';assert ns['make']()==(p/'sources/checkpoint_authority_rotator.sv').read_text()
 # The frozen TB factory imports its sibling builder; use a disposable module context.
 import importlib.util
 spec=importlib.util.spec_from_file_location('frozen_rotate_tb',p/'sources/build_tb.py');tb=importlib.util.module_from_spec(spec);spec.loader.exec_module(tb);tb.b.BASE=p/'sources/checkpoint_authority_reader.sv';assert tb.make()==(p/'sources/tb_rotate.sv').read_text()
 proven=Path('/tmp/B_state_residency_offer_20261025/cold_axi_fixed_v1/sources')
 for n,base in [('checkpoint_authority_reader.sv',proven/'checkpoint_authority_reader.sv'),('owner_state_store.sv',proven/'access_owner_v3_20261024/owners/owner_state_store.sv'),('axi_file_memory.sv',proven/'axi_file_memory.sv')]:assert sha(p/'sources'/n)==sha(base)
 bundle=Path(m['bundle']);mf=verify(bundle);assert sha(bundle/'manifest.json')==m['bundle_manifest_sha256'];initial=Path(m['initial'])
 old=(initial/'owners.bin').read_bytes()+(initial/'owner_allocator.bin').read_bytes();warm=(bundle/'owner_primary.bin').read_bytes()+(bundle/'owner_allocator.bin').read_bytes();assert len(old)==len(warm)
 added_keys=set(struct.iter_unpack('<2I',(bundle/'journal_absorbed.u32').read_bytes()));expected=bytearray(old)
 for node,net in added_keys:
  assert struct.unpack_from('<4I',old,node*16)==(0,0,0,0);struct.pack_into('<4I',expected,node*16,net+1,65537,0,0)
 assert expected==warm
 assert (p/'old.bin').read_bytes()==old and (p/'warm.bin').read_bytes()==warm and sha(p/'old.bin')==m['old_sha256']and sha(p/'warm.bin')==m['warm_sha256']
 OLD=0x1000000000;WARM=0x2000000000;D=mf['design'];N=mf['node_count'];NETS=mf['net_count'];BYTES=len(warm)-64
 physical=replay(p/'snapshot_axi.txt',[(OLD,p/'old.bin'),(WARM,p/'warm.bin')]);assert physical['error_read_beats']==1 and physical['write_beats']==physical['write_replies']==physical['error_write_replies']==0
 lines=[l.split()for l in(p/'events.txt').read_text().splitlines()];counts=Counter(t[0]for t in lines)
 active=None;candidate=None;slot=0;pending=None;rearm=False;native_rearm=False;rearm_cancel=False;query=None;fault=False;ars=[];rstatus=[];covered=set();hits=defaultdict(set);cfg_statuses=[];publications=[]
 for t in lines:
  kind=t[0]
  if kind=='C':
   assert pending is None and not rearm and query is None
   stage=int(t[2]);desc=(int(t[3],16),int(t[4],16),int(t[5]),int(t[6],16))
   rejected=(not stage and active is not None)or(stage and(active is None or candidate is not None or desc[0]!=active[0]or desc[1]<=active[1]or desc[2]<=active[2]))
   pending={'stage':stage,'desc':desc,'reject':bool(rejected),'target':slot^stage,'native_sent':False,'native_status':None,'abort':False}
  elif kind=='K':
   assert pending and not pending['reject']and not pending['native_sent'];assert [int(t[2]),int(t[3],16),int(t[4])]==[pending['target'],pending['desc'][1],pending['desc'][2]];pending['native_sent']=True
  elif kind=='L':
   status=int(t[3]);is_rearm=int(t[4]);bank=int(t[2])
   if rearm:assert bank==slot and status==(3 if rearm_cancel else 0)and is_rearm==1;native_rearm=True
   else:
    assert pending and pending['native_sent']and not is_rearm and bank==pending['target'];expected=3 if pending['abort']else 2 if pending['desc'][3]%64 else 0;assert status==expected;pending['native_status']=status
  elif kind=='F':
   status,is_rearm,observed,staged=int(t[2]),int(t[3]),int(t[4],16),int(t[5]);assert staged==0
   if rearm:
    assert native_rearm and is_rearm and status==(3 if rearm_cancel else 0)and observed==active[1];fault=rearm_cancel;rearm=False;native_rearm=False;rearm_cancel=False
   else:
    assert pending and not is_rearm
    expected=1 if pending['reject']else pending['native_status'];assert expected is not None and status==expected
    if status==0:
     if pending['stage']:candidate=pending['desc']
     else:active=pending['desc']
    assert observed==(active[1]if active else 0);pending=None
   cfg_statuses.append(status)
  elif kind=='P':
   assert pending is None and not rearm and query is None and candidate and not fault
   assert [int(t[2],16),int(t[3],16),int(t[4])]==[active[1],candidate[1],candidate[2]];publications.append((active[1],candidate[1]));active=candidate;candidate=None;slot^=1
  elif kind=='X':assert candidate and query is None and int(t[2],16)==active[1];candidate=None
  elif kind=='ABORT':
   assert query is None and int(t[2],16)==active[1];candidate=None
   if pending:pending['abort']=True
   if rearm:rearm_cancel=True
  elif kind=='A':assert fault and query is None and not pending and int(t[2],16)==active[1];rearm=True
  elif kind=='Q':
   assert active and query is None and pending is None and not rearm and not fault
   d,g,cp,node,net,cookie,inject=int(t[2],16),int(t[3],16),*map(int,t[4:]);status=1 if (d,g,cp)!=active[:3]else 2 if node>=N or net>=NETS else 9 if inject else 0;refs=occ=0
   if status not in [1,2]:
    ars.append(active[3]+BYTES);rstatus.append(2 if inject else 0)
    if not inject:
     assert active[3]in [OLD,WARM];data=old if active[3]==OLD else warm;word=struct.unpack_from('<4I',data,node*16);assert word[2:]==(0,0)
     occ=word[1]>>16;refs=(word[1]&65535)if word[0]==net+1 else 0;ars.append((active[3]+node*16)&~63);rstatus.append(0)
     if refs:hits[active[1]].add((node,net))
     if active[3]==WARM and refs:covered.add((node,net))
   query=(cookie,status,refs,occ)
  elif kind=='R':
   assert query and [int(t[2],16),int(t[3],16),int(t[4])]==list(active[:3]);assert tuple(map(int,t[5:]))==query
   if query[1]==9:fault=True
   query=None
  elif kind=='DONE':assert query is None and pending is None and not rearm and not fault and candidate is None;assert int(t[2])==int(t[3])==len(ars)and int(t[4])==0
  else:raise AssertionError(t)
 actual=(p/'snapshot_axi.txt').read_text().splitlines();assert [int(t.split()[1],16)for t in actual if t.startswith('A ')]==ars and [int(t.split()[3])for t in actual if t.startswith('R ')]==rstatus
 keys=set(struct.iter_unpack('<2I',(bundle/'journal_absorbed.u32').read_bytes()));assert keys<=covered and len(keys)==6
 existing=(0,struct.unpack_from('<I',old)[0]-1);assert existing not in keys and all(existing in hits[g]for g in [0x100000001,0x100000002,0x100000004])
 assert publications==[(0x100000001,0x100000002),(0x100000002,0x100000004)]and active[:3]==(D,0x100000004,20)
 assert cfg_statuses==[0,1,0,1,1,1,1,2,0,0,3,1,0,3,0]and counts['C']==13 and counts['F']==15 and counts['A']==2 and counts['Q']==counts['R']==28 and counts['K']==7 and counts['L']==9 and counts['ABORT']==3 and counts['P']==2 and counts['X']==1
 log=(p/'simulate.log').read_text();assert 'AUTHORITY_ROTATE_PASS checks=224 reads=45'in log and 'Fatal:'not in log
 result={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'replay_sha256':sha(ROOT/'scripts/audit_route_fault_axi.py'),'bundle_verifier_sha256':sha(ROOT/'scripts/verify_rtl_bundle.py'),'checks':224,'native_gets':28,'native_configurations':counts['K'],'native_config_replies':counts['L'],'publications':publications,'covered_warm_keys':sorted(keys),'preexisting_owner_preserved':existing,'physical':physical,'limits':['Component only: two native codec banks sharing a serialized read-only AXI service. GET blocked during config handling; prepared-but-unpublished old bank remains usable.','No coordinator journal/config/path/query/label joint commit or restore, no runtime working-DDR snapshot writer or full-system rotation recovery yet; saved paths must be restored after target reset before work resumes.','G4 reuses the immutable warm image to test namespace selection; not a newly captured G4 full-state bundle. No synthesis/timing/board or durable anti-replay proof.']}
 (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','checks':224,'native_gets':28,'read_beats':len(ars),'publications':publications}))
if __name__=='__main__':main()
