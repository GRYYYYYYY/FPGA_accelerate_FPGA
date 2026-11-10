"""Audit wide codec correctness, immutable composition, paired cycles and resources."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,hashlib,importlib.util,json,re,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def hashes(files):
 for p,h in files.items():
  if sha(p)!=h:raise ValueError('Changed evidence '+p)
def counters(out):
 result={}
 with (out/'profile.counts.csv').open() as f:
  for r in csv.DictReader(f):
   key=(r['group'],int(r['op']),int(r['index']))
   if key in result:raise ValueError('Duplicate profile counter')
   result[key]=int(r['cycles'])
 return result
PHASES={'idle_and_response_hold':[0],'ordinary_page_commands':[1,2],'owner_lookup':[3,4],'transfer_start':[5,6,7],'write_export_and_feed':[8,9,10],'read_decode_and_beat':[11,12,13],'memory_completion_wait':[14],'page_complete_and_address_retire':[15,16,17,18],'address_recycle':[19,20]}
def audit(out):
 build=out/'verified_build';bm=build/'build_manifest.json';b=json.loads(bm.read_text())
 if b['status']!='completed':raise ValueError('Build incomplete')
 hashes(b['files']);files=dict(b['files'])
 for p,h in files.items():
  if sha(build/'sources'/Path(p).relative_to(ROOT))!=h:raise ValueError('Frozen source mismatch')
 baseline=ROOT/'results/rtl_memory_profile_20261023';pm=baseline/'manifest.json'
 if sha(pm)!='ffb831197bb24124b95429f9d241443adf7ca8975505c04a7f5745ff0365e9a1':raise ValueError('Baseline profile changed')
 p=json.loads(pm.read_text());hashes(p['files']);hashes(p['artifacts'])
 endpoint=ROOT/'results/rtl_memory_endpoint_20261023/manifest.json';ep=json.loads(endpoint.read_text());hashes(ep['files']);hashes(ep['artifacts'])
 with tempfile.TemporaryDirectory(prefix='b_wide_audit_') as tmp:
  root=Path(tmp);(root/'hardware/rtl').mkdir(parents=True);(root/'hardware/tb').mkdir()
  inputs=['hardware/rtl/record_backing_service.sv','hardware/rtl/memory_scratch_endpoint.sv','hardware/tb/tb_scratch_page_codec.sv','hardware/tb/tb_memory_endpoint.sv','hardware/tb/tb_memory_endpoint_profile.sv']
  for name in inputs:shutil.copy2(ROOT/name,root/name)
  spec=importlib.util.spec_from_file_location('b_wide_generator',ROOT/'hardware/scripts/make_wide_codec_composition.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.ROOT=root;mod.main()
  for name in ('hardware/rtl/record_backing_service_wide.sv','hardware/rtl/memory_scratch_endpoint_wide.sv','hardware/tb/tb_scratch_page_codec_wide.sv','hardware/tb/tb_memory_endpoint_wide.sv','hardware/tb/tb_memory_endpoint_wide_profile.sv'):
   if sha(root/name)!=sha(ROOT/name):raise ValueError('Composition/stimulus differs '+name)
 cases={
  'codec':('tb_scratch_page_codec_wide','scratch_page_codec',dict(checks=5645,encoded=64,decoded=65,rejected=7,aborted=5,stalls=3620),833270),
  'small':('tb_memory_endpoint_wide_small','memory_endpoint',ep['simulation']['small_final'],601030),
  'actual':('tb_memory_endpoint_wide_profile','memory_endpoint',ep['simulation']['actual_final'],82490050)}
 artifacts=[bm,pm,endpoint];sim={}
 for directory,(top,label,expected,endtime) in cases.items():
  d=out/directory;log=(d/'session.log').read_text()
  if '\0' in log or re.search(r'(?im)^\s*(ERROR|FATAL|Fatal):',log) or 'PROFILE_INCOMPLETE' in log:raise ValueError('Positive simulation failed')
  matches=re.findall(r'^TEST_PASS '+label+r' (.*)$',log,re.M)
  if len(matches)!=1 or {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',matches[0])}!=expected:raise ValueError('Wrong case results '+directory)
  if f'$finish called at time : {endtime} ns' not in log:raise ValueError('Wrong end time')
  for stage in ("'compile' step finished","'elaborate' step finished",'XSim completed.'):
   if log.count(stage)!=1:raise ValueError('Incomplete positive flow')
  if 'Built simulation snapshot '+top+'_behav' not in (d/'elaborate.log').read_text():raise ValueError('Missing elaboration')
  sim[directory]=dict(expected,end_time_ns=endtime);artifacts.extend(x for x in d.iterdir() if x.is_file())
 old=counters(baseline);new=counters(out);base_total=old[('scalar',-1,0)];new_total=new[('scalar',-1,0)]
 if base_total!=10516484 or new_total!=8249001:raise ValueError('Wrong paired totals')
 if 'PROFILE_PASS samples=8249001 accepted=77099 retired=77099' not in (out/'actual/session.log').read_text():raise ValueError('Missing profile terminal')
 for group,n in (('endpoint',21),('directory',7),('codec',14),('axi',5),('service',8)):
  if sum(new[(group,-1,i)] for i in range(n))!=new_total:raise ValueError('Cycle partition invalid')
 for key in (2,3,4,5,6,7,8,12,13,14):
  if new[('scalar',-1,key)]!=old[('scalar',-1,key)]:raise ValueError('Changed semantic work count')
 for state in range(1,7):
  if new[('directory',-1,state)]!=old[('directory',-1,state)]:raise ValueError('Changed directory work')
 with (baseline/'profile.commands.csv').open() as f:before=list(csv.DictReader(f))
 with (out/'profile.commands.csv').open() as f:after=list(csv.DictReader(f))
 if len(before)!=77099 or len(after)!=77099:raise ValueError('Missing per-command profile')
 per_op=defaultdict(lambda:dict(count=0,baseline_cycles=0,wide_cycles=0));per_query=[];inclusive=Counter();last=0
 for index,(a,brow) in enumerate(zip(before,after)):
  a={k:int(v) for k,v in a.items()};z={k:int(v) for k,v in brow.items()};op=z['op']
  if any(a[k]!=z[k] for k in ('index','op','query','page')) or z['index']!=index:raise ValueError('Changed command sequence')
  start,available,end=z['accept_cycle'],z['response_cycle'],z['retire_cycle']
  if not last<start<available<=end or end-available!=4:raise ValueError('Invalid wide timing')
  if op==0:per_query.append(dict(query_ordinal=len(per_query),commands=0,baseline_cycles=0,wide_cycles=0))
  old_cycles=a['retire_cycle']-a['accept_cycle']+1;wide_cycles=end-start+1
  for row in (per_op[op],per_query[-1]):
   row['baseline_cycles']+=old_cycles;row['wide_cycles']+=wide_cycles
  per_op[op]['count']+=1;per_query[-1]['commands']+=1;inclusive[op]+=wide_cycles;last=end
 if last!=new_total or len(per_query)!=19:raise ValueError('Incomplete command coverage')
 if sum(inclusive.values())+new[('scalar',-1,1)]!=new_total:raise ValueError('Inclusive cycle accounting failed')
 for op in range(16):
  if sum(new[('operation',op,s)] for s in range(21))!=inclusive[op]:raise ValueError('Per-op cycle accounting failed')
 for state in range(21):
  assigned=sum(new[('operation',op,state)] for op in range(16))+(new[('scalar',-1,1)] if state==0 else 0)
  if assigned!=new[('endpoint',-1,state)]:raise ValueError('Per-state attribution failed')
 if sum(r['baseline_cycles']-r['wide_cycles'] for r in per_query)!=base_total-new_total:raise ValueError('Paired delta mismatch')
 phases={name:dict(baseline_cycles=sum(old[('endpoint',-1,i)] for i in indices),wide_cycles=sum(new[('endpoint',-1,i)] for i in indices)) for name,indices in PHASES.items()}
 controls={'bypass_commit':'record exposed before successful commit','ignore_failed_commit':'record exposed before successful commit','ignore_bad_format':'malformed page accepted','ignore_cancel':'abort did not terminate page','wrong_first_word':'encoded byte mismatch','drop_presence':'encoded byte mismatch','truncate_without_padding_check':'malformed page accepted'}
 if set(b['negative_controls'])!=set(controls):raise ValueError('Missing negative scenario')
 original=(ROOT/'hardware/rtl/scratch_page_codec_wide.sv').read_text()
 for name,row in b['negative_controls'].items():
  if row['status']!='expected_failure_observed' or row['expected_failure']!=controls[name]:raise ValueError('Wrong negative status')
  hashes(row['artifacts']);d=build/'negative_controls'/name
  if [c['stage'] for c in row['commands']]!=['compile','elaborate','simulate'] or any(c['exit_code'] for c in row['commands'][:2]):raise ValueError('Negative failed before runtime')
  log=(d/'simulate.log').read_text();fatal=[x for x in log.splitlines() if x.startswith('Fatal:')]
  if fatal!=[row['causal_failure']] or controls[name] not in fatal[0] or 'TEST_PASS' in log:raise ValueError('Wrong negative failure')
  if original.count(row['removed'])!=1 or (d/'scratch_page_codec_wide.sv').read_text()!=original.replace(row['removed'],row['replacement']):raise ValueError('Undeclared mutation')
 sy=b['synthesis'];sd=build/'synthesis';hashes(sy['artifacts']);log=(sd/'synthesize.log').read_text()
 if sy['status']!='exited_zero' or len(sy['commands'])!=1 or sy['commands'][0]['exit_code']!=0:raise ValueError('Synthesis incomplete')
 if 'synth_design completed successfully' not in log or '0 Critical Warnings and 0 Errors' not in log or re.search(r'(?im)^\s*(ERROR|CRITICAL WARNING):',log) or 'dissolved into registers' in log:raise ValueError('Synthesis/RAM failure')
 rams=(sd/'ram_cells.txt').read_text().splitlines();codec_rams=[r for r in rams if r.startswith('memory/codec/')]
 if len(codec_rams)==0 or any('RAMB' not in r for r in rams) or sum('memory/memory_service/directory/' in r for r in rams)!=18 or sum('pages/endpoint/storage/' in r for r in rams)!=2:raise ValueError('Missing memory domain')
 if f'B_WIDE_CODEC_SYNTH_PASS ram_cells={len(rams)}' not in log:raise ValueError('Missing terminal synthesis marker')
 util=(sd/'utilization.rpt').read_text()
 def used(label):
  m=re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)\s*\|',util,re.M)
  if not m:raise ValueError('Missing resource '+label)
  v=float(m[1]);return int(v) if v.is_integer() else v
 resources=dict(luts=used('CLB LUTs*'),registers=used('CLB Registers'),bram_tiles=used('Block RAM Tile'),latches=used('Register as Latch'))
 if resources['latches']!=0:raise ValueError('Unexpected latch')
 artifacts.extend(sd/n for n in ('synthesize.tcl','synthesize.log','utilization.rpt','utilization_hierarchical.rpt','ram_cells.txt','memory_scratch_endpoint_wide.dcp'))
 artifacts.extend(out/n for n in ('profile.commands.csv','profile.counts.csv'))
 for path in (ROOT/'hardware/WIDE_CODEC_CONTRACT.md',Path(__file__).resolve()):
  files[str(path)]=sha(path);dest=out/'audit_sources'/path.relative_to(ROOT)
  if dest.exists() and sha(dest)!=sha(path):raise ValueError('Audit source changed')
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes())
 return dict(status='passed',toolchain='Vivado/XSim 2022.2',part='xcu280-fsvh2892-2L-e',board_performance=None,simulation=sim,
  paired_cycles=dict(baseline=base_total,wide=new_total,saved=base_total-new_total,reduction_fraction=1-new_total/base_total,same_clock_cycle_ratio=base_total/new_total,phases=phases,operations={str(k):v for k,v in per_op.items()},queries=per_query),
  synthesis=dict(top='memory_scratch_endpoint_wide',frames=23405,ram_cells=rams,codec_ram_cells=codec_rams,utilization=resources,baseline_utilization=ep['synthesis']['utilization']),
  negative_failures={k:v['causal_failure'] for k,v in b['negative_controls'].items()},warnings=[x for x in log.splitlines() if x.startswith('WARNING:')],
  files=files,artifacts={str(x):sha(x) for x in artifacts},
  scope='Paired deterministic 19-small-query state-endpoint simulation. Width changes codec memory access, no controller or stimulus semantics changed. Timing phase can change fixed-calendar stalls. More/fewer simulated cycles and OOC resources do not establish clock frequency, power or board routing speed.')
if __name__=='__main__':
 out=Path(sys.argv[1]).resolve();record=audit(out);path=out/'manifest.json'
 if path.exists() and json.loads(path.read_text())!=record:raise ValueError('Do not overwrite different evidence')
 path.write_text(json.dumps(record,indent=2)+'\n')
 summary={k:record[k] for k in ('status','simulation','synthesis','scope')};summary['paired_cycles']={k:record['paired_cycles'][k] for k in ('baseline','wide','saved','reduction_fraction','same_clock_cycle_ratio','phases')};summary['manifest_sha256']=sha(path)
 (out/'completion_audit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
