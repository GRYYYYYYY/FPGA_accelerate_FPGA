from pathlib import Path
from collections import Counter
import hashlib,json,struct,mmap,sys,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 unit=Path(sys.argv[1]).resolve();syn=Path(sys.argv[2]).resolve();m=json.loads((unit/'manifest.json').read_text());assert m['status']=='passed'
 for n,h in m['sources'].items():assert sha(unit/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(unit/n)==h
 assert len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
 log=(unit/'simulate.log').read_text();assert 'ROUTE_COMMIT_PASS checks=25'in log and 'Fatal:'not in log and '$finish called'in log
 expected=[];paths=[]
 for phase,(capture,sink)in enumerate(zip(m['captures'],[150697,128009])):
  p=Path(capture);assert sha(p/'source_bound_audit.json')==m['captures'][capture];chain=[]
  with(p/'search_final_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as mm:
   node=sink
   while node!=0xffffffff:
    assert node not in chain;chain.append(node);v=struct.unpack_from('<11I',mm,node*44);words=[v[0],v[1],v[3],v[4],v[5]];expected.append([str(phase),str(node),f'{sum(x<<(32*j)for j,x in enumerate(words)):040x}']);node=v[3]
  paths.append(chain[1:-1])
 assert list(map(str.split,(unit/'labels.txt').read_text().splitlines()))==expected
 rows=[l.split()for l in(unit/'events.txt').read_text().splitlines()];R=[[int(v)for v in t[1:]]for t in rows if t[0]=='R']
 assert len(R)==25 and R[:7]==[[0,0,6,6],[0,1,0,0],[0,0,6,6],[0,1,0,0],[0,1,0,0],[0,0,6,6],[0,0,6,6]]
 assert R[7:18]==[[1,2,1,0],[2,2,6,0],[3,4,0,0],[4,4,0,0],[9,3,8,0],[5,5,6,1],[10,6,0,0],[10,6,6,1],[8,6,0,0],[10,6,0,0],[10,6,6,1]]
 assert R[18:]==[[11,6,0,0],[12,6,0,0],[13,6,0,0],[14,6,0,0],[15,0,0,0],[15,0,0,0],[16,0,6,6]]
 assert [[int(t[2]),int(t[3])]for t in rows if t[:2]==['L','0']]==[[int(x[0]),int(x[1])]for x in expected]
 counts=Counter();ops=[]
 for op,path in [(1,paths[0]),(1,paths[1]),(2,paths[0]),(2,paths[1])]:
  for node in path:counts[node]+=1 if op==1 else -1;ops.append([op,node,counts[node]])
 assert [[int(v)for v in t[2:]]for t in rows if t[:2]==['O','0']]==ops
 core='route_commit_controller.sv';sm=json.loads((syn/'manifest.json').read_text());assert sha(syn/'sources'/core)==sm['rtl_sha256']==sha(unit/'sources'/core)==sha(ROOT/'hardware/variants/route_commit_v1'/core)
 assert sha(syn/'synth.tcl')==sm['tcl_sha256']
 slog=(syn/'vivado.log').read_text();assert 'ROUTE_COMMIT_SYNTH_DONE'in slog and 'synth_design completed successfully'in slog and not re.search(r'^ERROR:',slog,re.M)
 report=(syn/'utilization.rpt').read_text();assert 'Vivado v.2022.2'in report and 'Synthesized'in report and 'xcu280-fsvh2892-2L-e'in report
 def number(label):return int(re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*(\d+)',report,re.M)[1])
 util={key:number(label)for key,label in [('LUT','CLB LUTs*'),('FF','CLB Registers'),('latches','Register as Latch'),('BRAM','Block RAM Tile'),('DSP','DSPs')]};assert util['latches']==util['BRAM']==util['DSP']==0
 warnings=Counter(re.findall(r'^WARNING: \[([^]]+)\]',slog,re.M));assert set(warnings)<=set(['Synth 8-7129','Synth 8-7080','Synth 8-3917','Netlist 29-101'])
 assert (syn/'synth.dcp').stat().st_size>1000 and (syn/'synth.v').stat().st_size>1000
 ug=dict(status='passed',manifest_sha256=sha(unit/'manifest.json'),auditor_sha256=sha(Path(__file__)),checks=25,paths=paths,scope='Synthesizable controller with real CPU label payloads in registered mock services; saved slots, shared refs, corruption/timeout/abort/context/backpressure boundaries. No actual pager/owner AXI or whole-search integration.')
 (unit/'source_bound_audit.json').write_text(json.dumps(ug,indent=2)+'\n')
 sg=dict(status='passed',manifest_sha256=sha(syn/'manifest.json'),auditor_sha256=sha(Path(__file__)),utilization=util,warnings=dict(warnings),files={str(p.relative_to(syn)):sha(p)for p in syn.rglob('*')if p.is_file()and p.name!='source_bound_audit.json'},scope='Default MAX_PATH32/two slots OOC synthesis. Unit sim MAX_PATH8. No constraints/placement/route/Fmax or resource feasibility of whole accelerator.')
 (syn/'source_bound_audit.json').write_text(json.dumps(sg,indent=2)+'\n');print(json.dumps(dict(unit=ug,synthesis=sg),indent=2))
if __name__=='__main__':main()
