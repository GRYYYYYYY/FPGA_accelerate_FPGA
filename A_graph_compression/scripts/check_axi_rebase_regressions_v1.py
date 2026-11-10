#!/usr/bin/env python3
"""Re-read the structural and behavioral evidence before full native execution."""
import json
from pathlib import Path
import re
from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]


def audit():
    files = {}
    def read(path):
        path = Path(path); result = json.loads(path.read_text())
        files[str(path)] = digest(path)
        for name, sha in result.get('files', {}).items():
            require(name not in files or files[name] == sha, 'Conflicting evidence')
            files[name] = sha
        return result
    structural = read(ROOT/'results/compact_nonzero_axi_models_structure_audit_20261029_v1.json')
    require(structural['status'] == 'all30_original_model_bodies_and_complete_address_wrapper_connections_independently_verified', 'Wrong structure proof')
    require(len(structural['models']) == len({m['bundle'] for m in structural['models']}) == 30, 'Incomplete models')
    for m in structural['models']:
        require(m['preserved_parameters'] == 14 and m['original_model_body_exact'] and m['address_translations'] == 2, 'Incomplete preservation')
    guards = read(ROOT/'results/axi_rebase_guard_regression_20261029_v3.json')
    models = read(ROOT/'results/axi_rebase_model_regression_20261029_v3.json')
    require(guards['status'] == 'rebase_guard_1300_accepted_requests_and20_invalid_handshakes_verified' and guards['accepted_requests'] == 1300 and len(guards['rejected_cases']) == 20, 'Guard scope differs')
    require(models['status'] == 'six_original_full_depth_models_all4pages_rebased_response_payload_and_readonly_regression_verified', 'Missing model regression')
    expected = {'completion_mem': (32,65536), 'state_mem': (64,65), 'site_scratch_mem': (128,81920),
                'node_meta_mem': (256,1), 'tree_meta_mem': (512,1), 'batch_input_mem': (512,2)}
    require({m['bundle']: (m['data_bits'],m['depth']) for m in models['models']} == expected and len(models['models']) == 6, 'Model capacity/width matrix differs')
    for m in models['models']:
        require(m['pages'] == 4 and m['response_cycles_compared'], 'Four-page response evidence missing')
        if m['bundle'] == 'batch_input_mem': require(m['readonly_write_and_zero_strobe_rejected'], 'RO zero strobes omitted')
        else: require(m['all_output_words_verified'] == m['depth']*4, 'Partial model outputs')
    gd = ROOT/'data/derived/axi_rebase_guard_regression_20261029_v3'
    checks = [(gd,'xvlog',None,None), (gd,'xelab',None,None), (gd,'positive',0,None)]
    checks += [(gd,c['name'],i,c['expected']) for i,c in enumerate(guards['rejected_cases'],1)]
    for bundle in expected:
        directory = ROOT/'data/derived/axi_rebase_model_regression_20261029_v3'/bundle/'sim/verilog'
        checks += [(directory,'xvlog',None,None), (directory,'xelab',None,None), (directory,'positive',0,None)]
        if bundle == 'batch_input_mem': checks += [(directory,'readonly_'+str(i),i,'A_RO_WRITE_VIOLATION') for i in [1,2]]
    for directory,phase,case,error in checks:
        rp = directory/(phase+'.receipt.json'); lp = directory/(phase+'.log')
        require(str(rp) in files and str(lp) in files, 'Unbound execution evidence')
        receipt = json.loads(rp.read_text()); log = lp.read_text()
        require(receipt['log_sha256'] == digest(lp) and receipt['elapsed_seconds'] > 0, 'Changed/empty execution')
        require(receipt['expected_failure'] == error, 'Different expected verdict')
        if case is not None:
            require(re.findall(r'^SELECTED_CASE=(\d+)$',log,re.M) == [str(case)], 'Wrong case selected')
            require(receipt['command'][-2:] == ['-testplusarg','CASE='+str(case)], 'Different test command')
        if error:
            require(receipt['exit_code'] in [0,1] and 'Fatal:' in log and error in log and 'UNEXPECTED_ACCEPTANCE' not in log and '_PASS' not in log, 'Negative case not rejected')
        else:
            require(receipt['exit_code'] == 0 and not any(x in log for x in ['ERROR:','Fatal:','FATAL','UNEXPECTED_ACCEPTANCE']), 'Unexpected execution failure')
            if case == 0: require(('A_REBASE_GUARD_PASS widths=5 accepted_requests=1300' if directory == gd else 'MODEL_REBASE_PASS bundle='+directory.parents[1].name) in log, 'Missing terminal pass')
    for name,sha in files.items(): require(digest(name) == sha, 'Changed regression evidence: '+name)
    files[str(Path(__file__).resolve())] = digest(__file__)
    return dict(status='all30_structure_1300_positive20_negative_six_full_depth_models_evidence_independently_rechecked', files=files,
                models=30, pointers=44, transactions=4, guard_requests=1300, negative_guard_cases=20,
                representative_models=6, executed_phases=len(checks), full_kernel_verified=False)


if __name__ == '__main__':
    result = audit(); target = ROOT/'results/axi_rebase_regressions_independent_audit_20261029_v1.json'
    with target.open('x') as f: json.dump(result,f,indent=2); f.write('\n')
    print(result['status'],len(result['files']))
