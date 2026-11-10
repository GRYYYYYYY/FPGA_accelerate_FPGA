from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha
base=Path('/tmp/B_state_residency_offer_20261025');names=['authority_rotate_v5_unfixed','authority_rotate_v6'];receipts={n:json.loads((ROOT/f'results/{n}_restore_20261025.json').read_text())for n in names};assert all(v['status']=='passed'and v['audit_byte_identical']for v in receipts.values())
a=json.loads((base/names[1]/'source_bound_audit.json').read_text());assert a['status']=='passed'
closure=ROOT/'results/authority_rotate_sources_20261026';closure.mkdir();d=ROOT/'hardware/variants/authority_rotate_v1';paths=sorted(d.glob('*.sv'))+sorted(d.glob('*.py'))+[d/'CONTRACT.md']+[ROOT/'scripts'/n for n in ['run_authority_rotate.py','audit_authority_rotate.py','audit_authority_rotate_negative.py','report_authority_rotate.py','verify_rtl_bundle.py','audit_route_fault_axi.py']];sources={}
for p in paths:
 n=str(p.relative_to(ROOT));q=closure/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);sources[n]=sha(q)
for n in ['checkpoint_authority_rotator.sv','tb_rotate.sv']:assert sha(base/names[1]/'sources'/n)==sha(d/n)
r={'status':'passed','selected':str(base/names[1]),'audit':a,'negative':json.loads((base/names[0]/'source_bound_audit.json').read_text()),'archives':receipts,'sources':sources,'remaining':['Joint staged publication of coordinator journal/checkpoint and saved effective config with authority under real lease.','Preserve/restore path/query/label state and floors after target reset before allowing work; full-system post-rotation recovery.','Runtime working-state snapshot writer/general multi-net-overflow bundles, synthesis/timing and durable/board evaluation.']}
(ROOT/'results/authority_rotate_20261026.json').write_text(json.dumps(r,indent=2)+'\n');(closure/'manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
body='''# 双槽authority组件与身份回退修复（2026-10-26）

选定authority_rotate_v6。新增checkpoint_authority_rotator，两个原生reader/GET codec共用串行只读AXI；配置处理阻止GET，准备完成未发布时服务旧槽。publish要求两槽物理和逻辑退休、无请求争用、外部许可，握手原子切换活动槽。配置/GET背压阻止发布，discard/abort不改活动身份。

真实反例v5_unfixed：SLVERR后rearm被取消，configured变0；旧包装器错误允许重新初绑，将已发布G2回退G1，未发生publish。唯一修复以保留的非零bound_generation判定身份已建立，不能再用configured。随后正常rearm仍回到原G2。

224次检查、28原生GET、7配置+2rearm、45个64B读beat、两次发布G1→G2→G4通过。原生布局失败2、配置取消3、真实R SLVERR错误9均有原生握手记录。独立namespace状态机核对C/K/L/F/P/X/A/Q/R，全部AXI地址/数据/status与两份真实完整owner图像重放一致，无写请求。旧失败与修复两归档实际恢复复审audit一致，当前源冻结results/authority_rotate_sources_20261026。

初始owner表已有其他net占用；warm相对初始仅六个目标资源变为ref1/occ1，其他字节完全保留。已有node0/net4754和六个目标资源已实际GET验证，按不同net计占用。开发审计中的“初始全零”假设已纠正。

这只是双槽读取基线选择组件，publish_permit尚由TB驱动，未接全系统lease/manifest授权与coordinator journal/config/path/query/label联合发布或恢复。G4复用同一warm owner图像，不是新捕获完整G4快照。未综合/时序/板卡或持久化anti-replay证明。

下一优先coordinator及有效配置的影子prepare/publish，再接真实lease形成同拍联合提交；之后验证换代后的warm恢复，尤其target reset后保存路径/序号等必须恢复完成再放行。运行中工作DDR快照生产、通用多net/overflow、价格/回绕/未知页/持久化/板卡仍缺。goal active。
'''
(ROOT/'results/authority_rotate_20261026.md').write_text(body)
header='''# 双槽authority组件通过并修复身份回退（2026-10-26，优先历史）

详见 results/authority_rotate_20261026.md/.json 与 hardware/variants/authority_rotate_v1/CONTRACT.md。选定authority_rotate_v6：双原生reader槽、共用串行只读AXI；配置处理阻止GET，准备完成后未publish前仍服务旧槽。发布需两槽退休/无争用/外部许可，单拍切换；held回复、discard和abort行为验证。

真实v5反例：rearm取消使configured=0后，旧包装器允许重初绑，从G2退回G1且无publish。修复首次绑定资格改查保留的bound_generation，服务就绪与身份存续分开。224检查、28GET、7配置+2rearm、45R beat，G1→G2→G4两次publish、原生布局失败/取消/SLVERR、恢复原身份通过。全图像/AXI/独立状态机审核，两归档实际恢复复审一致，源冻结results/authority_rotate_sources_20261026。

初始图像并非空表，其他net已有占用；warm仅新增六个目标资源，所有其他字节不变，已有node0/net4754与六个新资源实际GET验证。G4复用warm图像，仅组件namespace测试。未接全系统，publish_permit为TB输入；无联合journal/config/path/query/label提交/恢复、工作DDR快照生产或新综合/时序/板卡结论。

下一优先coordinator/有效配置影子prepare/publish与真实lease联合提交，再warm换代恢复（target reset后必须恢复路径/序号等才放行）。通用多net/overflow、持久化下限/认证、未知页/价格/回绕/容量/断电/板卡仍缺。goal active。以下保留历史。

'''
for n in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
 p=ROOT/n;s=p.read_text();assert not s.startswith(header.splitlines()[0]);p.write_text(header+s)
print('authority rotation component evidence frozen',len(sources))
