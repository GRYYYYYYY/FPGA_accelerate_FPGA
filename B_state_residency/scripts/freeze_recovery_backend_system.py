"""Freeze one full-system route idle-blocking regression, without structural acceptance."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
scratch=Path('/tmp/B_state_residency_offer_20261025')
names=['recovery_backend_system_crc_pressure_v2']
cases={};receipts={};manifests={}
for name in names:
    p=scratch/name;a=json.loads((p/'source_bound_audit.json').read_text());m=json.loads((p/'manifest.json').read_text())
    r=json.loads((ROOT/'results'/f'{name}_restore_20261025.json').read_text())
    assert a['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json')
    assert r['status']=='passed'and r['audit_byte_identical']and r['audit_sha256']==sha(p/'source_bound_audit.json')
    assert len(a['exact_comparisons'])==27
    cases[name]=a;receipts[name]=r;manifests[name]=m
result=dict(status='one_native_backend_crc_pressure_case_passed',cases=cases,restoration=receipts,
    compared_files=27,full_root_loop_free=False,full_matrix_complete=False,
    scope='Four native backend exclusion changes on restored route-block baseline; nine cumulative unique production sources. Observation-only TB monitors check both native interfaces. One CRC pressure case only; zero-depth capture retirement and full structural/timing/matrix acceptance not included.')
report=ROOT/'results/recovery_backend_system_crc_20261027.json';assert not report.exists()
report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
md='''# 原生后端互斥候选完整CRC恢复回归通过

recovery_backend_system_crc_pressure_v2在已恢复route_block参考上修改coordinator/residency/search/query四源，累计九个生产文件。通用组件EXCLUSIVE_BACKEND_RESPONSES默认关闭，原生query顶层开启，去掉互斥接口不可能的AS/OS READY分支。时序逻辑与输入不变；NORMAL候选、capture退休新修改均未包含。

完整27文件（12AXI、native事件及周期、DDR、恢复流等）逐字节等于参考，结束48288200ns一致。实际CRC末记录失败、错误回复保持/消费/退休、旧attempt拒绝、新attempt8非冷恢复781标签/156path/10query、最终回复消费后放行、CPU q4 83poll/82expand/402candidate/231cost及其他net保留结论适用于相同字节观察。

TB只读监视4828815个非冷复位周期，原生authority请求/回复各26，owner请求/回复各32，READY与回复VALID无重叠或未知重叠条件，覆盖非空journal修复及验证；没有修改握手或输入。此前九项原生coordinator模型测试验证默认兼容性，不能替代本完整系统，两个证据范围单列。

379文件归档实际恢复复审audit逐字节一致。归档fd9f4d2253b4cccdcd51034ae4df510529922762bd49324e2044d62dd1a5ab1b，audit2e9a1c160c8eaf3e40e45199aebddfb21f2dd24f3eed1e24cee6591730f5abcb。源码和检查工具冻结。

V1仅因TB声明顺序编译失败，V2生产RTL与V1完全相同，失败证据已另行保留。该结果只有单槽CRC一项，不代表其余七项矩阵、完整消环或物理时序通过。原生后端加capture退休的合并版本已由唯一后续链开始独立验证；当前报告不覆盖该额外修改。固定价格、可信初始快照、持久化floor/认证、自然overflow、物理实现与板卡缺口保持。
'''
(ROOT/'results/recovery_backend_system_crc_20261027.md').write_text(md)
frozen=ROOT/'results/recovery_backend_system_crc_sources_20261027';frozen.mkdir();files={};seen={};source_map={}
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
for n in ['run_recovery_backend_system_v2.py','audit_recovery_backend_system_v2.py','freeze_recovery_backend_system.py','run_checkpoint_authority.py']:
    copy(ROOT/'scripts'/n,Path('scripts')/n)
for n in ['recovery_backend_system_crc_20261027.json','recovery_backend_system_crc_20261027.md']:
    copy(ROOT/'results'/n,Path('reports')/n)
for n in ['build.py','CONTRACT.md']+[mode+'/'+name for mode in ['baseline','fixed']for name in ['recovery_coordinator.sv','residency_system.sv','search_residency_system.sv','query_residency_system.sv']]:
    copy(ROOT/'hardware/variants/recovery_backend_loops_v2'/n,Path('variant')/n)
copy(ROOT/'scripts/analyze_recovery_backend_exclusion.py',Path('scripts/analyze_recovery_backend_exclusion.py'))
copy(ROOT/'results/recovery_backend_exclusion_20261027.json',Path('reports/recovery_backend_exclusion_20261027.json'))
(frozen/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,source_map=source_map,full_matrix_complete=False),indent=2,sort_keys=True)+'\n')
print('RECOVERY_BACKEND_SYSTEM_FROZEN',len(files),'files')
