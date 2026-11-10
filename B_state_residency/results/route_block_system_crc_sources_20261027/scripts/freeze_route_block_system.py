"""Freeze one full-system route idle-blocking regression, without structural acceptance."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
scratch=Path('/tmp/B_state_residency_offer_20261025')
names=['route_block_system_crc_pressure_v1']
cases={};receipts={};manifests={}
for name in names:
    p=scratch/name;a=json.loads((p/'source_bound_audit.json').read_text());m=json.loads((p/'manifest.json').read_text())
    r=json.loads((ROOT/'results'/f'{name}_restore_20261025.json').read_text())
    assert a['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json')
    assert r['status']=='passed'and r['audit_byte_identical']and r['audit_sha256']==sha(p/'source_bound_audit.json')
    assert len(a['exact_comparisons'])==27
    cases[name]=a;receipts[name]=r;manifests[name]=m
result=dict(status='one_route_block_crc_pressure_case_passed',cases=cases,restoration=receipts,
    compared_files=27,full_root_loop_free=False,full_matrix_complete=False,
    scope='Two route idle-blocking source changes on the restored five-source baseline; seven cumulative source changes. Only one full CRC-pressure case passed. NORMAL coordinator candidate is separate. Remaining matrix and structural/timing/board acceptance not implied.')
report=ROOT/'results/route_block_system_crc_20261027.json';assert not report.exists()
report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
md='''# 路由空闲封锁候选的完整CRC失败重试回归通过

route_block_system_crc_pressure_v1在已恢复审计的五源combined_loops_system_crc_pressure_v1上，仅改变route_commit_controller和route_commit_host_adapter：新增idle_fault接口，block_external以held||c_busy||c_idle_fault形成。完整fault、FSM、路径/checkpoint、journal与在途事务逻辑未变；累计七份生产源变化，其余RTL、TB、输入、参数均与参考相同。

27文件逐字节匹配参考，包括12路AXI、native事件与实际周期、最终DDR、恢复流和数据文件；结束48288200ns一致。对应参考的CRC末记录失败、保持/消费/退休、旧attempt拒绝、更高attempt非冷恢复781标签/156path/10query、三回执与最终回复消费后放行、CPU q4 83poll/82expand/402candidate/231cost及其他net保留结论适用于这些相同观察。没有改写日志或归一化周期。

实验归档实际恢复重审audit字节一致，源码及检查工具另行冻结。该项只覆盖优化开启、单槽CRC故障；其余七项矩阵尚未因此通过。匹配完整综合route_block_synth_v1的结构、资源与时序结论须单独读取，行为一致不证明无环或板卡收益。独立recovery_normal_loops_v2未接入本结果，不能把其组件回归计入此完整系统。

原固定价格/history、可信初始快照、持久化floor/认证、自然overflow分配回收与物理实现/板卡等缺口继续保留。
'''
(ROOT/'results/route_block_system_crc_20261027.md').write_text(md)
frozen=ROOT/'results/route_block_system_crc_sources_20261027';frozen.mkdir();files={};seen={};source_map={}
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
for n in ['run_route_block_system.py','audit_route_block_system.py','freeze_route_block_system.py','run_checkpoint_authority.py']:
    copy(ROOT/'scripts'/n,Path('scripts')/n)
for n in ['route_block_system_crc_20261027.json','route_block_system_crc_20261027.md']:
    copy(ROOT/'results'/n,Path('reports')/n)
for n in ['build.py','CONTRACT.md','baseline/route_commit_controller.sv','baseline/route_commit_host_adapter.sv','fixed/route_commit_controller.sv','fixed/route_commit_host_adapter.sv']:
    copy(ROOT/'hardware/variants/route_block_loops_v1'/n,Path('variant')/n)
copy(ROOT/'scripts/analyze_route_block_identity.py',Path('scripts/analyze_route_block_identity.py'))
copy(ROOT/'results/route_block_identity_20261027.json',Path('reports/route_block_identity_20261027.json'))
(frozen/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,source_map=source_map,full_matrix_complete=False),indent=2,sort_keys=True)+'\n')
print('ROUTE_BLOCK_SYSTEM_FROZEN',len(files),'files')
