from pathlib import Path
import hashlib,json,sys,re,mmap
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());selected_case=sys.argv[2] if len(sys.argv)>2 else None
 assert m['status']=='passed' or (selected_case is not None and m['cases'][selected_case]['status']=='passed')
 for n,s in m['sources'].items():assert sha(out/'sources'/n)==s['sha256']==sha(Path(s['path']))
 for path,digest in m['gates'].items():assert sha(Path(path))==digest
 inputs=ROOT/'results/candidate_occupied_inputs_v2_20261025';im=json.loads((inputs/'manifest.json').read_text());gate=json.loads((inputs/'source_bound_audit.json').read_text());assert gate['status']=='passed'and gate['manifest_sha256']==sha(inputs/'manifest.json')
 assert sha(inputs/'vectors.txt')==im['artifacts']['vectors.txt']
 expected=[];cookie=0
 for line in (inputs/'vectors.txt').read_text().splitlines():
  row=line.split()
  if row[0]=='E':cookie=int(row[1])
  if row[0]=='A':
   ordinal,node,bits,action,svc,*cfg=map(int,row[1:]);packed=sum(w<<(32*i)for i,w in enumerate(cfg));expected.append((cookie,ordinal,node,bits,action,packed))
 # Reverse only the owner-backend mux/ports; every other core byte stays identical.
 old=(ROOT/'hardware/variants/candidate_cost_state_v1/candidate_query_core.sv').read_text()
 clone=(out/'sources/priced/candidate_prefetch_query_core.sv').read_text()
 clone=clone.replace('module candidate_prefetch_query_core #(','module candidate_query_core #(',1)
 start=clone.index(' input wire p_o_req_valid,');end=clone.index(' output wire operation_pending,',start);clone=clone[:start]+clone[end:]
 start=clone.index(' // One accepted backend operation');end=clone.index(' owner_state_store owner_store(',start);clone=clone[:start]+clone[end:]
 start=clone.index(' owner_state_store owner_store(');end=clone.index('\n);',start)+3
 part=clone[start:end]
 for field in ['req_valid','req_ready','req_op','req_cookie','req_node','req_net','rsp_valid','rsp_ready','rsp_status','rsp_cookie','rsp_count','rsp_occupancy','rsp_will_overuse']:
  part=part.replace('(mux_'+field+')','(o_b_'+field+')')
 clone=clone[:start]+part+clone[end:];assert clone==old
 cg=ROOT/'results/cost_state_synthesis_20261025';cgate=json.loads((cg/'final_audit.json').read_text());assert cgate['status']=='passed'
 assert sha(out/'sources/priced/cost_state_store.sv')==sha(cg/'sources/cost_state_store.sv')
 cost_input=ROOT/'results/cost_state_inputs_20261025';cim=json.loads((cost_input/'manifest.json').read_text());assert cim['status']=='passed'
 cost_file=inputs/'cost.bin';assert sha(cost_file)==im['artifacts']['cost.bin']
 layout=cim['cases']['real']['layout'];cost_expected=[];prep_expected=[];current_cookie=0
 owner_bytes=(inputs/'owners.bin').read_bytes()
 ol=json.loads((ROOT/'results/candidate_initial_owner_20261024/manifest.json').read_text())['layout']
 cost_bytes=cost_file.read_bytes()
 def owner_at(node,net):
  p=owner_bytes[node*16:node*16+16];key=int.from_bytes(p[:4],'little');refs=int.from_bytes(p[4:6],'little');occ=int.from_bytes(p[6:8],'little');ptr=int.from_bytes(p[8:12],'little')
  count=refs if key==net+1 else 0;seen=set()
  while ptr:
   assert ptr not in seen and 0<ptr<=ol['pool_capacity'];seen.add(ptr)
   r=owner_bytes[ol['pool_offset']+(ptr-1)*16:ol['pool_offset']+ptr*16]
   if int.from_bytes(r[:4],'little')==net+1:count=int.from_bytes(r[4:8],'little')
   ptr=int.from_bytes(r[8:12],'little')
  return count,occ
 for line in (inputs/'vectors.txt').read_text().splitlines():
  v=line.split()
  if v[0]=='E':current_cookie=int(v[1]);parent=int(v[2])
  elif v[0]=='D':net=int(v[3])
  elif v[0]=='A' and int(v[4])!=0:
   ordinal=int(v[1]);child=int(v[2]);count,occ=owner_at(child,net);index=occ-(count!=0);assert 0<=index<256
   offsets=[child*4,layout['prices_offset']+index*4,layout['nets_offset']+net*16]
   for offset in offsets:cost_expected.append((current_cookie,offset&~63))
   h,p,n=[int.from_bytes(cost_bytes[offset:offset+(16 if i==2 else 4)],'little') for i,offset in enumerate(offsets)]
   prep_expected.append((current_cookie,ordinal,child,net,count,occ,index,h,p,n))
  elif v[0]=='Z' and current_cookie==10:cost_expected.append((current_cookie,(parent*4)&~63))
 own=inputs;om=im;assert sha(own/'owners.bin')==om['artifacts']['owners.bin']
 assert gate['edited_nodes']==8 and gate['overflow_records']==54 and gate['all_other_owner_cost_bytes_unchanged']
 # No new synthesizable RTL: compare all modules with the previous accepted prefetch composition.
 previous=ROOT/'results/candidate_prefetch_pressure_20261025';prior=json.loads((previous/'manifest.json').read_text())
 current={Path(n).name:item for n,item in m['sources'].items()};same_modules=0
 for n,item in prior['sources'].items():
  if Path(n).suffix not in ['.sv','.v'] or Path(n).name.startswith('tb_'):continue
  assert current[Path(n).name]['sha256']==item['sha256']==sha(previous/'sources'/n);same_modules+=1
 oldtb=(ROOT/'hardware/variants/candidate_prefetch_v1/tb_candidate_prefetch.sv').read_text()
 assert (out/'sources/tb_candidate_occupied.sv').read_text()==oldtb.replace('tb_candidate_prefetch','tb_candidate_occupied').replace('CANDIDATE_PREFETCH_PASS','CANDIDATE_OCCUPIED_PASS')
 # Bind every unchanged baseline module and the exact previously verified center ABI/core.
 baseline=ROOT/'results/candidate_cost_state_full_20261025';bm=json.loads((baseline/'manifest.json').read_text())
 bg=json.loads((baseline/'source_bound_audit.json').read_text());assert bg['status']=='passed' and bg['manifest_sha256']==sha(baseline/'manifest.json')
 frozen={Path(n).name:(n,item) for n,item in m['sources'].items()};assert len(frozen)==len(m['sources'])
 shared=0
 for n,item in bm['sources'].items():
  if Path(n).name in ['candidate_cost_state_engine.sv','candidate_query_core.sv','tb_candidate_cost_state.sv','runner.py']:continue
  new_n,new_item=frozen[Path(n).name];assert new_item['sha256']==item['sha256']==sha(baseline/'sources'/n);shared+=1
 hls=ROOT/'results/cost_center_hls_20261025';hm=json.loads((hls/'manifest.json').read_text());hg=json.loads((hls/'source_bound_audit.json').read_text())
 assert hg['status']=='passed' and hg['manifest_sha256']==sha(hls/'manifest.json')
 center_rtl=0
 for rel,digest in hm['generated_rtl_artifacts'].items():
  if '/syn/verilog/' in rel and Path(rel).suffix=='.v':assert frozen[Path(rel).name][1]['sha256']==digest==sha(hls/rel);center_rtl+=1
 service=ROOT/'results/cost_center_service_v2_20261025';sm=json.loads((service/'manifest.json').read_text());sg=json.loads((service/'source_bound_audit.json').read_text())
 assert sg['status']=='passed' and sg['manifest_sha256']==sha(service/'manifest.json')
 for name in ['cost_center_memory_call.sv','cost_center_service.sv']:assert frozen[name][1]['sha256']==sm['sources'][name]['sha256']
 counts={}
 for case,cm in m['cases'].items():
  if selected_case is not None and case!=selected_case:continue
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
  prep=[]
  for line in (d/'prep_inputs.txt').read_text().splitlines():
   r=line.split();assert r[0]=='P' and len(r)==11
   prep.append(tuple(map(int,r[1:8]))+tuple(int(w,16) for w in r[8:11]))
  expected_prep=[r for r in prep_expected if not cm['limit'] or r[0]<=cm['limit']];assert prep==expected_prep
  result['prefetch_calls']=len(prep);result['prefetch_same_net']=sum(r[4]!=0 for r in prep)
  result['prefetch_occupied']=sum(r[5]!=0 for r in prep);result['price_indices']=sorted({r[6] for r in prep})
  assert f"PREFETCH_INPUTS_PASS calls={len(prep)}" in (d/'simulate.log').read_text()
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
  assert pending is None and cost_reads==selected and len(cost_reads)==len(selected)
  assert result['cs_calls']==result['cs_gets']+(6 if not cm['limit']else 2)
  result['cost_R_beats_independently_checked']=len(cost_reads)
  center=[]
  for line in (d/'center_calls.txt').read_text().splitlines():
   r=line.split();assert len(r)==8 and r[0]=='C';center.append(tuple(map(int,r[1:6]))+(int(r[6],16),int(r[7],16)))
  exp=[];q=price=0;version=0;cookie=0
  for line in (inputs/'vectors.txt').read_text().splitlines():
   r=line.split()
   if r[0]=='Q' and int(r[1])==0:q,price=map(int,r[2:4]);version=price
   if r[0]=='E':cookie=int(r[1])
   if cm['limit'] and cookie>cm['limit']:break
   if r[0]=='A':exp.append((len(exp),0,q,price,version,0x123456789abcdef0,0x40e0000000000000))
   if r[0]=='Z' and cookie!=10:exp.append((len(exp),1,q,price,version,0x123456789abcdef0,0x40e0000000000000))
  assert center==exp,(case,center[:2],exp[:2])
  result['center_calls']=len(center);result['center_retired_checks']=sum(r[1] for r in center)
  assert f"CENTER_LIFETIME_PASS calls={len(center)} retired={result['center_retired_checks']}" in (d/'simulate.log').read_text()
  # File model zero-fills a short final 64B beat. Verify graph/table bytes too,
  # rather than treating inherited fread warnings as an unchecked exemption.
  for logname,windows in [
   ('graph_axi.txt',[(0x1fffff000,ROOT/'results/graph_image_20261024/offsets.u32le',36356096),(0x10fffff000,ROOT/'results/graph_image_20261024/edges.u32le',161878144),(0x20fffff000,ROOT/'results/graph_image_20261024/nodes.rrt32',290848320)]),
   ('table_axi.txt',[(0x41fffff000,ROOT/'results/coordinate_inputs_20261024/real/rows.bin',2496)])]:
   opened=[(base,path.open('rb'),size) for base,path,size in windows];maps=[(base,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ),size) for base,f,size in opened]
   beats=short=0
   for line in (d/logname).read_text().splitlines():
    r=line.split()
    if r[0]=='A':continue
    assert r[0]=='R' and r[3]=='0';address=int(r[1],16)
    matches=[(base,image,size) for base,image,size in maps if base<=address<base+size];assert len(matches)==1
    base,image,size=matches[0];offset=address-base;expected_bytes=image[offset:offset+64];assert expected_bytes
    short+=len(expected_bytes)<64;expected_bytes=expected_bytes.ljust(64,b'\0')
    assert int(r[2],16).to_bytes(64,'little')==expected_bytes,(case,logname,address)
    beats+=1
   for _,image,_ in maps:image.close()
   for _,f,_ in opened:f.close()
   result[logname+'_R_beats_checked']=beats;result[logname+'_short_beats_zero_padding_checked']=short
  counts[case]=result
 result={'status':'passed','selected_completed_case':selected_case,'manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'counts':counts,'unchanged_baseline_sources':shared,'frozen_generated_center_modules':center_rtl,'identical_prior_rtl_modules':same_modules,'scope':'Actual candidate-triggered owner lookup and internal history/occupancy-indexed price/net reads on real graph with scripted nonzero owner/history/factor changes, independently rebuilt from actual AXI images and fresh original CPU decisions. SKIP has no prefetch. Center arithmetic remains a TB fixture; no post-prev geometry or cost23 packet yet. Source-bound original CPU decisions/Config14 under scripted owner edits, with the full modified owner image unchanged throughout simulation; full cases complete final design backing. Scripted query context, no cost/push/route/board claim.'}
 (out/(('completed_'+selected_case+'_audit.json') if selected_case else 'source_bound_audit.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
