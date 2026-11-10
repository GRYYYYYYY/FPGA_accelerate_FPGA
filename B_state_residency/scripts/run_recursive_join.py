from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();base=ROOT/'results/candidate_recursive_pilot_20261025';bm=json.loads((base/'manifest.json').read_text());bg=json.loads((base/'source_bound_audit.json').read_text());assert bm['status']==bg['status']=='passed'and bg['manifest_sha256']==sha(base/'manifest.json')
 inp=Path(sys.argv[2]).resolve();im=json.loads((inp/'manifest.json').read_text());ig=json.loads((inp/'source_bound_audit.json').read_text());assert im['status']==ig['status']=='passed'and ig['manifest_sha256']==sha(inp/'manifest.json')
 m={'status':'running','sources':{},'cases':{},'input':str(inp),'input_manifest_sha256':sha(inp/'manifest.json'),'base_manifest_sha256':sha(base/'manifest.json'),'base_audit_sha256':sha(base/'source_bound_audit.json'),'scope':'Explicit synthetic five-node mapped across label pages; actual full recursive candidate/geometry/cost/native commit/OFFER path. No board performance or natural-route claim.'}
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
 rtl.append(freeze(ROOT/'hardware/variants/candidate_recursive_v1/tb_recursive_join.sv','tb_recursive_join.sv'));freeze(Path(__file__),'runner.py');m['rtl']=[str(p.relative_to(src))for p in rtl];save()
 try:
  for case,define in [('full',None),('pressure','PRESSURE')]:
   d=out/case;d.mkdir();cm=m['cases'][case]={'status':'running','commands':[]};save()
   for n in ['design.bin','owners.bin','cost.bin']:shutil.copyfile(inp/n,d/n)
   with(d/'labels.bin').open('wb')as f:f.truncate(3145728)
   for p in src.rglob('*.dat'):shutil.copyfile(p,d/p.name)
   (d/'run.tcl').write_text('run 10ms\nquit\n')
   args=[BIN/'xsim','joined','--tclbatch','run.tcl','--log','simulate.log']
   params={'graph0':inp/'offsets.u32le','graph1':inp/'edges.u32le','graph2':inp/'nodes.rrt32','graphlog':d/'graph_axi.txt','design0':d/'design.bin','designlog':d/'design_axi.txt','tables0':inp/'rows.bin','tables1':inp/'columns.bin','tableslog':d/'table_axi.txt','labels0':d/'labels.bin','labelslog':d/'label_axi.txt','owners0':d/'owners.bin','ownerslog':d/'owner_axi.txt','cost0':d/'cost.bin','costlog':d/'cost_axi.txt','qstate0':inp/'connections.bin','qstatelog':d/'qstate_axi.txt','costvectors':inp/'cost_vectors.txt','finallabels':inp/'final_labels.txt'}
   for k,v in params.items():args+=['--testplusarg',k+'='+str(v)]
   stages=[('compile',[BIN/'xvlog','--sv']+(['--define',define]if define else[])+rtl),('elaborate',[BIN/'xelab','tb_candidate_offer','-s','joined','--debug','typical','--mt','2']),('simulate',args)]
   for stage,argv in stages:
    start=time.monotonic();argv=list(map(str,argv))
    with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=240)
    cm['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,(case,stage)
   log=(d/'simulate.log').read_text();hits=[l for l in log.splitlines()if l.startswith('RECURSIVE_JOIN_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and '$finish called'in log,log[-3000:]
   assert sha(d/'design.bin')==sha(inp/'expected_design.bin');assert sha(d/'owners.bin')==sha(inp/'owners.bin') and sha(d/'cost.bin')==sha(inp/'cost.bin')
   cm.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in ['.bin','.log','.tcl','.txt']});save();print(case,hits[0],flush=True)
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:save()
if __name__=='__main__':main()
