"""Audit the integrated build controller, collector and actual generated HLS regression."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/children_engine_v2_20261024';m=read(out/'manifest.json');assert m['status']=='passed'
 for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']==sha(Path(spec['path']))
 for path,digest in m['gates'].items():assert sha(Path(path))==digest and read(Path(path))['status']=='passed'
 hls=ROOT/'results/children_hls_20261024';h=read(hls/'source_bound_audit.json');assert h['manifest_sha256']==sha(hls/'manifest.json')
 for bits in [32,3]:
  for name,digest in h['cases'][str(bits)]['generated_rtl_artifacts'].items():assert sha(out/f'sources/hls{bits}'/name)==digest
 hm=read(hls/'manifest.json')
 for name,spec in m['sources'].items():
  if name.startswith('oracle/'):
   filename=Path(name).name
   if filename=='original_testbench.cpp':filename='testbench.cpp'
   part='src'if filename in ['kernel_hls.cpp','children_port.hpp','children_machine.hpp']else'tb'
   assert spec['sha256']==hm['sources'][f'rearchitect/v1/{part}/{filename}']
 for name,digest in m['oracle'].items():assert sha(out/name)==digest
 assert [c['stage']for c in m['commands']]==['oracle_build','oracle_run'] and all(c['exit_code']==0 for c in m['commands'])
 # Independently parse all records and check phase/position/node/output-count transitions.
 totals=Counter();selected={};phase_counts=Counter()
 with (out/'vectors.txt').open()as f:
  for index in range(93728):
   head=[int(v,16)for v in next(f).split()];assert len(head)==8
   parent,count,prune,query,price,emitted,n,cookie=head
   assert parent<2**24 and count<=18 and prune in [0,1] and query==index%4 and price==index%16 and cookie==index+1
   phase=0 if count else 5 if prune else 7;pos=0;node=parent;kept=0;alive=False
   for _ in range(n):
    event=[int(v,16)for v in next(f).split()];assert len(event)==5
    p,i,nd,value,aux=event;assert (p,i,nd)==(phase,pos,node)
    phase_counts[p]+=1;advance=False
    if p==0:
     assert value<2**24 and aux in [0,1]
     if prune and not aux:alive=True
     phase=1;node=value
    elif p==1:
     assert value in [0,1] and aux==0
     if value:advance=True
     else:phase=2
    elif p==2:
     assert value==aux==0;phase=3
    elif p==3:
     assert value in [0,1] and aux in [0,1]
     if value or (prune and aux):advance=True
     else:phase=4
    elif p==4:
     assert value==aux==0;kept+=1;advance=True
    elif p==5:
     assert value in [0,1] and aux==0;phase=6 if value else 7
    elif p==6:
     assert value==aux==0;phase=7
    elif p==7:
     assert value==aux==0;phase=8;node=0
    else:raise AssertionError('service after publish')
    if advance:
     pos+=1;node=parent;phase=0 if pos<count else 5 if prune and not alive else 7
   assert phase==8 and pos==count and kept==emitted
   totals['builds']+=1;totals['services']+=n;totals['emissions']+=emitted
   if index+1 in [7,1024,93728]:selected[index+1]=dict(totals)
  assert not f.read().strip()
 assert dict(totals)=={'builds':93728,'services':813439,'emissions':46896}
 assert dict(phase_counts)=={0:252794,1:252794,2:66833,3:66833,4:46896,5:32917,6:644,7:93728}
 defs={'collector':None,'gen3':'GEN3','pilot':'PILOT','full':None};results={}
 assert set(m['cases'])==set(defs)
 for case,define in defs.items():
  c=m['cases'][case];assert c['status']=='passed' and c['define']==define
  assert [x['stage']for x in c['commands']]==['compile','elaborate','simulate'] and all(x['exit_code']==0 for x in c['commands'])
  argv=c['commands'][0]['argv']
  if define:assert argv[argv.index('--define')+1]==define
  else:assert '--define'not in argv
  compiled={Path(x).relative_to(out/'sources').as_posix()for x in argv if x.endswith(('.sv','.v'))}
  if case=='collector':expected={'engine/children_hls_call.sv','engine/tb_children_hls_call.sv'}
  else:
   bits=3 if case=='gen3'else 32
   expected={f'hls{bits}/'+name for name in h['cases'][str(bits)]['generated_rtl_artifacts']if name.endswith('.v')}
   expected|={'engine/'+name for name in ['children_hls_call.sv','children_build_controller.sv','children_build_engine.sv','tb_children_build_engine.sv']}
  assert compiled==expected
  for name,digest in c['artifacts'].items():assert sha(out/case/name)==digest
  log=(out/case/'simulate.log').read_text();assert log.count(c['result'])==1 and '$finish called'in log and not re.search(r'^(Fatal:|Error:|ERROR:)',log,re.M)
  v={k:int(n)for k,n in re.findall(r'(\w+)=(\d+)',c['result'])}
  if case=='collector':assert v=={'permutations':4228,'coherent_calls':4229,'fault_cases':19}
  elif case=='gen3':assert v=={'builds':14,'services':selected[7]['services']*2,'hls_calls':100,'responses':84,'errors':2,'checks':16}
  else:
   size=1024 if case=='pilot'else 93728;oracle=selected[size]
   assert v['builds']==size and v['services']==oracle['services'] and v['errors']==26 and v['checks']==size+27
   assert v['hls_calls']==size+oracle['services']+114 and v['responses']==oracle['services']+88 and v['blocked']>2*oracle['services']
  results[case]=v
 # Preserve and explicitly diagnose the first failed observation, without changing RTL.
 bad=ROOT/'results/children_engine_20261024';bm=read(bad/'manifest.json');assert bm['status']=='failed'
 assert 'Time: 155 ns' in (bad/'gen3/simulate.log').read_text() and 'Fatal: service disagrees' in (bad/'gen3/simulate.log').read_text()
 for name,spec in bm['sources'].items():
  if name not in ['engine/tb_children_build_engine.sv','runner.py']:assert sha(out/'sources'/name)==spec['sha256']
 old=(bad/'sources/engine/tb_children_build_engine.sv').read_text();new=(out/'sources/engine/tb_children_build_engine.sv').read_text()
 assert new==old.replace('wait(svc_valid);','wait(svc_valid);@(negedge clk);')
 diag=ROOT/'results/children_engine_diagnose_20261024';dm=read(diag/'manifest.json');assert dm['status']=='finished'
 for name,digest in dm['artifacts'].items():assert sha(diag/name)==digest
 dl=(diag/'simulate.log').read_text()
 assert 'time=155000 gen=00000000/00000001'in dl and 'time=156000 gen=00000001/00000001'in dl and 'Time: 255 ns'in dl
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'oracle':dict(totals),'phase_counts':dict(phase_counts),'cases':results,'negative_manifest_sha256':sha(bad/'manifest.json'),'diagnostic_manifest_sha256':sha(diag/'manifest.json'),'recovery_rtl_unchanged':True,'scope':m['scope']}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
