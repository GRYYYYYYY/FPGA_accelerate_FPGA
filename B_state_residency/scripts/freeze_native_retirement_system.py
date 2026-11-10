"""Freeze one full-system route idle-blocking regression, without structural acceptance."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
scratch=Path('/tmp/B_state_residency_offer_20261025')
names=['native_retirement_system_crc_pressure_v1']
cases={};receipts={};manifests={}
for name in names:
    p=scratch/name;a=json.loads((p/'source_bound_audit.json').read_text());m=json.loads((p/'manifest.json').read_text())
    r=json.loads((ROOT/'results'/f'{name}_restore_20261025.json').read_text())
    assert a['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json')
    assert r['status']=='passed'and r['audit_byte_identical']and r['audit_sha256']==sha(p/'source_bound_audit.json')
    assert len(a['exact_comparisons'])==27
    cases[name]=a;receipts[name]=r;manifests[name]=m
result=dict(status='one_native_retirement_crc_pressure_case_passed',cases=cases,restoration=receipts,
    compared_files=27,full_root_loop_free=None,full_matrix_complete=False,
    scope='Four native backend exclusion changes plus one zero-depth capture retirement change on restored route-block baseline; ten cumulative unique production sources. One complete CRC pressure case, with exact outputs/cycles and observation-only native interface/retirement monitors. Structural and remaining matrix acceptance are separate.')
report=ROOT/'results/native_retirement_system_crc_20261027.json';assert not report.exists()
report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
coverage=cases[names[0]]['capture_retirement']
backend=cases[names[0]]['backend_exclusion']
receipt=receipts[names[0]]
md=f'''# 后端互斥与capture退休合并版本完整CRC回归通过

native_retirement_system_crc_pressure_v1基于已恢复route_block参考，合并后端四源与query core退休一源，累计相对原seed十个唯一生产文件。通用backend参数默认关闭，原生query显式开启；retired_idle保留零depth条件，仅删除由零depth蕴含的无capture结果项。全部时序逻辑和输入不变，未包含独立NORMAL候选。

27文件（12AXI、native事件/周期、DDR、恢复流等）逐字节匹配，结束48288200ns一致；实际CRC错误、保持/消费/退休、旧attempt拒绝、attempt8非冷恢复781标签/156path/10query、CPU q4 83poll/82expand/402candidate/231cost和其他net保留结论适用于相同观察。未归一化日志或放宽周期检查。

backend只读观测{backend['cycles']}周期、authority请求回复各{backend['authority']}、owner各{backend['owner']}，两接口READY与回复VALID互斥成立。capture退休观测{coverage['cycles']}周期，非零depth共{coverage['nonzero_cycles']}周期、结果VALID共{coverage['reply_cycles']}周期；零depth无结果，实际retired_idle逐周期等于完整原谓词，没有强制DUT信号。

{receipt['files']}文件归档已实际恢复复审，audit逐字节一致。archive {receipt['archive_sha256']}，audit {receipt['audit_sha256']}。源码、工具与局部8192组二态证明冻结；局部证明并非X/Z形式等价，本回归也不代表所有输入。

仅单槽CRC压力例完成；同源综合见独立结构报告，不能从行为一致推断无组合环或时序。其余七项最终矩阵待独立执行；原始CRC参考直接核对由audit_native_matrix_crc_anchor.py单列，避免重复仿真。固定价格、可信初始快照、持久化floor/认证、自然overflow、物理实现和板卡缺口保持。
'''
(ROOT/'results/native_retirement_system_crc_20261027.md').write_text(md)
frozen=ROOT/'results/native_retirement_system_crc_sources_20261027';frozen.mkdir();files={};seen={};source_map={}
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
for n in ['run_native_retirement_system.py','audit_native_retirement_system.py','freeze_native_retirement_system.py','run_checkpoint_authority.py']:
    copy(ROOT/'scripts'/n,Path('scripts')/n)
for n in ['native_retirement_system_crc_20261027.json','native_retirement_system_crc_20261027.md']:
    copy(ROOT/'results'/n,Path('reports')/n)
for n in ['build.py','CONTRACT.md']+[mode+'/'+name for mode in ['baseline','fixed']for name in ['recovery_coordinator.sv','residency_system.sv','search_residency_system.sv','query_residency_system.sv','priced/candidate_recursive_query_core.sv']]:
    copy(ROOT/'hardware/variants/native_retirement_loops_v1'/n,Path('variant')/n)
copy(ROOT/'scripts/analyze_recovery_backend_exclusion.py',Path('scripts/analyze_recovery_backend_exclusion.py'))
copy(ROOT/'results/recovery_backend_exclusion_20261027.json',Path('reports/recovery_backend_exclusion_20261027.json'))
for parent in ['recovery_backend_loops_v2','capture_retirement_loops_v1']:
    for n in ['build.py','CONTRACT.md']:
        copy(ROOT/'hardware/variants'/parent/n,Path('parent_variants')/parent/n)
copy(ROOT/'scripts/analyze_capture_retirement_identity.py',Path('scripts/analyze_capture_retirement_identity.py'))
copy(ROOT/'results/capture_retirement_identity_20261027.json',Path('reports/capture_retirement_identity_20261027.json'))
(frozen/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,source_map=source_map,full_matrix_complete=False),indent=2,sort_keys=True)+'\n')
print('NATIVE_RETIREMENT_SYSTEM_FROZEN',len(files),'files')
