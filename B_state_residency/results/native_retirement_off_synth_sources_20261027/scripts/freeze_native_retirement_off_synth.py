"""Publish only terminal, restored cumulative OOC observations, never timing approval."""
from pathlib import Path
import json, shutil
from run_checkpoint_authority import ROOT, sha

p = Path('/tmp/B_state_residency_offer_20261025/native_retirement_synth_off_v1')
m = json.loads((p / 'manifest.json').read_text())
a = json.loads((p / 'source_bound_audit.json').read_text())
receipt = ROOT / 'results/native_retirement_synth_off_v1_restore_20261025.json'
r = json.loads(receipt.read_text())
assert m['status'] == 'observed' and a['status'] == r['status'] == 'passed'
assert a['manifest_sha256'] == sha(p / 'manifest.json')
assert r['audit_byte_identical'] and r['audit_sha256'] == sha(p / 'source_bound_audit.json')
assert not a['timing_qualified']
ref = Path(m['reference'])
old = json.loads((ref / 'source_bound_audit.json').read_text())
assert sha(ref / 'source_bound_audit.json') == a['reference_audit_sha256']
walks = json.loads((p / 'loop_walks.json').read_text())
result = dict(status='artifact_integrity_verified_no_timing_acceptance', audit=a,
    restoration=r, literal_walks=walks,
    reference_summary={k: old[k] for k in ['design_acceptance', 'check_timing_counts',
        'drc_loop_cell_counts', 'utilization', 'preplacement_wns_ns']},
    utilization_delta_off_minus_on={k: a['utilization'][k] - old['utilization'][k] for k in a['utilization']},
    behavior_matrix_assessed_here=False,
    scope='Same final133 production sources as restored bypass-on reference. Only ENABLE_RESTORE_SEED_BYPASS differs1 to0; part, clock and all other parameters unchanged. Matched OOC resource and preplacement timing observations, not physical implementation or board speed.')
out = ROOT / 'results/native_retirement_off_synth_20261027.json'
assert not out.exists()
out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
assert a['only_parameter_changed']=='ENABLE_RESTORE_SEED_BYPASS'
reference_sources=json.loads((ref/'manifest.json').read_text())['sources']
for n in m['rtl']:assert m['sources'][n]==reference_sources[n]
md = f'''# 修复后同源关闭/开启旁路OOC对照

关闭版native_retirement_synth_off_v1与已实际恢复的开启版native_retirement_synth_v1使用完全相同133份生产RTL。唯一参数差异为ENABLE_RESTORE_SEED_BYPASS从1变0，其余参数、U280器件、10ns时钟和Tcl命令保持匹配；除实验路径与这一项generic外脚本逐字节一致。没有沿用旧含组合环版本的资源差值。

关闭版check_timing组合环{a['check_timing_counts']['loops']}，LUTLP-1区域LUT计数{a['drc_loop_cell_counts']}，开启版组合环{old['check_timing_counts']['loops']}。关闭版自动环切断警告{len(a['timing_loop_warnings'])}次；若出现环或自动切断，不把相关slack解释为有效时序。零latch/blackbox。

关闭版LUT {a['utilization']['LUT']:g}、FF {a['utilization']['FF']:g}、BRAM {a['utilization']['BRAM']:g}、DSP {a['utilization']['DSP']:g}、URAM {a['utilization']['URAM']:g}；开启版LUT {old['utilization']['LUT']:g}、FF {old['utilization']['FF']:g}、BRAM {old['utilization']['BRAM']:g}、DSP {old['utilization']['DSP']:g}。JSON的utilization_delta_off_minus_on为关闭减开启，不混用差值方向。布局前WNS关闭{a['preplacement_wns_ns']:g}ns/开启{old['preplacement_wns_ns']:g}ns。

两者没有IO延迟/物理时钟位置/布局布线证据，不能把资源与估计slack直接转换成板卡收益或闭合频率。关闭版design_acceptance={a['design_acceptance']}、timing_qualified=false。产物审计与归档实际恢复通过，audit字节一致，相关源和工具冻结；八项行为矩阵另行审计，不由本资源对照代替。
'''
(ROOT / 'results/native_retirement_off_synth_20261027.md').write_text(md)
frozen = ROOT / 'results/native_retirement_off_synth_sources_20261027'
frozen.mkdir()
files = {}
def copy(src, rel):
    dest = frozen / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    assert sha(dest) == sha(src)
    files[str(rel)] = dict(source=str(src), sha256=sha(dest))

for n, h in m['sources'].items():
    assert sha(p / 'sources' / n) == h
    copy(p / 'sources' / n, Path('sources') / n)
for n in ['prepare_native_retirement_off_synth.py', 'run_restore_seed_synth.py',
          'inspect_restore_seed_synth.py', 'audit_native_retirement_off_synth.py',
          'audit_restore_seed_diagnostics.py', 'read_tcl_list_records.tcl',
          'analyze_restore_seed_loops.py', 'freeze_native_retirement_off_synth.py',
          'run_checkpoint_authority.py', 'archive_offer_result.py',
          'restore_offer_result.py', 'verify_search_retire_restore.py',
          'analyze_route_block_identity.py']:
    copy(ROOT / 'scripts' / n, Path('scripts') / n)
for n in ['manifest.json', 'source_bound_audit.json', 'diagnostic_audit.json',
          'loop_walks.json', 'synth.tcl', 'clock.xdc', 'facts.txt', 'utilization.rpt',
          'check_timing.rpt', 'timing_synth.rpt', 'clocks.rpt']:
    copy(p / n, Path('reports') / n)
for n in ['manifest.json', 'inspect.tcl', 'effective.xdc', 'loops.rpt',
          'methodology.rpt', 'methodology_objects.tcllist', 'loop_objects.tcllist',
          'loop_elements.tcllist', 'timing_path_objects.tcllist', 'check_timing.rpt']:
    copy(p / 'results/methodology_v1' / n, Path('reports/methodology') / n)
for n in ['native_retirement_off_synth_20261027.json', 'native_retirement_off_synth_20261027.md',
          'native_retirement_synth_off_v1_restore_20261025.json', 'route_block_identity_20261027.json']:
    copy(ROOT / 'results' / n, Path('reports') / n)
for variant in ['native_retirement_loops_v1','recovery_backend_loops_v2','capture_retirement_loops_v1']:
    for name in ['build.py','CONTRACT.md']:
        copy(ROOT/'hardware/variants'/variant/name,Path('variants')/variant/name)
for name in ['analyze_recovery_backend_exclusion.py','analyze_capture_retirement_identity.py']:
    copy(ROOT/'scripts'/name,Path('scripts')/name)
for name in ['recovery_backend_exclusion_20261027.json','capture_retirement_identity_20261027.json']:
    copy(ROOT/'results'/name,Path('reports')/name)
(frozen / 'manifest.json').write_text(json.dumps(dict(status='frozen', files=files,
    design_acceptance=a['design_acceptance'], timing_qualified=False), indent=2, sort_keys=True) + '\n')
print('NATIVE_OFF_SYNTH_FROZEN', len(files))
