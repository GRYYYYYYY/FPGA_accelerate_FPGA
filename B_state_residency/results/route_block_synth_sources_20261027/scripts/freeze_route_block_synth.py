"""Publish only terminal, restored cumulative OOC observations, never timing approval."""
from pathlib import Path
import json, shutil
from run_checkpoint_authority import ROOT, sha

p = Path('/tmp/B_state_residency_offer_20261025/route_block_synth_v1')
m = json.loads((p / 'manifest.json').read_text())
a = json.loads((p / 'source_bound_audit.json').read_text())
receipt = ROOT / 'results/route_block_synth_v1_restore_20261025.json'
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
    scope='Seven-source cumulative structural recheck; matched 133 RTL list, parameters, part and 10ns clock. No IO timing, placement/routing or board conclusion. One CRC-pressure full behavioral regression passed separately; remaining seven matrix cases not implied.')
out = ROOT / 'results/route_block_synth_20261027.json'
assert not out.exists()
out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
md = f'''# 路由门控修改后的完整综合复查

route_block_synth_v1在已审计五源combined参考上新增controller idle_fault和host adapter门控两源变化，累计七个生产文件。133 RTL、所有参数、U280器件、10ns时钟保持一致；只有实验根路径变化。原生完整CRC行为27文件/48288200ns匹配另见route_block_system_crc_20261027。

完整综合与独立重开DCP诊断结束。产物完整性审计passed；设计仍为{a['design_acceptance']}，timing_qualified=false。check_timing报告{a['check_timing_counts']['loops']}个组合环，原参考{old['check_timing_counts']['loops']}；LUTLP-1区域LUT计数{a['drc_loop_cell_counts']}。文本{walks['explicit_walks']}条闭合pin walk，是否列出报告全部环为{walks['all_reported_loops_have_walks']}。环数变化不是已修复独立故障数量。

LUT {a['utilization']['LUT']:g}、FF {a['utilization']['FF']:g}、BRAM {a['utilization']['BRAM']:g}、DSP {a['utilization']['DSP']:g}、URAM {a['utilization']['URAM']:g}；零latch/blackbox。布局前WNS {a['preplacement_wns_ns']:g}ns，参考{old['preplacement_wns_ns']:g}ns。仍有自动环切断，不能把时序数值当有效频率或板卡收益；无IO时序/物理时钟位置/布局布线。

归档已实际恢复复审，audit逐字节一致；源、工具与报告冻结。当前路径涉及authority请求READY与恢复/发布故障反馈，及core capture/退休/fence反馈。下一候选recovery_backend_loops_v2仅对已证明READY与回复VALID互斥的原生query接线去掉不可能分支，通用参数默认关闭；九项原生组件测试通过但完整CRC仍需单独取得终态审计。该候选不在本次综合内，不能把本结果称下一候选的结构验证。

正常off/on双容量、cancel双容量及CRC full其余七项矩阵仍待最终候选验证。固定价格、可信初始快照、持久化floor/认证、自然overflow分配回收、物理实现和板卡缺口保持。
'''
(ROOT / 'results/route_block_synth_20261027.md').write_text(md)
frozen = ROOT / 'results/route_block_synth_sources_20261027'
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
for n in ['prepare_route_block_synth.py', 'run_restore_seed_synth.py',
          'inspect_restore_seed_synth.py', 'audit_route_block_synth.py',
          'audit_restore_seed_diagnostics.py', 'read_tcl_list_records.tcl',
          'analyze_restore_seed_loops.py', 'freeze_route_block_synth.py',
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
for n in ['route_block_synth_20261027.json', 'route_block_synth_20261027.md',
          'route_block_synth_v1_restore_20261025.json', 'route_block_identity_20261027.json']:
    copy(ROOT / 'results' / n, Path('reports') / n)
(frozen / 'manifest.json').write_text(json.dumps(dict(status='frozen', files=files,
    design_acceptance=a['design_acceptance'], timing_qualified=False), indent=2, sort_keys=True) + '\n')
print('ROUTE_BLOCK_SYNTH_FROZEN', len(files))
