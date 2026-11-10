"""Independent terminal audit of the synthesizable record memory adapter."""
from pathlib import Path
import hashlib,importlib.util,json,re,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def hashes(files):
 for p,h in files.items():
  if sha(p)!=h:raise ValueError('Evidence changed '+p)
def audit(out):
 build=out/'verified_build_v2';bm=build/'build_manifest.json';b=json.loads(bm.read_text())
 if b['status']!='completed':raise ValueError('Build incomplete')
 hashes(b['files']);files=dict(b['files'])
 for p,h in files.items():
  if sha(build/'sources'/Path(p).relative_to(ROOT))!=h:raise ValueError('Source snapshot mismatch')
 prior=Path(b['prior_build']['path'])
 if sha(prior)!=b['prior_build']['sha256']:raise ValueError('Prior classification evidence changed')
 # Reproduce derived source without editing either frozen baseline or output.
 with tempfile.TemporaryDirectory(prefix='b_record_audit_') as tmp:
  root=Path(tmp);(root/'hardware/rtl').mkdir(parents=True);(root/'hardware/tb').mkdir()
  for name in ('hardware/rtl/backing_frame_directory.sv','hardware/rtl/backing_page_service.sv','hardware/tb/tb_backing_page_service.sv'):
   shutil.copy2(ROOT/name,root/name)
  for generator,outputs in (
   ('make_lookup_service.py',['hardware/rtl/backing_frame_directory_lookup.sv','hardware/rtl/backing_page_service_lookup.sv']),
   ('make_record_backing_tb.py',['hardware/tb/tb_record_backing_service.sv'])):
   spec=importlib.util.spec_from_file_location('b_audit_generator',ROOT/'hardware/scripts'/generator);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.ROOT=root;mod.main()
   for name in outputs:
    if sha(root/name)!=sha(ROOT/name):raise ValueError('Generator does not reproduce '+name)
 parent=ROOT/'results/rtl_page_codec_20261023';pm=parent/'manifest.json'
 if sha(pm)!='ff8d055be3acaa280e834a2027034377dafce8a4bdaf0c3c8062e945693de003':raise ValueError('Parent manifest changed')
 p=json.loads(pm.read_text());hashes(p['files']);hashes(p['artifacts'])
 fixtures=ROOT/'results/rtl_backing_axi_20261023/fixtures'
 fm=fixtures/'manifest.json';f=json.loads(fm.read_text());hashes(f['files']);files.update(f['files'])
 raw=(fixtures/'pages.bin').read_bytes();beats=(fixtures/'pages.hex').read_text().splitlines();records=(parent/'records.hex').read_text().splitlines()
 if len(raw)!=86016 or len(beats)!=1344 or len(records)!=4096:raise ValueError('Wrong fixture sizes')
 if b''.join(int(v,16).to_bytes(64,'little') for v in beats)!=raw:raise ValueError('Beat packing mismatch')
 for page in range(64):
  base=page*1344;bitmap=int.from_bytes(raw[base:base+8],'little')
  for node in range(64):
   value=int(records[page*64+node],16);label=raw[base+8+20*node:base+28+20*node]
   if value>>160!=((bitmap>>node)&1) or (value&((1<<160)-1)).to_bytes(20,'little')!=label:raise ValueError('Record packing mismatch')
 log=(out/'simulation_session.log').read_text()
 if '\0' in log or re.search(r'(?im)^\s*(ERROR|FATAL|Fatal):',log):raise ValueError('Positive simulation failed/corrupt')
 found={k:{a:int(v) for a,v in re.findall(r'(\w+)=(\d+)',line)} for k,line in re.findall(r'^TEST_PASS (\w+) (.*)$',log,re.M)}
 expected={'record_adapter':dict(records=4288,lookup_checks=195,bad_inputs=3,malformed_reads=3),
  'record_backing_service':dict(checks=1144,write_pages=79,read_pages=67,error_cases=8,aw_bursts=106,ar_bursts=95,b_responses=106,r_beats=1554)}
 if found!=expected or len(re.findall(r'^TEST_PASS ',log,re.M))!=2:raise ValueError('Wrong positive coverage')
 if log.count("'compile' step finished")!=1 or log.count("'elaborate' step finished")!=1 or log.count('XSim completed.')!=1 or '$finish called at time : 2968490 ns' not in log:raise ValueError('Incomplete simulation stages')
 if 'Built simulation snapshot tb_record_backing_service_behav' not in (out/'final_sim/elaborate.log').read_text():raise ValueError('No elaborated design')
 controls={'start_before_validation':'record input timeout','lookup_allocates_empty':'service mismatch','lookup_allocates_nonempty':'service mismatch',
  'respond_before_records':'success before all decoded records consumed','ignore_bad_decoded_page':'service mismatch','allow_commands_after_fault':'service mismatch','omit_codec_cancel':'response stuck'}
 if set(b['negative_controls'])!=set(controls):raise ValueError('Missing negative control')
 for name,row in b['negative_controls'].items():
  if row['status']!='expected_failure_observed' or row['expected_failure']!=controls[name]:raise ValueError('Wrong negative result')
  hashes(row['artifacts']);d=Path(row.get('inherited_from',bm)).parent/'negative_controls'/name
  if [x['stage'] for x in row['commands']]!=['compile','elaborate','simulate'] or any(x['exit_code'] for x in row['commands'][:2]):raise ValueError('Negative failed before runtime')
  text=(d/'simulate.log').read_text();fatal=[x for x in text.splitlines() if x.startswith('Fatal:')]
  if fatal!=[row['causal_failure']] or controls[name] not in fatal[0] or 'TEST_PASS' in text:raise ValueError('Wrong causal failure')
  original=(ROOT/'hardware/rtl'/row['file']).read_text()
  if original.count(row['removed'])!=1 or (d/row['file']).read_text()!=original.replace(row['removed'],row['replacement']):raise ValueError('Undeclared mutation')
 sy=b['synthesis'];sd=build/'synthesis';hashes(sy['artifacts']);text=(sd/'synthesize.log').read_text()
 if sy['status']!='exited_zero' or len(sy['commands'])!=1 or sy['commands'][0]['exit_code']!=0:raise ValueError('Synthesis incomplete')
 if 'synth_design completed successfully' not in text or '0 Critical Warnings and 0 Errors' not in text or re.search(r'(?im)^\s*(ERROR|CRITICAL WARNING):',text) or 'dissolved into registers' in text:raise ValueError('Synthesis/RAM failure')
 rams=(sd/'ram_cells.txt').read_text().splitlines()
 if sum('RAMB36E2' in r for r in rams)!=18 or sum('RAMB18E2' in r for r in rams)!=1 or len(rams)!=19:raise ValueError('Missing combined default-capacity BRAM mapping')
 if 'codec/words_reg RAMB18E2' not in rams or not all('memory_service/directory/' in r for r in rams if 'RAMB36E2' in r):raise ValueError('Unexpected RAM hierarchy')
 if 'B_RECORD_BACKING_SYNTH_PASS ram_cells=19' not in text:raise ValueError('No synthesis terminal marker')
 util=(sd/'utilization.rpt').read_text()
 def used(label):
  m=re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)\s*\|',util,re.M)
  if not m:raise ValueError('Missing resource '+label)
  v=float(m[1]);return int(v) if v.is_integer() else v
 resources=dict(luts=used('CLB LUTs*'),registers=used('CLB Registers'),bram_tiles=used('Block RAM Tile'),latches=used('Register as Latch'))
 if resources['latches']!=0:raise ValueError('Unexpected latch')
 artifacts=[bm,prior,pm,fm,parent/'records.hex',out/'simulation_session.log']
 artifacts.extend(p for p in (out/'final_sim').iterdir() if p.is_file())
 artifacts.extend(sd/name for name in ('synthesize.tcl','synthesize.log','utilization.rpt','utilization_hierarchical.rpt','ram_cells.txt','record_backing_service.dcp'))
 for p in (ROOT/'hardware/RECORD_BACKING_CONTRACT.md',Path(__file__).resolve()):
  files[str(p)]=sha(p);snap=out/'audit_sources'/p.relative_to(ROOT)
  if snap.exists() and sha(snap)!=sha(p):raise ValueError('Audit source changed')
  snap.parent.mkdir(parents=True,exist_ok=True);snap.write_bytes(p.read_bytes())
 return dict(status='passed',performance=None,toolchain='Vivado/XSim 2022.2',part='xcu280-fsvh2892-2L-e',
  simulation=found,fixtures=dict(actual_pages=62,directed_pages=2,stride=1344),
  synthesis=dict(top='record_backing_service',frames=23405,ram_cells=rams,utilization=resources),
  negative_failures={k:v['causal_failure'] for k,v in b['negative_controls'].items()},
  warnings=[x for x in text.splitlines() if x.startswith('WARNING:')],files=files,artifacts={str(p):sha(p) for p in artifacts},
  scope='Synthesizable record codec + nonallocating lookup directory + AXI service. Internal memory-success-to-commit and error-to-cancel sequencing; upstream page COMPLETE, RETIRE and fence coordination remain unconnected. Linear lookup and serial codec; no full routing replay, post-route timing, board throughput or acceleration claim.')
if __name__=='__main__':
 out=Path(sys.argv[1]).resolve();record=audit(out);path=out/'manifest.json'
 if path.exists() and json.loads(path.read_text())!=record:raise ValueError('Do not overwrite different evidence')
 path.write_text(json.dumps(record,indent=2)+'\n')
 summary={k:record[k] for k in ('status','simulation','synthesis','scope')};summary['manifest_sha256']=sha(path)
 (out/'completion_audit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
