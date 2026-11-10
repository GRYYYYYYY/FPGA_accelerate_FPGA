from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];BASE=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 inp=BASE/'natural_query_inputs_v1';oracle=BASE/'natural_query_oracle_v1';a=json.loads((inp/'source_bound_audit.json').read_text());b=json.loads((oracle/'source_bound_audit.json').read_text());m=json.loads((inp/'manifest.json').read_text());om=json.loads((oracle/'manifest.json').read_text())
 assert a['status']==b['status']=='passed' and a['manifest_sha256']==sha(inp/'manifest.json') and b['manifest_sha256']==sha(oracle/'manifest.json')
 assert b['input_audit_sha256']==sha(inp/'source_bound_audit.json')
 for n,v in om['artifacts'].items():assert sha(oracle/n)==v
 for n,v in m['artifacts'].items():assert sha(inp/n)==v
 o=dict(status='passed',input_root=str(inp),oracle_root=str(oracle),input_audit_sha256=sha(inp/'source_bound_audit.json'),oracle_audit_sha256=sha(oracle/'source_bound_audit.json'),nodes=a['nodes'],connections=a['connections'],live_owner_nodes=a['live_owner_nodes'],total_references=a['total_references'],design_sink_nodes=a['design_sink_nodes'],cost_packets=a['cost_packets'],cost_input_words=a['cost_input_words'],cost_result_words=a['cost_result_words'],cost_child_types=a['cost_child_types'],raw_children=b['raw_children'],filtered_children=b['filtered_children'],decisions=b['decisions'],created_transitions=b['created_transitions'],label_import_records=b['label_import_records'],logical_pages=b['logical_pages'],scope='Natural hardware input codecs, binary32 cost and eager filter decisions verified. No natural-query RTL/board execution or acceleration claim.')
 (ROOT/'results/natural_query_inputs_20261025.json').write_text(json.dumps(o,indent=2)+'\n');print(json.dumps(o,indent=2))
if __name__=='__main__':main()
