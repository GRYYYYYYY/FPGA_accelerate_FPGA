from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();base=ROOT/'results/candidate_recursive_pilot_20261025';bm=json.loads((base/'manifest.json').read_text());bg=json.loads((base/'source_bound_audit.json').read_text());assert bm['status']==bg['status']=='passed'and bg['manifest_sha256']==sha(base/'manifest.json')
 inp=Path(sys.argv[2]).resolve();im=json.loads((inp/'manifest.json').read_text());ig=json.loads((inp/'source_bound_audit.json').read_text());assert im['status']==ig['status']=='passed'and ig['manifest_sha256']==sha(inp/'manifest.json')
 m={'status':'running','sources':{},'cases':{},'input':str(inp),'input_manifest_sha256':sha(inp/'manifest.json'),'base_manifest_sha256':sha(base/'manifest.json'),'base_audit_sha256':sha(base/'source_bound_audit.json'),'scope':'Same-instance two natural queries plus synthesizable route controller actual q1/q2 trace/commit and saved-path ripups via real host ports; only initial union import. Actual graph/design/access/cost/commit/OFFER/EARLY. No board performance claim.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 def freeze(p,name):
  q=src/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][name]={'path':str(p),'sha256':sha(q)};return q
 rtl=[]
 for name in bm['rtl']:
  p=base/'sources'/name
  if p.name.startswith('tb_'):continue
  assert sha(p)==bm['sources'][name]['sha256'];rtl.append(freeze(p,name))
 for name,v in bm['sources'].items():
  if name.endswith('.dat'):assert sha(base/'sources'/name)==v['sha256'];freeze(base/'sources'/name,name)
 for p in [ROOT/'hardware/variants/route_commit_v1/route_commit_controller.sv',ROOT/'hardware/variants/route_commit_join_drain_v2/route_commit_host_adapter.sv',ROOT/'hardware/variants/route_commit_join_drain_v2/axi_drain_watch.sv']:rtl.append(freeze(p,p.name))
 rtl.append(freeze(ROOT/'hardware/variants/route_commit_join_drain_v2/tb_route_join_drain.sv','tb_route_join_drain.sv'));freeze(Path(__file__),'runner.py');m['rtl']=[str(p.relative_to(src))for p in rtl];save()
 try:
  oracle=Path('/tmp/B_state_residency_offer_20261025/continuous_oracle_v1');og=json.loads((oracle/'source_bound_audit.json').read_text());assert og['status']=='passed' and og['input_audit_sha256']==sha(inp/'source_bound_audit.json')
  graph=ROOT/'results/graph_image_20261024';m['oracle_audit_sha256']=sha(oracle/'source_bound_audit.json');m['graph_audit_sha256']=sha(graph/'source_bound_audit.json');save()
  import struct
  for source,target in [('initial_label_imports.u32','imports.txt'),('expected_label_reads.u32','finals.txt'),('prepared.u32','prepared.txt'),('final2.u32','finals2.txt')]:
   data=(oracle/source).read_bytes();(out/target).write_text(''.join(str(row[0])+' '+ ' '.join(f'{v:08x}'for v in row[1:])+'\n' for row in struct.iter_unpack('<6I',data)))
  cpu=Path(json.loads((inp/'manifest.json').read_text())['base']);lines=(cpu/'events.txt').read_text().splitlines();cand=[];polls=[]
  for i,line in enumerate(lines):
   if line.startswith('C '):
    v=list(map(int,line.split()[1:]));act=int(i+1<len(lines)and lines[i+1].startswith('W '));cand.append(f'{v[0]} {v[1]} {v[2]} {act} {v[7]}\n')
   if line.startswith('P '):polls.append(line[2:]+'\n')
  (out/'candidates.txt').write_text(''.join(cand));(out/'polls.txt').write_text(''.join(polls));m['scoreboards']={n:sha(out/n)for n in ['imports.txt','finals.txt','candidates.txt','polls.txt']};save()
  q2=ROOT/'results/followup_q2_v1';q2cost=ROOT/'results/followup_q2_cost_v1';m['q2_audit_sha256']=sha(q2/'source_bound_audit.json');m['q2_cost_audit_sha256']=sha(q2cost/'source_bound_audit.json')
  lines2=(q2/'events.txt').read_text().splitlines();cand2=[];polls2=[]
  for i,line in enumerate(lines2):
   if line.startswith('C '):
    v=list(map(int,line.split()[1:]));act=int(i+1<len(lines2)and lines2[i+1].startswith('W '));cand2.append(f'{v[0]} {v[1]} {v[2]} {act} {v[7]}\n')
   if line.startswith('P '):polls2.append(line[2:]+'\n')
  (out/'candidates2.txt').write_text(''.join(cand2));(out/'polls2.txt').write_text(''.join(polls2));m['scoreboards'].update({n:sha(out/n)for n in ['prepared.txt','finals2.txt','candidates2.txt','polls2.txt']});save()
  for case,define in [('full',None),('pressure','PRESSURE')]:
   d=out/case;d.mkdir();cm=m['cases'][case]={'status':'running','commands':[]};save()
   for n in ['design.bin','owners.bin','cost.bin']:shutil.copyfile(inp/n,d/n)
   with(d/'owners.bin').open('ab')as f:f.write((inp/'owner_allocator.bin').read_bytes())
   with(d/'labels.bin').open('wb')as f:f.truncate(3145728)
   for p in src.rglob('*.dat'):shutil.copyfile(p,d/p.name)
   (d/'run.tcl').write_text('run 30ms\nquit\n')
   args=[BIN/'xsim','joined','--tclbatch','run.tcl','--log','simulate.log']
   params={'graph0':graph/'offsets.u32le','graph1':graph/'edges.u32le','graph2':graph/'nodes.rrt32','graphlog':d/'graph_axi.txt','design0':d/'design.bin','designlog':d/'design_axi.txt','tables0':inp/'rows.bin','tables1':inp/'columns.bin','tableslog':d/'table_axi.txt','labels0':d/'labels.bin','labelslog':d/'label_axi.txt','owners0':d/'owners.bin','ownerslog':d/'owner_axi.txt','cost0':d/'cost.bin','costlog':d/'cost_axi.txt','qstate0':inp/'connections.bin','qstatelog':d/'qstate_axi.txt','costvectors':inp/'cost_vectors.txt','finallabels':out/'finals.txt','imports':out/'imports.txt','candidates':out/'candidates.txt','polls':out/'polls.txt','prepared':out/'prepared.txt','cost2':q2cost/'cost_vectors.txt','candidates2':out/'candidates2.txt','polls2':out/'polls2.txt','finals2':out/'finals2.txt'}
   for k,v in params.items():args+=['--testplusarg',k+'='+str(v)]
   stages=[('compile',[BIN/'xvlog','--sv']+(['--define',define]if define else[])+rtl),('elaborate',[BIN/'xelab','tb_candidate_offer','-s','joined','--debug','typical','--mt','2']),('simulate',args)]
   for stage,argv in stages:
    start=time.monotonic();argv=list(map(str,argv))
    with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=600)
    cm['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,(case,stage)
   log=(d/'simulate.log').read_text();hits=[l for l in log.splitlines()if l.startswith('NATURAL_QUERY_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and '$finish called'in log,log[-3000:]
   assert (d/'owners.bin').read_bytes()==(inp/'owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes();assert sha(d/'cost.bin')==sha(inp/'cost.bin')
   cm.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in ['.bin','.log','.tcl','.txt']});save();print(case,hits[0],flush=True)
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:save()
if __name__=='__main__':main()
