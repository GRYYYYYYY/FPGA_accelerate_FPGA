from pathlib import Path
import json,hashlib,shutil,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();m={'status':'running','sources':{},'commands':[],'scope':'Host bit-exact characterization of net-center distance, extracted original float expression vs integer binary32 helper. Actual values sampled from graph/net import, not live evaluateCost trace, HLS or joined packet proof.'}
 for p in [*(ROOT/'hardware/hls/cost_center/v1').glob('*'),ROOT/'hardware/hls/search_cost/exact_v2/softfloat32.hpp']:
  rel=Path('hls/search_cost/exact_v2/softfloat32.hpp')if p.name=='softfloat32.hpp'else Path('hls/cost_center/v1')/p.name;q=src/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][str(rel)]={'path':str(p),'sha256':sha(p)}
 original=ROOT/'results/graph_image_20261024/reference/trace.cpp';s=original.read_text();a=s.index('        float distToCenter = std::abs(getEndTileXCoordinate(id) - nw.xCenter) +');b=s.index('        float biasCost',a);fragment=s[a:b];assert 'getEndTileYCoordinate(id) - nw.yCenter'in fragment
 base=src/'hls/cost_center/v1';(base/'original_center.inc').write_text(fragment);m['original_sha256']=sha(original);m['fragment_sha256']=sha(base/'original_center.inc')
 inp=ROOT/'results/cost_state_inputs_20261025/real';layout=json.loads((inp/'layout.json').read_text());image=(inp/'initial.bin').read_bytes();(out/'net_records.bin').write_bytes(image[layout['nets_offset']:layout['nets_offset']+layout['net_count']*16]);m['net_sha256']=sha(out/'net_records.bin');m['input_manifest_sha256']=sha(inp.parent/'manifest.json')
 graph=ROOT/'results/graph_image_20261024/nodes.rrt32';env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 shutil.copyfile(__file__,out/'runner.py');save()
 try:
  for stage,args in [('compile',['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-fsanitize=undefined',str(base/'kernel.cpp'),str(base/'testbench.cpp'),'-o',str(out/'center')]),('execute',[str(out/'center'),str(graph),str(out/'net_records.bin'),str(layout['nodes']),str(out/'vectors.txt')])]:
   with (out/(stage+'.log')).open('w')as f:code=subprocess.call(args,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT)
   m['commands'].append({'stage':stage,'argv':args,'exit_code':code});save();assert code==0,stage
  log=(out/'execute.log').read_text();assert log.startswith('COST_CENTER_CPU_PASS ')and 'runtime error:'not in log
  m.update(status='passed',result=log.strip(),vectors_sha256=sha(out/'vectors.txt'),artifacts={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'});save();print(log.strip())
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
