"""Real snapshot, CPU map/model and byte-exact physical memory/write audit."""
from pathlib import Path
import sys,json,struct,subprocess,shutil,runpy,os
from run_checkpoint_authority import ROOT,sha
from audit_route_fault_axi import replay
from audit_authority_recovery import decode
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256'],n
base=Path(m['base']);assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
for n in ['owner_state_store.sv','checkpoint_authority_reader.sv','axi_file_memory.sv']:assert sha(p/'sources'/n)==sha(base/'sources'/n)
t=runpy.run_path(str(p/'sources/build_tb.py'));assert t['make']()==(p/'sources/tb_multi_owner.sv').read_text()
if m['fixed']:
 b=runpy.run_path(str(p/'sources/build.py'));assert b['make']()==(p/'sources/recovery_coordinator.sv').read_text()
else:assert sha(p/'sources/recovery_coordinator.sv')==sha(p.parent/'warm_retry_system_v2/sources/recovery_coordinator.sv')
assert all(x['exit_code']==0 for x in m['commands'])and len(m['commands'])==3
f=m['fixture'];codec=Path(f['codec']);cm=json.loads((codec/'manifest.json').read_text());assert json.loads((codec/'source_bound_audit.json').read_text())['status']=='passed'and sha(codec/'source_bound_audit.json')==f['codec_audit_sha256']
for n,h in f['input_hashes'].items():assert sha(p/n)==h
for n,old in [('primary.bin','owners.bin'),('pool.bin','owner_pool.bin'),('allocator.bin','owner_allocator.bin')]:assert sha(p/n)==sha(codec/old)
primary=(p/'primary.bin').read_bytes();pool=(p/'pool.bin').read_bytes();alloc=(p/'allocator.bin').read_bytes();node=f['node'];C=f['capacity'];assert struct.unpack_from('<4I',alloc)==(C,0,C,0)
original,entries=decode(primary,pool,node,C);assert original=={6632:1,17601:2}and entries=={0}
cpu=Path(cm['base']);owners={}
with(cpu/'initial_nodes.u32').open('rb')as g:g.seek(node*44);r=struct.unpack('<11I',g.read(44));owners[r[6]]=r[7]
for n,net,refs in struct.iter_unpack('<III',(cpu/'initial_overflow.u32').read_bytes()):
 if n==node:owners[net]=refs
assert owners==original
rows=[x.split()for x in(p/'events.txt').read_text().splitlines()]
def by(tag):return[x for x in rows if x[0]==tag]
assert len(by('J'))==4 and [(int(x[2]),int(x[3]),int(x[4]))for x in by('J')]==[(n,t,o)for o,n,t,*_ in f['mutations']]
assert len({(x[2],x[3])for x in by('J')})==3
commands=[];pending=None
for r in rows:
 if r[0]in ['H','O']:
  assert pending is None;pending=r
 elif r[0]in ['HB','OB']:
  assert pending is not None and r[0]==pending[0]+'B' and int(pending[1])<int(r[1]);commands.append([*map(int,pending[2:]),*map(int,r[2:])]);pending=None
assert pending is None
h=by('H');assert [list(map(int,r[2:]))for r in h[:4]]==[[o,n,t]for o,n,t,*_ in f['mutations']]
kd=[list(map(int,r[2:]))for r in by('KD')];assert kd==([[0,6,0,3],[1,3,0,3]]if m['expected_failure']else[[0,6,0,3],[1,0,4,0]])
assert len(by('RESET'))==2 and len(by('SOFT'))==1 and all(x[2]=='3'for x in by('RESET')+by('SOFT'))
aa=by('AK');ab=by('AB');assert len(aa)==len(ab)and ab[0][2:5]==['9','0','0']
keys=[6632,0,17601]
if m['expected_failure']:
 assert len(aa)==2 and not by('LABELS_MOCK')
 assert [list(map(int,r[2:]))for r in by('OB')]==[[0,0,2],[5,0,2]]
else:
 assert len(aa)==10 and len(by('LABELS_MOCK'))==1
 assert [int(x[4])for x in aa[1:]]==keys*3 and [int(x[2])for x in aa[1:]]==[0]*6+[1]*3
 assert len({x[5]for x in aa[1:]})==9
 assert [list(map(int,r[2:]))for r in h[4:]]==[[0,node,k]for k in keys]
 for x,b in zip(aa[1:],ab[1:]):assert list(map(int,b[2:5]))==[0,owners.get(int(x[4]),0),2]
for x,b in zip(aa,ab):assert int(x[1])<int(b[1])and x[6]==b[5]=='0000000100000002'
# Every actual owner operation is checked against the independent executable model.
v=p/'verification';v.mkdir(exist_ok=True)
for old,n in [(ROOT/'hardware/variants/multi_owner_recovery_v1/check_model.cpp','check_model.cpp'),(ROOT/'hardware/search/owner_state_v1/owner_store.hpp','owner_store.hpp')]:
 if (v/n).exists():assert sha(v/n)==sha(old)
 else:shutil.copyfile(old,v/n)
(v/'commands.txt').write_text(''.join(' '.join(map(str,x))+'\n'for x in commands))
env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
subprocess.run(['g++','-std=c++17','-O2','-I',str(v),str(v/'check_model.cpp'),'-o',str(v/'check')],check=True,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
r=subprocess.run([str(v/'check'),*[str(p/n)for n in ['primary.bin','pool.bin','allocator.bin','live.bin']],str(v/'commands.txt'),str(f['nodes']),str(C),str(f['primary_bytes']),str(f['pool_bytes']),str(v/'expected_writes.txt')],check=True,env=env,capture_output=True,text=True);model=json.loads(r.stdout)
expected=[(int(x[0],16),int(x[1],16))for x in map(str.split,(v/'expected_writes.txt').read_text().splitlines())];actual=[]
for r in map(str.split,(p/'live_axi.txt').read_text().splitlines()):
 if r[0]!='W':continue
 mask=int(r[2],16);lane=(mask&-mask).bit_length()-1;assert lane in [0,16,32,48]and mask==0xffff<<lane
 value=(int(r[3],16)>>(lane*8))&((1<<128)-1);actual.append((int(r[1],16)-0xa1fffff000+lane,value))
assert actual==expected and len(actual)==model['record_writes']==(8 if m['expected_failure']else 16)
initial=primary+pool+alloc;memory=dict(live=replay(p/'live_axi.txt',[(0xa1fffff000,initial)],p/'live.bin'),snapshot=replay(p/'snapshot_axi.txt',[(0x91fffff000,p/'primary.bin'),(0x91fffff000+f['primary_bytes'],p/'pool.bin'),(0x91fffff000+f['primary_bytes']+f['pool_bytes'],p/'allocator.bin')]))
assert memory['snapshot']['error_read_beats']==1 and memory['snapshot']['write_beats']==0 and memory['live']['error_read_beats']==memory['live']['error_write_replies']==0
assert memory['snapshot']['read_beats']==(4 if m['expected_failure']else 28)
log=(p/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log and ('MULTI_OWNER_CAPACITY_REPRO'if m['expected_failure']else 'MULTI_OWNER_RECOVERY_PASS')in log
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),expected_failure=m['expected_failure'],full_pool=C,same_node=node,initial_owners=owners,journal_keys=3,mutations=4,capacity_refusals=model['capacity_refusals'],corrected=0 if m['expected_failure']else 4,final_journal=3 if m['expected_failure']else 0,model=model,verification_hashes={n:sha(v/n)for n in ['check_model.cpp','owner_store.hpp','commands.txt','expected_writes.txt','check']},memory=memory,limits=['Real prepared snapshot and real owner/authority/coordinator component; callbacks for reconfigure and labels are modeled. Not full warm routing checkpoint integration.','Deterministic full-pool primary promotion/free-list reuse, not all permutations or arbitrary corruption.'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('MULTI_OWNER_AUDIT_PASSED',model,flush=True)
