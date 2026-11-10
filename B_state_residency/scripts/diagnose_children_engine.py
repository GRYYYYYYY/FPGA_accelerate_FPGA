"""Preserve first request fields before/after a delta-cycle settle; do not modify tested RTL."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=ROOT/'results/children_engine_20261024';out=ROOT/'results/children_engine_diagnose_20261024';out.mkdir()
 cm=json.loads((base/'manifest.json').read_text())['cases']['gen3'];original=base/'sources/engine/tb_children_build_engine.sv'
 s=original.read_text();needle='                    wait(svc_valid);\n'
 display='$display("FIELDS time=%0t gen=%h/%h parent=%h/%h pos=%h/%h phase=%h/%h node=%h/%h emitted=%h/%h count=%h/%h prune=%h/%h query=%h/%h price=%h/%h",$time,svc_generation,expected_gen,svc_parent,header[0],svc_position,event_row[1],svc_phase,event_row[0],svc_node,event_row[2],svc_emitted,emitted_model,svc_count,header[1],svc_prune,header[2],svc_query,header[3],svc_price,header[4]);'
 assert s.count(needle)==1;s=s.replace(needle,needle+'                    if(index==0&&k==0)begin '+display+' #1; '+display+' end\n')
 tb=out/original.name;tb.write_text(s);(out/'run.tcl').write_text('run 1ms\nquit\n')
 m={'status':'running','original_tb_sha256':sha(original),'diagnostic_tb_sha256':sha(tb),'commands':[]}
 for command in cm['commands']:
  stage=command['stage'];argv=[str(tb)if x==str(original)else x for x in command['argv']]
  with (out/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT)
  m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode});assert r.returncode==0
 m['status']='finished';m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()};(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print((out/'simulate.log').read_text()[-3500:])
if __name__=='__main__':main()
