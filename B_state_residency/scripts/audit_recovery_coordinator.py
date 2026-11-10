from pathlib import Path
from collections import Counter
import json,hashlib,re,sys
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
 log=(unit/'simulate.log').read_text();assert 'RECOVERY_COORDINATOR_PASS checks=28'in log and '$finish called'in log and 'Fatal:'not in log
 rows=[l.split()for l in(unit/'events.txt').read_text().splitlines()];R=[list(map(int,t[1:]))for t in rows if t[0]=='R']
 expected=[[0,0,5,0],[0,0,1,0],[1,2,0,4],[2,2,0,4],[3,2,0,4],[4,4,5,4],[5,3,0,4],[6,3,0,4],[7,3,1,4],[0,6,0,4],[0,6,0,4],[10,6,1,4],[11,6,0,4],[12,6,0,4],[13,6,5,4]]+[[14,1,0,0]]*5+[[14,0,0,0],[15,5,0,4],[16,0,3,0],[17,0,6,0],[18,6,0,0],[19,2,0,4],[21,0,0,0],[22,4,1,1]]
 assert R==expected
 # Reconstruct first two successful episodes from the emitted physical mock ops.
 ends=[i for i,t in enumerate(rows)if t[0]=='R']
 current={(100,1):1,(100,2):2,(200,2):0,(200,1):1};wanted={(100,1):2,(100,2):0,(200,2):1,(200,1):0};mutations=0;temporary_multi_net=False
 for t in rows[:ends[0]]:
  if t[0]=='A':mode,verify,node,net,refs=map(int,t[1:]);assert mode==0 and refs==wanted[node,net]
  elif t[0]=='O':
   mode,verify,op,node,net,count=map(int,t[1:]);assert mode==0
   if op:assert verify==0;current[node,net]+=1 if op==1 else -1;mutations+=1
   assert count==current[node,net]
   if verify:assert count==wanted[node,net] and sum(current.get((node,n),0)>0 for n in [1,2])==1
   if node==100 and op==1:temporary_multi_net=sum(current.get((node,n),0)>0 for n in [1,2])==2
 assert current==wanted and mutations==5 and temporary_multi_net
 second=[t for t in rows[ends[0]+1:ends[1]]if t[0]in ['A','O']]
 assert second==[['A','0','0','100','1','3'],['O','0','0','0','100','1','2'],['O','0','0','1','100','1','3'],['A','0','1','100','1','3'],['O','0','1','0','100','1','3']]
 core='recovery_coordinator.sv';sm=json.loads((syn/'manifest.json').read_text());assert sm['status']=='passed'
 assert sha(syn/'sources'/core)==sm['rtl_sha256']==sha(unit/'sources'/core)==sha(ROOT/'hardware/variants/recovery_coordinator_v1'/core)
 assert sha(syn/'synth.tcl')==sm['tcl_sha256']
 slog=(syn/'vivado.log').read_text();assert 'RECOVERY_COORDINATOR_SYNTH_DONE'in slog and 'synth_design completed successfully'in slog and not re.search(r'^ERROR:',slog,re.M)
 report=(syn/'utilization.rpt').read_text();assert 'Vivado v.2022.2'in report and 'Synthesized'in report and 'xcu280-fsvh2892-2L-e'in report
 def number(label):return int(re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*(\d+)',report,re.M)[1])
 util={key:number(label)for key,label in [('LUT','CLB LUTs*'),('FF','CLB Registers'),('latches','Register as Latch'),('BRAM','Block RAM Tile'),('DSP','DSPs')]};assert util['latches']==util['BRAM']==util['DSP']==0
 warnings=Counter(re.findall(r'^WARNING: \[([^]]+)\]',slog,re.M));assert set(warnings)=={'Synth 8-6014','Synth 8-7080','Netlist 29-101'}
 for n in ['synth.dcp','synth.v']:assert (syn/n).stat().st_size>1000
 ug=dict(status='passed',manifest_sha256=sha(unit/'manifest.json'),auditor_sha256=sha(Path(__file__)),response_checks=28,first_episode_corrections=5,second_episode_corrections=1,temporary_multi_net_before_second_pass=temporary_multi_net,scope='Journal/reset-domain/reconfiguration and two-pass arbitrary-ref owner recovery prototype. Registered mock authority/owner plus trusted labels callback, unit ENTRIES4/MAX_CORRECTIONS4. Not real AXI coordinator integration or durable checkpoint validation.')
 (unit/'source_bound_audit.json').write_text(json.dumps(ug,indent=2)+'\n')
 sg=dict(status='passed',manifest_sha256=sha(syn/'manifest.json'),auditor_sha256=sha(Path(__file__)),utilization=util,warnings=dict(warnings),files={str(p.relative_to(syn)):sha(p)for p in sorted(syn.rglob('*'))if p.is_file()and p.name!='source_bound_audit.json'},scope='Default32 journal entries OOC synthesis only. No clock/IO constraints, place/route/Fmax, full coordinator platform or power-loss persistence.')
 (syn/'source_bound_audit.json').write_text(json.dumps(sg,indent=2)+'\n');print(json.dumps(dict(unit=ug,synthesis=sg),indent=2))
if __name__=='__main__':main()
