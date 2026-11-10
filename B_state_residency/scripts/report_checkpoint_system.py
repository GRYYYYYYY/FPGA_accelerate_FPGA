"""Freeze full-system cancellation evidence only after restored re-audit."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
name='checkpoint_system_v4';p=Path('/tmp/B_state_residency_offer_20261025')/name
a=json.loads((p/'source_bound_audit.json').read_text());assert a['status']=='passed'
r=json.loads((ROOT/f'results/{name}_restore_20261025.json').read_text());assert r['status']=='passed'and r['audit_byte_identical']
d=ROOT/'hardware/variants/checkpoint_system_v1';closure=ROOT/'results/checkpoint_system_sources_20261026';closure.mkdir()
paths=sorted(d.glob('*.sv'))+sorted(d.glob('*.py'))+[d/'CONTRACT.md']+[ROOT/'scripts'/n for n in ['run_checkpoint_system.py','audit_checkpoint_system.py','report_checkpoint_system.py']]
sources={}
for f in paths:
 n=str(f.relative_to(ROOT));q=closure/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q);sources[n]=sha(q)
for n in ['query_residency_system.sv','search_residency_system.sv','residency_system.sv','build.py','build_tb.py']:assert sha(d/n)==sha(p/'sources'/n)
(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
(ROOT/'results/checkpoint_system_20261026.json').write_text(json.dumps(dict(status='passed',selected=str(p),audit=a,restore=r,sources=sources),indent=2)+'\n')
body='''# 完整层级元数据准备与取消通过（2026-10-26）

详见 results/checkpoint_system_20261026.json 与 hardware/variants/checkpoint_system_v1/CONTRACT.md。选定 checkpoint_system_v4，将双槽 authority、发布屏障、coordinator/config shadow 通过三个实际层级接入 query_residency_system，沿用原生 checkpoint lease 和真实物理/逻辑退休信号。共同发布许可与新准备请求许可分离，避免 commit 自身关闭 publish_ready。

32 槽和单槽压力两例完成真实查询、owner 写故障、修复及重试，再在实际工作产生的六项 journal 上准备 coordinator/config、保持准备回复、提供路径/查询导入争用、取消、保持完成回复。取消始终保留 checkpoint17、旧 generation 和六项 journal；完成消费后继续成功导出保存路径、查询序号、配置和 journal。两例共 24 文件与既有已审计基线逐字节一致：每例八路 AXI 日志和四份最终 DDR。原生准备/回复/取消/丢弃/完成事件独立核对，保存路径、配置、上下文、journal 与恢复 floor 导出一致。归档已实际恢复重审，audit 逐字节一致；源码冻结 results/checkpoint_system_sources_20261026。

本轮没有准备 authority 候选或在完整层级成功发布；三方同拍提交目前仍只由前轮元数据切片证明。manifest_ready 仍为外部输入。完整换代后故障恢复，尤其 target reset 后保存 path/query/label 与序号下限恢复再放行业务，仍未实现/验证。运行中工作 DDR 快照生产、多 net/overflow、综合/时序/板卡收益仍缺。

下一步在完整层级接入实际 warm authority 图像并验证三方共同提交，再执行换代后故障恢复，完成路径/查询/标签恢复联锁。研究继续，goal active。
'''
(ROOT/'results/checkpoint_system_20261026.md').write_text(body)
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 f=ROOT/n;s=f.read_text();assert not s.startswith(body.splitlines()[0]);f.write_text(body+'\n以下保留历史。\n\n'+s)
print('full-system metadata cancellation evidence frozen',len(sources))
