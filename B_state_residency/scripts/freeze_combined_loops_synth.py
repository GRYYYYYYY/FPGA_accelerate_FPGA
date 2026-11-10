"""Publish only terminal, restored cumulative OOC observations, never timing approval."""
from pathlib import Path
import json, shutil
from run_checkpoint_authority import ROOT, sha

p = Path('/tmp/B_state_residency_offer_20261025/combined_loops_synth_v1')
m = json.loads((p / 'manifest.json').read_text())
a = json.loads((p / 'source_bound_audit.json').read_text())
receipt = ROOT / 'results/combined_loops_synth_v1_restore_20261025.json'
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
    scope='Five-source cumulative structural recheck; matched 133 RTL list, parameters, part and 10ns clock. No IO timing, placement/routing or board conclusion. One CRC-pressure full behavioral regression passed separately; remaining seven matrix cases not implied.')
out = ROOT / 'results/combined_loops_synth_20261027.json'
assert not out.exists()
out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
md = f'''# 五源合并的完整层级结构复查

combined_loops_synth_v1仅合并已审计capture两源与REARM三源；133 RTL列表、全部参数、U280器件、10ns实验clock与restore_seed_synth_on_v1相同。Tcl只改变实验根路径，XDC逐字节一致。运行终态后实际重新打开DCP，提取LUTLP-1、methodology、check_timing及对象/cells/nets/pins；没有waiver或人工false-path。

产物来源及完整性审计passed；设计分类为{a['design_acceptance']}，timing_qualified=false。check_timing报告{a['check_timing_counts']['loops']}个环，独立LUTLP-1反馈区域包含的LUT数为{a['drc_loop_cell_counts']}。原参考分别为{old['check_timing_counts']['loops']}个环与{old['drc_loop_cell_counts']}。两类报告计数单位不同，不能相减解释为修复多少独立故障。当前文本列出{walks['explicit_walks']}条闭合pin walk，是否覆盖报告全部环为{walks['all_reported_loops_have_walks']}；未列出的路径不补造。

资源LUT {a['utilization']['LUT']:g}、FF {a['utilization']['FF']:g}、BRAM {a['utilization']['BRAM']:g}、DSP {a['utilization']['DSP']:g}、URAM {a['utilization']['URAM']:g}；latch/blackbox均为0。布局前WNS {a['preplacement_wns_ns']:g}ns，原参考{old['preplacement_wns_ns']:g}ns。报告包含自动环切断时，slack不能作为有效时序证明；无顶层IO延迟、物理时钟位置或place/route，资源变化不等于板卡收益。

归档实际恢复并重新独立审计，audit逐字节一致，源、工具和报告另行冻结。五源合并的CRC pressure完整行为回归单独见results/combined_loops_system_crc_20261027.json/.md；27文件及48288200ns与参考一致，不能替代本结构检查。其余七项矩阵仍未完成。

下一依据实际闭合pin walk与RTL接线隔离残余反馈，优先核对route host block及authority/发布路径。results/route_block_identity_20261027.json仅证明实际adapter资格下的局部二态恒等式，没有修改生产RTL或宣称全系统消环。完整物理时序、板卡、固定价格之外的有效性、持久化floor/认证与自然overflow分配回收仍未证明。
'''
(ROOT / 'results/combined_loops_synth_20261027.md').write_text(md)
frozen = ROOT / 'results/combined_loops_synth_sources_20261027'
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
for n in ['prepare_combined_loops_synth.py', 'run_restore_seed_synth.py',
          'inspect_restore_seed_synth.py', 'audit_combined_loops_synth.py',
          'audit_restore_seed_diagnostics.py', 'read_tcl_list_records.tcl',
          'analyze_restore_seed_loops.py', 'freeze_combined_loops_synth.py',
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
for n in ['combined_loops_synth_20261027.json', 'combined_loops_synth_20261027.md',
          'combined_loops_synth_v1_restore_20261025.json', 'route_block_identity_20261027.json']:
    copy(ROOT / 'results' / n, Path('reports') / n)
(frozen / 'manifest.json').write_text(json.dumps(dict(status='frozen', files=files,
    design_acceptance=a['design_acceptance'], timing_qualified=False), indent=2, sort_keys=True) + '\n')
print('COMBINED_SYNTH_FROZEN', len(files))
