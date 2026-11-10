from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
base=Path('/tmp/B_state_residency_offer_20261025');names=['warm_shared_first_v1','warm_shared_last_v1'];receipts={n:json.loads((ROOT/f'results/{n}_restore_20261025.json').read_text())for n in names};assert all(r['status']=='passed'and r['audit_byte_identical']for r in receipts.values());audits={n:json.loads((base/n/'source_bound_audit.json').read_text())for n in names};assert all(a['status']=='passed'for a in audits.values())
d=ROOT/'hardware/variants/warm_shared_v1';closure=ROOT/'results/warm_shared_sources_20261026';closure.mkdir();paths=[d/n for n in ['build_tb.py','tb_shared.sv','CONTRACT.md']]+[ROOT/'scripts'/n for n in ['run_warm_shared.py','audit_warm_shared.py','report_warm_shared.py']];sources={}
for f in paths:
 n=str(f.relative_to(ROOT));q=closure/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q);sources[n]=sha(q)
for name in names:assert sha(d/'tb_shared.sv')==sha(base/name/'sources/tb_query_fault.sv')and sha(d/'build_tb.py')==sha(base/name/'sources/shared_build_tb.py')
phases={}
for name in names:
 phases[name]={}
 for mode in ['full_5','pressure_5']:
  p=base/name/mode/'natural_trace.txt';r=[x.split()for x in p.read_text().splitlines()];cyc=lambda tag:int(next(x for x in r if x[0]==tag)[1]);phases[name][mode]=dict(trace_sha256=sha(p),owner_cycles=cyc('WARM_OWNER_REPAIRED')-cyc('WA'),label_cycles=cyc('WL')-cyc('WARM_OWNER_REPAIRED'),fault_to_retry_cycles=cyc('WARM_RETRY')-int([x for x in r if x[0]=='FI'][-1][1]))
(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n');(ROOT/'results/warm_shared_20261026.json').write_text(json.dumps(dict(status='passed',audits=audits,restores=receipts,simulation_phase_cycles=phases,sources=sources),indent=2)+'\n')
body='''# 两共享资源故障与5/6项journal修复通过（2026-10-26）

详见 results/warm_shared_20261026.json 与 hardware/variants/warm_shared_v1/CONTRACT.md。选定 warm_shared_first_v1/last_v1，仅改变TB错误注入时机及观察；所有生产RTL与warm_system_v2逐文件SHA一致，无新增生产修复。

真实q2共享节点554512/263946分别是第5/6次owner写。32槽和单槽共四例通过：前4/5个物理B成功，第5/6个SLVERR，产生5/6项实际journal。G2原生两轮GET返回四个新资源ref0和一/两个共享资源ref1；旧G1对应共享行全零。工作owner实际GET/DEC/GET验证，共享ref2降至1而occupancy保持1，保留q1关系，不能混同旧G1的ref0。第5写场景中未纳入journal的另一共享行也保留。

同实例不中途冷复位/重装工作DDR，完成328标签、q1路径与源查询镜像恢复及新attempt5/3/5下q2重试。CPU数值oracle43poll/42expand/176candidate/122cost、最终标签、两条原生路径拆线、共享2→1→0通过。独立字节/事件审计全部8AXI及最终DDR，核对5/6键、G2两轮地址/返回、15/18工作owner操作和全部回执；其他net状态保留。两归档实际恢复重审audit一致，新增源冻结results/warm_shared_sources_20261026。JSON阶段周期仅行为仿真，不是板卡速度或加速比。

价格/history内容不变，仅attempt标签变化。仍是一个net/两路径、capacity0的两个确定共享写错误点；无任意价格变化距离有效性、通用多net/overflow、运行中工作DDR快照、持久化认证/下限、综合时序或板卡结论。下一优先真实恢复流/AXI在途取消、已受理回复退休及恢复过程失败后非冷复位重试，再回绕/未知页等。研究继续，goal active。
'''
(ROOT/'results/warm_shared_20261026.md').write_text(body)
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 f=ROOT/n;s=f.read_text();assert not s.startswith(body.splitlines()[0]);f.write_text(body+'\n以下保留历史。\n\n'+s)
print('shared warm recovery evidence frozen',len(sources))
