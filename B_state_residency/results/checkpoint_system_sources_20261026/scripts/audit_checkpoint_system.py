"""Independent source and full-output comparison for integrated cancellation."""
from pathlib import Path
import json,sys,runpy,tempfile
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());partial='--partial'in sys.argv;assert m['status']=='observed'or partial
base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text());assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256'],n
stage=p.parent/'checkpoint_joint_v7';sm=json.loads((stage/'manifest.json').read_text());sa=json.loads((stage/'source_bound_audit.json').read_text());assert sa['status']=='passed' and sa['manifest_sha256']==sha(stage/'manifest.json')
for n in ['recovery_coordinator.sv','config_restore_controller.sv','checkpoint_publish_barrier.sv','checkpoint_authority_rotator.sv']:assert sha(p/'sources'/n)==sm['sources'][n]['sha256'],n
changed={'residency_system.sv','search_residency_system.sv','query_residency_system.sv','recovery_coordinator.sv','config_restore_controller.sv','tb_query_fault.sv','runner.py','build.py','build_tb.py','checkpoint_authority_rotator.sv','checkpoint_publish_barrier.sv'}
for n in set(m['sources'])-changed:
 if n=='boot_restore_gate.sv':assert sha(p/'sources'/n)==sha(Path(m['production'])/'sources'/n)
 else:assert sha(p/'sources'/n)==bm['sources'][n]['sha256'],n
# Rebuild full hierarchy from frozen builder without touching current sources.
b=runpy.run_path(str(p/'sources/build.py'))
with tempfile.TemporaryDirectory() as temp:
 b['make'].__globals__['HERE']=Path(temp);b['make']()
 for n in ['residency_system.sv','search_residency_system.sv','query_residency_system.sv']:assert sha(Path(temp)/n)==sha(p/'sources'/n),n
sys.path.insert(0,str(p/'sources'))
t=runpy.run_path(str(p/'sources/build_tb.py'))
tb=t['make']((base/'sources/tb_query_fault.sv').read_text())
ties=".boot_required(1'b0),.boot_cfg_valid(1'b0),.boot_verify_valid(1'b0),.boot_rsp_ready(1'b0),.boot_design(64'd0),.boot_generation(64'd0),.boot_checkpoint(32'd0),.boot_version(32'd0),.boot_nodes(32'd0),.boot_label_count(32'd0),.boot_label_crc(32'd0),.boot_path_crc(32'd0),.boot_query_crc(32'd0),.boot_query(2'd0),.boot_slots(2'd0),.boot_price(4'd0),.boot_payload(2304'd0),"
tb=tb.replace(')system(.jp_start',')system('+ties+'.jp_start').replace('endmodule','always @(posedge clk)if(!k_cold_rst&&!rst)begin if(system.boot_pending||system.boot_rsp_valid)$fatal(1,"normal start entered bootstrap");end\nendmodule')
assert tb==(p/'sources/tb_query_fault.sv').read_text()
report={}
if not partial:assert set(m['cases'])=={'full_5','pressure_5'}
for name,c in m['cases'].items():
 if c['status']!='observed':assert partial;continue
 assert all(x['exit_code']==0 for x in c['commands'])
 d=p/name;log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and 'JOINT_SYSTEM_CANCEL_PASS journal=6 checkpoint=17'in log and 'QUERY_FAULT_OBSERVED case=5 outcome=recovered_retry'in log
 # Exact physical transaction stream, DDR and immutable authority image output.
 names=['graph_axi.txt','cost_axi.txt','design_axi.txt','owner_axi.txt','label_axi.txt','qstate_axi.txt','table_axi.txt','snapshot_axi.txt','owners.bin','labels.bin','cost.bin','design.bin']
 exact={n:sha(d/n)for n in names}
 for n,h in exact.items():assert h==sha(base/name/n),(name,n)
 rows=[x.split()for x in(d/'natural_trace.txt').read_text().splitlines()]
 ev={tag:[r for r in rows if r[0]==tag]for tag in ['JS','JK','JC','JKR','JCR','JX','JD','JE','JOINT_SYSTEM_CANCEL']}
 assert all(len(ev[t])==1 for t in ev),(name,{t:len(v)for t,v in ev.items()})
 start=int(ev['JS'][0][1]);kr=int(ev['JK'][0][1]);cr=int(ev['JC'][0][1]);ka=int(ev['JKR'][0][1]);ca=int(ev['JCR'][0][1]);cancel=int(ev['JX'][0][1]);drop=int(ev['JD'][0][1]);end=int(ev['JE'][0][1]);finish=int(ev['JOINT_SYSTEM_CANCEL'][0][1])
 assert start<min(kr,cr) and ka-kr>=8 and ca-cr>=8 and max(ka,ca)<cancel<drop<end<finish
 assert ev['JS'][0][2:]==['17','6','4','4','1']
 assert ev['JK'][0][2:]==ev['JC'][0][2:]==['18','4']
 assert ev['JKR'][0][2:]==['0','17','6'] and ev['JCR'][0][2:]==['0','17']
 assert ev['JX'][0][2:]==['3'] and ev['JD'][0][2:]==['6','6']
 assert ev['JE'][0][2:]==['2','17','6','17','1'] and ev['JOINT_SYSTEM_CANCEL'][0][2:]==['6','17']
 # Saved path, query floor, config and journal exported after cancellation match baseline.
 old=[x.split()for x in(base/name/'natural_trace.txt').read_text().splitlines()]
 for tag in ['BPATH','QCM','QCS','QCP','BCFG','BCONTEXT','BFLOORS','BJ']:
  a=[r for r in rows if r[0]==tag];o=[r for r in old if r[0]==tag];assert a and a==o,(name,tag)
 report[name]=dict(exact_files=exact,events=ev,result=next(l for l in log.splitlines()if l.startswith('QUERY_FAULT_OBSERVED')))
r=dict(status='partial'if partial else 'passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),stage_audit_sha256=sha(stage/'source_bound_audit.json'),cases=report,scope='Full-system actual six-entry journal after fault/retry; staged coordinator/config cancel under native lease, no authority candidate and no publication. Physical streams and four DDR images exact baseline. Not successful full joint publication or post-rotation warm recovery.')
(p/('partial_audit.json'if partial else 'source_bound_audit.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(status=r['status'],cases=list(report),exact_files=12*len(report))))
