"""Freeze the first cumulative five-source system regression; keep full matrix open."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
scratch=Path('/tmp/B_state_residency_offer_20261025')
names=['combined_loops_system_crc_pressure_v1']
cases={};receipts={};manifests={}
for name in names:
    p=scratch/name;a=json.loads((p/'source_bound_audit.json').read_text());m=json.loads((p/'manifest.json').read_text())
    r=json.loads((ROOT/'results'/f'{name}_restore_20261025.json').read_text())
    assert a['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json')
    assert r['status']=='passed'and r['audit_byte_identical']and r['audit_sha256']==sha(p/'source_bound_audit.json')
    assert len(a['exact_comparisons'])==27
    cases[name]=a;receipts[name]=r;manifests[name]=m
result=dict(status='one_combined_crc_pressure_case_passed',cases=cases,restoration=receipts,
    compared_files=27,full_root_loop_free=False,full_matrix_complete=False,
    scope='Five audited capture and REARM source changes are integrated in one real CRC-failure and noncold-retry pressure case. Other capacity/default-off/cancel cases remain required. Full-root structural synthesis is separate; no timing/board claim.')
report=ROOT/'results/combined_loops_system_crc_20261027.json';assert not report.exists()
report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
md='''# 五源合并的完整CRC失败与非冷重试回归通过

combined_loops_system_crc_pressure_v1使用capture两源与REARM三源的实际已恢复审计候选；其余生产RTL、测试台、输入及参数与restore_seed_retry_crc_pressure_v1相同。residency_system新增退休信号在本例经过真实完整层级编译和仿真，组件测试没有覆盖的父层接线在此获得一项完整行为证据。

27文件逐字节匹配参考，包括全部12路AXI、native事件及实际周期、最终DDR、781标签/路径/query恢复流及数据文件；结束48288200ns一致。由相同观察继承已恢复审计参考的CRC末记录失败、回复保持/真实退休、旧attempt拒绝、更高attempt非冷重试、781标签回读、156path/10query字节、三回执与最终消费后放行、CPU q4 83poll/82expand/402candidate/231cost以及owner/foreign net保留结论。没有修改或归一化日志，也不把原单组件J0用例当本系统的journal证据。

新归档已实际恢复并重审，audit逐字节相同；源和工具另行冻结。本报告只覆盖优化开启、单槽、CRC故障配置。其余七项正常off/on双容量及cancel/CRC配置未因此通过。五源合并的完整综合、残余组合环与物理时序结论须另查结构报告；行为一致不证明结构无环或板卡加速。固定价格、外部初始快照、持久化floor/认证和自然overflow分配回收缺口保持。
'''
(ROOT/'results/combined_loops_system_crc_20261027.md').write_text(md)
frozen=ROOT/'results/combined_loops_system_crc_sources_20261027';frozen.mkdir();files={};seen={};source_map={}
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
for n in ['run_combined_loop_system.py','audit_combined_loop_system.py','freeze_combined_loop_system.py','run_checkpoint_authority.py']:
    copy(ROOT/'scripts'/n,Path('scripts')/n)
for n in ['combined_loops_system_crc_20261027.json','combined_loops_system_crc_20261027.md']:
    copy(ROOT/'results'/n,Path('reports')/n)
(frozen/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,source_map=source_map,full_matrix_complete=False),indent=2,sort_keys=True)+'\n')
print('COMBINED_SYSTEM_FROZEN',len(files),'files')
