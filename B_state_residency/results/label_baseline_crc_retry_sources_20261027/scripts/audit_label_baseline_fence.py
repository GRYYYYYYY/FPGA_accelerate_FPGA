from pathlib import Path
import json,sys,runpy,struct
from run_checkpoint_authority import ROOT,sha
from audit_route_fault_axi import replay
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'and m['abort_case']and len(m['cases'])==1
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256'],n
b=runpy.run_path(str(p/'sources/iter2_build_tb.py'));b['make'].__globals__['BASE']=ROOT/'hardware/variants/label_baseline_system_v1/build_tb.py';assert b['make']()==(p/'sources/tb_query_fault.sv').read_text()
f=runpy.run_path(str(p/'sources/fence_build.py'));f['make'].__globals__['BASE']=ROOT/'hardware/variants/label_baseline_system_v1'
for n,t in f['make']().items():
 if m['negative']and n=='residency_system.sv':t=t.replace('&&(!ENABLE_BASELINE||baseline_retired)','').replace('(!ENABLE_BASELINE||baseline_retired)&&','')
 assert t==(p/'sources'/n).read_text(),n
unit=p.parent/'baseline_guard_unit_v1';assert json.loads((unit/'source_bound_audit.json').read_text())['status']=='passed';assert sha(unit/'sources/baseline_retirement_guard.sv')==sha(p/'sources/baseline_retirement_guard.sv')
case=next(iter(m['cases']));d=p/case;rows=[t.split()for t in(d/'natural_trace.txt').read_text().splitlines()]
def by(k):return[t for t in rows if t[0]==k]
assert len(by('BM'))==1 and int(by('BM')[0][2])==66893
assert len(by('B_ABORT'))==1 and not by('I')and not by('Z')and not by('P')and not by('O')and not by('C')and not by('RO')
image=Path(m['baseline_image']);im=json.loads((image/'manifest.json').read_text());assert sha(image/'manifest.json')==m['baseline_manifest_sha256']
assert sha(image/'baseline.bin')==im['baseline_sha256'];source=Path(im['source']);assert sha(source)==im['source_sha256']
with source.open('rb')as f:f.seek(66893*44);u=struct.unpack('<11I',f.read(44));v=[u[j]for j in [0,1,3,4,5]]
axi=[s.split()for s in(d/'baseline_axi.txt').read_text().splitlines()];addr=0xb000000000+66892*32;assert axi[0]==['A',f'{addr:016x}','1']
negative=m['negative'];log=(d/'simulate.log').read_text()
if negative:
 assert 'Fatal: premature baseline retirement'in log and not by('BASELINE_ABORT_PASS')and len(axi)==1 and not by('BR')
 t=by('B_EARLY');assert len(t)==1 and t[0][2:]==['0','0','1','0','0','0']or len(t)==1 and t[0][2:]==['0','0','1','1','0','0']
 summary=dict(counterexample=True,accepted_ar=1,consumed_r=0,old_f_all_drained=1,checks=1)
else:
 assert 'Fatal:'not in log and 'BASELINE_ABORT_PASS'in log
 waits=by('BWAIT');assert len(waits)>=48 and all(t[2:]==['0']*6 for t in waits)
 assert len(axi)==2 and axi[1][0]=='R'and int(axi[1][1],16)==addr and axi[1][3]=='0'
 with(image/'baseline.bin').open('rb')as f:f.seek(66892*32);assert int(axi[1][2],16)==int.from_bytes(f.read(64),'little')
 assert len(by('BR'))==1 and by('BR')[0][2:]==['66893','0',f'{sum(x<<(32*i)for i,x in enumerate(v)):040x}']
 native=by('NB');writes=[t for t in native if t[2]=='3'];assert len(writes)==5
 assert [(int(t[4])*8+int(t[6]),int(t[7]),int(t[8],16))for t in writes]==[(66893,i,x)for i,x in enumerate(v)]
 responses=by('NR');assert len(responses)==len(native);records={}
 for t,r in zip(native,responses):
  op=int(t[2]);status=present=payload=0
  if op==6:status=8
  if op==3:records[int(t[7])]=int(t[8],16);present=1;payload=sum(records.get(i,0)<<(32*i)for i in range(5))
  elif op==2 and records:present=1;payload=sum(records.get(i,0)<<(32*i)for i in range(5))
  else:assert op in [0,1,2,6,12],op
  assert r[2:]==[str(status),str(present),f'{payload:040x}']
 terminal=by('BASELINE_ABORT_PASS');assert len(terminal)==1 and terminal[0][2:]==[str(len(waits)),'1','1','7']
 assert int(terminal[0][1])>int(by('BR')[0][1])>int(waits[-1][1])
 summary=dict(counterexample=False,accepted_ar=1,consumed_r=1,consumed_source_reply=1,inflight_checks=len(waits),native_seed_writes=5,query_status=7,prepare_acked=0,held_query_reply_cycles=8)
# Query cancelled in source-check: no owner mutations or DDR label writeback.
bind=json.loads(Path(m['binding']).read_text());reg=bind['regions'];initial=b''.join(Path(reg[k]['path']).read_bytes()for k in ['owners','owner_pool','owner_allocator'])
assert(d/'owners.bin').read_bytes()==initial and(d/'labels.bin').read_bytes()==bytes(3145728)
assert not any(t.startswith('W ')for t in(d/'owner_axi.txt').read_text().splitlines())
graph=ROOT/'results/graph_image_20261024'
regions=[('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),('design',[(0x31fffff000,Path(reg['design']['path']))],d/'design.bin'),('cost',[(0x71fffff000,Path(reg['cost_history_prices_nets']['path']))],d/'cost.bin'),('owner',[(0x61fffff000,initial)],d/'owners.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('qstate',[(0x81fffff000,Path(reg['connections']['path']))],None),('table',[(0x41fffff000,Path(reg['rows']['path'])),(0x51fffff000,Path(reg['columns']['path']))],None),('snapshot',[(0x91fffff000,initial),(0xa000000000,initial)],None)]
memory={tag:replay(d/(tag+'_axi.txt'),rr,ff)for tag,rr,ff in regions}
r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),case=case,**summary,memory=memory,limits=['Query-only abort at first baseline AR during SOURCE_CHECK, held failure response; no recovery command or target reset executed. Native baseline seed completes, not rollback.','Selected source/context and all-node baseline externally trusted. No G2 warm integration or general cancellation/board proof.'])
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('BASELINE_FENCE_AUDITED',case,negative)
