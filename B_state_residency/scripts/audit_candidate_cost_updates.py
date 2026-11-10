from pathlib import Path
import hashlib,json,sys,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for name,s in m['sources'].items():assert sha(out/'sources'/name)==s['sha256']==sha(Path(s['path']))
 for path,digest in m['gates'].items():assert sha(Path(path))==digest
 previous=ROOT/'results/candidate_cost_state_full_20261025';pm=json.loads((previous/'manifest.json').read_text());pg=json.loads((previous/'source_bound_audit.json').read_text());assert pg['status']=='passed'and pg['manifest_sha256']==sha(previous/'manifest.json')
 shared=0
 for name,s in m['sources'].items():
  if name.endswith(('.v','.sv'))and not Path(name).name.startswith('tb_'):
   assert pm['sources'][name]['sha256']==s['sha256'];shared+=1
 input_dir=ROOT/'results/cost_state_inputs_20261025';im=json.loads((input_dir/'manifest.json').read_text());ic=im['cases']['real'];cost0=input_dir/'real/initial.bin';assert sha(cost0)==ic['artifacts']['initial.bin'];initial_cost=cost0.read_bytes();po=ic['layout']['prices_offset'];no=ic['layout']['nets_offset']
 owners=ROOT/'results/candidate_initial_owner_20261024/owners.bin';design=ROOT/'results/candidate_decisions_20261024/initial_design.bin';cpu_record=(ROOT/'results/candidate_decisions_20261024/expected_design.bin').open('rb').read(16)
 counts={}
 modes={'update':0,'stale_open':1,'stale_expand':2,'nodes':3,'design_id':4,'read_error':5,'write_error':6,'abort_ar':7}
 for case,cm in m['cases'].items():
  mode=modes[case];d=out/case;assert cm['status']=='passed'and all(c['exit_code']==0 for c in cm['commands'])
  for name,digest in cm['artifacts'].items():assert sha(d/name)==digest
  assert sha(d/'owners.bin')==sha(owners)
  with (d/'design.bin').open('rb')as actual,design.open('rb')as original:
   first=original.read(16);assert actual.read(16)==(cpu_record if mode in [0,5,7]else first)
   while data:=original.read(1<<20):assert actual.read(len(data))==data
   assert not actual.read(1)
  mem=bytearray(initial_cost);pending=None;pending_b=False;read_offsets=[];writes=[];rerr=berr=0
  for line in(d/'cost_axi.txt').read_text().splitlines():
   r=line.split()
   if r[0]=='A':assert pending is None and not pending_b and r[2]=='1';pending=int(r[1],16)
   elif r[0]=='R':
    address=int(r[1],16);offset=address-0x71fffff000;assert address==pending and 0<=offset<=len(mem)-64
    assert int(r[2],16).to_bytes(64,'little')==mem[offset:offset+64];assert int(r[3])==(2 if mode==5 else 0)
    rerr+=r[3]!='0';pending=None;read_offsets.append(offset)
   elif r[0]=='W':
    assert pending is None and not pending_b and mode in [0,6]
    offset=int(r[1],16)-0x71fffff000;mask=int(r[2],16);data=int(r[3],16).to_bytes(64,'little')
    assert mask==15 and offset in [0,po]and 0<=offset<=len(mem)-64
    expected=0x40000000 if offset==0 else 0x3fc00000;assert int.from_bytes(data[:4],'little')==expected
    for j in range(64):
     if mask&(1<<j):mem[offset+j]=data[j]
    writes.append(offset);pending_b=True
   elif r[0]=='B':assert pending_b and int(r[1])==(2 if mode==6 else 0);berr+=r[1]!='0';pending_b=False
   else:raise AssertionError(r)
  assert pending is None and not pending_b and(d/'cost.bin').read_bytes()==mem
  expected_reads={0:[0,po,no,0,0,po],5:[0],7:[0]}.get(mode,[]);assert read_offsets==expected_reads
  assert writes==([0,po]if mode==0 else[0]if mode==6 else[])
  assert rerr==(mode==5)and berr==(mode==6)
  log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log and cm['result']in log
  result={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])};assert result['mode']==mode and result['cost_reads']==len(read_offsets)and result['cost_writes']==len(writes)and result['cost_bs']==len(writes)
  assert result['version']==(4 if mode==0 else 3)
  if mode==0:assert result['cs_calls']==11 and result['cs_gets']==6
  if mode in [1,2,3,4]:assert result['cost_reads']==result['cost_writes']==result['graph_reads']==result['design_reads']==result['design_writes']==0
  result['cost_R_errors']=rerr;result['cost_B_errors']=berr;counts[case]=result
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'same_shared_RTL_files':shared,'validated_cases':list(counts),'counts':counts,'scope':'Selected named cases in validated_cases for actual joined candidate/pager/cost state: update visibility, identity/configuration rejection or actual AXI faults, as present in counts; no coverage claim for absent cases. Complete cost/owner/design backing and all cost beats checked. Each case imports fresh backing; in-session fault recovery and cost packet/arithmetic/search are not proven.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
