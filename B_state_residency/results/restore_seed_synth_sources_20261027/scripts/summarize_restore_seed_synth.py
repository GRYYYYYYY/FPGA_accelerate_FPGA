"""Publish the matched, restored synthesis rejection and freeze its evidence tools."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha

scratch=Path('/tmp/B_state_residency_offer_20261025')
cases={};manifests={};receipts={}
for mode in ['off','on']:
    name=f'restore_seed_synth_{mode}_v1';p=scratch/name
    m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
    rpath=ROOT/'results'/f'{name}_restore_20261025.json';r=json.loads(rpath.read_text())
    assert m['status']=='observed'and m['exit_code']==0
    assert a['status']=='passed'and a['design_acceptance']=='rejected_combinational_loops'
    assert a['manifest_sha256']==sha(p/'manifest.json')
    assert r['status']=='passed'and r['audit_byte_identical']and r['audit_sha256']==sha(p/'source_bound_audit.json')
    assert a['parameters']['ENABLE_RESTORE_SEED_BYPASS']==int(mode=='on')
    manifests[mode]=m;cases[mode]=a;receipts[mode]=r
assert manifests['off']['sources']==manifests['on']['sources']
assert {k:v for k,v in manifests['off']['parameters'].items()if k!='ENABLE_RESTORE_SEED_BYPASS'}=={k:v for k,v in manifests['on']['parameters'].items()if k!='ENABLE_RESTORE_SEED_BYPASS'}
assert all(cases[x]['check_timing_counts']['loops']==20 for x in cases)
assert cases['off']['drc_loop_cell_counts']==[103]and cases['on']['drc_loop_cell_counts']==[107]
delta={k:cases['on']['utilization'][k]-cases['off']['utilization'][k]for k in cases['off']['utilization']}
result=dict(status='diagnosed_design_rejected',design_acceptance='rejected_combinational_loops',timing_qualified=False,
    source_identical=True,only_generic_difference='ENABLE_RESTORE_SEED_BYPASS',cases=cases,
    on_minus_off_resources=delta,archive_restoration=receipts,
    conclusions=[
      'Both matched roots synthesize, but both fail structural timing acceptance.',
      'check_timing reports20 loops in each; LUTLP-1 reports one103/107-LUT region. These are different report units.',
      'Both baseline and bypass configurations contain feedback; these runs do not isolate the introducing historical change.',
      'Observed resource deltas are for these exact synthesized roots only, not implemented hardware or universal optimization savings.',
      'Behavioral label recovery cycle savings remain scoped to the prior audited simulation. No timing closure, frequency or board speedup claim.'],
    next_plan='hardware/variants/timing_loops_v1/PLAN.md',
    limits=manifests['on']['scope'])
out=ROOT/'results'/'restore_seed_synth_20261027.json';assert not out.exists()
out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
text='''# 匹配参数综合完成，组合环导致设计验收失败

两版均为Vivado2022.2、U280 query_residency_system OOC；133份RTL相同，唯一generic差异ENABLE_RESTORE_SEED_BYPASS。4路径、32槽、16384帧、1024恢复记录、baseline/warm开启、测试注入关闭；全部runtime端口保留。资源报告和独立DCP诊断已经审计，两归档实际恢复后审计字节一致。产物审计通过不等于设计验收通过。

| 指标 | 关闭 | 开启 |
| --- | ---: | ---: |
| LUT | 140295 | 139752 |
| FF | 88213 | 88155 |
| BRAM tile | 163 | 163 |
| DSP | 23 | 23 |
| URAM/latch/blackbox | 0 | 0 |
| check_timing组合环 | 20 | 20 |
| LUTLP-1区域内LUT数 | 103 | 107 |
| 10ns布局前WNS/ns | -9.941 | -9.910 |

开启减543 LUT/58 FF，仅为这两个具体综合结果；不能把带组合环的时序估计当作可实现频率。最差开启版路径从directory lease_phase寄存器到search error_code，有84级逻辑，估计19.892ns数据路径。当前首先消除反馈，再处理长路径。实际DCP诊断未添加waiver、ALLOW_COMBINATORIAL_LOOPS或false-path；导出XDC仅含10ns时钟，不能据此否认综合内部自动切环。

每版methodology返回SYNTH-10=23、TIMING-16=1000、TIMING-18=1000、TIMING-23=1个对象；1000是本次返回数量，不能当作完整端点总数。check_timing列明关闭46801、开启46802输入以及各10419输出无IO delay，是本OOC接口边界未定义；无no_clock或内部未约束端点。10ns只是实验目标，尚无板级接口延迟和物理时钟位置约束。

check_timing报告20环，但只列出关闭18条/开启9条完整pin walk；分析器显式保存缺口。LUTLP-1通过对象查询提取全部103/107个cells并与描述核对；它与20环不是相同计数单位。共有反馈涉及recovery、authority、publication、fence、label、route和child_capture。源码可疑依赖和后续原生组件/完整系统回归要求见hardware/variants/timing_loops_v1/PLAN.md；尚未应用生产修复。

新审计器开发中，原先拒绝所有critical warning的门槛遇到实际Synth8-295；现明确记录该已检查的失败证据，并将design_acceptance标为rejected_combinational_loops，未知critical仍拒绝。原审计器和失败说明保留在restore_seed_synth_loop_observation_20261027。无原始数据或生产源码修改。

外部baseline provider和snapshot writers不在query root内。此前仿真正确性与23.6%/30.3%标签阶段周期减少保持其原范围，尚无硬件时序、板卡性能或全局任意输入保证。下一优先隔离原生握手与REARM反馈、完整消环和协议/AXI/数值回归；研究继续。
'''
(ROOT/'results'/'restore_seed_synth_20261027.md').write_text(text)
freeze=ROOT/'results'/'restore_seed_synth_sources_20261027';freeze.mkdir()
files={}
def copy(src,rel):
    dst=freeze/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    assert sha(src)==sha(dst);files[str(rel)]=dict(source=str(src),sha256=sha(dst))
base=scratch/'restore_seed_synth_on_v1'
for name,h in manifests['on']['sources'].items():
    assert sha(base/'sources'/name)==h
    copy(base/'sources'/name,Path('rtl')/name)
for name in ['prepare_restore_seed_synth.py','run_restore_seed_synth.py','audit_restore_seed_synth.py',
             'inspect_restore_seed_synth.py','analyze_restore_seed_loops.py','audit_restore_seed_diagnostics.py',
             'read_tcl_list_records.tcl','summarize_restore_seed_synth.py','run_checkpoint_authority.py',
             'archive_offer_result.py','restore_offer_result.py','verify_search_retire_restore.py','release_experiment_cache.py']:
    copy(ROOT/'scripts'/name,Path('scripts')/name)
for f in sorted((ROOT/'hardware/variants/timing_loops_v1').iterdir()):
    if f.is_file():copy(f,Path('variant')/f.name)
for f in sorted((ROOT/'results/restore_seed_synth_loop_observation_20261027').iterdir()):
    if f.is_file():copy(f,Path('early_observation')/f.name)
for mode in ['off','on']:
    p=scratch/f'restore_seed_synth_{mode}_v1'
    for name in ['manifest.json','synth.tcl','clock.xdc','source_bound_audit.json','diagnostic_audit.json','loop_walks.json']:
        copy(p/name,Path('cases')/mode/name)
    for name in ['manifest.json','inspect.tcl','methodology.rpt','loops.rpt','effective.xdc','loop_elements.tcllist']:
        copy(p/'results/methodology_v1'/name,Path('cases')/mode/'diagnostics'/name)
for name in ['restore_seed_synth_20261027.json','restore_seed_synth_20261027.md',
             'restore_seed_synth_off_v1_restore_20261025.json','restore_seed_synth_on_v1_restore_20261025.json']:
    copy(ROOT/'results'/name,Path('reports')/name)
(freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',design_acceptance='rejected_combinational_loops',files=files),indent=2,sort_keys=True)+'\n')
print('SYNTHESIS_REJECTION_RECORDED',delta,'frozen_files',len(files))
