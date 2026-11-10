"""Freeze reviewed cold boot evidence and update handoff context once."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
out=Path('/tmp/B_state_residency_offer_20261025/cold_boot_v2');unit=Path('/tmp/B_state_residency_offer_20261025/boot_gate_v2');a=json.loads((out/'source_bound_audit.json').read_text());assert a['status']=='passed'
receipts={n:json.loads((ROOT/f'results/{n}_restore_20261025.json').read_text())for n in ['cold_boot_v2','boot_gate_v2']};assert all(x['status']=='passed'and x['audit_byte_identical']for x in receipts.values())
closure=ROOT/'results/cold_boot_sources_20261026';closure.mkdir();sources={}
paths=[*sorted((ROOT/'hardware/variants/cold_boot_v1').glob('*.sv')),*sorted((ROOT/'hardware/variants/cold_boot_v1').glob('*.py')),ROOT/'hardware/variants/cold_boot_v1/CONTRACT.md',*[ROOT/'scripts'/n for n in ['run_cold_boot.py','audit_cold_boot.py','run_boot_gate.py','audit_boot_gate.py','report_cold_boot.py','verify_rtl_bundle.py','audit_route_fault_axi.py']]]
for p in paths:
 n=str(p.relative_to(ROOT));dest=closure/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);sources[n]=sha(dest)
for n in ['query_residency_system.sv','boot_restore_gate.sv','tb_cold_boot.sv']:
 assert sha(out/'sources'/n)==sha(ROOT/'hardware/variants/cold_boot_v1'/n)
assert sha(unit/'sources/boot_restore_gate.sv')==sha(out/'sources/boot_restore_gate.sv')
report={'status':'passed','experiment':str(out),'component_experiment':str(unit),'audit_sha256':sha(out/'source_bound_audit.json'),'component_checks':31,'cases':a['cases'],'archives':receipts,'sources':sources,'scope':a['limits'],'remaining':['Actual interrupted/failed bootstrap integration and recovery; component reset/collision tests do not prove all full-system interruption cases.','Normal-mode full-system regression and synthesis/timing of the new boot-gated root.','Running authority rotation and general multi-net/overflow checkpoint.','Durable floors/authentication, unknown pages/price/epoch/capacity and board tests.']}
(ROOT/'results/cold_boot_20261026.json').write_text(json.dumps(report,indent=2)+'\n');(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
body='''# 冷恢复后继续真实查询通过（2026-10-26）

新RTL实例从已提交G2/checkpoint18 bundle恢复，boot_required从cold reset封锁业务。真实六端点/协调器/保存配置共8配置回执、owner/authority完整绑定、标签读回CRC/count、路径/query实际导入回复共同放行；完成回复消费前保持业务与lease释放关闭。修复配置/标签更新与成功回复同周期时旧资格重新生效的反例，失效优先并取消在途资格。组件31项检查通过。

两种容量从空标签DDR/新目录以native IO重建328记录，使用bundle的effective4/query2/price4；query40B/path312B原生导入。旧seq1在空闲slot1/合法上下文被拒绝，prepare/commit为0；seq2与独立CPU oracle一致：43poll、42expand、176candidate、122cost。共享节点263946/554512 refs1→2，两次ripup2→1→0；每例42实际owner probes，完整owner最终图像一致。

32槽/单槽周期344879/344954，含主机驱动重建、核验、查询、探针与撤销，不能作加速比较。全部8AXI无错误且逐字节重放/最终可写图像一致。两归档527文件实际恢复并重新审核，audit字节一致；当前源冻结至results/cold_boot_sources_20261026。

详见 [报告](cold_boot_20261026.json)、硬件约定hardware/variants/cold_boot_v1/CONTRACT.md。该fixture仍是capacity0/同网两路径，DDR预载/发布为主机参考流程；不是自主DMA/板卡恢复。新门控尚无综合/时序结果；完整系统中断恢复、普通启动回归、运行中authority换代、任意多net/overflow快照、持久化anti-replay/认证、未知页/价格/回绕/容量/板卡仍待验证，goal active。
'''
(ROOT/'results/cold_boot_20261026.md').write_text(body)
header='''# 冷恢复后继续真实查询通过（2026-10-26，优先历史）

详见 results/cold_boot_20261026.md/.json 与 hardware/variants/cold_boot_v1/CONTRACT.md。选定cold_boot_v2：新RTL实例冷复位后从已提交G2/checkpoint18 bundle恢复，真实8配置回执、owner/authority绑定、328标签native重建/CRC/count、path/query导入回执及完成回复消费共同开放业务。修复更新/完成同周期旧资格复活；组件31项检查通过。

32槽/单槽均拒绝合法上下文空闲slot的旧seq1（零prepare/commit），seq2对照独立CPU为43poll/42expand/176candidate/122cost。共享263946/554512 refs1→2，双ripup2→1→0；每例42owner probes，全部8AXI字节重放/最终owner图像通过。周期344879/344954包含恢复/查询/核验/撤销，非加速。两归档527文件实际恢复复审audit一致；当前源冻结results/cold_boot_sources_20261026。

这是capacity0/同网两路径的主机预载参考冷恢复，不是FPGA自主DMA/板卡证明。下一优先：完整系统恢复中断/错误与普通启动回归，补新门控综合；再运行中authority换代与通用多net/overflow快照。持久化下限/认证、未知页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

'''
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 p=ROOT/n;s=p.read_text();assert not s.startswith(header.splitlines()[0]);p.write_text(header+s)
print('cold boot report and handoff updated',len(sources),'frozen sources')
