"""Typed current native/paired/tree/full30 predecessors; no memory admission gate."""
import json
from pathlib import Path
from check_vitis_kernel import digest,require
from route_tree_serial_prerequisites_v1 import validate_predecessors,ROOT,NATIVE,CSR,COMPACT
from owned_sim_resource_policy_v1 import POLICY

TREE='route_tree_rtl_recovery_audit_20261029_v2.json'
SNAPSHOT='snapshot_dpi_rtl_audit_20261029_v5.json'
READ='search_read_control_staging_rtl_audit_20261029_v4.json'
SNAPSHOT_STATUS='full30_snapshot_dpi_rtl_original_c_and_every_complete_output_word_independently_verified'
ADDRESS='snapshot_read_original_address_audit_20261029_v1.json'


def merge_report(path,files):
    require(path.is_file(),'Serialized RTL prerequisite missing: '+path.name)
    r=json.loads(path.read_text());bindings=r.get('files')
    require(isinstance(bindings,dict) and bindings,'Missing predecessor bindings')
    for p,h in bindings.items():
        require(p not in files or files[p]==h,'Conflicting predecessor evidence')
        if p not in files:require(digest(p)==h,'Changed predecessor evidence: '+p)
        files[p]=h
    files[str(path)]=digest(path)
    return r


def tree_scope(r):
    require(r.get('status')=='production_route_tree_full_depth_50_transactions_rtl_verified' and r.get('transactions')==50,'Partial/unaccepted full50 tree')
    require(r.get('capacities')==dict(nodes=1048576,path_edges=524288,state_words=65) and r.get('production_synthesis')=='unchanged','Different tree capacities/DUT')
    require(len(r.get('cycles',[]))==50 and all(type(v) is int and v>0 for v in r['cycles']),'Incomplete tree cycles')


def snapshot_scope(r):
    require(r.get('status')==SNAPSHOT_STATUS and r.get('rtl_verified') is True,'Unaccepted full30 snapshot')
    require((r.get('transactions'),r.get('pointers'),r.get('models'),r.get('pages'),r.get('readonly_models'))==(30,13,10,4,8),'Partial snapshot interface')
    require(r.get('original_address_environment_unchanged') is True and r.get('resource_policy')==POLICY,'Different snapshot identity/resource policy')
    require(len(r.get('cycles',[]))==30 and all(type(v) is int and v>0 for v in r['cycles']),'Incomplete snapshot cycles')


def validate_snapshot(root=ROOT):
    files=validate_predecessors(root)
    tree=merge_report(root/'results'/TREE,files);tree_scope(tree)
    control=root/'data/derived/route_tree_rtl_recovery_control_20261029_v2/state.json'
    state=json.loads(control.read_text())
    require(state['status']=='complete' and state['exit_code']==0 and not state.get('resource_abort',False) and state['resource_policy']==POLICY,'Tree controller not successfully complete')
    for name in [NATIVE,CSR,COMPACT]:
        p=str(root/'results'/name)
        require(state['predecessors'].get(p)==files[p],'Tree used a different graph predecessor')
    files[str(control)]=digest(control)
    address=merge_report(root/'results'/ADDRESS,files)
    require(address['status']=='original_snapshot13_and_read13_pointer_vectors_bound_full27_read_C_vectors_equal_actual_search_baseline' and address['address_relocation_applied'] is False,'Different original address preparation')
    require([(r['label'],r['transactions'],r['pointers']) for r in address['scopes']]==[('snapshot',30,13),('read',2,13)] and address['read_complete_c_vector_files']==27,'Partial original address inventory')
    files[str(Path(__file__).resolve())]=digest(__file__)
    return files


def validate_read(root=ROOT):
    files=validate_snapshot(root)
    snapshot=merge_report(root/'results'/SNAPSHOT,files);snapshot_scope(snapshot)
    require(snapshot['files'].get(str(root/'results'/TREE))==files[str(root/'results'/TREE)],'Snapshot used a different tree acceptance')
    baseline=merge_report(root/'results/search_axi_dpi_replay_audit_20261025_v3.json',files)
    require(baseline['status']=='full_declared_depth_two_transaction_dpi_replay_cycles_all_output_bytes_and_original_c_oracle_independently_verified' and baseline['cycles']==[2132461,12404] and (baseline['transactions'],baseline['models'],baseline['output_files'])==(2,7,5),'Different actual original search baseline')
    return files
