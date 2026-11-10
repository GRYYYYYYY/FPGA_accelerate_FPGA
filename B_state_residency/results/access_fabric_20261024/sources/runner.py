from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();inp=ROOT/'results/access_fabric_inputs_20261024';im=read(inp/'manifest.json');assert im['status']=='passed'
 m={'status':'running','sources':{},'gates':{},'cases':{},'inputs':str(inp),'scope':'Actual resident access HLS + dispatch + shared paged labels and graph/table coordinate service. Ownership queries 4/6 use an explicit count/occupancy model; physical occupancy, metadata production and full routing not yet integrated.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 def freeze(p,n):
  q=src/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][n]={'path':str(p),'sha256':sha(p)};return q
 rtl=[]
 for name,pre in [('coordinate_service_v2_20261024','coordinate'),('access_service_20261024','access')]:
  dep=ROOT/'results'/name;dm=read(dep/'manifest.json');g=read(dep/'source_bound_audit.json');assert g['status']=='passed'and g['manifest_sha256']==sha(dep/'manifest.json')
  for n in ['manifest.json','source_bound_audit.json']:m['gates'][str(dep/n)]=sha(dep/n)
  for n,s in dm['sources'].items():
   if not n.endswith(('.v','.sv'))or Path(n).name.startswith('tb_'):continue
   p=dep/'sources'/n;assert sha(p)==s['sha256'];rtl.append(freeze(p,pre+'/'+n))
 for p in (ROOT/'hardware/variants/access_fabric_v1').iterdir():
  if p.is_file():
   q=freeze(p,'fabric/'+p.name)
   if q.suffix in ['.v','.sv']:rtl.append(q)
 for n,h in im['artifacts'].items():assert sha(inp/n)==h
 m['gates'][str(inp/'manifest.json')]=sha(inp/'manifest.json');freeze(Path(__file__),'runner.py');m['rtl']=[str(p.relative_to(src))for p in rtl];save()
 try:
  for case,fixture,define in [('synthetic','synthetic',None),('real','real',None),('pressure','synthetic','PRESSURE')]:
   d=out/case;d.mkdir();meta=im['cases'][fixture];gp=Path(meta['graph']);tp=Path(meta['tables']);ids=None
   contexts=(inp/fixture/'contexts.txt').read_text().splitlines();vectors=(inp/fixture/'vectors.txt').read_text().splitlines()
   if case=='pressure':
    ids={int(s.split()[0])for s in contexts if int(s.split()[0])%19==0};contexts=[s for s in contexts if int(s.split()[0])in ids];vectors=[s for s in vectors if int(s.split()[1])in ids]
   (d/'vectors.txt').write_text('\n'.join(vectors)+'\n');(d/'contexts.txt').write_text('\n'.join(contexts)+'\n');(d/'labels.bin').write_bytes(bytes(3145728));(d/'run.tcl').write_text('run 1000ms\nquit\n')
   cm=m['cases'][case]={'status':'running','fixture':fixture,'define':define,'case_ids':sorted(ids)if ids else None,'commands':[]};save()
   params={'graph0':gp/'offsets.u32le','graph1':gp/'edges.u32le','graph2':gp/'nodes.rrt32','graphlog':d/'graph_axi.txt','tables0':tp/'rows.bin','tables1':tp/'columns.bin','tableslog':d/'table_axi.txt','labels0':d/'labels.bin','labelslog':d/'label_axi.txt','vectors':d/'vectors.txt','contexts':d/'contexts.txt','output':d/'observed.txt',**{k:meta[k]for k in ['nodes','edges','rows','columns']}}
   args=[BIN/'xsim','test','--tclbatch','run.tcl','--log','simulate.log']
   for k,v in params.items():args+=['--testplusarg',k+'='+str(v)]
   for stage,argv in [('compile',[BIN/'xvlog','--sv']+(['--define',define]if define else [])+rtl),('elaborate',[BIN/'xelab','tb_access_fabric','-s','test','--debug','typical','--mt','2']),('simulate',args)]:
    c={'stage':stage,'argv':list(map(str,argv))};cm['commands'].append(c);save();t=time.monotonic()
    with (d/(stage+'.stdout.log')).open('w')as log:c['exit_code']=subprocess.call(c['argv'],cwd=d,stdout=log,stderr=subprocess.STDOUT)
    c['elapsed_s']=time.monotonic()-t;save();assert c['exit_code']==0,(case,stage)
   log=(d/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('ACCESS_FABRIC_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,log[-2500:]
   cm.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in ['.log','.tcl','.txt','.bin']});save();print(case,hits[0],flush=True)
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
