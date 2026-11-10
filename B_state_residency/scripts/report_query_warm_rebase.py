from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
base=Path('/tmp/B_state_residency_offer_20261025');names=['query_warm_rebase_v3','query_rebase_normal_v2'];receipts={n:json.loads((ROOT/f'results/{n}_restore_20261025.json').read_text())for n in names};assert all(r['status']=='passed'and r['audit_byte_identical']for r in receipts.values())
audits={n:json.loads((base/n/'source_bound_audit.json').read_text())for n in names};assert all(a['status']=='passed'for a in audits.values())
d=ROOT/'hardware/variants/query_warm_rebase_v1';closure=ROOT/'results/query_warm_rebase_sources_20261026';closure.mkdir();paths=[d/n for n in ['build.py','query_lifecycle.sv','tb_rebase.sv','CONTRACT.md']]+[ROOT/'scripts'/n for n in ['run_query_warm_rebase.py','audit_query_warm_rebase.py','run_query_rebase_regression.py','audit_query_rebase_regression.py','report_query_warm_rebase.py']];sources={}
for f in paths:
 n=str(f.relative_to(ROOT));q=closure/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q);sources[n]=sha(q)
for n in ['build.py','query_lifecycle.sv','tb_rebase.sv']:assert sha(d/n)==sha(base/names[0]/'sources'/n)
(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n');(ROOT/'results/query_warm_rebase_20261026.json').write_text(json.dumps(dict(status='passed',audits=audits,restores=receipts,sources=sources),indent=2)+'\n')
body='''# 查询恢复上下文转换通过，完整 warm 恢复仍待接入（2026-10-26）

详见 results/query_warm_rebase_20261026.json 与 hardware/variants/query_warm_rebase_v1/CONTRACT.md。选定 query_warm_rebase_v3：原生 query_lifecycle 增加默认关闭的 ENABLE_REBASE；开启后以恢复许可与选定 source 上下文验证原始40B镜像及原 CRC，再把 ledger 原子绑定到新 attempt 上下文，保留序号下限。不改输入字节，不伪造原 CRC，也不把距离标签自动视为新价格下有效。

真实 G2 bundle version4/query2/price4/seq1 → version5/query3/price5/seq1。119次检查、12事务和独立事件/字节CRC状态机审计通过：无许可、错误 CRC/generation/source、部分流、完整包后发布前许可撤销、abort、序号回退均不发布；成功后导出新上下文与新CRC，seq1重放被拒绝。此处恢复许可及source descriptor来自TB，尚未接完整恢复fence。

默认 ENABLE_REBASE=0 的完整32槽与单槽回归 query_rebase_normal_v2 通过：每例8 AXI+4 DDR+完整native协议+directory，共28文件逐字节及最终周期一致，保留前轮共同发布/G2原生GET/q2能力。两归档实际恢复后重审audit一致；源码冻结 results/query_warm_rebase_sources_20261026。

尚未实现或验证完整换代后的 warm 故障恢复。下一优先 recovery fence 下管理员资格、label/path/query真实回执联合完成（label回复可先被消费）、上下文转换接线，再G2原生GET修复/恢复q1保存状态/新上下文q2重试。运行中工作DDR快照、多net/overflow、持久化认证、综合时序和板卡仍缺。研究继续，goal active。
'''
(ROOT/'results/query_warm_rebase_20261026.md').write_text(body)
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 f=ROOT/n;s=f.read_text();assert not s.startswith(body.splitlines()[0]);f.write_text(body+'\n以下保留历史。\n\n'+s)
print('query warm ledger rebase evidence frozen',len(sources))
