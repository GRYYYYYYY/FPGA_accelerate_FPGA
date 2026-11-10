# 2026-10-25 更新

已修复故障时metadata/access逻辑回复尚在途就提前暴露最终结果的问题，并增加无归属回复检查。控制单测268项/27错误处理通过；相同修复RTL的32槽、单槽、默认163840帧/18位目录三组真实输入回归均通过，每组1212扩展/3022判定/60EARLY，完整后备状态一致。

实际AXI边界另通过metadata图AR阻塞时abort保持VALID/字段并排空，以及图R错误传播/停止。owner文件均不变。逻辑回复排空不等于物理总线已经全部排空；未覆盖写错误或复位重载恢复。

最终修订绑定：`candidate_revision_20261025.json`。联合综合、完整search和平台/板上仍未完成。

---

# 候选链路实际联合功能

真实CSR驱动的children→metadata→access/owner/coordinate/pager已通过32槽与单槽联合RTL仿真及源绑定审计。每组1212扩展、3229过滤子节点、3022判定、60EARLY，结果和Config14与CPU相同；EARLY之后排空余下子节点回放。

每组42117 graph读、9131 design读、2500 design写、194 owner读。完整设计后备逐字节相等，owner后备全文件保持不变，每笔owner R与真实初始镜像一致。整个operation的host锁探测通过。仿真周期分别1319315/1211128，不是板上性能数据。测试使用FRAMES16384/INDEX14/HASH15，未验证默认完整目录参数。

真实初始owner导出覆盖9089009节点和180326初始引用，与独立加载事件逐项一致。初始overflow0且本阶段只读，容量64的空pool仅适用于此阶段。

证据：`candidate_pipeline_full_20261024/source_bound_audit.json`，输入`candidate_decisions_20261024/source_bound_audit.json`，初始owner`candidate_initial_owner_20261024/manifest.json`。pilot和之前编译/仲裁证据均保留。

CPU对照保留原判定体，仅替换cost调用为记录；query标签/target是脚本测试状态。没有cost/push/内部标签更新、Frontier或完整路由。下一步联合故障/身份/排空边界及默认参数验证，再联合综合。契约见`hardware/CANDIDATE_PIPELINE_CONTRACT.md`。
