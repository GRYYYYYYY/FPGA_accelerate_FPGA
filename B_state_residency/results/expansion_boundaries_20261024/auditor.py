from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/expansion_boundaries_20261024';base=ROOT/'results/expansion_20261024';m=read(out/'manifest.json');assert m['status']=='passed'
 assert m['base_manifest_sha256']==sha(base/'manifest.json')and m['base_audit_sha256']==sha(base/'source_bound_audit.json')
 for name,digest in m['sources'].items():assert sha(out/'sources'/name)==digest==read(base/'manifest.json')['sources'][name]['sha256']
 for name,spec in m['new_sources'].items():assert sha(out/'sources'/name)==spec['sha256']==sha(Path(spec['path']))
 for group,gm in m['groups'].items():
  assert all(c['exit_code']==0 for c in gm['commands'])
  for name,digest in gm['artifacts'].items():assert sha(out/group/name)==digest
  args=gm['commands'][0]['argv'];assert (['TOKEN_LIMIT']if group=='token'else ['OWNER_LIMIT']if group=='owner'else [])==[a for a in args if a in ['TOKEN_LIMIT','OWNER_LIMIT']]
 assert set(m['cases'])==set(map(str,range(15)));initial=(ROOT/'results/expansion_inputs_20261024/initial_design.bin').read_bytes();cases={}
 expected_claim={0:0,1:0,2:0,3:1,4:1,5:1,6:1,7:0,8:1,9:1,10:0,11:0,12:0,13:1,14:0}
 for key,cm in m['cases'].items():
  scenario=int(key);d=out/f'case{scenario:02}';assert cm['status']=='passed'and all(c['exit_code']==0 for c in cm['commands'])
  for name,digest in cm['artifacts'].items():assert sha(d/name)==digest
  log=(d/'simulate.log').read_text();assert cm['result']in log and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log
  values={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])};assert values['scenario']==scenario and values['fault']==(scenario!=0)and values['claim']==expected_claim[scenario]
  memory=bytearray(initial);pending=None;reads=writes=0;b=[]
  for line in (d/'design_axi.txt').read_text().splitlines():
   p=line.split()
   if p[0]=='A':assert pending is None and int(p[2])==1;pending=int(p[1],16);reads+=1
   elif p[0]=='R':
    address=int(p[1],16);assert pending==address;pending=None;offset=address-0x31fffff000;assert offset%64==0 and 0<=offset<=len(memory)-64
    assert int(p[2],16)==int.from_bytes(memory[offset:offset+64],'little')and int(p[3])==(2 if scenario==2 else 0)
   elif p[0]=='W':
    offset=int(p[1],16)-0x31fffff000;strb=int(p[2],16);payload=int(p[3],16).to_bytes(64,'little');assert offset%64==0 and 0<=offset<=len(memory)-64 and strb in [65535<<(16*j)for j in range(4)]
    for j in range(64):
     if strb>>j&1:memory[offset+j]=payload[j]
    writes+=1
   else:assert p[0]=='B';b.append(int(p[1]))
  assert pending is None and reads==values['design_reads']and writes==values['design_writes']and len(b)==writes
  assert all(code==(2 if scenario in(4,5)else 0)for code in b)
  assert hashlib.sha256(memory).hexdigest()==sha(d/'design.bin')
  assert (d/'labels.bin').read_bytes()==bytes(49152)
  if scenario==5:assert int.from_bytes(memory[:4],'little')&4 # physical valid can precede failed acknowledgement
  if scenario==13:assert values['token']==15 and values['owner']==1 and values['claim']==1 and writes==2
  if scenario==14:assert values['owner']==7 and values['token']==15 and values['graph_reads']==14 and writes==1
  cases[key]=values
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'base_audit_sha256':m['base_audit_sha256'],'cases':cases,'scope':'Same integration RTL; invalid inputs, config mismatch, graph/design AXI faults, forced pager fault/wrong reply cookies, held-result/stream faults, actual 4-bit token and 3-bit owner exhaustion. Each scenario starts a pristine initialized backing; no failed-design retry claim.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
