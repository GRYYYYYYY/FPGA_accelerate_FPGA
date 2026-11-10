"""Source-bound obligations for a complete consistent routing checkpoint."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fact(path,needles):
 p=ROOT/path;lines=p.read_text().splitlines();hits=[]
 for needle in needles:
  matching=[{'line':i+1,'text':line.strip()}for i,line in enumerate(lines)if needle in line];assert matching,(path,needle);hits+=matching[:3]
 return {'source':path,'sha256':sha(p),'evidence':hits}
def main():
 full='results/recovery_retry_normal_v1/sources/'
 facts=[fact('hardware/variants/route_checkpoint_v1/route_commit_controller.sv',['cp_valid,output wire cp_ready','CP_VERIFY:begin','slot_valid[a]<=cp_stage']),fact(full+'route_commit_controller.sv',['reg[31:0]path','slot_valid<=0']),fact(full+'residency_system.sv',['route_commit_host_adapter #','snapshot_cookie_held']),fact(full+'recovery_coordinator.sv',['attempt_version','journal_count<=0']),fact(full+'config_restore_controller.sv',['descriptor','attempt_reset']),fact(full+'label_restore_controller.sv',['start_count>MAX_RECORDS','rows[0:MAX_RECORDS-1]']),fact(full+'query_lifecycle.sv',['last_sequence','label_state_dirty'])]
 top=(ROOT/(full+'residency_system.sv')).read_text();assert '.cp_valid('not in top
 obligations=[
 {'state':'saved_connection_paths','status':'component_verified_not_integrated','remaining':'Connect atomic capture/restore through route adapter and system checkpoint fence; bind same owner image and checkpoint identity.','evidence':[0,1,2]},
 {'state':'owner_primary_overflow_allocator','status':'retained_backing_and_route_journal_only','remaining':'Capture full owner backing/pool/allocator and provide generic checkpoint-bound authority lookup; current real recovery authority has six q1 rows.','evidence':[2,3]},
 {'state':'design_created_and_children_cache','status':'physical_backing_retained','remaining':'Consistent full-image backup/restore and graph/layout identity; current recovery does not reconstruct these after backing loss.','evidence':[2]},
 {'state':'history_prices_net_cost_configuration','status':'retained_same_actual_prices','remaining':'Capture full cost tables and version-bound descriptor; verify real price change and invalidation rather than renumbering only.','evidence':[2,4]},
 {'state':'labels_and_page_directory','status':'trusted_external_known328_stream','remaining':'Hardware snapshot production, dynamic complete workset/directory capture or dense authoritative initialization, unknown-page default/old-prev rules; restore cache512 is not a complete design snapshot.','evidence':[2,5]},
 {'state':'query_sequence_epoch_and_version_floors','status':'runtime_only','remaining':'Persist and restore lifecycle last_sequence/label_state_dirty plus successful and attempted recovery versions; prove no stale query admission or version rollback.','evidence':[3,4,6]},
 {'state':'frontier_recursive_capture_and_live_queries','status':'not_checkpointed','remaining':'Choose and verify drained restart boundary or serialize full live heap/control contexts; ordinary AXI drain alone does not establish algorithmic emptiness.','evidence':[2]},
 {'state':'journal_and_atomic_checkpoint_publication','status':'runtime_journal_preserved_during_retry','remaining':'Whole-system freeze, immutable staging generation, data/config/journal binding, commit marker and acknowledgement; cold reset currently clears journal. Power-loss durability needs a separate persistence protocol.','evidence':[2,3,4]}
 ]
 report={'status':'incomplete','meaning':'Explicit completion obligations; new saved-path component closes one storage-interface gap, not the complete checkpoint objective.','facts':facts,'obligations':obligations,'next_experiment':'Integrate saved-path checkpoint with actual two-query/shared-owner AXI fixture and unified fence, then capture consistent owner/design/labels/config under the same checkpoint identity.','analyzer_sha256':sha(Path(__file__))}
 (ROOT/'results/checkpoint_coverage_20261025.json').write_text(json.dumps(report,indent=2)+'\n');print('CHECKPOINT_COVERAGE_INCOMPLETE',len(obligations))
if __name__=='__main__':main()
