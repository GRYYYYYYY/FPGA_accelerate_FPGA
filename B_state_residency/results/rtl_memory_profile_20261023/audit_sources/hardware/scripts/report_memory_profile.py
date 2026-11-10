"""Audit passive cycle accounting against frozen real vectors and baseline run."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,hashlib,json,math,re,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def audit(out):
 inputs=json.loads((out/'inputs.json').read_text());parent=Path(inputs['parent'])
 if sha(parent)!=inputs['parent_sha256']:raise ValueError('Parent changed')
 p=json.loads(parent.read_text())
 for name,h in inputs['files'].items():
  if sha(name)!=h or sha(out/'sources'/Path(name).relative_to(ROOT))!=h:raise ValueError('Input changed '+name)
 log=(out/'simulation_session.log').read_text()
 if '\0' in log or re.search(r'(?im)^\s*(ERROR|FATAL|Fatal):',log) or 'PROFILE_INCOMPLETE' in log:raise ValueError('Profile simulation failed')
 matches=re.findall(r'^TEST_PASS memory_endpoint (.*)$',log,re.M)
 if len(matches)!=1 or {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',matches[0])}!=p['simulation']['actual_final']:raise ValueError('Observer perturbed baseline')
 if 'PROFILE_PASS samples=10516484 accepted=77099 retired=77099' not in log or '$finish called at time : 105164880 ns' not in log:raise ValueError('Different cycle trace')
 for stage in ("'compile' step finished","'elaborate' step finished",'XSim completed.'):
  if log.count(stage)!=1:raise ValueError('Incomplete simulation stages')
 if 'Built simulation snapshot tb_memory_endpoint_profile_behav' not in (out/'final_sim/elaborate.log').read_text():raise ValueError('Missing elaboration')
 counts={}
 with (out/'profile.counts.csv').open() as f:
  for row in csv.DictReader(f):
   key=(row['group'],int(row['op']),int(row['index']))
   if key in counts:raise ValueError('Duplicate counter')
   counts[key]=int(row['cycles'])
 def group(name,n):return [counts[(name,-1,i)] for i in range(n)]
 scalar=group('scalar',19);samples=scalar[0];endpoint=group('endpoint',21)
 for name,n in (('endpoint',21),('directory',7),('codec',14),('axi',5),('service',8)):
  if sum(group(name,n))!=samples:raise ValueError('Cycle partition incomplete '+name)
 if samples!=10516484 or scalar[2:4]!=[77099]*2 or scalar[4:8]!=[472689]*4 or scalar[12:15]!=[172928,216576,308396]:raise ValueError('Wrong handshake counts')
 cmd_counts=Counter();inclusive=Counter();latencies=defaultdict(list);retire_latencies=defaultdict(list);last=0
 vectors=ROOT/'results/rtl_memory_endpoint_20261023/vectors/actual.txt'
 comparisons=0;allocations=0;owners={}
 with vectors.open() as source,(out/'profile.commands.csv').open() as trace:
  rows=list(csv.DictReader(trace))
  if len(rows)!=77099:raise ValueError('Incomplete command trace')
  for index,row in enumerate(rows):
   a=[int(x,16) for x in next(source).split()];r={k:int(v) for k,v in row.items()};op=a[0]
   if (r['index'],r['op'],r['query'],r['page'])!=(index,op,a[3],a[2]):raise ValueError('Command trace reordered')
   start,available,end=r['accept_cycle'],r['response_cycle'],r['retire_cycle']
   if not last<start<available<=end or end-available!=4:raise ValueError('Invalid response timing')
   cmd_counts[op]+=1;inclusive[op]+=end-start+1;latencies[op].append(available-start);retire_latencies[op].append(end-start);last=end
   if op in (5,6):
    key=(a[2],a[3],a[4])
    if op==5 and key not in owners:
     comparisons+=len(owners);owners[key]=len(owners);allocations+=1
    else:
     if key not in owners:raise ValueError('Unknown lookup owner')
     comparisons+=owners[key]+1
   if op==11:owners.clear()
  if source.read().strip():raise ValueError('Missing commands')
 if last!=samples or sum(inclusive.values())+scalar[1]!=samples:raise ValueError('Command cycle conservation failed')
 for op in range(16):
  if sum(counts[('operation',op,s)] for s in range(21))!=inclusive[op]:raise ValueError('Per-operation accounting mismatch')
 for state in range(1,21):
  if sum(counts[('operation',op,state)] for op in range(16))!=endpoint[state]:raise ValueError('State attribution mismatch')
 if sum(counts[('operation',op,0)] for op in range(16))+scalar[1]!=endpoint[0]:raise ValueError('Idle accounting mismatch')
 directory=group('directory',7)
 if directory[1:3]!=[comparisons]*2 or directory[3]!=allocations:raise ValueError('Independent lookup work mismatch')
 names=['IDLE','Q_HOST_SEND','Q_HOST_WAIT','M_LOOK_SEND','M_LOOK_WAIT','Q_START_SEND','Q_START_WAIT','M_TRANSFER_SEND','WB_EXPORT_SEND','WB_EXPORT_WAIT','WB_PUT','RF_GET','RF_BEAT_SEND','RF_BEAT_WAIT','M_STATUS','Q_COMPLETE_SEND','Q_COMPLETE_WAIT','M_RETIRE_SEND','M_RETIRE_WAIT','M_RECYCLE_SEND','M_RECYCLE_WAIT']
 def stats(values):
  values=sorted(values);return dict(count=len(values),sum=sum(values),mean=sum(values)/len(values),p50=values[math.ceil(.5*len(values))-1],p95=values[math.ceil(.95*len(values))-1],maximum=values[-1])
 opstats={str(op):dict(response_latency=stats(latencies[op]),retire_latency=stats(retire_latencies[op]),inclusive_cycles=inclusive[op]) for op in sorted(cmd_counts)}
 phase_sets={'idle_and_response_hold':[0],'ordinary_page_commands':[1,2],'owner_lookup':[3,4],'transfer_start':[5,6,7],'write_export_and_feed':[8,9,10],'read_decode_and_beat':[11,12,13],'memory_completion_wait':[14],'page_complete_and_address_retire':[15,16,17,18],'address_recycle':[19,20]}
 phases={name:dict(cycles=sum(endpoint[i] for i in indices),fraction=sum(endpoint[i] for i in indices)/samples) for name,indices in phase_sets.items()}
 codec=group('codec',14)
 serialized_codec_work=sum(codec[i] for i in (2,3,4,5,8,11,12))
 files=dict(inputs['files']);script=Path(__file__).resolve();files[str(script)]=sha(script);snap=out/'audit_sources'/script.relative_to(ROOT)
 if snap.exists() and sha(snap)!=sha(script):raise ValueError('Audit script changed')
 snap.parent.mkdir(parents=True,exist_ok=True);snap.write_bytes(script.read_bytes())
 artifacts=[parent,out/'inputs.json',out/'simulation_session.log',out/'profile.counts.csv',out/'profile.commands.csv',vectors]
 artifacts.extend(x for x in (out/'final_sim').iterdir() if x.is_file())
 return dict(status='passed',simulation_cycles=samples,board_performance=None,baseline_unchanged=True,simulation=p['simulation']['actual_final'],
  endpoint_states={name:dict(cycles=endpoint[i],fraction=endpoint[i]/samples) for i,name in enumerate(names)},phases=phases,
  operation_latencies=opstats,overlapping_submodules=dict(directory=directory,codec=codec,axi=group('axi',5),record_service=group('service',8)),
  observations=dict(independent_scan_comparisons=comparisons,directory_scan_cycles=2*comparisons,allocations=allocations,serialized_codec_state_cycles=serialized_codec_work,serialized_codec_fraction=serialized_codec_work/samples,
   page_queue_roundtrips=scalar[4],record_inputs=scalar[12],record_outputs=scalar[13],host_response_stalls=scalar[14],axi_aw_stalls=scalar[15],axi_w_stalls=scalar[16],axi_ar_stalls=scalar[17],axi_r_stalls=scalar[18]),
  files=files,artifacts={str(x):sha(x) for x in artifacts},
  scope='Passive pre-edge cycle census of the fixed 19-small-query RTL test. Endpoint phases are mutually exclusive; module-state activity overlaps and cannot be added to infer speedup. Fixed scheduling and synthetic AXI timings, no clock closure or board result.')
if __name__=='__main__':
 out=Path(sys.argv[1]).resolve();record=audit(out);path=out/'manifest.json'
 if path.exists() and json.loads(path.read_text())!=record:raise ValueError('Do not overwrite different evidence')
 path.write_text(json.dumps(record,indent=2)+'\n')
 summary={k:record[k] for k in ('status','simulation_cycles','baseline_unchanged','phases','observations')};summary['manifest_sha256']=sha(path)
 (out/'completion_audit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
