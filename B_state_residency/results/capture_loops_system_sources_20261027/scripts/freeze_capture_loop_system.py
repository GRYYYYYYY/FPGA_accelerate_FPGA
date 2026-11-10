"""Freeze two exact full-system capture-fix regressions; remaining matrix stays open."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
scratch=Path('/tmp/B_state_residency_offer_20261025')
names=['capture_loops_system_on_full_v1','capture_loops_system_crc_pressure_v1']
cases={};receipts={};manifests={}
for name in names:
    p=scratch/name;a=json.loads((p/'source_bound_audit.json').read_text());m=json.loads((p/'manifest.json').read_text())
    r=json.loads((ROOT/'results'/f'{name}_restore_20261025.json').read_text())
    assert a['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json')
    assert r['status']=='passed'and r['audit_byte_identical']and r['audit_sha256']==sha(p/'source_bound_audit.json')
    assert len(a['exact_comparisons'])==27
    cases[name]=a;receipts[name]=r;manifests[name]=m
result=dict(status='two_full_system_cases_passed',cases=cases,restoration=receipts,
    compared_files=54,full_root_loop_free=False,full_matrix_complete=False,
    scope='Only the two capture-loop production source rewrites are integrated here. REARM candidates are separate work. Other capacity/default-off/cancel cases and all combined-fix regressions remain required; no full-root loop-free or timing/board claim.')
report=ROOT/'results/capture_loops_system_20261027.json';assert not report.exists()
report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
md='''# 查询展开消环的两个真实系统回归通过

capture_loops_system_on_full_v1（正常G4恢复）和capture_loops_system_crc_pressure_v1（单槽G4恢复末记录CRC失败、旧attempt拒绝、更高attempt非冷重试）仅替换recursive_candidate_controller和expansion_capture两份生产RTL，其余生产代码、TB、输入及编译参数与各自已审计参考相同。

每例27文件、共54文件逐字节相同：全部12路AXI、native事件及实际周期、最终DDR、恢复流及数据文件。所有参考均已实际归档恢复独立审计；本次没有改写日志或归一化周期。结束时刻分别44590330ns与48288200ns，与原参考精确相同。由这些相同观察数据继承原CPU q4的83poll/82expand/402candidate/231cost、全部781标签回读、owner及foreign net保留、恢复回执/退休/放行顺序的既有结论。

两个新归档已实际恢复并重审，audit逐字节一致。源和工具冻结单独目录。此前原生组件基线的3-LUT环已由小切片证明被去除，但这两个行为回归没有进行完整root重新综合，也没有证明其他组合反馈消失。

当前仅上述两例通过。优化关闭、其他容量、取消及其余CRC配置的完整矩阵仍未完成；计划在后续组合修复后统一执行，不能把这些未运行配置视为通过。另行开发的REARM三源修复尚未接入本结果。初始快照/固定价格、持久化floor/认证、自然overflow分配回收、物理时序和板卡收益等研究缺口不变。
'''
(ROOT/'results/capture_loops_system_20261027.md').write_text(md)
frozen=ROOT/'results/capture_loops_system_sources_20261027';frozen.mkdir();files={};seen={};source_map={}
def copy(src,rel):
    dst=frozen/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    assert sha(dst)==sha(src);files[str(rel)]=dict(source=str(src),sha256=sha(dst))
for name in names:
    p=scratch/name;source_map[name]={}
    for n,e in manifests[name]['sources'].items():
        src=p/'sources'/n;h=sha(src);assert h==e['sha256']
        if h not in seen:
            rel=Path('sources')/name/n;copy(src,rel);seen[h]=str(rel)
        source_map[name][n]=seen[h]
    for n in ['manifest.json','source_bound_audit.json']:copy(p/n,Path('reports')/name/n)
    copy(ROOT/'results'/f'{name}_restore_20261025.json',Path('reports')/f'{name}_restore.json')
for n in ['run_capture_loop_system.py','audit_capture_loop_system.py','freeze_capture_loop_system.py','run_checkpoint_authority.py']:
    copy(ROOT/'scripts'/n,Path('scripts')/n)
for n in ['capture_loops_system_20261027.json','capture_loops_system_20261027.md']:
    copy(ROOT/'results'/n,Path('reports')/n)
(frozen/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,source_map=source_map,full_matrix_complete=False),indent=2,sort_keys=True)+'\n')
print('CAPTURE_SYSTEM_FROZEN',len(files),'files')
