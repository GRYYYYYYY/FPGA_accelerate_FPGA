"""Publish the bounded research result only after both evidence audits complete."""
from pathlib import Path
import json
from run_query_fault import ROOT, sha

def main():
    roots=[ROOT/'results/query_fault_v1',ROOT/'results/query_fault_fixed_v2']
    audits=[json.loads((p/'source_bound_audit.json').read_text()) for p in roots]
    for p,a in zip(roots,audits):
        assert a['status']=='passed' and a['manifest_sha256']==sha(p/'manifest.json')
    assert audits[0]['outcomes']=={'recovered_retry':5,'stalled':6}
    assert audits[1]['outcomes']=={'recovered_retry':2}
    report={'status':'completed_bounded_experiment','baseline_outcomes':audits[0]['outcomes'],
            'isolated_route_fix_outcomes':audits[1]['outcomes'],
            'evidence':[{'root':str(p),'manifest_sha256':sha(p/'manifest.json'),'audit_sha256':sha(p/'source_bound_audit.json')} for p in roots],
            'unresolved':['Graph read fault: internal expansion result does not retire.','Cost read fault: failed prefetch reply cannot retire through successful-candidate completion gate.'],
            'limits':audits[0]['limits']}
    restore_paths=[ROOT/'results'/f'{p.name}_restore_20261025.json' for p in roots]
    if all(p.exists() for p in restore_paths):
        restores=[json.loads(p.read_text()) for p in restore_paths]
        assert all(r['status']=='passed' and r['audit_byte_identical'] for r in restores)
        report['archive_restore']={'files':sum(r['files'] for r in restores),'receipts':[str(p) for p in restore_paths],'audit_byte_identical':True}
    (ROOT/'results/query_fault_20261025.json').write_text(json.dumps(report,indent=2)+'\n')
    names={1:'源标签 R 错误',2:'准备阶段标签 B 错误',3:'图数据 R 错误',4:'代价 R 错误',5:'占用提交 B 错误',6:'清理刷回 B 错误'}
    rows=[]
    for n in range(1,7):
        cells=[]
        for mode in ['full','pressure']:
            case=audits[0]['cases'].get(f'{mode}_{n}')
            cells.append('未触发此场景' if case is None else '恢复并重跑' if case['outcome']=='recovered_retry' else '卡住，未恢复')
        rows.append('| '+names[n]+' | '+' | '.join(cells)+' |')
    text='''# 真实查询故障与恢复交接（2026-10-25）

完成原版 11 个真实服务故障用例，以及隔离修复版 2 个占用提交故障用例。原版 5 例恢复后完整重跑、6 例卡住；修复版的 32 槽和单槽用例均恢复重跑。**审计通过是证据及结论通过，不能称为 13 个故障全部恢复成功。**

| 故障注入 | 原版 32 槽 | 原版单槽 |
| --- | --- | --- |
'''+ '\n'.join(rows)+'''

准备写回错误只在单槽场景注入：实际 dirty eviction 在 SOURCE_LB 阶段触发 B 回复；不能将没有相应物理写回的 32 槽场景算作覆盖。所有错误直接由原 AXI file agent 返回 SLVERR，日志记录实际 R/B 状态。每例恰好一个错误响应，其余服务没有错误响应。

## 修复的交接问题

原版占用提交错误已完成请求退休：AXI drained=1、backend idle=1、normal retired=1、fence=BLOCKED，但查询停在 DRAIN。路由适配器把锁存故障包括在 busy 中，外层等待 !rc_busy，使自身无法返回；恢复命令又被 qc_busy 挡住。

`hardware/variants/query_recovery_v2/` 只修改顶层一个排空条件：保留所有退休、后端排空、AXI 排空、搜索退休检查，允许 rc_fault 且围栏 BLOCKED 的已退休路由故障交接。全部接口和内部生产 RTL 保持。无路由故障时该表达式与原版恒等；旧源与反例完整保留。入口 `run_query_fault.py RESULT --route-fix` 显式选择新变体，旧正常实验入口没有被静默替换。

两种容量的修复用例均显示：错误提交报告成功 ACK=0，但物理内存已修改 1 项。journal/authority 查出并修复这一项，随后恢复初始 328 标签、切换 query epoch=2 / price=4 / version=4，再完整重跑 q1。最终六个内部路径节点 refs=1、distinct-net occupancy=1，全 owner 图像与 CPU 参考逐字节一致，无重复占用。

原版清理刷回故障在路径已经提交后发生，返回 committed=1 / ACK=6。恢复实际修复 6 项后重跑，同样得到精确一次的最终占用。committed 标记或 ACK=0 均不能独立判断是否有物理副作用。

## 尚未解决的两个内部退休问题

图读取与代价读取错误在 32 槽和单槽均复现：错误后继续观察 32768 周期，AXI 已排空，但 qc=QW、search=WAIT_REPLY、fence=LRSP，backend idle=0 / normal retired=0。没有强制 reset，没有伪造查询完成或恢复成功。

结合冻结源码，图读取错误的完成进入 capture/frame 错误路径，frame fault 屏蔽 frame_done，递归控制器仍等待 e_done；还需处理相关内部服务回复的退休。代价错误则保留预取回复，但候选输出要求后续 post/cost/commit/OFFER 全部完成，后续服务又已被 fault 停止。这两类需要明确的失败事务退休协议，不能仅放宽 AXI 空闲条件。

## 验证范围与限制

独立审计绑定全部生产源码和测试激励；原版生产 RTL 与上一正常实验逐 SHA 相同，修复版独立核对只改变约定排空谓词。逐字节重放七类 AXI，核验实际错误响应、完整 design/label/owner 物理文件和 cost 不变；table 仍闲置。恢复例核对初始 328 标签恢复读回、完整重跑的 73 POLL / 72 expand / 271 候选 / 171 cost、CPU 路径、最终标签目标位清零及全 owner 图像。全部 16 个 host 入口和手动 route 在持有查询完成及恢复时竞争，原断言持续检查围栏。

恢复 fixture 仍只提供 q1 六个内部节点的 owner authority 和 CPU 已知 328 条初始标签。design backing memory 保留；本次重跑通过不能推广成任意 created/cache/frontier/path 的完整 checkpoint。没有多目标、未知页、价格真实变动、持久化掉电或板卡测量。新隔离谓词尚未重新综合，不能沿用旧资源数字声称测得新版本面积或频率。

复现：`python3 scripts/run_query_fault.py RESULT`；修复版加 `--route-fix`；审计 `python3 scripts/audit_query_fault.py RESULT`。结果目录为 `results/query_fault_v1`、`results/query_fault_fixed_v2`；新源闭包为 `results/query_fault_sources_20261025`。归档收据单独记录，不以生成归档替代真实恢复检查。

下一步优先修复图/cost 失败事务的内部回复退休，并用保留反例验证；随后补完整 checkpoint、未知工作集和同等负载性能测量。研究任务仍未完成。
'''
    if 'archive_restore' in report:
        text+='\n两份归档均实际移开原件、解压恢复并重新审计；共 '+str(report['archive_restore']['files'])+' 个文件，审计结果逐字节一致。收据：`query_fault_v1_restore_20261025.json`、`query_fault_fixed_v2_restore_20261025.json`。\n'
    (ROOT/'results/query_fault_20261025.md').write_text(text)
    notice='''# 真实查询故障矩阵与路由退休修复（2026-10-25，优先历史）

详见 results/query_fault_20261025.md/.json。原版真实 AXI 故障11例：5例恢复并完整重跑，6例卡住（graph/cost/owner各两种容量）；独立七AXI字节/全owner/CPU重跑审计通过仅表示结论可信，不能说所有故障恢复通过。源标签R、单槽prepare B、cleanup B可恢复；cleanup已提交6项，先修复6项再重跑。

隔离 query_recovery_v2 仅改外层排空谓词，解决route adapter busy包含锁存fault导致的DRAIN死等；仍要求normal_retired、backend_idle、AXI全排空、search退休，额外接受rc_fault且fence BLOCKED。32槽/单槽owner B错误各1例均修复实际副作用1项（ACK=0）后恢复初始328标签并完整重跑，最终全owner与CPU精确一次提交一致。显式入口run_query_fault.py RESULT --route-fix；旧正常入口与原基线不改，新谓词尚未重综合。

下一优先graph错误的capture/frame/递归完成退休、cost错误的候选链失败退休：两者AXI虽空但内部仍owned，不能跳过退休强制reset。原版反例已保留。完整checkpoint仍缺，q1六owner authority/328已知标签受信任、design backing保留；无未知页/任意reroute/真实价格变化/耐掉电/板卡加速结论。以下保留历史。

'''
    for n in ['AGENTS.md','NEXT_STEPS.md','README.md','EXPERIMENTS.md','INTERFACES.md']:
        p=ROOT/n;old=p.read_text()
        if not old.startswith(notice.splitlines()[0]):p.write_text(notice+old)
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
