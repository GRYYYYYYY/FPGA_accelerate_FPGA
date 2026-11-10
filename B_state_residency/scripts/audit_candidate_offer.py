from pathlib import Path
import hashlib,json,sys,re,mmap,os
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
 inputs=ROOT/'results/commit_inputs_20261025';im=json.loads((inputs/'manifest.json').read_text());gate=json.loads((inputs/'source_bound_audit.json').read_text());assert gate['status']=='passed'and gate['manifest_sha256']==sha(inputs/'manifest.json')
 assert sha(inputs/'vectors.txt')==im['artifacts']['vectors.txt']
 expected=[];cookie=0
 for line in (inputs/'vectors.txt').read_text().splitlines():
  row=line.split()
  if row[0]=='E':cookie=int(row[1])
  if row[0]=='A':
   ordinal,node,bits,action,svc,*cfg=map(int,row[1:]);packed=sum(w<<(32*i)for i,w in enumerate(cfg));expected.append((cookie,ordinal,node,bits,action,packed))
 # Bind unchanged committed-label pipeline and reproduce top/frontier-only changes.
 import importlib.util
 dp=ROOT/'hardware/variants/candidate_offer_v1/derive_top.py';spec=importlib.util.spec_from_file_location('offer_top',dp);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 prior_dir=ROOT/'results/candidate_commit_full_20261025';pm=json.loads((prior_dir/'manifest.json').read_text());assert pm['status']=='passed'
 current_by_name={Path(n).name:(n,item)for n,item in m['sources'].items()}
 for n,item in pm['sources'].items():
  name=Path(n).name
  if name.endswith(('.sv','.v','.dat')) and not name.startswith('tb_') and name not in ['candidate_commit_engine.sv','query_frontier.sv']:
   cn,ci=current_by_name[name];assert ci['sha256']==item['sha256']==sha(prior_dir/'sources'/n)
 assert mod.derive((prior_dir/'sources/priced/candidate_commit_engine.sv').read_text())==(out/'sources/priced/candidate_offer_engine.sv').read_text()
 dc=ROOT/'hardware/variants/candidate_offer_v1/derive_frontier.py';spec=importlib.util.spec_from_file_location('offer_frontier',dc);frontier=importlib.util.module_from_spec(spec);spec.loader.exec_module(frontier)
 assert frontier.derive((prior_dir/'sources/postprev/query_frontier.sv').read_text())==(out/'sources/offer/query_frontier_offer.sv').read_text()
 for group,depname in [('geometry','search_geometry_hls_20261024'),('exact','search_cost_exact_hls_20261024')]:
  dep=ROOT/'results'/depname;dm=json.loads((dep/'manifest.json').read_text());dg=json.loads((dep/'source_bound_audit.json').read_text());assert dg['status']=='passed' and dg['manifest_sha256']==sha(dep/'manifest.json')
  for rel,digest in dm['generated_rtl_artifacts'].items():
   if '/syn/verilog/'in rel and Path(rel).suffix=='.v':assert m['sources'][group+'/'+Path(rel).name]['sha256']==digest
 service=ROOT/'results/cost_service_v2_20261024';sm=json.loads((service/'manifest.json').read_text())
 for name in ['cost_service.sv','cost_memory_call.sv']:assert m['sources']['cost_service_v2/'+name]['sha256']==sm['sources'][name]['sha256']
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
 assert gate['sll']>0 and gate['causal_y_flip_from_minus_one']>0 and gate['explicit_geometry_patches']==4
 # No new synthesizable RTL: compare all modules with the previous accepted prefetch composition.
 previous=ROOT/'results/candidate_prefetch_pressure_20261025';prior=json.loads((previous/'manifest.json').read_text())
 current={Path(n).name:item for n,item in m['sources'].items()};same_modules=0
 for n,item in prior['sources'].items():
  if Path(n).suffix not in ['.sv','.v'] or Path(n).name.startswith('tb_') or Path(n).name in ['candidate_prefetch_query_core.sv','candidate_prefetch_engine.sv']:continue
  assert current[Path(n).name]['sha256']==item['sha256']==sha(previous/'sources'/n);same_modules+=1
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
 fh=ROOT/'results/frontier_hls_relative_project_20261024';fg=json.loads((fh/'source_bound_audit.json').read_text());assert fg['status']=='passed'
 for n,h in fg['generated_rtl_artifacts'].items():
  if Path(n).suffix in ['.v','.dat']:assert m['sources']['frontier/'+n]['sha256']==h
 fs=ROOT/'results/frontier_service_v3_20261024';fm=json.loads((fs/'manifest.json').read_text());assert fm['status']=='passed';fsa=json.loads((fs/'source_bound_audit.json').read_text());assert fsa['status']=='passed'and fsa['manifest_sha256']==sha(fs/'manifest.json')
 for n in ['frontier_service.sv','frontier_hls_call.sv']:assert m['sources']['frontier/'+n]['sha256']==fm['sources'][n]['sha256']
 counts={}
 for case,cm in m['cases'].items():
  if selected_case is not None and case!=selected_case:continue
  assert cm['status']=='passed'and all(c['exit_code']==0 for c in cm['commands'])
  d=out/case
  for name,digest in fg['generated_rtl_artifacts'].items():
   if Path(name).suffix=='.dat':assert sha(d/name)==digest
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
   ('graph_axi.txt',[(0x1fffff000,ROOT/'results/graph_image_20261024/offsets.u32le',36356096),(0x10fffff000,ROOT/'results/graph_image_20261024/edges.u32le',161878144),(0x20fffff000,inputs/'graph_attrs.rrt32',290848320)]),
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
  sys.path.insert(0,str(ROOT/'scripts'))
  from audit_offer_trace import check_case
  result.update(check_case(d,inputs,cm['limit']))
  table=(ROOT/'results/connection_state_inputs_20261025/connections.bin').read_bytes();expansions=[];q=price=0;cookie=0
  for line in(inputs/'vectors.txt').read_text().splitlines():
   t=line.split()
   if t[0]=='Q' and int(t[1])==0:q,price=map(int,t[2:4])
   elif t[0]=='E':cookie=int(t[1])
   elif t[0]=='D' and (not cm['limit'] or cookie<=cm['limit']):
    ci,sink,net,seq,flags=map(int,t[1:6]);expansions.append((cookie,ci,net,sink,flags&24,q,price,price,0x123456789abcdef0))
  actual_q=[];actual_s=[];actual_m=[];cycles_q={};cycles_s={};cycles_m={}
  for line in(d/'params_observed.txt').read_text().splitlines():
   t=line.split()
   if t[0]=='W':
    waits=list(map(int,t[1:]));assert len(waits)==3 and all(x>0 for x in waits);result['delayed_wait_cycles_skip_allow_empty']=waits;continue
   cy=int(t[1]);c=int(t[2]);ci=int(t[3])
   if t[0]=='Q':actual_q.append(tuple(map(int,t[2:10]))+(int(t[10],16),));cycles_q[c]=cy
   elif t[0]=='S':
    assert int(t[4])==0 and int(t[5],16)==int.from_bytes(table[ci*64:(ci+1)*64],'little');actual_s.append((c,ci));cycles_s[c]=cy
   elif t[0]=='M':
    assert int(t[4])==1 and int(t[5],16)==int.from_bytes(table[ci*64:(ci+1)*64],'little');actual_m.append((c,ci));cycles_m[c]=cy
   else:raise AssertionError(t)
  assert actual_q==expansions and actual_s==actual_m==[(r[0],r[1])for r in expansions]
  for c,ci,*_ in expansions:assert cycles_q[c]<cycles_s[c]<cycles_m[c]
  for line in(d/'post_order.txt').read_text().splitlines():
   t=line.split()
   if t[0]=='LQ' and int(t[4])==1:assert int(t[1])>cycles_s[int(t[2])]
  ars=[];reads=[]
  for line in(d/'qstate_axi.txt').read_text().splitlines():
   t=line.split();address=int(t[1],16);ci=(address-0x81fffff000)//64;assert address==0x81fffff000+ci*64 and 0<=ci<180326
   if t[0]=='A':assert t[2]=='1';ars.append(ci)
   else:assert t[0]=='R' and t[3]=='0' and int(t[2],16)==int.from_bytes(table[ci*64:(ci+1)*64],'little');reads.append(ci)
  assert ars==reads==[r[1]for r in expansions]
  result['params_expansions']=len(expansions);result['params_AXI_R_words_checked']=len(reads)*16
  costinp=ROOT/'results/commit_inputs_20261025';cim=json.loads((costinp/'manifest.json').read_text());cig=json.loads((costinp/'source_bound_audit.json').read_text());assert cig['status']=='passed' and cig['manifest_sha256']==sha(costinp/'manifest.json') and cim['artifacts']['vectors.txt']==sha(inputs/'vectors.txt')
  oracle={}
  for line in(costinp/'cost_vectors.txt').read_text().splitlines():
   t=line.split();key=tuple(map(int,t[:2]))
   if not cm['limit'] or key[0]<=cm['limit']:oracle[key]=[int(w,16)for w in t[2:]]
  pack=lambda words:sum(w<<(32*i)for i,w in enumerate(words))
  config={};connections={};expansion=0
  for line in(inputs/'vectors.txt').read_text().splitlines():
   t=line.split()
   if t[0]=='E':expansion=int(t[1])
   elif t[0]=='D':connections[expansion]=int(t[1])
   elif t[0]=='A' and int(t[4])!=0:config[(expansion,int(t[1]))]=list(map(int,t[6:]))
  prefix={tuple(v[:2]):v for v in (list(map(int,line.split()))for line in(inputs/'post_vectors.txt').read_text().splitlines())}
  observed={}
  for line in(d/'cost23_observed.txt').read_text().splitlines():
   t=line.split();assert t[0]=='K' and len(t)==7;key=tuple(map(int,t[1:3]));assert key not in observed
   packet,values,geometry,gresult=[int(x,16)for x in t[3:]];assert packet==pack(oracle[key][:23]) and values==pack(oracle[key][23:])
   cfg=config[key];p=prefix[key];row=[int.from_bytes(table[connections[key[0]]*64+i*4:connections[key[0]]*64+i*4+4],'little')for i in range(16)]
   assert row[11]==row[9]==0
   words=[p[4],p[5],cfg[8],cfg[9],0,0,0,row[10],0,0,cfg[10],cfg[11],0];assert geometry==pack(words)
   dx=abs(p[4]-cfg[8]);dy=abs(p[5]-cfg[9]);assert gresult==pack([0,dx,dy,dx+dy]) and dx+dy==oracle[key][12]
   observed[key]=(packet,values,geometry,gresult)
  assert set(observed)==set(oracle)
  events={key:[]for key in oracle};post_done={}
  for line in(d/'post_order.txt').read_text().splitlines():
   t=line.split()
   if t[0]=='AR':post_done[tuple(map(int,t[2:4]))]=int(t[1])
  for line in(d/'cost23_order.txt').read_text().splitlines():
   t=line.split();key=tuple(map(int,t[2:4]));assert key in oracle;events[key].append(t)
  for key,es in events.items():
   assert [t[0]for t in es]==['I','GQ','GR','CQ','CR'] and post_done[key]<int(es[0][1])
   assert all(int(a[1])<int(b[1])for a,b in zip(es,es[1:]))
   packet,values,geometry,gresult=observed[key];assert [int(t[4],16)for t in es[1:]]==[geometry,gresult,packet,values]
  assert f"COST23_INPUTS_PASS calls={len(oracle)}"in(d/'simulate.log').read_text()
  result['actual_cost23_calls']=len(oracle);result['cost23_input_words_bitexact']=len(oracle)*23;result['cost23_output_words_bitexact']=len(oracle)*5;result['actual_geometry_calls']=len(oracle)
  heap=ROOT/'results/offer_heap_inputs_20261025';hm=json.loads((heap/'manifest.json').read_text());hg=json.loads((heap/'source_bound_audit.json').read_text());assert hg['status']=='passed' and hg['manifest_sha256']==sha(heap/'manifest.json')
  hn='pilot'if cm['limit']else'full';expected_queue=[list(map(int,line.split()))for line in(heap/(hn+'_expected.txt')).read_text().splitlines()];actual_queue=[];pending=None;owners=[]
  for line in(d/'queue_calls.txt').read_text().splitlines():
   t=line.split()
   if t[0]=='Q':
    assert pending is None;pending=[int(t[2]),int(t[3],16),*map(int,t[4:8])];owners.append(int(t[8]))
   else:
    assert t[0]=='R' and pending is not None and [int(t[6]),int(t[7]),int(t[8])]==[pending[3],pending[4],pending[5]]
    actual_queue.append(pending+[int(t[2]),int(t[3],16),int(t[4]),int(t[5])]);pending=None
  assert pending is None and actual_queue==expected_queue
  seed=sum(row[0]==1 and owner==2 for row,owner in zip(actual_queue,owners));cost=sum(row[0]==1 and owner==3 for row,owner in zip(actual_queue,owners))
  assert cost==result['actual_cost_offers'] and seed==result['seed_offers']
  result['queue_commands_original_CPU_checked']=len(actual_queue);result['queue_successful_verification_polls']=sum(row[0]==2 and row[6]==0 for row in actual_queue);result['queue_empty_polls']=sum(row[0]==2 and row[6]==1 for row in actual_queue);result['queue_peak']=max(row[9]for row in actual_queue)
  counts[case]=result
 result={'status':'passed','selected_completed_case':selected_case,'manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'trace_auditor_sha256':sha(ROOT/'scripts/audit_offer_trace.py'),'counts':counts,'unchanged_baseline_sources':shared,'frozen_generated_center_modules':center_rtl,'identical_prior_rtl_modules':same_modules,'params_derive_sha256':sha(dp),'cost_core_derive_sha256':sha(dc),'cost_input_auditor_sha256':sha(ROOT/'scripts/audit_commit_inputs.py'),'scope':'Actual cost OFFER after three native label ACKs; full original CPU8-ary queue command/response stream plus query-end verification polls and CP SIZE. Existing cost/label/native backing checks retained. Action2 callback still has no recursive hardware scheduler; no full routing or board proof.'}
 (out/(('completed_'+selected_case+'_audit.json') if selected_case else 'source_bound_audit.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
