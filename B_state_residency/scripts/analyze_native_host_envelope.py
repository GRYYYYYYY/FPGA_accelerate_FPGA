"""Conditional host-boundary serialization/latency sensitivity, not measurements."""
from pathlib import Path
import hashlib,json,datetime
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=ROOT/'results/record_epoch16_full_20261024';mp=base/'manifest.json';m=json.loads(mp.read_text());a=json.loads((base/'source_bound_audit.json').read_text());assert m['status']=='passed' and a['status']=='passed' and a['manifest_sha256']==sha(mp)
 vec=ROOT/'results/small_checkpoint_vectors_full_20261023';vm=json.loads((vec/'manifest.json').read_text());assert vm['status']=='passed'
 ca=json.loads((vec/'completion_audit.json').read_text());assert ca['status']=='passed' and ca['manifest_sha256']==sha(vec/'manifest.json')
 core=base/'pilot/sources/memory_scratch_endpoint_small_staticcodec.sv';digest=sha(core)
 assert digest==next(v for k,v in m['cases']['pilot']['sources'].items() if Path(k).name==core.name)
 text=core.read_text();assert 'TX_BITS=16,GENERATION_BITS=16' in text
 # Fixed native public-port layout, excluding valid/ready and scheduling signals.
 # Counts describe an uncompressed serialization choice, not an information bound.
 command_fields={'op':4,'slot':5,'query':2,'page':21,'price':4,'generation':16,'offset':3,'field':3,'value':32}
 response_fields={'status':4,'payload':160,'present':1,'dirty':1,'tx':16}
 for token in ['[3:0] cmd_op','[4:0] cmd_slot','[1:0] cmd_query','[20:0] cmd_page','[3:0] cmd_price','[GENERATION_BITS-1:0] cmd_generation','[2:0] cmd_offset','[2:0] cmd_field','[31:0] cmd_value','[3:0] rsp_status','[159:0] rsp_payload','rsp_present,rsp_dirty','[TX_BITS-1:0] rsp_tx']:assert token in text
 commands=vm['public_commands'];assert commands==sum(vm['counts'].values())==m['cases']['pilot']['counts']['checks']
 accesses=vm['field_replay']['field_accesses'];assert accesses==vm['counts']['2']+vm['counts']['3']
 transfer_bytes=vm['transfers']*192;reference_ns=m['cases']['pilot']['end_ns'];assert reference_ns==a['end_ns']
 rows=[{'extra_serial_latency_ns_per_command':extra,'added_latency_ns':commands*extra,'reference_plus_added_ns':reference_ns+commands*extra,'added_over_reference_fraction':commands*extra/reference_ns} for extra in [0,50,100,250,1000,10000]]
 result={'status':'conditional_model_verified','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script_sha256':sha(Path(__file__)),'native_manifest_sha256':sha(mp),'native_audit_sha256':sha(base/'source_bound_audit.json'),'vector_manifest_sha256':sha(vec/'manifest.json'),'native_rtl_sha256':digest,'queries':vm['queries'],'public_commands':commands,'field_accesses':accesses,'public_operation_counts':vm['counts'],'command_fields_bits':command_fields,'response_fields_bits':response_fields,'uncompressed_fixed_bits_per_command':sum(command_fields.values())+sum(response_fields.values()),'uncompressed_fixed_bitpacked_bytes':commands*(sum(command_fields.values())+sum(response_fields.values()))//8,'illustrative_aligned_command_bytes':16,'illustrative_aligned_response_bytes':32,'illustrative_aligned_control_bytes':commands*48,'backing_axi_payload_bytes':transfer_bytes,'reference_replay_ns_including_tb_pacing':reference_ns,'reference_ns_per_public_command':reference_ns/commands,'extra_serial_latency_scenarios':rows,'assumptions':['All public commands cross a hypothetical external host boundary and each gets one reply. Internal EXPORT/BEAT/RF_MASK are excluded.','Uncompressed fixed layout;16/32byte alignment is illustrative, not a new implemented ABI or an information-theoretic lower bound.','Extra latency is hypothetical additional serialized overhead beyond existing TB pacing, with no overlap or batching; it is not a PCIe/XRT measurement.','Native replay reference includes initialization/protocol and fixed TB checks; it is not pure device-compute time.','Backing AXI payload and host control may be on different physical links and must not be added as measured PCIe traffic.','If native commands are produced by an on-device graph-search engine, the per-command external-host assumption does not apply.'],'implication':'Address64 composition alone does not establish a practical per-field host API. Locate frontier/search control on-device or define semantically valid coarse commands before claiming host synchronization benefit. No new grouped-query or XRT engine implemented.'}
 assert result['uncompressed_fixed_bits_per_command']==272
 out=ROOT/'results/native_host_envelope_20261024';out.mkdir();(out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','public_commands','field_accesses','uncompressed_fixed_bits_per_command','uncompressed_fixed_bitpacked_bytes','illustrative_aligned_control_bytes','backing_axi_payload_bytes','reference_ns_per_public_command']},indent=2))
 print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
