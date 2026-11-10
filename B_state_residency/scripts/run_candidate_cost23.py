from pathlib import Path
import json,hashlib,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();rtl=[]
 base=ROOT/'results/candidate_compile_v2_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 m={'status':'running','scope':'Actual candidate integration with real CSR and scripted occupied owner/history/price image with fresh CPU decisions; scripted query labels; Internal owner/history/occupancy-indexed price/net prefetch plus TB fixture center arithmetic; ordered prev write + post-prev coordinate/upstream and actual center arithmetic; no cost23/label commit/full routing or board','sources':{},'cases':{},'gates':{}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 def sparse_copy(a,b):subprocess.run(['cp','--sparse=always',str(a),str(b)],check=True)
 def freeze(p,name):
  q=src/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][name]={'path':str(p),'sha256':sha(q)};return q
 for pstr in bm['rtl']:
  p=Path(pstr)
  if p.name.startswith('tb_'):continue
  rel=str(p.relative_to(base/'sources'));assert sha(p)==bm['sources'][rel]['sha256']
  if p.name=='candidate_controller.sv':p=ROOT/'hardware/variants/candidate_pipeline_v1/candidate_controller.sv'
  
  if p.name=='candidate_engine.sv':continue
  rtl.append(freeze(p,rel))
 for p in [ROOT/'hardware/variants/candidate_cost23_v1/candidate_cost23_query_core.sv',ROOT/'hardware/variants/candidate_cost23_v1/candidate_cost23_engine.sv',ROOT/'hardware/variants/cost_state_v1/cost_state_store.sv']:rtl.append(freeze(p,'priced/'+p.name))
 for name,p in [('tb_candidate_cost23.sv',ROOT/'hardware/variants/candidate_cost23_v1/tb_candidate_cost23.sv'),('axi_file_memory.sv',ROOT/'results/access_owner_v3_20261024/sources/coordinate/axi_file_memory.sv')]:rtl.append(freeze(p,name))
 hls=ROOT/'results/cost_center_hls_20261025';hm=json.loads((hls/'manifest.json').read_text());hg=hls/'source_bound_audit.json';assert json.loads(hg.read_text())['status']=='passed';m['gates'][str(hg)]=sha(hg)
 for rel,digest in hm['generated_rtl_artifacts'].items():
  p=hls/rel
  if '/syn/verilog/'in rel and p.suffix=='.v':
   assert sha(p)==digest;rtl.append(freeze(p,'center/'+p.name))
 for name in ['cost_center_memory_call.sv','cost_center_service.sv']:
  rtl.append(freeze(ROOT/'hardware/variants/cost_center_service_v1'/name,'center/'+name))
 rtl.append(freeze(ROOT/'hardware/variants/candidate_prefetch_v1/cost_inputs_prefetch.sv','priced/cost_inputs_prefetch.sv'))
 rtl.append(freeze(ROOT/'hardware/variants/connection_state_v1/connection_state_reader.sv','params/connection_state_reader.sv'))
 rtl.append(freeze(ROOT/'hardware/variants/candidate_cost23_v1/cost23_inputs.sv','cost23/cost23_inputs.sv'))
 for group,result in [('geometry','search_geometry_hls_20261024'),('exact','search_cost_exact_hls_20261024')]:
  dep=ROOT/'results'/result;dm=json.loads((dep/'manifest.json').read_text());gate=dep/'source_bound_audit.json';assert json.loads(gate.read_text())['status']=='passed';m['gates'][str(gate)]=sha(gate)
  for rel,digest in dm['generated_rtl_artifacts'].items():
   if '/syn/verilog/'in rel and Path(rel).suffix=='.v':
    p=dep/rel;assert sha(p)==digest;rtl.append(freeze(p,group+'/'+p.name))
 for group,names in [('geometry_service_v1',['geometry_service.sv','geometry_memory_call.sv']),('cost_service_v2',['cost_service.sv','cost_memory_call.sv'])]:
  for name in names:rtl.append(freeze(ROOT/'hardware/variants'/group/name,group+'/'+name))
 for name in ['postprev_inputs.sv','query_frontier.sv']:rtl.append(freeze(ROOT/'hardware/variants/candidate_postprev_v1'/name,'postprev/'+name))
 fh=ROOT/'results/frontier_hls_relative_project_20261024';fg=json.loads((fh/'source_bound_audit.json').read_text());assert fg['status']=='passed';m['gates'][str(fh/'source_bound_audit.json')]=sha(fh/'source_bound_audit.json')
 for name,digest in fg['generated_rtl_artifacts'].items():
  p=fh/'frontier_step/solution1/syn/verilog'/name;assert sha(p)==digest
  if p.suffix in ['.v','.dat']:
   q=freeze(p,'frontier/'+name)
   if p.suffix=='.v':rtl.append(q)
 for name in ['frontier_service.sv','frontier_hls_call.sv']:rtl.append(freeze(ROOT/'hardware/variants/frontier_service_v3'/name,'frontier/'+name))
 for name in ['derive_core.py','derive_top.py']:freeze(ROOT/'hardware/variants/candidate_postprev_v1'/name,'postprev/'+name)
 freeze(Path(__file__),'runner.py');m['rtl']=[str(p.relative_to(src))for p in rtl]
 inp=ROOT/'results/cost23_inputs_20261025';own=ROOT/'results/candidate_initial_owner_20261024';graph=ROOT/'results/graph_image_20261024';tables=ROOT/'results/coordinate_inputs_20261024/real'
 ig=inp/'source_bound_audit.json';ia=json.loads(ig.read_text());assert ia['status']=='passed'and ia['manifest_sha256']==sha(inp/'manifest.json');m['gates'][str(ig)]=sha(ig)
 for dep in [base,inp,own]:assert json.loads((dep/'manifest.json').read_text())['status']=='passed';m['gates'][str(dep/'manifest.json')]=sha(dep/'manifest.json')
 qinp=ROOT/'results/connection_state_inputs_20261025';qgate=qinp/'source_bound_audit.json';assert json.loads(qgate.read_text())['status']=='passed';m['gates'][str(qgate)]=sha(qgate);m['gates'][str(qinp/'connections.bin')]=sha(qinp/'connections.bin')
 save()
 try:
  cases=[('pilot',160,None)]if len(sys.argv)<3 else [('full',0,None),('pressure',0,'PRESSURE')]
  for case,limit,define in cases:
   d=out/case;d.mkdir();
   for dat in (src/'frontier').glob('*.dat'):shutil.copyfile(dat,d/dat.name)
   cm=m['cases'][case]={'status':'running','limit':limit,'commands':[]};save()
   sparse_copy(inp/'initial_design.bin',d/'design.bin');sparse_copy(inp/'owners.bin',d/'owners.bin');sparse_copy(inp/'cost.bin',d/'cost.bin');(d/'labels.bin').open('wb').truncate(31457280 if define=='DEFAULT_DIRECTORY'else 3145728);(d/'run.tcl').write_text('run 1000ms\nquit\n')
   args=[BIN/'xsim','candidate','--tclbatch','run.tcl','--log','simulate.log']
   params={'costvectors':inp/'cost_vectors.txt','qstate0':qinp/'connections.bin','qstatelog':d/'qstate_axi.txt','postvectors':inp/'post_vectors.txt','cost0':d/'cost.bin','costlog':d/'cost_axi.txt','graph0':graph/'offsets.u32le','graph1':graph/'edges.u32le','graph2':inp/'graph_attrs.rrt32','graphlog':d/'graph_axi.txt','design0':d/'design.bin','designlog':d/'design_axi.txt','tables0':tables/'rows.bin','tables1':tables/'columns.bin','tableslog':d/'table_axi.txt','labels0':d/'labels.bin','labelslog':d/'label_axi.txt','owners0':d/'owners.bin','ownerslog':d/'owner_axi.txt','vectors':inp/'vectors.txt','output':d/'observed.txt','limit':limit}
   for k,v in params.items():args+=['--testplusarg',k+'='+str(v)]
   for stage,argv in [('compile',[BIN/'xvlog','--sv']+(['--define',define]if define else [])+rtl),('elaborate',[BIN/'xelab','tb_candidate_cost23','-s','candidate','--debug','typical','--mt','2']),('simulate',args)]:
    start=time.monotonic();row={'stage':stage,'argv':list(map(str,argv))};cm['commands'].append(row);save()
    with (d/(stage+'.stdout.log')).open('w')as f:row['exit_code']=subprocess.call(row['argv'],cwd=d,stdout=f,stderr=subprocess.STDOUT)
    row['elapsed_s']=time.monotonic()-start;save();assert row['exit_code']==0,(case,stage)
   log=(d/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('CANDIDATE_COST23_PASS ')];assert len(hits)==1 and 'CENTER_LIFETIME_PASS 'in log and 'PREFETCH_INPUTS_PASS 'in log and 'POSTPREV_INPUTS_PASS 'in log and 'COST23_INPUTS_PASS 'in log and 'Fatal:'not in log and '$finish called'in log,log[-3000:]
   assert sha(d/'owners.bin')==sha(inp/'owners.bin')
   assert sha(d/'cost.bin')==sha(inp/'cost.bin')
   if not limit:assert sha(d/'design.bin')==sha(inp/'expected_design.bin')
   cm.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in ['.bin','.txt','.log','.tcl']});save();print(hits[0],flush=True)
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
