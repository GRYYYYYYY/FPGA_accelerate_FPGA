"""Freeze native lifecycle equivalence separately from any full-root structure claim."""
from pathlib import Path
import json, shutil
from run_checkpoint_authority import ROOT, sha

scratch = Path('/tmp/B_state_residency_offer_20261025')
names = ['recovery_normal_native_v1', 'recovery_normal_native_v2']
evidence = {}
for name in names:
    p = scratch / name
    m = json.loads((p / 'manifest.json').read_text())
    a = json.loads((p / 'source_bound_audit.json').read_text())
    receipt = ROOT / 'results' / f'{name}_restore_20261025.json'
    r = json.loads(receipt.read_text())
    assert a['status'] == r['status'] == 'passed'
    assert a['manifest_sha256'] == sha(p / 'manifest.json')
    assert r['audit_byte_identical'] and r['audit_sha256'] == sha(p / 'source_bound_audit.json')
    evidence[name] = dict(audit=a, restoration=r)
proof = ROOT / 'results/recovery_normal_identity_20261027.json'
result = dict(status='native_component_behavior_passed_structure_not_tested', evidence=evidence,
    identity=json.loads(proof.read_text()), selected_variant='recovery_normal_loops_v2',
    complete_system_tested=False, synthesized=False,
    scope='One coordinator NORMAL admission rewrite on the already fixed REARM native slice. No full fault or sequential change. Initial declaration-order compile failure is preserved separately. Current route_block full jobs do not contain this candidate.')
out = ROOT / 'results/recovery_normal_native_20261027.json'
assert not out.exists()
out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
md = '''# NORMAL准入特化的原生恢复生命周期回归通过

选定recovery_normal_loops_v2，仅改coordinator五个原有NORMAL/!cold_rst门控输出staged_valid、permit_work、j_ready、recover_ready、cfg_ready。normal_unexpected使用两个回复VALID，normal_fault使用stopped/abort/timeout/normal_unexpected，避免在NORMAL阶段引入AS/OS的READY资格。完整fault、unexpected、fail_now、attempt_reset和所有时序逻辑不变；失败后重试的safe/drained/retired覆盖条件保持。

独立source-bound分析枚举65536组二态输入，证明普通准入与recover_ready内核等价，以及普通许可蕴含原完整fault为假。这不授权替换任意其他fault消费者，不是X/Z、可达性或时序证明。

原生回归复用已实际恢复审计的rearm_loops_component_v2固定标签服务、wrapper和TB，只替换coordinator。三场景、179检查、31条RESET/WRITE/RESULT事件及3836ns结束时刻与参考一致：实际CRC失败、错误回复保持与退休、旧attempt拒绝、撤销safe或迟到authority回复不清状态、更高attempt非冷重试；共15字段写、3条实际回读、10失败/拒绝结果和3成功结果。J0、无owner/authority请求，标签RAM/config/外部退休是模型，非完整AXI系统。

初版recovery_normal_native_v1因normal_fault在timeout声明前使用而被VRFC 10-3380拒绝，未展开或仿真。v2先声明normal_fault，保留原timeout定义，再连续赋值；原始失败源码与日志保留。失败14文件和成功40文件归档均实际恢复重审audit字节一致；失败audit通过仅表示证据完整。

源码、工具与报告另行冻结。该候选尚未综合、未接入当前route_block完整实验；不能把这三个小场景当完整系统或消环证明。下一结合route_block终态DCP残余路径决定接入并运行完整结构与行为矩阵。固定价格、外部可信快照、持久化floor/认证、自然overflow分配回收、物理时序和板卡缺口保留。
'''
(ROOT / 'results/recovery_normal_native_20261027.md').write_text(md)
frozen = ROOT / 'results/recovery_normal_native_sources_20261027'
frozen.mkdir()
files = {}
def copy(src, rel):
    dest = frozen / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    assert sha(dest) == sha(src)
    files[str(rel)] = dict(source=str(src), sha256=sha(dest))
for name in names:
    p = scratch / name
    m = json.loads((p / 'manifest.json').read_text())
    for n, h in m['sources'].items():
        assert sha(p / 'sources' / n) == h
        copy(p / 'sources' / n, Path('sources') / name / n)
    for n in ['manifest.json', 'source_bound_audit.json', 'runner.py']:
        copy(p / n, Path('reports') / name / n)
    log = 'compile.stdout.log' if name.endswith('v1') else 'simulate.log'
    copy(p / 'simulate' / log, Path('reports') / name / log)
    copy(ROOT / 'results' / f'{name}_restore_20261025.json', Path('reports') / f'{name}_restore.json')
copy(ROOT / 'hardware/variants/recovery_normal_loops_v2/baseline/recovery_coordinator.sv', Path('sources/baseline/recovery_coordinator.sv'))
for n in ['analyze_recovery_normal_identity.py', 'run_recovery_normal_native.py',
          'run_recovery_normal_native_v2.py', 'audit_recovery_normal_native.py',
          'audit_recovery_normal_compile.py', 'freeze_recovery_normal_native.py',
          'run_checkpoint_authority.py']:
    copy(ROOT / 'scripts' / n, Path('scripts') / n)
for n in ['recovery_normal_native_20261027.json', 'recovery_normal_native_20261027.md',
          'recovery_normal_identity_20261027.json']:
    copy(ROOT / 'results' / n, Path('reports') / n)
(frozen / 'manifest.json').write_text(json.dumps(dict(status='frozen', files=files,
    complete_system_tested=False, synthesized=False), indent=2, sort_keys=True) + '\n')
print('RECOVERY_NORMAL_FROZEN', len(files))
