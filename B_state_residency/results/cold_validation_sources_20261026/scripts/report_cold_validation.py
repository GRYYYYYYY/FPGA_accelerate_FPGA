"""Freeze ordinary-start equivalence and boot-root OOC resource evidence."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
base=Path('/tmp/B_state_residency_offer_20261025');names=['cold_normal_v1','cold_axi_synth_v1'];receipts={n:json.loads((ROOT/f'results/{n}_restore_20261025.json').read_text())for n in names};assert all(v['status']=='passed'and v['audit_byte_identical']for v in receipts.values())
normal=json.loads((base/names[0]/'source_bound_audit.json').read_text());synth=json.loads((base/names[1]/'source_bound_audit.json').read_text());prior=json.loads((base/'bundle_capture_synth_v1/source_bound_audit.json').read_text());assert normal['status']==synth['status']=='passed'
for n in ['query_residency_system.sv','boot_restore_gate.sv']:assert sha(base/names[0]/'sources'/n)==sha(base/names[1]/'sources'/n)
closure=ROOT/'results/cold_validation_sources_20261026';closure.mkdir();paths=[ROOT/'scripts'/n for n in ['run_cold_normal.py','audit_cold_normal.py','prepare_cold_axi_synth.py','audit_cold_axi_synth.py','audit_authority_query_synth.py','report_cold_validation.py']]+[ROOT/'hardware/variants/cold_axi_abort_v1'/n for n in ['build.py','query_residency_system.sv','boot_restore_gate.sv','CONTRACT.md']];sources={}
for p in paths:
 n=str(p.relative_to(ROOT));q=closure/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);sources[n]=sha(q)
u=synth['utilization'];delta={k:u[k]-prior['utilization'][k]for k in ['LUT','FF','BRAM','DSP']}
assert delta['BRAM']==delta['DSP']==0
report={'status':'passed','normal':normal,'synth':synth,'resource_delta_vs_bundle_capture':delta,'archives':receipts,'sources':sources,'remaining':['Runtime authority rotation and general multi-net/overflow snapshots.','Constrained timing/place/route, no-reset recovery, durable floors/authentication, unknown pages/price/epoch/capacity and board proof.']}
(ROOT/'results/cold_validation_20261026.json').write_text(json.dumps(report,indent=2)+'\n');(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
body=f'''# 普通启动回归与冷恢复顶层综合（2026-10-26）

明确boot_required=0、其余boot输入为0，沿用旧bundle_capture_v3完整TB/CPU/AXI/data/faultcase5，仅换最新cold_axi_abort_v1生产root并加入gate定义。32槽/单槽均完成owner B故障、真实恢复、完整重跑和lease捕获。每例8AXI日志、4完整DDR图像、native全协议与目录记录共14文件逐字节一致，合计28；周期836290/893444及repair1也与旧基线相同。本结论限于该代表fixture，不是任意输入形式等价。

完整U280 OOC：LUT {u['LUT']:g}、FF {u['FF']:g}、BRAM {u['BRAM']:g}、DSP {u['DSP']:g}。相对无boot门控的bundle_capture综合增量LUT {delta['LUT']:+g}、FF {delta['FF']:+g}、BRAM {delta['BRAM']:+g}、DSP {delta['DSP']:+g}。全部runtime descriptor/context输入保留，测试注入默认关，latch/blackbox/file-agent/directory-observer均0。487逻辑端口/62227接口位；端口与源码事实详见JSON。新增19420条gate sp切片无负载告警已逐项分类，对应6条未观察lane、control请求payload与label IO未观察字段；非黑盒/锁存器告警。

综合经真实Vivado2022.2 MCP Tcl完成并关闭专用会话，122生产RTL。未约束时序、未布局布线，不报告Fmax或板卡收益。两归档实际移开原目录后恢复复审，audit字节一致；当前源冻结results/cold_validation_sources_20261026。

下一优先运行中authority换代和统一发布协议，随后通用多net/overflow快照。带约束时序/实现、无复位恢复、持久化下限/认证、未知页/价格/回绕/容量/断电及板卡仍缺。goal active。
'''
(ROOT/'results/cold_validation_20261026.md').write_text(body)
header=f'''# 普通启动回归与新顶层OOC通过（2026-10-26，优先历史）

详见 results/cold_validation_20261026.md/.json。cold_axi_abort_v1明确boot_required=0，与原bundle_capture_v3同TB/输入/CPU/故障：32槽/单槽各14文件（8AXI、4DDR、完整native协议和目录）逐字节一致，28文件；周期836290/893444、repair1一致。

完整U280 OOC {u['LUT']:g}LUT/{u['FF']:g}FF/{u['BRAM']:g}BRAM/{u['DSP']:g}DSP；相对bundle_capture增LUT {delta['LUT']:+g}、FF {delta['FF']:+g}，BRAM/DSP不变。122生产RTL，runtime配置输入保留，零latch/blackbox/file-agent/observer。专用Vivado2022.2 MCP会话关闭；两归档实际恢复复审audit一致，源冻结results/cold_validation_sources_20261026。

本轮仅代表fixture普通启动回归和未约束OOC，不证明形式等价/时序闭合/板卡收益。下一优先运行中authority换代与统一发布，再通用多net/overflow快照。带约束时序/实现、无复位恢复、持久化下限/认证、未知页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

'''
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 p=ROOT/n;s=p.read_text();assert not s.startswith(header.splitlines()[0]);p.write_text(header+s)
print('normal-start and OOC evidence frozen',u,delta)
