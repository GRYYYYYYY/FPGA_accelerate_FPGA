"""Terminal audit of codec correctness, AXI composition, negatives and BRAM mapping."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def validate_hashes(files):
 for p,h in files.items():
  if sha(p)!=h:raise ValueError('Changed evidence '+p)
def audit(out):
 build=out/'verified_build_v2';bm=build/'build_manifest.json';b=json.loads(bm.read_text())
 if b['status']!='completed':raise ValueError('Build incomplete')
 validate_hashes(b['files']);files=dict(b['files'])
 for p,h in files.items():
  if sha(build/'sources'/Path(p).relative_to(ROOT))!=h:raise ValueError('Frozen source mismatch')
 prior=Path(b['prior_build']['path'])
 if sha(prior)!=b['prior_build']['sha256']:raise ValueError('Prior failed build changed')
 parent=ROOT/'results/rtl_backing_axi_20261023';pm=parent/'manifest.json'
 if sha(pm)!='89db1f91e32e60307840b66ebf3f08c6b4cfd8f8243fe7ad6989b8acc6347980':raise ValueError('Parent evidence changed')
 parent_record=json.loads(pm.read_text());validate_hashes(parent_record['files'])
 fm=parent/'fixtures/manifest.json';f=json.loads(fm.read_text());validate_hashes(f['files']);files.update(f['files'])
 if (f['status'],f['pages'],f['actual_pages'],f['stride'],f['beats'])!=('passed',64,62,1344,21):raise ValueError('Wrong fixtures')
 raw=(parent/'fixtures/pages.bin').read_bytes();beats=(parent/'fixtures/pages.hex').read_text().splitlines();records=(out/'records.hex').read_text().splitlines()
 if len(raw)!=86016 or len(beats)!=1344 or len(records)!=4096:raise ValueError('Incomplete fixtures')
 if b''.join(int(x,16).to_bytes(64,'little') for x in beats)!=raw:raise ValueError('Beat endian mismatch')
 for page in range(64):
  base=page*1344;bitmap=int.from_bytes(raw[base:base+8],'little')
  if any(raw[base+1288:base+1344]):raise ValueError('Invalid page tail')
  for node in range(64):
   label=raw[base+8+node*20:base+28+node*20];present=(bitmap>>node)&1
   value=int(records[page*64+node],16)
   if value>>160!=present or (value&((1<<160)-1)).to_bytes(20,'little')!=label:raise ValueError('Record mismatch')
   if any(label[17:]) or (not present and any(label)):raise ValueError('Noncanonical record')
 rm=out/'records_manifest.json';validate_hashes(json.loads(rm.read_text())['files'])
 # Page1 includes exact NaN payload, negative zero and present-zero node63.
 if int(records[64],16)&0xffffffffffffffff!=0x800000007fc12345 or int(records[127],16)!=(1<<160):raise ValueError('Directed bit patterns missing')
 simulation={}
 expected={
  'standalone_final':('tb_scratch_page_codec',{'scratch_page_codec':dict(checks=5645,encoded=64,decoded=65,rejected=7,aborted=5,stalls=13024)}),
  'integration_final':('tb_codec_axi',{'codec_axi':dict(records=4096,raw_beats=2942),'codec_axi_service':dict(checks=910,write_pages=73,read_pages=64,error_cases=8,aw_bursts=100,ar_bursts=89,b_responses=100,r_beats=1428)})}
 artifacts=[bm,prior,pm,fm,rm,out/'records.hex']
 for directory,(top,rows) in expected.items():
  d=out/directory;log=(d/'session.log').read_text()
  if '\0' in log or re.search(r'(?im)^\s*(ERROR|FATAL|Fatal):',log):raise ValueError('Corrupt/failed positive simulation')
  matches=re.findall(r'^TEST_PASS (\w+) (.*)$',log,re.M)
  found={key:{k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)} for key,line in matches}
  if found!=rows or len(matches)!=len(rows):raise ValueError('Wrong simulation results '+directory)
  if log.count("'compile' step finished")!=1 or log.count("'elaborate' step finished")!=1 or log.count('XSim completed.')!=1 or '$finish called at time' not in log:raise ValueError('Incomplete simulation flow')
  if 'Built simulation snapshot '+top+'_behav' not in (d/'elaborate.log').read_text():raise ValueError('Missing elaboration')
  simulation.update(found);artifacts.extend(p for p in d.iterdir() if p.is_file())
 controls={'bypass_commit':'record exposed before successful commit','ignore_failed_commit':'record exposed before successful commit',
  'ignore_bad_format':'malformed page accepted','ignore_cancel':'abort did not terminate page',
  'reverse_record_words':'encoded byte mismatch','drop_presence':'encoded byte mismatch'}
 if set(b['negative_controls'])!=set(controls):raise ValueError('Missing negatives')
 original=(ROOT/'hardware/rtl/scratch_page_codec.sv').read_text()
 for name,row in b['negative_controls'].items():
  if row['status']!='expected_failure_observed' or row['expected_failure']!=controls[name]:raise ValueError('Wrong negative status')
  validate_hashes(row['artifacts'])
  commands=row['commands']
  if [c['stage'] for c in commands]!=['compile','elaborate','simulate'] or any(c['exit_code'] for c in commands[:2]):raise ValueError('Negative did not reach runtime')
  d=Path(row.get('inherited_from',bm)).parent/'negative_controls'/name
  log=(d/'simulate.log').read_text();fatal=[x for x in log.splitlines() if x.startswith('Fatal:')]
  if fatal!=[row['causal_failure']] or controls[name] not in fatal[0] or 'TEST_PASS' in log:raise ValueError('Wrong negative failure')
  if original.count(row['removed'])!=1 or (d/'scratch_page_codec.sv').read_text()!=original.replace(row['removed'],row['replacement']):raise ValueError('Undeclared mutation')
 sy=b['synthesis'];sd=build/'synthesis';validate_hashes(sy['artifacts']);log=(sd/'synthesize.log').read_text()
 if sy['status']!='exited_zero' or len(sy['commands'])!=1 or sy['commands'][0]['exit_code']!=0:raise ValueError('Synthesis incomplete')
 if 'synth_design completed successfully' not in log or '0 Critical Warnings and 0 Errors' not in log or re.search(r'(?im)^\s*(ERROR|CRITICAL WARNING):',log) or 'dissolved into registers' in log:raise ValueError('Synthesis/RAM failure')
 rams=(sd/'ram_cells.txt').read_text().splitlines()
 if not rams or any('RAMB' not in x for x in rams) or f'B_CODEC_SYNTH_PASS ram_cells={len(rams)}' not in log:raise ValueError('Missing BRAM proof')
 util=(sd/'utilization.rpt').read_text()
 def used(label):
  m=re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)\s*\|',util,re.M)
  if not m:raise ValueError('Missing resource '+label)
  v=float(m[1]);return int(v) if v.is_integer() else v
 resources=dict(luts=used('CLB LUTs*'),registers=used('CLB Registers'),bram_tiles=used('Block RAM Tile'),latches=used('Register as Latch'))
 if resources['latches']!=0:raise ValueError('Unexpected latches')
 artifacts.extend(sd/name for name in ('synthesize.tcl','synthesize.log','utilization.rpt','ram_cells.txt','scratch_page_codec.dcp'))
 for p in (ROOT/'hardware/PAGE_CODEC_CONTRACT.md',Path(__file__).resolve()):
  files[str(p)]=sha(p);snap=out/'audit_sources'/p.relative_to(ROOT)
  if snap.exists() and sha(snap)!=sha(p):raise ValueError('Audit source changed')
  snap.parent.mkdir(parents=True,exist_ok=True);snap.write_bytes(p.read_bytes())
 return dict(status='passed',performance=None,toolchain='Vivado/XSim 2022.2',part='xcu280-fsvh2892-2L-e',
  simulation=simulation,fixtures=dict(actual_pages=62,directed_pages=2,records=4096,stride=1344),
  synthesis=dict(top='scratch_page_codec',ram_cells=rams,utilization=resources),
  negative_failures={k:v['causal_failure'] for k,v in b['negative_controls'].items()},
  warnings=[x for x in log.splitlines() if x.startswith('WARNING:')],files=files,artifacts={str(p):sha(p) for p in artifacts},
  scope='Standalone codec plus AXI-service composition driven by testbench tasks. Commit/abort sequencing is not yet a synthesizable adapter, queued page COMPLETE/RETIRE/fence remain unconnected. Serial word conversion; no post-route timing, board measurement or acceleration claim.')
if __name__=='__main__':
 out=Path(sys.argv[1]).resolve();record=audit(out);path=out/'manifest.json'
 if path.exists() and json.loads(path.read_text())!=record:raise ValueError('Do not overwrite different evidence')
 path.write_text(json.dumps(record,indent=2)+'\n')
 summary={k:record[k] for k in ('status','simulation','synthesis','scope')};summary['manifest_sha256']=sha(path)
 (out/'completion_audit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
