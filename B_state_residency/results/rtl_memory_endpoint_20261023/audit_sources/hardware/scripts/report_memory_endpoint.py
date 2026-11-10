"""Independent audit: real public-command projection, closed RTL, failure guards,
whole default-capacity synthesis. Does not claim FPGA routing performance.
"""
from pathlib import Path
from collections import Counter
import hashlib,importlib.util,json,re,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def hashes(files):
 for p,h in files.items():
  if sha(p)!=h:raise ValueError('Changed evidence '+p)
def audit(out):
 build=out/'verified_build_v2';bm=build/'build_manifest.json';b=json.loads(bm.read_text())
 if b['status']!='completed':raise ValueError('Build incomplete')
 hashes(b['files']);files=dict(b['files'])
 for p,h in files.items():
  if sha(build/'sources'/Path(p).relative_to(ROOT))!=h:raise ValueError('Frozen source differs')
 prior=Path(b['prior_build']['path'])
 if sha(prior)!=b['prior_build']['sha256']:raise ValueError('Prior driver evidence changed')
 with tempfile.TemporaryDirectory(prefix='b_memory_audit_') as tmp:
  root=Path(tmp);(root/'hardware/tb').mkdir(parents=True)
  for name in ('tb_backing_page_service.sv','memory_endpoint_stimulus.svh'):shutil.copy2(ROOT/'hardware/tb'/name,root/'hardware/tb'/name)
  spec=importlib.util.spec_from_file_location('b_generator',ROOT/'hardware/scripts/make_memory_endpoint_tb.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.ROOT=root;mod.main()
  if sha(root/'hardware/tb/tb_memory_endpoint.sv')!=sha(ROOT/'hardware/tb/tb_memory_endpoint.sv'):raise ValueError('TB generator differs')
 parent=ROOT/'results/rtl_record_backing_20261023/manifest.json'
 if sha(parent)!='95603ad1496c22a604b79ce1dd35cdd5b31b136935a6e31c15e9e432aedb57f0':raise ValueError('Record adapter parent changed')
 parent_record=json.loads(parent.read_text());hashes(parent_record['files']);hashes(parent_record['artifacts'])
 vm=out/'vectors/manifest.json';v=json.loads(vm.read_text());hashes(v['files']);files.update(v['files'])
 if (v['status'],v['public_commands'],v['field_accesses'],v['transfers'],v['peak_reserved_owners'],v['alignment_offsets'])!=('passed',77099,56588,6086,390,64):raise ValueError('Vector manifest incomplete')
 src=ROOT/'results/rtl_page_controller_20261023/vectors/actual.txt';oldm=src.parent/'vectors_manifest.json';old=json.loads(oldm.read_text());hashes(old['files'])
 # Independently consume all old transport commands and match every new host
 # command and every expected AXI byte, with a separate owner/address table.
 owners={};peak=0;transfers=0;counts=Counter();alignments=set()
 with src.open() as source,(out/'vectors/actual.txt').open() as host,(out/'vectors/pages.hex').open() as pages:
  for row in host:
   a=[int(x,16) for x in next(source).split()];h=[int(x,16) for x in row.split()]
   op=a[0];frame=0;index=0
   if a[15]!=0:raise ValueError('Unexpected actual failure')
   if op in (5,6):
    key=(a[2],a[3],a[4])
    if op==5 and key not in owners:owners[key]=len(owners)
    if key not in owners:raise ValueError('RF lacks prior WB')
    frame=owners[key];index=transfers;transfers+=1;peak=max(peak,len(owners));alignments.add((frame*21)%64)
    bitmap=0;blob=bytearray(1344)
    for position in range(64):
     transport=[int(x,16) for x in next(source).split()]
     if transport[0]!=(9 if op==5 else 7) or transport[1:6]!=a[1:6] or transport[6]!=a[19] or transport[7]!=(op==6) or transport[9]!=position or transport[15]!=0:raise ValueError('Invalid transport source')
     present,value=(transport[17],transport[16]) if op==5 else (transport[8],transport[12])
     if value>>136 or (not present and value):raise ValueError('Noncanonical page record')
     bitmap|=present<<position;blob[8+position*20:28+position*20]=value.to_bytes(20,'little')
    done=[int(x,16) for x in next(source).split()]
    if done[0]!=8 or done[1:6]!=a[1:6] or done[6]!=a[19] or done[7]!=(op==6) or done[15]!=0:raise ValueError('Missing logical COMPLETE')
    blob[:8]=bitmap.to_bytes(8,'little')
    if b''.join(int(next(pages),16).to_bytes(64,'little') for _ in range(21))!=blob:raise ValueError('Wrong expected AXI bytes')
   elif op in (7,8,9):raise ValueError('Orphan internal source')
   expected=[a[i] for i in (0,1,2,3,4,5,9,10,11,15,16,17,18,19,20)]+[frame,index]
   if h!=expected:raise ValueError('Host projection mismatch')
   counts[str(op)]+=1
   if op==11:owners.clear()
  if source.read().strip() or pages.read().strip():raise ValueError('Truncated projection')
 if dict(counts)!=v['counts'] or transfers!=6086 or peak!=390 or len(alignments)!=64:raise ValueError('Projection coverage differs')
 expected_sims={
  'small_final':dict(small=1,checks=370,transfers=46,fences=25,tag_wraps=12,errors=9,gap_cycles=200,host_stalls=1480,aw=40,ar=19,b=40,r=378),
  'actual_final':dict(small=0,checks=77099,transfers=6086,fences=19,tag_wraps=4,errors=0,gap_cycles=152,host_stalls=308396,aw=3521,ar=4454,b=3521,r=71064)}
 sim_results={};artifacts=[bm,prior,parent,vm,oldm]
 for directory,expected in expected_sims.items():
  d=out/directory;log=(d/'session.log').read_text();top='tb_memory_endpoint_'+('small' if expected['small'] else 'actual')
  if '\0' in log or re.search(r'(?im)^\s*(ERROR|FATAL|Fatal):',log):raise ValueError('Positive simulation corrupt/failed')
  lines=re.findall(r'^TEST_PASS memory_endpoint (.*)$',log,re.M)
  if len(lines)!=1 or {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',lines[0])}!=expected:raise ValueError('Missing positive result '+directory)
  if log.count("'compile' step finished")!=1 or log.count("'elaborate' step finished")!=1 or log.count('XSim completed.')!=1 or '$finish called at time' not in log:raise ValueError('Incomplete sim stages')
  if 'Built simulation snapshot '+top+'_behav' not in (d/'elaborate.log').read_text():raise ValueError('Missing elaborated design')
  sim_results[directory]=expected;artifacts.extend(p for p in d.iterdir() if p.is_file())
 controls={
  'complete_before_memory':'COMPLETE before memory and 64 record acknowledgements','retire_before_page_ack':'address RETIRE before page COMPLETE acknowledgement',
  'skip_last_beat_ack':'COMPLETE before memory and 64 record acknowledgements','skip_address_recycle':'fence never reached address recycle',
  'ignore_fault_guard':'host mismatch','allow_external_complete':'COMPLETE before memory and 64 record acknowledgements','accept_during_recycle':'new host command before address recycle'}
 if set(b['negative_controls'])!=set(controls):raise ValueError('Missing negative controls')
 original=(ROOT/'hardware/rtl/memory_scratch_endpoint.sv').read_text()
 for name,row in b['negative_controls'].items():
  if row['status']!='expected_failure_observed' or row['expected_failure']!=controls[name]:raise ValueError('Wrong negative status')
  hashes(row['artifacts']);d=Path(row.get('inherited_from',bm)).parent/'negative_controls'/name
  if [c['stage'] for c in row['commands']]!=['compile','elaborate','simulate'] or any(c['exit_code'] for c in row['commands'][:2]):raise ValueError('Negative did not reach runtime')
  log=(d/'simulate.log').read_text();fatal=[x for x in log.splitlines() if x.startswith('Fatal:')]
  if fatal!=[row['causal_failure']] or controls[name] not in fatal[0] or 'TEST_PASS' in log:raise ValueError('Wrong negative failure')
  if original.count(row['removed'])!=1 or (d/'memory_scratch_endpoint.sv').read_text()!=original.replace(row['removed'],row['replacement']):raise ValueError('Undeclared mutation')
 sy=b['synthesis'];sd=build/'synthesis';hashes(sy['artifacts']);log=(sd/'synthesize.log').read_text()
 if sy['status']!='exited_zero' or len(sy['commands'])!=1 or sy['commands'][0]['exit_code']!=0:raise ValueError('Synthesis incomplete')
 if 'synth_design completed successfully' not in log or '0 Critical Warnings and 0 Errors' not in log or re.search(r'(?im)^\s*(ERROR|CRITICAL WARNING):',log) or 'dissolved into registers' in log:raise ValueError('Synthesis/RAM failure')
 rams=(sd/'ram_cells.txt').read_text().splitlines()
 if sum('RAMB36E2' in r for r in rams)!=20 or sum('RAMB18E2' in r for r in rams)!=1 or len(rams)!=21:raise ValueError('Unexpected whole-top RAM mapping')
 if sum('memory/memory_service/directory/' in r for r in rams)!=18 or sum('pages/endpoint/storage/' in r for r in rams)!=2 or 'memory/codec/words_reg RAMB18E2' not in rams:raise ValueError('Missing memory domain')
 if 'B_MEMORY_ENDPOINT_SYNTH_PASS ram_cells=21' not in log:raise ValueError('Missing terminal synthesis marker')
 util=(sd/'utilization.rpt').read_text()
 def used(label):
  m=re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)\s*\|',util,re.M)
  if not m:raise ValueError('Missing resource '+label)
  v=float(m[1]);return int(v) if v.is_integer() else v
 resources=dict(luts=used('CLB LUTs*'),registers=used('CLB Registers'),bram_tiles=used('Block RAM Tile'),latches=used('Register as Latch'))
 if resources['latches']!=0:raise ValueError('Unexpected latches')
 artifacts.extend(sd/name for name in ('synthesize.tcl','synthesize.log','utilization.rpt','utilization_hierarchical.rpt','ram_cells.txt','memory_scratch_endpoint.dcp'))
 for p in (ROOT/'hardware/MEMORY_ENDPOINT_CONTRACT.md',Path(__file__).resolve()):
  files[str(p)]=sha(p);snap=out/'audit_sources'/p.relative_to(ROOT)
  if snap.exists() and sha(snap)!=sha(p):raise ValueError('Audit source changed')
  snap.parent.mkdir(parents=True,exist_ok=True);snap.write_bytes(p.read_bytes())
 return dict(status='passed',performance=None,toolchain='Vivado/XSim 2022.2',part='xcu280-fsvh2892-2L-e',
  simulation=sim_results,actual_projection=dict(public_commands=77099,field_accesses=56588,queries=19,transfers=transfers,peak_reserved_owners=peak,alignment_offsets=64),
  synthesis=dict(top='memory_scratch_endpoint',frames=23405,tx_bits=16,generation_bits=16,tag_bits=2,ram_cells=rams,utilization=resources),
  negative_failures={k:v['causal_failure'] for k,v in b['negative_controls'].items()},warnings=[x for x in log.splitlines() if x.startswith('WARNING:')],
  files=files,artifacts={str(p):sha(p) for p in artifacts},
  scope='Closed single-clock serial command state endpoint, including internal page COMPLETE, address RETIRE and two-domain fence recycle. Real 19 small-query field traces replay through independent AXI slave memory. No full FPGA search/router, CDC, hidden producers, arbitrary fault recovery, post-route clock closure or measured board acceleration.')
if __name__=='__main__':
 out=Path(sys.argv[1]).resolve();record=audit(out);path=out/'manifest.json'
 if path.exists() and json.loads(path.read_text())!=record:raise ValueError('Do not overwrite different evidence')
 path.write_text(json.dumps(record,indent=2)+'\n')
 summary={k:record[k] for k in ('status','simulation','actual_projection','synthesis','scope')};summary['manifest_sha256']=sha(path)
 (out/'completion_audit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
