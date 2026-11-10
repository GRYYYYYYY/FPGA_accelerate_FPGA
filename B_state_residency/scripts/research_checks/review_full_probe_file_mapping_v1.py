"""Check original AXI memory file modes against prepared full-probe plusargs."""
from pathlib import Path
import json,re,hashlib,datetime
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');p=B/'ka_publication_release_full_rtl_v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pr=json.loads((p/'preparation.json').read_text());text=(p/'sources/tb_query_fault.sv').read_text();argv=pr['commands'][2];args={};duplicates=[]
for i,v in enumerate(argv):
 if v=='--testplusarg':
  key,value=argv[i+1].split('=',1)
  if key in args:assert args[key]==value;duplicates.append(key)
  args[key]=value
assert 'graph0' in args and 'owners0' in args
# Parse balanced parameter and port lists, preserving nested expressions/quotes.
def balanced(start):
 assert text[start]=='(';i=start+1;depth=1;quote=False;escape=False
 while depth:
  c=text[i];i+=1
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':depth+=1
  elif c==')':depth-=1
 return text[start+1:i-1],i
instances=[];writable=set();readonly=set();logs=set()
for match in re.finditer(r'\baxi_file_memory\s*#\s*\(',text):
 parameters,end=balanced(match.end()-1);tail=re.match(r'\s*(\w+)\s*\(',text[end:]);assert tail
 name=tail.group(1);ports,finish=balanced(end+tail.end()-1)
 def parameter(name,default):
  m=re.search(r'\.'+name+r'\s*\(\s*([^)]*)\)',parameters);return default if m is None else m.group(1).strip()
 tag=parameter('TAG','"memory"');assert re.fullmatch(r'"\w+"',tag);tag=tag[1:-1]
 ro=parameter('READ_ONLY','0');second=parameter('SECONDARY_WRITABLE','0');third=parameter('TERTIARY_WRITABLE','0');assert all(v in ['0','1'] for v in [ro,second,third])
 maps=[]
 for index in range(3):
  key=tag+str(index)
  if key not in args:
   assert index>0;continue
  path=Path(args[key]);is_write=(ro=='0' and (index==0 or (index==1 and second=='1') or (index==2 and third=='1')))
  if is_write:
   assert path.parent==p/'full',('external writable input',name,key,str(path));writable.add(path.name)
  else:readonly.add(str(path))
  maps.append({'plusarg':key,'path':str(path),'open_mode':'r+b' if is_write else 'rb'})
 log=Path(args[tag+'log']);assert log.parent==p/'full';logs.add(log.name)
 instances.append({'instance':name,'tag':tag,'READ_ONLY':ro,'SECONDARY_WRITABLE':second,'TERTIARY_WRITABLE':third,'file_maps':maps,'log':str(log)})
assert len(instances)>=10
plan=json.loads((p/'input_plan.json').read_text());assert sha(p/'input_plan.json')==pr['input_plan_sha256']
created={'design.bin','cost.bin','allocator.bin','owners.bin','snapshot.bin','pool.bin','g3.bin','labels.bin'};assert writable<=created,('unprepared writable image',writable-created)
old=B/'stage_static_cp_host_full_static_v1';assert all(not str(old/'full') in args[k] for k in args)
# Caller-provided baseline sources and graph/table files are strictly read-only.
for f in readonly:
 path=Path(f)
 if path.parent!=p/'full':assert path.is_file()
assert not list((p/'full').glob('*.bin'))
report={'status':'full_probe_all_axi_file_modes_and_mutable_paths_preparation_reviewed','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preparation_sha256':sha(p/'preparation.json'),'reviewer_sha256':sha(Path(__file__)),'instances':instances,'writable_files':sorted(writable),'readonly_paths':sorted(readonly),'log_files':sorted(logs),'identical_duplicate_plusargs':duplicates,'fresh_creation_names':sorted(created),'scope':'Original AXI file model open-mode/plusarg/path closure only; no big input image creation, no compile/simulation, no full-data or functional verdict. External read-only paths checked for existence, not rehashed here.','full_system_functional_netlist_validated':False,'physical_gate_open':False};out=R/'results/ka_publication_release_full_rtl_v2_file_mapping_review_20261101.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'instances':len(instances),'writable_files':sorted(writable),'status':report['status']}))
