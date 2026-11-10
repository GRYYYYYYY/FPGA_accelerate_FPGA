"""Independent terminal audit for the backing directory/AXI service milestone."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def audit(out):
 build=out/'verified_build';bm=build/'build_manifest.json';b=json.loads(bm.read_text())
 if b['status']!='completed':raise ValueError('Build incomplete')
 files=dict(b['files'])
 for path,digest in files.items():
  if sha(path)!=digest or sha(build/'sources'/Path(path).relative_to(ROOT))!=digest:raise ValueError('Source changed '+path)
 fm=out/'fixtures/manifest.json';f=json.loads(fm.read_text())
 if (f['status'],f['pages'],f['actual_pages'],f['stride'],f['beats'])!=('passed',64,62,1344,21):raise ValueError('Wrong fixtures')
 for path,digest in f['files'].items():
  if sha(path)!=digest:raise ValueError('Fixture/source changed '+path)
 files.update(f['files'])
 raw=(out/'fixtures/pages.bin').read_bytes();hexwords=(out/'fixtures/pages.hex').read_text().splitlines()
 if len(raw)!=64*1344 or len(hexwords)!=1344 or b''.join(int(x,16).to_bytes(64,'little') for x in hexwords)!=raw:raise ValueError('Fixture byte packing mismatch')
 sim=(out/'simulation_session.log').read_text()
 if '\0' in sim or re.search(r'(?im)^\s*(ERROR|FATAL|Fatal):',sim):raise ValueError('Positive simulation failed/corrupt')
 pattern=r'TEST_PASS backing_page_service checks=(\d+) write_pages=(\d+) read_pages=(\d+) error_cases=(\d+) aw_bursts=(\d+) ar_bursts=(\d+) b_responses=(\d+) r_beats=(\d+)'
 matches=re.findall(pattern,sim)
 if len(matches)!=1 or tuple(map(int,matches[0]))!=(905,73,64,7,99,89,99,1428):raise ValueError('Incomplete positive simulation')
 if sim.count("'compile' step finished")!=1 or sim.count("'elaborate' step finished")!=1 or sim.count('XSim completed.')!=1:raise ValueError('Missing simulation stage')
 if 'Built simulation snapshot tb_backing_page_service_behav' not in (out/'final_sim/elaborate.log').read_text():raise ValueError('Missing elaboration')
 expected={'complete_before_B':'early B completion','ignore_B_error':'service mismatch',
  'release_before_consumer':'lease released before consumer commit','recycle_without_fence':'service mismatch','old_read_error_stop':'undrained read burst'}
 if set(b['negative_controls'])!=set(expected):raise ValueError('Missing negative scenario')
 for name,row in b['negative_controls'].items():
  d=build/'negative_controls'/name
  if row['status']!='expected_failure_observed' or row['expected_failure']!=expected[name]:raise ValueError('Unverified negative scenario')
  if [c['stage'] for c in row['commands']]!=['compile','elaborate','simulate'] or any(c['exit_code'] for c in row['commands'][:2]):raise ValueError('Negative failed before runtime')
  log=(d/'simulate.log').read_text();fatal=[x for x in log.splitlines() if x.startswith('Fatal:')]
  if fatal!=[row['causal_failure']] or expected[name] not in fatal[0] or 'TEST_PASS' in log:raise ValueError('Wrong negative behavior')
  original=(ROOT/'hardware/rtl'/row['file']).read_text()
  variant=(out/'protocol_gap'/row['file']).read_text() if name=='old_read_error_stop' else original.replace(row['removed'],row['replacement'])
  if (d/row['file']).read_text()!=variant:raise ValueError('Undeclared negative changes')
  for path,digest in row['artifacts'].items():
   if sha(path)!=digest:raise ValueError('Negative artifact changed')
 sy=b['synthesis'];sd=build/'synthesis';log=(sd/'synthesize.log').read_text()
 if sy['status']!='exited_zero' or len(sy['commands'])!=1 or sy['commands'][0]['exit_code']!=0:raise ValueError('Synthesis stage failed')
 for path,digest in sy['artifacts'].items():
  if sha(path)!=digest:raise ValueError('Synthesis artifact changed')
 if 'synth_design completed successfully' not in log or '0 Critical Warnings and 0 Errors' not in log:raise ValueError('No clean synthesis terminal')
 if re.search(r'(?im)^\s*(ERROR|CRITICAL WARNING):',log) or 'dissolved into registers' in log:raise ValueError('Synthesis/RAM failure')
 rams=(sd/'ram_cells.txt').read_text().splitlines()
 if not rams or any('RAMB' not in x for x in rams) or f'B_BACKING_SYNTH_PASS ram_cells={len(rams)}' not in log:raise ValueError('Invalid RAM proof')
 util=(sd/'utilization.rpt').read_text()
 def used(label):
  m=re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)\s*\|',util,re.M)
  if not m:raise ValueError('Missing resource '+label)
  value=float(m[1]);return int(value) if value.is_integer() else value
 xrt=json.loads((out/'xrt_host.json').read_text())['system']['host']
 if xrt['xrt']['version']!='2.14.354' or xrt.get('devices') not in ('',[],None):raise ValueError('Unexpected environment evidence')
 extra=[ROOT/'hardware/BACKING_AXI_CONTRACT.md',Path(__file__).resolve()]
 for p in extra:
  files[str(p)]=sha(p);snapshot=out/'audit_sources'/p.relative_to(ROOT)
  if snapshot.exists() and sha(snapshot)!=sha(p):raise ValueError('Audit source changed')
  snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(p.read_bytes())
 artifacts=[bm,fm,out/'simulation_session.log',out/'final_sim/elaborate.log',out/'xrt_host.json',out/'protocol_gap/scratch_page_axi.sv',out/'protocol_gap/finding.json',out/'build_manifest.json']
 artifacts += [sd/name for name in ('synthesize.tcl','synthesize.log','utilization.rpt','ram_cells.txt','backing_page_service.dcp')]
 return dict(status='passed',performance=None,toolchain='Vivado/XSim 2022.2',part='xcu280-fsvh2892-2L-e',
  simulation=dict(checks=905,successful_write_pages=73,successful_read_pages=64,error_cases=7,aw_bursts=99,ar_bursts=89,b_responses=99,r_beats=1428,test_frames=64,alignment_offsets=64,retained_lease_slots=4),
  fixtures=dict(actual_pages=62,directed_pages=2,stride=1344),
  synthesis=dict(frames=23405,backing_bytes=23405*1344,ram_cells=rams,
   utilization=dict(luts=used('CLB LUTs*'),registers=used('CLB Registers'),bram_tiles=used('Block RAM Tile'),latches=used('Register as Latch'))),
  negative_failures={k:v['causal_failure'] for k,v in b['negative_controls'].items()},
  warnings=[x for x in log.splitlines() if x.startswith('WARNING:')],
  environment=dict(xrt_version=xrt['xrt']['version'],visible_devices=0,drivers=xrt['xrt']['drivers']),
  files=files,artifacts={str(p):sha(p) for p in artifacts},
  scope='Address-directory plus raw-page AXI service. Linear owner lookup, serial memory operation, sticky error state. Payload codec is software-generated, and connection to queued scratch endpoint/record codec/fence retirement remains incomplete. No default-capacity behavioral exhaustion, full AXI protocol proof, CDC, post-route timing or board speed result.')
if __name__=='__main__':
 out=Path(sys.argv[1]).resolve();record=audit(out);path=out/'manifest.json'
 if path.exists() and json.loads(path.read_text())!=record:raise ValueError('Do not overwrite different evidence')
 path.write_text(json.dumps(record,indent=2)+'\n')
 summary={k:record[k] for k in ('status','simulation','synthesis','environment','scope')};summary['manifest_sha256']=sha(path)
 (out/'completion_audit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
