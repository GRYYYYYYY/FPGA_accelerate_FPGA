from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
name='warm_receipt_join_v4';p=Path('/tmp/B_state_residency_offer_20261025')/name
r=json.loads((ROOT/f'results/{name}_restore_20261025.json').read_text());assert r['status']=='passed'and r['audit_byte_identical'];a=json.loads((p/'source_bound_audit.json').read_text());assert a['status']=='passed'
d=ROOT/'hardware/variants/warm_receipt_join_v1';closure=ROOT/'results/warm_receipt_join_sources_20261026';closure.mkdir();paths=[d/n for n in ['warm_restore_receipt_join.sv','tb_join.sv','CONTRACT.md']]+[ROOT/'scripts'/n for n in ['run_warm_receipt_join.py','audit_warm_receipt_join.py','report_warm_receipt_join.py']];sources={}
for f in paths:
 n=str(f.relative_to(ROOT));q=closure/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q);sources[n]=sha(q)
for n in ['warm_restore_receipt_join.sv','tb_join.sv']:assert sha(d/n)==sha(p/'sources'/n)
(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n');(ROOT/'results/warm_receipt_join_20261026.json').write_text(json.dumps(dict(status='passed',audit=a,restore=r,sources=sources),indent=2)+'\n')
body='''# 原生标签/路径/查询回执联合逻辑通过（2026-10-26）

详见 results/warm_receipt_join_20261026.json 与 hardware/variants/warm_receipt_join_v1/CONTRACT.md。选定 warm_receipt_join_v4：锁存 G2/CP18 快照身份、目标上下文、cookie、标签数量与原始 path/query CRC；只有实际原生受理/消费形成回执。标签回复即使先消费也保留成功记录；路径/查询各只准入一次；已受理导入的 admin_safe 不随自身 busy 关闭。全部回执齐全并退休后才 joined，最终恢复回复消费前保持 owned；abort 同拍不放行。

389次检查、9场景，8轮原生 label_restore 的2624行回读验证/13120字段真实RAM写入；原生路径78字及 ENABLE_REBASE=1 查询40B实际恢复（新上下文5/3/5、seq1）。回复保持、标签持续start offer、部分路径/查询、物理退休暂停、错误cookie/CP/上下文、CRC错误、原生成功但不符选定bundle CRC的镜像均验证。独立逐周期模型核对72个状态观察，标签写入/读回请求和源数据/CRC重放通过。归档实际恢复复审一致，源冻结 results/warm_receipt_join_sources_20261026。

范围仍是原生三控制器切片：标签后端为可变RAM模型；recovery_owned/owner_repaired/活动上下文来自TB，没有完整fence/coordinator、工作owner AXI修复或q2搜索重试。HALT当前只支持退休后的冷复位，不是无复位恢复证明；无距离标签跨价格有效性、持久化授权、综合时序或板卡结论。

接入约束已明确：现有 lr_rsp_ready=!k_labels_valid 必须在warm模式替换，避免与联合完成相互等待；用 label_allow 屏蔽持续 labels_valid 重启。joined 的 retired 不能包含正等待该回调的coordinator busy/recovery-owned。下一优先实际backend recover握手arm、recovery fence管理员和三层接线，再完整G2换代后q2故障/原生GET修复/保存q1状态/新上下文CPU重试。研究继续，goal active。
'''
(ROOT/'results/warm_receipt_join_20261026.md').write_text(body)
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 f=ROOT/n;s=f.read_text();assert not s.startswith(body.splitlines()[0]);f.write_text(body+'\n以下保留历史。\n\n'+s)
print('native warm receipt join evidence frozen',len(sources))
