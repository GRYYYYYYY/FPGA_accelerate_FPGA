"""Small-equivalence pilot then full actual checkpoint streaming RTL replay."""
from pathlib import Path
import argparse,json,subprocess,re,hashlib
from make_checkpoint_stream_tb import generate
ROOT=Path(__file__).resolve().parents[2];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--full',action='store_true');a=ap.parse_args()
 out=a.output.resolve();out.mkdir();sources=out/'sources';sources.mkdir()
 vdir=ROOT/('results/checkpoint_vectors_'+('full' if a.full else 'small')+'_20261023');vp=vdir/'manifest.json';v=json.loads(vp.read_text())
 assert v['status']=='passed' and sha(vp)==json.loads((vdir/'completion_audit.json').read_text())['manifest_sha256']
 for name,digest in v['artifacts'].items():assert sha(vdir/name)==digest
 expected=(21662794,2743929,38,31) if a.full else (77099,6086,19,0)
 assert (v['public_commands'],v['transfers'],v['queries'],v['counts'].get('12',0))==expected
 parent=ROOT/'results/rtl_retained_endpoint_pilot_20261023/manifest.json';pm=json.loads(parent.read_text())
 assert sha(parent)=='e6c446cd38f6fdaf9e9385bddabfaa55aee7e2ad9555b6e9a02934c7c95ab0fe'
 tb=ROOT/'hardware/tb/tb_memory_endpoint_checkpoint_stream_cycle64.sv';assert tb.read_text()==generate().replace('memory_endpoint_checkpoint_stream','memory_endpoint_checkpoint_stream_cycle64').replace('integer cycle=0;','longint unsigned cycle=0;')
 paths=[Path(p) for p in pm['sources'] if '/rtl/' in p]+[tb,Path(__file__).resolve(),ROOT/'hardware/scripts/make_checkpoint_stream_tb.py']
 m={'status':'running','full':a.full,'sources':{},'vector_manifest_sha256':sha(vp),'commands':[],'board_performance':None,'full_router':False}
 if a.full:
  pp=ROOT/'results/rtl_checkpoint_stream_cycle64_pilot_20261023/manifest.json';pilot=json.loads(pp.read_text());assert pilot['status']=='passed';m['pilot_sha256']=sha(pp)
 for p in paths:
  if '/rtl/' in str(p):assert sha(p)==pm['sources'][str(p)]
  if a.full:assert sha(p)==pilot['sources'][str(p)]
  (sources/p.name).write_bytes(p.read_bytes());m['sources'][str(p)]=sha(p)
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save();(out/'run.tcl').write_text('run 501s\nquit\n')
 try:
  cmds=[('compile',[BIN/'xvlog','--sv',*[sources/p.name for p in paths if p.suffix=='.sv']]),('elaborate',[BIN/'xelab','tb_memory_endpoint_checkpoint_stream_cycle64_'+('large' if a.full else 'small'),'-s','checkpoint_tb','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','checkpoint_tb','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','VECTORS='+str(vdir/'actual.txt'),'--testplusarg','PAGES='+str(vdir/'pages.hex')])]
  for stage,cmd in cmds:
   args=list(map(str,cmd))
   with (out/(stage+'.stdout.log')).open('w') as f:
    proc=subprocess.Popen(args,cwd=out,stdout=f,stderr=subprocess.STDOUT);row={'stage':stage,'argv':args,'pid':proc.pid,'exit_code':None};m['commands'].append(row);save();row['exit_code']=proc.wait();save()
   assert row['exit_code']==0,stage
  text=(out/'simulate.log').read_text();assert 'Fatal:' not in text
  lines=re.findall(r'^TEST_PASS memory_endpoint (.+)$',text,re.M);assert len(lines)==1
  counts={k:int(val) for k,val in re.findall(r'(\w+)=(\d+)',lines[0])}
  cp=re.findall(r'^STREAM_CHECKPOINT_DONE (.+)$',text,re.M);queries=re.findall(r'^STREAM_QUERY_DONE (.+)$',text,re.M)
  assert (counts['checks'],counts['transfers'],counts['fences'],len(cp))==expected and len(queries)==v['queries']
  end=int(re.search(r'\$finish called at time : (\d+) ns',text)[1])
  if not a.full:assert end==72898860
  for path,digest in m['sources'].items():assert sha(Path(path))==digest
  m.update(status='passed',counts=counts,checkpoint_receipts=cp,query_receipts=queries,end_ns=end,artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.suffix in ('.log','.tcl')});save()
  (out/'completion_audit.json').write_text(json.dumps({'status':'passed','manifest_sha256':sha(out/'manifest.json')},indent=2)+'\n');print(counts,end,flush=True)
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
