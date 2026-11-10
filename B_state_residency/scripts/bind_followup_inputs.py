"""Bind separately audited persistent and cost/State regions without changing baselines."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 warm,cost,oracle=map(lambda s:Path(s).resolve(),sys.argv[1:4]);out=Path(sys.argv[4]);wm=json.loads((warm/'manifest.json').read_text());cm=json.loads((cost/'manifest.json').read_text());base=Path(cm['base']);assert wm['base']==cm['base']
 gates={str(p):sha(p/'source_bound_audit.json')for p in [warm,cost,oracle]}
 for p in [warm,cost,oracle]:assert json.loads((p/'source_bound_audit.json').read_text())['status']=='passed'
 cg=json.loads((cost/'source_bound_audit.json').read_text());og=json.loads((oracle/'source_bound_audit.json').read_text());assert og['input_audit_sha256']==sha(cost/'source_bound_audit.json')
 wa=json.loads((warm/'source_bound_audit.json').read_text());assert cm['base_audit_sha256']==wm['base_audit_sha256']==sha(base/'source_bound_audit.json')
 layout=json.loads((cost/'input_layout.json').read_text());wl=json.loads((warm/'layout.json').read_text());assert layout['nodes']==wl['nodes']==cg['nodes']==wa['rows_verified']
 with (warm/'history.bin').open('rb')as f,(cost/'cost.bin').open('rb')as g:
  for b in iter(lambda:f.read(1<<20),b''):assert g.read(len(b))==b
  assert g.tell()==layout['price_offset'];assert g.read(1024)==(warm/'prices.u32').read_bytes()
 state=json.loads((base/'source_bound_audit.json').read_text())['state'];assert state['conn_index']==[layout['query']]
 regions={}
 for name,p in [('design',warm/'design.bin'),('owners',warm/'owners.bin'),('owner_pool',warm/'owner_pool.bin'),('owner_allocator',warm/'owner_allocator.bin'),('native_labels_import',warm/'initial_labels.native160'),('cost_history_prices_nets',cost/'cost.bin'),('connections',cost/'connections.bin'),('rows',cost/'rows.bin'),('columns',cost/'columns.bin'),('label_working_set_oracle',oracle/'initial_label_imports.u32')]:regions[name]=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
 result=dict(status='passed',binder_sha256=sha(Path(__file__)),base=str(base),audits=gates,state=state,layout=dict(layout,owner_pool_capacity=wl['owner_pool_capacity']),regions=regions,scope='Consistent separately audited real prepared input image set. Legacy cost-only capacity zero overridden from owner layout. No address allocation, sequence-to-epoch conversion, unknown-page initialization, RTL execution, backtrace or owner commit. Oracle label imports still presuppose CPU future footprint.')
 out.write_text(json.dumps(result,indent=2)+'\n');print('FOLLOWUP_INPUT_REGIONS_BOUND',out)
if __name__=='__main__':main()
