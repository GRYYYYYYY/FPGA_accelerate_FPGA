"""Independent selected-cell and source-wiring audit; no full-system verdict."""
from pathlib import Path
import hashlib,json,re
B=Path('/tmp/B_state_residency_offer_20261025');R=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
p=B/'ka_coordinator_config_generation_formal_v1'; receipt=read(p/'preparation.json');cfg=receipt['configuration']
source=Path(cfg['source_json']);assert sha(source)==cfg['source_json_sha256']
a=read(source)['modules'][cfg['module']];b=read(p/'kernel.json')['modules'][cfg['module']]
assert sha(p/'kernel.json')==receipt['kernel_json_sha256']
assert len(b['cells'])==receipt['selected_cells']==256
retained=receipt['retained_state_cells'];cuts=receipt['cuts'];assert len(retained)==2
assert sum(len(a['cells'][n]['connections']['Q']) for n in retained)==5
for n,c in b['cells'].items():
 original=a['cells'][n]
 if n not in cuts:assert c==original
 else:
  cut=cuts[n]; assert original['type']==cut['original_type']=='$dff'
  assert original['connections'][cut['original_port']]==cut['bits']
  assert c=={'hide_name':1,'type':'$anyseq','parameters':{'WIDTH':format(len(cut['bits']),'032b')},'attributes':{},'port_directions':{'Y':'output'},'connections':{'Y':cut['bits']}}
for n in retained:
 assert b['cells'][n]==a['cells'][n]
 assert b['cells'][n]['connections']['CLK']==a['ports']['clk']['bits']
for n,port in a['ports'].items():
 if port['direction']=='input':assert b['ports'][n]==port
for n,net in a['netnames'].items():
 expected=json.loads(json.dumps(net));expected.get('attributes',{}).pop('init',None);assert b['netnames'][n]==expected
for n in cfg['roots']:assert b['ports'][n]=={'direction':'output','bits':a['netnames'][n]['bits']}
for n,net in cfg['observations'].items():assert b['ports'][n]=={'direction':'output','bits':a['netnames'][net]['bits']}
assert len(cuts)==24
src=B/'stage_static_cp_shadow_system_v6/sources'
names=['recovery_coordinator.sv','residency_system.sv','search_residency_system.sv','query_residency_system.sv'];texts={n:(src/n).read_text() for n in names}
co=texts['recovery_coordinator.sv'];assert re.findall(r'\bconfigured\s*<=\s*([^;]+)',co)==['0','1']
staging=co[co.index('else if(cfg_stage)begin'):co.index('else if(!cfg_authoritative')]
assert '!configured' in staging and 'configured<=' not in staging
assert 'else begin configured<=1;' in co
lines={}
for name,needle in [('residency_system.sv',' recovery_ctl('),('search_residency_system.sv','residency_system #('),('query_residency_system.sv','search_residency_system #(')]:
 line=next(x for x in texts[name].splitlines() if (needle in x if name=='residency_system.sv' else x.lstrip().startswith(needle)));lines[name]=line
 if name=='residency_system.sv':
  for token in ['.cfg_stage(jp_permit)','.cold_rst(k_cold_rst)','.clk(clk)','.ENTRIES(32)','.RESET_HOLD(5)','.MAX_CYCLES(1048576)', '.cfg_authoritative(jp_permit?1\'b1:(fd_fa_authoritative&&as_configured&&as_bound_design==fd_fa_design&&as_bound_checkpoint==fd_fa_checkpoint&&as_bound_generation!=0))']:assert token in line
 else:
  for token in ['.as_bound_generation(as_bound_generation)','.k_cold_rst(k_cold_rst)','.clk(clk)']:assert token in line
  assert ('.EXCLUSIVE_BACKEND_RESPONSES(1)' if name.startswith('query') else '.EXCLUSIVE_BACKEND_RESPONSES(EXCLUSIVE_BACKEND_RESPONSES)') in line
au=next(x for x in texts['query_residency_system.sv'].splitlines() if 'checkpoint_authority_rotator authority(' in x)
for token in ['.rst(k_cold_rst)','.clk(clk)','.bound_generation(as_bound_generation)']:assert token in au
contracts=read(p/'contracts.json');parent=contracts['generation_persistence_contract'];assert sha(Path(parent['review']))==parent['review_sha256']
assert sha(src/'residency_system.sv')==contracts['native_authoritative_contract']['source_sha256']
for entry in cfg['source_bindings'].values():assert sha(Path(entry['source']))==entry['sha256']
assert (B/'ka_coordinator_contract_core_v1/recovery_coordinator.sv').read_bytes()==(src/'recovery_coordinator.sv').read_bytes()
rr=R/'results/ka_coordinator_config_generation_receipt_review_20261031.json';evidence=read(rr)
assert evidence['status']=='coordinator_proof_receipts_verified_actual_archive_restore_complete'
report={'status':'selected_transition_cells_and_native_generation_contract_integration_reviewed','selected_cells':256,'retained_bits':5,'retained_dff':2,'arbitrary_state_cuts':24,'reviewer_sha256':sha(Path(__file__)),'receipt_review_sha256':sha(rr),'source_sha256':{n:sha(src/n) for n in names},'actual_instance_lines':lines,'authority_instance_line':au,'correction':'Only the native non-stage branch first sets coordinator configured; staging requires configured already. Earlier publication-first-install obligations are superseded for this flag.','contract_clock_reset':'Both authority rst and coordinator cold_rst map to k_cold_rst, with clk unchanged through query/search/residency.','proved_scope':'Under reviewed native admission and independently reviewed generation persistence contracts, the five-bit coordinator proof establishes AS implies generation nonzero.','remaining':['Authority configured at AS still requires retirement and configuration-preservation composition.','Reader idle and no competing authority operation needed for KA ready proof.','No KA stall-unreachability or full-system acceptance conclusion.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_coordinator_transition_integration_v2_review_20261031.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(out)
