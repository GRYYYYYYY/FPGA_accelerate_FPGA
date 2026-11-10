"""Complete six-permutation supplemental CPU experiment; original seven blocks stay fixed."""
from collections import Counter
from itertools import permutations
import json
from pathlib import Path
import random
from check_vitis_kernel import digest,require
from owned_sim_resource_policy_v1 import POLICY

ROOT=Path(__file__).resolve().parents[1]
VALIDATION=ROOT/'data/derived/source_to_route_training_validation_20261027_v2'
VALIDATION_AUDIT=ROOT/'results/source_to_route_training_validation_audit_20261027_v2.json'
ORIGINAL=ROOT/'results/source_to_route_training_statistics_audit_20261027_v2.json'
INTEGRITY=ROOT/'results/source_to_route_training_statistics_integrity_20261029_v1.json'
ORDER_EVIDENCE=ROOT/'results/figures/training_inclusive_cpu_20261029_v2/manifest.json'
OUT=ROOT/'data/derived/training_order_control_20261029_v1'
CONTROL=ROOT/'data/derived/training_order_control_supervision_20261029_v1'
PREPARATION=ROOT/'results/training_order_control_preparation_20261029_v1.json'
FINAL=ROOT/'results/training_order_control_audit_20261029_v1.json'
DRIVER=ROOT/'scripts/source_to_route_with_training_v2.py'
BLOCK_CHECKER=ROOT/'scripts/check_source_to_route_with_training_v2.py'
SEED=20261029
CPU=121
AS_BYTES=16*1024**3
ACCEPTED='all_six_order_permutations_18_complete_training_inclusive_workers_independently_audited'


def schedule():
    rows=[list(p) for p in permutations(range(3))]
    random.Random(SEED).shuffle(rows)
    validate_schedule(rows)
    return rows


def validate_schedule(rows):
    require(isinstance(rows,list) and len(rows)==6 and all(isinstance(row,list) and len(row)==3 and all(type(x) is int for x in row) for row in rows),'Incomplete six-permutation schedule')
    require(set(map(tuple,rows))==set(permutations(range(3))),'Missing/duplicate full permutation')
    require(all(Counter(row[pos] for row in rows)=={0:2,1:2,2:2} for pos in range(3)),'Unbalanced positions')
    require(all(sum(row.index(a)<row.index(b) for row in rows)==3 for a in range(3) for b in range(3) if a!=b),'Unbalanced pairwise order')
    require(Counter((row[i],row[i+1]) for row in rows for i in range(2))=={(a,b):2 for a in range(3) for b in range(3) if a!=b},'Unbalanced within-block predecessor pairs')


def verify(files):
    require(isinstance(files,dict) and files,'Missing bindings')
    for p,h in files.items():require(digest(p)==h,'Changed complete experiment evidence: '+p)


def prior_evidence():
    original=json.loads(ORIGINAL.read_text());integrity=json.loads(INTEGRITY.read_text())
    require(original['status']=='complete_source_to_route_statistics_audited' and original['completed_workers']==21 and integrity['report_sha256']==digest(ORIGINAL) and integrity['completed_paired_blocks']==7,'Original seven-block result missing')
    files=dict(integrity['files']);verify(files)
    for p in [ORIGINAL,INTEGRITY,ORDER_EVIDENCE,VALIDATION_AUDIT]:files[str(p)]=digest(p)
    evidence=json.loads(ORDER_EVIDENCE.read_text());verify(evidence['files'])
    files.update(evidence['files'])
    audit=json.loads(VALIDATION_AUDIT.read_text());require(audit['status']=='all_source_to_route_integration_trials_audited' and audit['completed_workers']==3,'Original full validation missing')
    verify(audit['artifacts']);files.update(audit['artifacts'])
    base_path=VALIDATION/'plan.json';base=json.loads(base_path.read_text())
    require(audit['artifacts'][str(base_path)]==digest(base_path) and base['training_inclusive'] is True,'Different full original worker protocol')
    require(base['files'][str(DRIVER)]==digest(DRIVER),'Original full worker changed')
    require(audit['auditor_sha256']==digest(BLOCK_CHECKER),'Original complete block checker changed')
    require({(j['mode'],j['execution']) for j in base['jobs']}=={('csr','direct'),('compact','direct'),('compact','expanded')} and len(base['jobs'])==3,'Different condition matrix')
    files.update(base['files']);verify(files)
    return base,files


def prepared():
    report=json.loads(PREPARATION.read_text())
    require(report['status']=='six_permutation_full_workload_cpu_control_prepared_not_executed' and report['orders']==schedule() and report['cpu']==CPU and report['worker_as_bytes']==AS_BYTES and report['resource_policy']==POLICY,'Different prepared order control')
    require((report['workers'],report['batches_per_worker'],report['nets_per_batch'])==(18,2,1062),'Reduced complete workload')
    verify(report['files'])
    require(report['execution_files'] and all(report['files'].get(p)==h for p,h in report['execution_files'].items()),'Unbound execution closure')
    return report
