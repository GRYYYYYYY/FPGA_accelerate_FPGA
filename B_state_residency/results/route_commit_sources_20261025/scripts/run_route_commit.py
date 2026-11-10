from pathlib import Path
import json,hashlib,shutil,struct,mmap,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();v=ROOT/'hardware/variants/route_commit_v1';sources={}
 for p in [v/'route_commit_controller.sv',v/'tb_route_commit.sv',Path(__file__)]:shutil.copyfile(p,src/p.name);sources[p.name]=sha(src/p.name)
 captures=[ROOT/'results/natural_query_v2',ROOT/'results/followup_q2_v1'];rows=[]
 for phase,(capture,sink)in enumerate(zip(captures,[150697,128009])):
  assert json.loads((capture/'source_bound_audit.json').read_text())['status']=='passed'
  with(capture/'search_final_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as mm:
   node=sink;seen=set()
   while node!=0xffffffff:
    assert node not in seen;seen.add(node);r=struct.unpack_from('<11I',mm,node*44);payload=sum(x<<(32*i)for i,x in enumerate([r[0],r[1],r[3],r[4],r[5]]));rows.append(f'{phase} {node} {payload:040x}\n');node=r[3]
  assert len(seen)==8
 (out/'labels.txt').write_text(''.join(rows));(out/'run.tcl').write_text('run 1ms\nquit\n')
 m=dict(status='running',sources=sources,captures={str(p):sha(p/'source_bound_audit.json')for p in captures},commands=[],scope='New synthesizable route controller, actual CPU label payloads in registered mock label/owner services, not full real graph/AXI integration.')
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  cmds=[('compile',[BIN/'xvlog','--sv',src/'route_commit_controller.sv',src/'tb_route_commit.sv']),('elaborate',[BIN/'xelab','tb_route_commit','-s','route','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','route','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','labels='+str(out/'labels.txt'),'--testplusarg','events='+str(out/'events.txt')])]
  for stage,cmd in cmds:
   t=time.monotonic();cmd=list(map(str,cmd))
   with(out/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(cmd,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   m['commands'].append(dict(stage=stage,argv=cmd,exit_code=r.returncode,elapsed_s=time.monotonic()-t));save();assert r.returncode==0,stage
  log=(out/'simulate.log').read_text();assert 'ROUTE_COMMIT_PASS checks='in log and 'Fatal:'not in log and '$finish called'in log
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('ROUTE_COMMIT_SIM_PASSED')
if __name__=='__main__':main()
