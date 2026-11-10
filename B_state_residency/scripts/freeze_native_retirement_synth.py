"""Publish only terminal, restored cumulative OOC observations, never timing approval."""
from pathlib import Path
import json, shutil
from run_checkpoint_authority import ROOT, sha

p = Path('/tmp/B_state_residency_offer_20261025/native_retirement_synth_v1')
m = json.loads((p / 'manifest.json').read_text())
a = json.loads((p / 'source_bound_audit.json').read_text())
receipt = ROOT / 'results/native_retirement_synth_v1_restore_20261025.json'
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
    utilization_delta={k: a['utilization'][k] - old['utilization'][k] for k in a['utilization']},
    full_behavior_matrix_complete=False,
    scope='Ten-source cumulative structural recheck; matched 133 RTL list, parameters, part and 10ns clock. No IO timing, placement/routing or board conclusion. One CRC-pressure full behavioral regression passed separately; remaining seven matrix cases not implied.')
out = ROOT / 'results/native_retirement_synth_20261027.json'
assert not out.exists()
out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
md = f'''# 原生后端与capture退休合并版本的完整综合复查

native_retirement_synth_v1在已恢复route_block参考上增加backend四源与capture退休一源，累计相对原seed十个唯一生产文件。133 RTL、全部参数、U280器件、10ns时钟一致，未合成TB监视器。默认通用backend协议保留，实际query原生接口互斥特化；退休仍要求零depth与其余所有服务退休。

完整综合及独立重开DCP诊断结束。check_timing组合环{a['check_timing_counts']['loops']}（参考{old['check_timing_counts']['loops']}），LUTLP-1区域LUT计数{a['drc_loop_cell_counts']}；文本闭合walk {walks['explicit_walks']}，覆盖全部报告路径为{walks['all_reported_loops_have_walks']}。这些是匹配综合网表的报告结果，不是任意配置无环或RTL形式证明。

LUT {a['utilization']['LUT']:g}、FF {a['utilization']['FF']:g}、BRAM {a['utilization']['BRAM']:g}、DSP {a['utilization']['DSP']:g}、URAM {a['utilization']['URAM']:g}，零latch/blackbox。布局前WNS {a['preplacement_wns_ns']:g}ns，参考{old['preplacement_wns_ns']:g}ns。自动Synth8-326环切断警告出现{len(a['timing_loop_warnings'])}次；若非零则不能用相关slack证明有效时序。无IO延迟/物理时钟位置/布局布线，即使未报环也不是物理时序或板卡频率。design_acceptance={a['design_acceptance']}，timing_qualified=false；产物完整性audit passed不等于硬件验收。

归档已实际恢复并重审audit字节一致，源、工具、局部证明与报告冻结。完整CRC行为由独立native_retirement_system_crc报告提供；同源八项矩阵仍需逐例审计，不能从结构检查推导行为正确。其余固定价格/可信初始快照/持久化floor认证/自然overflow/物理实现和板卡缺口保留。
'''
(ROOT / 'results/native_retirement_synth_20261027.md').write_text(md)
frozen = ROOT / 'results/native_retirement_synth_sources_20261027'
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
for n in ['prepare_native_retirement_synth.py', 'run_restore_seed_synth.py',
          'inspect_restore_seed_synth.py', 'audit_native_retirement_synth.py',
          'audit_restore_seed_diagnostics.py', 'read_tcl_list_records.tcl',
          'analyze_restore_seed_loops.py', 'freeze_native_retirement_synth.py',
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
for n in ['native_retirement_synth_20261027.json', 'native_retirement_synth_20261027.md',
          'native_retirement_synth_v1_restore_20261025.json', 'route_block_identity_20261027.json']:
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
print('NATIVE_RETIREMENT_SYNTH_FROZEN', len(files))
