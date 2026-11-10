"""Freeze the audited interface tests, keeping full-system/structure status separate."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha

scratch=Path('/tmp/B_state_residency_offer_20261025')
names=['recovery_backend_native_v1','recovery_backend_system_crc_pressure_v1']
evidence={}
for name in names:
    p=scratch/name
    m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
    r=json.loads((ROOT/'results'/f'{name}_restore_20261025.json').read_text())
    assert a['status']==r['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json')
    assert r['audit_byte_identical']and r['audit_sha256']==sha(p/'source_bound_audit.json')
    evidence[name]=dict(audit=a,restoration=r)
v1=ROOT/'hardware/variants/recovery_backend_loops_v1'
v2=ROOT/'hardware/variants/recovery_backend_loops_v2'
for p in (v1/'fixed').glob('*.sv'):assert sha(p)==sha(v2/'fixed'/p.name)
result=dict(status='native_contract_tests_passed_full_system_pending',evidence=evidence,
    source_proof=json.loads((ROOT/'results/recovery_backend_exclusion_20261027.json').read_text()),
    selected_variant='recovery_backend_loops_v2',production_v1_v2_byte_identical=True,
    full_system_root=str(scratch/'recovery_backend_system_crc_pressure_v2'),
    scope='Nine native coordinator cases with modeled callbacks and one journal key; three exact default-mode comparisons, legal exclusive-mode equality and two intentional contract violations rejected. Full-system CRC test remains a separate running experiment; no new synthesis conclusion.')
out=ROOT/'results/recovery_backend_native_20261027.json';assert not out.exists()
out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
(ROOT/'results/recovery_backend_native_20261027.md').write_text('''# 原生后端互斥条件与通用接口兼容性

当前query系统的原生authority reader/rotator/AP mux和transaction fence owner lane9保证请求READY与回复VALID互斥。逐条绑定实际源码与接线，枚举reader32、rotator144、fence512、coordinator144组二态赋值。此结论不是一般AXI性质、X/Z证明或完整形式验证。

coordinator新增默认关闭的EXCLUSIVE_BACKEND_RESPONSES，residency/search两个有外部authority输入的层级保持默认关闭，仅原生query顶层开启。开启时unexpected判断去掉AS/OS的READY资格；默认保留旧式请求周期出现回复。所有时序逻辑、超时、错误锁存、退休和状态转移保持原文。四源基于route_block已审计CRC参考；独立NORMAL准入候选未叠加。

九个实际XSim原生coordinator测试通过。baseline/default各覆盖正常后周期回复、authority请求周期回复、owner请求周期回复；三组逐事件/周期/结束时刻相同。exclusive合法模式同baseline。实际一键journal、两轮authority、两次GET与两次永久CAPACITY拒绝，status3/J1且保持失败回复8周期、消费后业务仍关闭。故意违反互斥条件的authority/owner两例在exclusive模式status6/J1拒绝；这两例不是合法原生后端能产生的行为。backend数据来自模型，非完整owner AXI证明。

首次完整回归因新增观察计数器在使用后声明而VRFC10-3380编译失败，未展开或仿真。V2仅把TB声明移到模块起始位置，四生产源逐字节不变。失败与九项组件测试均已归档实际恢复重审，audit逐字节一致。

完整CRC压力V2正在单独验证：增加只读互斥与非零请求/回复覆盖监视，不改输入/握手/原输出；须27文件与结束时间精确一致后方可接受。当前报告不表示完整系统、全部矩阵、完整消环或时序通过。固定价格、可信快照、持久化floor/认证、自然overflow、物理实现和板卡缺口保留。
''')
frozen=ROOT/'results/recovery_backend_native_sources_20261027';frozen.mkdir();files={}
def copy(src,rel):
    dest=frozen/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
    assert sha(dest)==sha(src);files[str(rel)]=dict(source=str(src),sha256=sha(dest))
for name in names:
    p=scratch/name
    for n in ['manifest.json','source_bound_audit.json']:
        copy(p/n,Path('reports')/name/n)
    copy(ROOT/'results'/f'{name}_restore_20261025.json',Path('reports')/f'{name}_restore.json')
for f in (scratch/names[0]/'sources').iterdir():copy(f,Path('native_sources')/f.name)
for name in json.loads((scratch/names[0]/'manifest.json').read_text())['cases']:
    copy(scratch/names[0]/name/'simulate.log',Path('native_logs')/(name+'.log'))
copy(scratch/names[1]/'pressure/compile.stdout.log',Path('reports/initial_compile_failure.log'))
for v in [v1,v2]:
    for f in sorted(v.rglob('*')):
        if f.is_file()and '__pycache__'not in f.parts:copy(f,Path('variants')/v.name/f.relative_to(v))
for n in ['analyze_recovery_backend_exclusion.py','run_recovery_backend_native.py',
    'audit_recovery_backend_native.py','run_recovery_backend_system.py','audit_recovery_backend_compile.py',
    'freeze_recovery_backend_native.py','run_checkpoint_authority.py']:
    copy(ROOT/'scripts'/n,Path('scripts')/n)
for n in ['recovery_backend_native_20261027.json','recovery_backend_native_20261027.md','recovery_backend_exclusion_20261027.json']:
    copy(ROOT/'results'/n,Path('reports')/n)
(frozen/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,complete_system_tested=False,synthesized=False),indent=2,sort_keys=True)+'\n')
print('RECOVERY_BACKEND_NATIVE_FROZEN',len(files))
