"""Calibrate conditional clear accounting against completed RTL boundary cases."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/epoch_lifecycle_20261024';mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='real_census_plus_conditional_model'
 for p,h in m['sources'].items():assert sha(Path(p))==h,p
 source=ROOT/'results/real_trace_20261022T165136Z';done=json.loads((source/'completion_audit.json').read_text());assert m['trace_sha256']==done['file_hashes_at_completion'][str(source/'trace_0.jsonl')]
 cases=[]
 for name,bits,slots in [('record_epoch6_default_wrap_20261024',6,1<<18),('record_epoch16_wrap_20261024',16,1<<6)]:
  p=ROOT/'results'/name/'source_bound_audit.json';a=json.loads(p.read_text());assert a['status']=='passed';c=a['counts'];assert c['epoch_wraps']==c['queries']//((1<<bits)-1)
  assert c['clear_cycles']==slots*(1+c['epoch_wraps']);cases.append({'case':name,'recycles':c['queries'],'epoch_bits':bits,'hash_slots':slots,'clear_cycles':c['clear_cycles'],'audit_sha256':sha(p)})
 p=ROOT/'results/rtl_small_directory_capacity_epoch6_20261023/final_audit.json';a=json.loads(p.read_text());assert a['status']=='passed' and a['observed_clear_cycles']==(1+a['full_recycles']//63)*(1<<18)
 cases.append({'case':'standalone_default_capacity_epoch6','recycles':a['full_recycles'],'clear_cycles':a['observed_clear_cycles'],'audit_sha256':sha(p)})
 p=ROOT/'results/record_epoch6_full_20261024';a=json.loads((p/'manifest.json').read_text());assert a['status']=='passed';log=(p/'pilot/simulate.log').read_text();line=re.search(r'^INDEX_ENDPOINT_PASS clear_cycles=(\d+) wraps=(\d+) overflows=(\d+)$',log,re.M);assert line and int(line[1])==262144 and int(line[2])==0
 cases.append({'case':'selected_38_epoch6','recycles':38,'clear_cycles':262144,'manifest_sha256':sha(p/'manifest.json')})
 result={'status':'clear_accounting_calibrated','model_manifest_sha256':sha(mp),'cases':cases,'scope':'Observed boundary counts support the counter model. 570286-attempt values remain conditional work estimates, not a measured full FPGA routing run.'}
 (out/'calibration_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('EPOCH_LIFECYCLE_BOUNDARY_CALIBRATION_PASS')
if __name__=='__main__':main()
