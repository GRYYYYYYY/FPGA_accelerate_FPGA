from pathlib import Path
import hashlib,json,sys,re,mmap
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,s in m['sources'].items():assert sha(out/'sources'/n)==s['sha256']==sha(Path(s['path']))
 for path,digest in m['gates'].items():assert sha(Path(path))==digest
 inputs=ROOT/'results/candidate_decisions_20261024';im=json.loads((inputs/'manifest.json').read_text());gate=json.loads((inputs/'source_bound_audit.json').read_text());assert gate['status']=='passed'and gate['manifest_sha256']==sha(inputs/'manifest.json')
 assert sha(inputs/'vectors.txt')==im['artifacts']['vectors.txt']
 expected=[];cookie=0
 for line in (inputs/'vectors.txt').read_text().splitlines():
  row=line.split()
  if row[0]=='E':cookie=int(row[1])
  if row[0]=='A':
   ordinal,node,bits,action,svc,*cfg=map(int,row[1:]);packed=sum(w<<(32*i)for i,w in enumerate(cfg));expected.append((cookie,ordinal,node,bits,action,packed))
 # The core adds only an output port for operation_pending; preserve its complete body.
 old=(ROOT/'hardware/variants/candidate_pipeline_v1/candidate_engine.sv').read_text()
 clone=old.replace('module candidate_engine #(','module candidate_query_core #(',1).replace(' input wire  clk,',' output wire operation_pending,\n input wire  clk,',1).replace(' wire  operation_pending;','')
 assert (out/'sources/priced/candidate_query_core.sv').read_text()==clone
 cg=ROOT/'results/cost_state_synthesis_20261025';cgate=json.loads((cg/'final_audit.json').read_text());assert cgate['status']=='passed'
 assert sha(out/'sources/priced/cost_state_store.sv')==sha(cg/'sources/cost_state_store.sv')
 cost_input=ROOT/'results/cost_state_inputs_20261025';cim=json.loads((cost_input/'manifest.json').read_text());assert cim['status']=='passed'
 cost_file=cost_input/'real/initial.bin';assert sha(cost_file)==cim['cases']['real']['artifacts']['initial.bin']
 layout=cim['cases']['real']['layout'];cost_expected=[];current_cookie=0
 for line in (inputs/'vectors.txt').read_text().splitlines():
  v=line.split()
  if v[0]=='E':current_cookie=int(v[1]);parent=int(v[2])
  elif v[0]=='D':net=int(v[3])
  elif v[0]=='A':
   ordinal=int(v[1]);child=int(v[2])
   for offset in [child*4,layout['prices_offset']+(ordinal%256)*4,layout['nets_offset']+net*16]:cost_expected.append((current_cookie,offset&~63))
  elif v[0]=='Z'and current_cookie==10:cost_expected.append((current_cookie,(parent*4)&~63))
 own=ROOT/'results/candidate_initial_owner_20261024';om=json.loads((own/'manifest.json').read_text());assert om['status']=='passed'
 assert sha(own/'owners.bin')==om['artifacts']['owners.bin']
 profile=ROOT/'results/owner_profile_real_v4_20261024';pm=json.loads((profile/'manifest.json').read_text());assert sha(profile/'owner.events')==pm['owner_events_sha256']
 assert om['gates'][str(profile/'manifest.json')]==sha(profile/'manifest.json')
 counts={}
 for case,cm in m['cases'].items():
  assert cm['status']=='passed'and all(c['exit_code']==0 for c in cm['commands'])
  d=out/case
  for n,digest in cm['artifacts'].items():assert sha(d/n)==digest
  rows=[]
  for line in (d/'observed.txt').read_text().splitlines():
   a=line.split();assert a[0]=='A'and len(a)==7;rows.append(tuple(map(int,a[1:6]))+(int(a[6],16),))
  subset=[r for r in expected if not cm['limit']or r[0]<=cm['limit']];assert rows==subset
  assert sha(d/'owners.bin')==om['artifacts']['owners.bin']
  owner_beats=0
  with (own/'owners.bin').open('rb')as backing:
   image=mmap.mmap(backing.fileno(),0,access=mmap.ACCESS_READ)
   for line in (d/'owner_axi.txt').read_text().splitlines():
    fields=line.split()
    if fields[0]=='R':
     address=int(fields[1],16);offset=address-0x61fffff000
     assert fields[3]=='0'and 0<=offset<=len(image)-64
     assert int(fields[2],16).to_bytes(64,'little')==image[offset:offset+64]
     owner_beats+=1
    else:assert fields[0]=='A'and fields[2]=='1'
   image.close()
  if not cm['limit']:assert sha(d/'design.bin')==im['artifacts']['expected_design.bin']
  result=dict((k,int(v))for k,v in re.findall(r'(\w+)=(\d+)',cm['result']));assert result['decisions']==len(rows)and result['host_blocks']>0
  assert owner_beats==result['owner_reads'];result['owner_beats_independently_checked']=owner_beats
  assert sha(d/'cost.bin')==sha(cost_file)
  selected=[offset for cookie,offset in cost_expected if not cm['limit']or cookie<=cm['limit']];cost_reads=[];pending=None
  with cost_file.open('rb')as backing:
   image=mmap.mmap(backing.fileno(),0,access=mmap.ACCESS_READ)
   for line in(d/'cost_axi.txt').read_text().splitlines():
    r=line.split()
    if r[0]=='A':assert pending is None and r[2]=='1';pending=int(r[1],16)
    else:
     assert r[0]=='R'and int(r[1],16)==pending and r[3]=='0';offset=pending-0x71fffff000
     assert int(r[2],16).to_bytes(64,'little')==image[offset:offset+64];cost_reads.append(offset);pending=None
   image.close()
  assert pending is None and cost_reads==selected and len(cost_reads)==result['cs_gets']
  assert result['cs_calls']==result['cs_gets']+(6 if not cm['limit']else 2)
  result['cost_R_beats_independently_checked']=len(cost_reads)
  counts[case]=result
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'counts':counts,'scope':'Actual pager/query and cost-state linkage, full version matching, lease after core retirement, queued OPEN versus PUBLISH; TB-issued state reads, not internal cost packet production. Source-bound RTL integration decisions and Config14, actual initial owner event binding and complete unchanged owner backing; full cases complete final design backing. Scripted query context, no cost/push/route/board claim.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
