"""Source-bound nondeterministic scalar cuts, preserving nine actual state DFFs."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');parent=B/'ka_as_lease_staging_exclusion_formal_v1';p=B/'ka_as_lease_staging_boundary_formal_v1';assert not p.exists();p.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pr=json.loads((parent/'preparation.json').read_text());a=json.loads((parent/'kernel.json').read_text());mod=a['modules']['query_residency_system'];cells=mod['cells'];drivers={}
for n,c in cells.items():
 for port,bits in c['connections'].items():
  if c['port_directions'][port]=='output':
   for bit in bits:
    if isinstance(bit,int):assert bit not in drivers;drivers[bit]=n
names=['f_backend_idle','f_all_drained','f_normal_retired','k_permit','qc_busy','qc_cp_busy','ss_busy','qc_fault','ss_fault','fault','rc_fault','k_fault','cf_fault','lr_fault','f_fault','as_cfg_lease','as_fault','boot_pending','cp_busy','qc_pending','as_busy','pc_route_retired','p_active','f_recovery_owned']
retained=set(pr['retained_state_cells']);protected={bit for n in retained for bit in cells[n]['connections']['Q']};cuts={};skipped={}
for signal in names:
 bits=mod['netnames'][signal]['bits'];assert len(bits)==1 and isinstance(bits[0],int) and bits[0] not in protected
 n=drivers[bits[0]];c=cells[n]
 if c['type']=='$anyseq':skipped[signal]='already arbitrary state boundary';continue
 assert n not in retained and c['type']!='$dff'
 out=[bs for port,bs in c['connections'].items() if c['port_directions'][port]=='output'];assert out==[bits],(signal,n)
 cuts[n]={'signal':signal,'original_cell':c};cells[n]={'hide_name':1,'type':'$anyseq','parameters':{'WIDTH':format(1,'032b')},'attributes':{},'port_directions':{'Y':'output'},'connections':{'Y':bits}}
# Prune unreachable former fanin after introducing only broader scalar choices.
needed=[bit for n in pr['configuration']['state_names']+pr['configuration']['roots']+list(pr['configuration']['observations'].values()) for bit in mod['netnames'][n]['bits']];seen=set();selected={}
while needed:
 bit=needed.pop()
 if not isinstance(bit,int) or bit in seen:continue
 seen.add(bit);name=drivers.get(bit)
 if name is None or name in selected:continue
 c=cells[name];selected[name]=c
 for port,bits in c['connections'].items():
  if c['port_directions'][port]=='input':needed.extend(bits)
assert retained<=set(selected);mod['cells']=selected
(p/'kernel.json').write_text(json.dumps(a,separators=(',',':'))+'\n');(p/'harness.sv').write_bytes((parent/'harness.sv').read_bytes())
receipt={'status':'prepared_boundary_overapproximation_not_proved','parent':str(parent),'parent_kernel_sha256':sha(parent/'kernel.json'),'parent_preparation_sha256':sha(parent/'preparation.json'),'retained_state_cells':sorted(retained),'retained_state_bits':9,'scalar_cuts':cuts,'skipped':skipped,'selected_cells':len(selected),'kernel_json_sha256':sha(p/'kernel.json'),'scope':'Only scalar combinational outputs replaced with unconstrained anyseq using identical bit IDs/aliases; original DFF cells and clock/reset unchanged. Every original trace has an arbitrary-choice extension; no new environment assumptions.'};(p/'boundary_preparation.json').write_text(json.dumps(receipt,indent=2)+'\n')
# Preserve original preparation for original-source/port mapping; boundary receipt is explicit.
(p/'preparation.json').write_bytes((parent/'preparation.json').read_bytes());m=json.loads((parent/'manifest.json').read_text());m={k:m[k] for k in ['original_core','original_core_sha256','sources','harness_sha256','preparation_sha256']};m.update(status='prepared',commands=[],scope=receipt['scope'],kernel_json_sha256=sha(p/'kernel.json'),boundary_preparation_sha256=sha(p/'boundary_preparation.json'));(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
s=(R/'scripts/research_checks/run_as_lease_staging_exclusion_formal_v1.py').read_text().replace("assert p == BASE / 'ka_as_lease_staging_exclusion_formal_v1'","assert p == BASE / 'ka_as_lease_staging_boundary_formal_v1'")
s=s.replace("assert sha(p / 'harness.sv') == m['harness_sha256']","assert sha(p / 'harness.sv') == m['harness_sha256']\n    assert sha(p / 'boundary_preparation.json') == m['boundary_preparation_sha256']")
(R/'scripts/research_checks/run_as_lease_staging_boundary_formal_v1.py').write_text(s);print({'selected_cells':len(selected),'cuts':len(cuts),'skipped':skipped})
