#!/usr/bin/env python3
"""Generate the real paging ablation report from completed, verified runs."""
import argparse
import json
from pathlib import Path
import statistics as st

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix",type=Path)
    parser.add_argument("diagnostic",type=Path)
    parser.add_argument("--output",type=Path,default=ROOT/"results/paged_real_20261022.md")
    args=parser.parse_args()
    matrix=args.matrix.resolve();diagnostic=args.diagnostic.resolve()
    m=json.loads((matrix/"manifest.json").read_text());d=json.loads((diagnostic/"manifest.json").read_text())
    if m["status"]!="passed" or d["status"]!="passed":raise ValueError("Both experiments must pass")
    if m["pilot"] or m["config"]["repetitions"]<3 or m["build"]["diagnostic"]:raise ValueError("Require repeated performance runs")
    groups={(mode,v):[r for r in m['runs'] if r['mode']==mode and r['variant']==v]
            for mode,variants in [('serial',['original','paged','node_epoch']),('batch',['paged','node_epoch'])] for v in variants}
    names={('serial','original'):'原始串行标记',('serial','paged'):'同序串行＋原始分页',('serial','node_epoch'):'同序串行＋逐节点 epoch',
           ('batch','paged'):'4 worker 批处理＋原始分页',('batch','node_epoch'):'4 worker 批处理＋逐节点 epoch'}
    lines=[]
    for key,rows in groups.items():
        if len(rows)!=m['config']['repetitions'] or not all(r['verified'] for r in rows):raise ValueError('Incomplete group')
        times=[r['metrics']['route_ms']/1000 for r in rows]
        lines.append(f"| {names[key]} | {st.median(times):.3f} | {min(times):.3f}–{max(times):.3f} | {st.median(r['metrics']['total_ms']/1000 for r in rows):.3f} | {st.median(r['max_rss_kib']/1024 for r in rows):.1f} |")
    def median(mode,variant,field='route_ms'):return st.median(r['metrics'][field] for r in groups[mode,variant])
    serial_reduction=100*(1-median('serial','node_epoch')/median('serial','paged'))
    batch_reduction=100*(1-median('batch','node_epoch')/median('batch','paged'))
    serial_slower=median('serial','node_epoch')/median('serial','original')
    serial_hash=groups['serial','original'][0]['result_sha256'];batch_hash=groups['batch','paged'][0]['result_sha256']
    serial_wl=groups['serial','original'][0]['metrics']['wire_length'];batch_wl=groups['batch','paged'][0]['metrics']['wire_length']
    ca,cb=[r['labels']['contexts'][0] for r in d['runs']]
    memory_rows=[]
    for key,rows in groups.items():
        if key[1]=='original':continue
        payload=st.median(sum(c['pool_capacity_bytes'] for c in r['labels']['contexts']) for r in rows)/2**20
        tags=st.median(sum(c['node_epoch_bytes'] for c in r['labels']['contexts']) for r in rows)/2**20
        table=st.median(sum(c['page_table_bytes'] for c in r['labels']['contexts']) for r in rows)/2**20
        peaks=[sum(c['peak_pool_nodes']*r['labels']['node_size'] for c in r['labels']['contexts'])/2**20 for r in rows]
        memory_rows.append(f"| {names[key]} | {payload:.1f} | {tags:.1f} | {table:.3f} | {min(peaks):.1f}–{max(peaks):.1f} |")
    memory_note='未取得外部 RSS 分阶段观察；以 /usr/bin/time 峰值与标签容量为准。'
    file=matrix/'memory_observation_summary.json'
    if file.exists():
        obs=json.loads(file.read_text())['runs'];rows=[]
        for key,rs in groups.items():
            values=[obs[r['name']]['observed_after_load_peak_rss_kib']/1024 for r in rs if r['repetition']>=1 and r['name'] in obs]
            if values:rows.append(f"- {names[key]}：后两次完整观察中，加载后 RSS 采样峰值 {min(values):.1f}–{max(values):.1f} MiB。")
        memory_note='另以 500 ms 间隔外部读取 /proc RSS；观察从首轮中途启动，以下只比较后两轮。此数值包含布线和写出阶段，会漏掉短暂峰值，不替代 time -v 的全进程峰值。\n\n'+'\n'.join(rows)
    report=f'''# 真实分页 / 逐节点 epoch 消融（2026-10-22）

逐节点 epoch 已接入真实路由器，三次重复中，同序串行分页的布线耗时下降 **{serial_reduction:.1f}%**，固定批处理配置下降 **{batch_reduction:.1f}%**。两种标签实现在同一调度下的结果与收敛过程逐字节/逐轮一致，独立图验证通过。

其耗时仍为原始串行标记的 **{serial_slower:.2f} 倍**，并增加 epoch 标签内存；本轮证明的是相对原始分页的完整 CPU 路径收益，不是超过最快串行基线或 FPGA 加速。

## 输入与受控改动

沿用 [真实轨迹实验](real_trace_20261022.md) 的 logicnets_jscl / xcvu3p 冻结 RRT：9089009 节点、27960 个 net、180326 条间接连接；输入 SHA256 `{m['config']['input_sha256']}`。原始参考与其他方案未修改。

`adapters/build_paged_router.py` 从固定 SHA256 源码生成本地副本。两种分页共用相同页表、512 节点页、2048 页初始池、倍增和批处理回收策略。唯一主要策略差异：原始分页在每次查询第一次触页时清零整页；候选为物理槽位增加 uint32 epoch，仅在节点第一次访问时清零。每次搜索失效，绝不跨价格版本复用距离。全局 dyn 中历史价格与 net 占用保持原路径。

串行适配沿用原有连接顺序、搜索、代价与提交，仅每次查询 reset 分页状态并将 source.prev 设为 -1（与原始 batch 入口一致）。原始 CPU 标记二进制另作实际基线。

批处理复用原始 CPU 路径：1 个 partition worker，4 个 batch worker，批宽 8，仅迭代 3–8 且 overused≥128 时启用，rollback 开启、bounce=0、预算 1048576。RRT1 已有完整 CSR，但原代码只由 JNI/GPU 加载器置 flatGraphBuilt；本地适配在检查邻接边界后置该标志，使实际 batch 入口可用。此适配对两种分页相同，没有改批成员选择/提交次序。

CPU Xeon Gold 6530；串行绑定 CPU 8，批处理限制在 CPU 8–12，关闭原程序自行跨 NUMA 绑核。每种配置三次，按固定随机种子在每个重复块内打乱五种配置，逐个进程运行。所有性能程序关闭逐访问计数。每次重新加载，文件缓存未清除；无独占机器或固定频率保证。

## 完整时间

| 配置 | 布线中位数 / s | 三次范围 / s | 加载＋布线＋写出 / s | 全进程峰值 RSS 中位数 / MiB |
|---|---:|---:|---:|---:|
{chr(10).join(lines)}

route 包含 bbox、标签初始分配、池增长/回收、完整拥塞迭代、回溯与提交；不包含一次性 Java 导出、结果验证或 Vivado。total 是原程序三阶段合计；相对原始分页，串行/批处理的 total 分别下降 {100*(1-median('serial','node_epoch','total_ms')/median('serial','paged','total_ms')):.1f}% / {100*(1-median('batch','node_epoch','total_ms')/median('batch','paged','total_ms')):.1f}%。外部进程墙钟另存在 manifest。此前 CPU 0 上的 23.22 s 不参与本轮速度比，全部对比使用本轮 CPU 8 的新基线。

## 正确性与调度差异

三个串行变体的全部重复均为 `{serial_hash}`。两种 batch 变体的全部重复均为 `{batch_hash}`。所有运行最终零过用、零未布通；同模式下比较逐轮 overuse、rerouted 等计数，任何差异都会中止矩阵。

批处理与串行的搜索/价格顺序不同，结果属于两个独立比较组。串行 totalLen={serial_wl}，batch totalLen={batch_wl}，差异 **{100*(batch_wl/serial_wl-1):.3f}%**，不能把跨组差异归因于 epoch。totalLen 不是布后时序指标。独立检查全部连接的端点、图边、环路和跨 net 资源冲突，均通过；尚未回写物理设计或做 Vivado DRC/时序验证。

原始 batch 日志的 pops/conn、noFloodPath 在无 CUDA 编译分支未累计，出现 0 不表示无搜索；本报告不使用这些字段推导工作量。

## 内存与容量

| 配置 | 结束时标签池 / MiB | epoch 数组 / MiB | 页表 / MiB | 各上下文历史最大池之和 / MiB |
|---|---:|---:|---:|---:|
{chr(10).join(memory_rows)}

每个 NodeDyn 24 B，新增 uint32 标签为 4 B/槽位；此方案减少初始化工作，**没有压缩页池**。全局 dyn（约 208 MiB，含持久历史）仍保留。批处理任务由 worker 动态领取，因此各 worker 的增长次数/峰值分配可不同，即使最终路径完全相同；“各上下文历史最大池之和”也不等于同时达到的进程峰值。RSS 还受分配器缓存及增长/回收时新旧缓冲区并存影响，不能只用结束时容量解释峰值差异。

{memory_note}

## 单独计数验证

另编译带 `B_LABEL_DIAGNOSTIC` 的程序，同样跑完整真实串行路径并核对原始结果哈希；这些运行时间不参与上表。两种实现都进行了 {ca['resets']:,} 次 reset、{ca['page_claims']:,} 次页认领。

| 指标 | 原始分页 | 逐节点 epoch |
|---|---:|---:|
| 查询首次触达导致的 NodeDyn 清零槽位 | {ca['cleared_nodes']:,} | {cb['cleared_nodes']:,} |
| 按 24 B/槽位计算的逻辑初始化字节 | {ca['cleared_nodes']*24:,} | {cb['cleared_nodes']*24:,} |

逻辑清零槽位减少 **{d['clear_slot_reduction_factor']:.2f} 倍**，与上一轮抽样的稀疏性一致；这不是 DRAM 实测流量或加速倍数，不含 vector 首次分配/扩容对存储的初始化。完整时间仍包含这些分配成本和每次访问的 epoch 检查。

## 验证、复现与下一步

两种生成后的真实标签类都经过 ASan/UBSan 检查：重复读写、页池增长、物理槽位换绑、独立上下文、uint32 epoch 回绕、回收后增长。没有 sanitizer 报错；真实路由结果另外验证。先导运行保留，未纳入正式三次统计。

- [正式矩阵]({matrix.name}/manifest.json)：15 次性能运行、完整命令、构建哈希、内存和正确性记录。
- [独立计数]({diagnostic.name}/manifest.json)：实际初始化计数及结果校验。
- `build/paged_real_v2/semantic_tests.json`：相同源码的 ASan/UBSan 测试记录。

```bash
# 已有冻结构建可直接运行；首次构建使用指定目录，存在时拒绝覆盖。
python3 adapters/build_paged_router.py --output build/paged_real_v2
python3 scripts/run.py benchmark-paged-real --skip-self-test
# 若没有匹配的已通过语义检查，去掉 --skip-self-test。
python3 adapters/build_paged_router.py --output build/paged_real_diag --diagnostic
python3 scripts/diagnose_paged_real.py
python3 scripts/report_paged_real.py results/<正式矩阵目录> results/<诊断目录>
```

下一步优先加入第二个独立设计，并在相同真实接口评估页粒度/紧凑槽位布局，量化容量、每次访问的额外检查和池回收成本。保留串行标记对照；当前证据支持分页场景中的稀疏初始化优化，尚不足以选择 FPGA 架构或宣称通用加速。
'''
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:f.write(report)
    print(args.output)


if __name__=='__main__':main()
