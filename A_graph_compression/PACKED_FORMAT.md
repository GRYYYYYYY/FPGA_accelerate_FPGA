# AGRAPH01 二进制格式与执行约定

实现见 `src/packed_graph.py` 和 `src/native/packed_bench.cpp`。全部整数小端；每个 section 起始地址和整个文件大小按 64 字节对齐。文件不能追加无关尾部数据。此布局是 CPU/硬件适配的执行格式，不等同于器件数据库的最优压缩方案。

头部为 `<8sIIII>`：magic `AGRAPH01`、版本 1、模式（0 CSR，1 模板）、端序标记 `0x01020304`、section 数量。目录每项 `<16sQQII>`：名称、字节偏移、字节大小、记录数、记录字节数。名称以零填充。

| 表 | 记录 | 内容 |
|---|---|---|
| STR_OFF / STR_DATA | u64 / byte | UTF-8 字符串偏移（N+1）与数据 |
| ATTR_OFF / ATTR_KV | u64 / 2×u32 | 属性集合偏移与 key/value 字符串 ID |
| TILE | 2×u32,3×i32,u32 | 名称、属性、COLUMN、ROW、SLR、类型 |
| NODE | 3×u32,i32 | 名称、属性、规范锚 tile、源邻接行（-1 为未知） |
| ROOT | 3×u32 | 节点 ID、原始物理 PIP 数、原始唯一 child 数 |
| ALIAS | 3×u32 | tile、wire 字符串、规范节点；按前两项排序 |
| GRID | 2×i32,u32 | COLUMN、ROW、tile；坐标只查 tile，不合并节点 |
| AUDIT | byte | 来源、元数据、采样信息 JSON；不参与运行时译码 |
| CSR_OFF / CSR_EDGE | u64 / 7×u32 | 源行偏移；边为 dst,tile,pip,up,down,属性,direction |
| TPL_OFF / RULE | u64 / 2×i32,5×u32 | 模板偏移；规则为 dx,dy,pip,up,down,属性,direction |
| INSTANCE | i32,6×u32 | 模板 ID、remove/add/patch 起点与数量；-1 为显式回退 |
| REMOVE / ADD / PATCH | u32 / RULE / 2×u32 | 局部规则序号、添加规则、规则序号及替代属性 ID |

CSR 模式没有模板表；模板模式没有 CSR 边表。未被评估实例引用的训练模板不写入运行文件，完整冻结训练库单独保存。方向 0 为 forward，1 为 reverse；`up/down` 始终保存物理 PIP 的上下游 wire，逆向遍历时交换。PIP 的 TILE 属性从实际 tile 恢复，其余导出属性保留原始字符串。

模板译码依次执行删除、属性补丁、添加，按相对 tile 坐标定位后分别查源、目标 wire 别名，确认源映射等于规范源 ID。输出排序为 `(dst,tile,pip,up,down,attr,direction)`；本实验全量邻接及所有查询的排序/路径与符号 CSR 验证一致。并行 PIP 各有独立记录。属性补丁关闭时，属性变化退化为完整规则删除/添加。

读入时检查目录边界/宽度/重叠/对齐、索引、源行、别名、异常索引等；完整语义检查进一步用原始图及独立 Vivado child oracle 对照。原生 C++ 全量导出 `<8I>`（source + 7 项边字段），与 Python 读出的所有边逐字节比较。二进制断裂、错误别名、错误属性、错误补丁都有回归。

## 计时与容量

`python3 scripts/run.py packed-check` 使用 g++ 编译本次源码，冻结训练库后加载评估数据，生成唯一目录并保存输入、源码、编译器、二进制和产物哈希。Linux 单核绑定在当前 affinity 允许的最小 CPU；每种变体独立进程。

- 文件大小包含所有表、属性、别名、审计数据、目录和填充。禁止只以 RULE 大小宣称总压缩率。
- 同一 C++ FIFO BFS 比较 CSR、模板全展开、直接模板和 0/16/64/256 行 LRU。状态数组、队列、父边布局一致；单位跳数代价，发现目标即终止。
- 分别记录文件加载、全展开准备、首轮查询、9 次驻留批次，以及状态初始化/核心搜索/回溯。首轮之前有全量边验证，不能称冷缓存结果。
- 文件常驻缓冲区在全展开模式也保留；额外分配按 vector capacity 记录。状态负载为 40×节点数；缓存边负载不含容器开销。
- `/proc/self/status` 的 VmHWM 提供程序执行后的进程内存峰值，包括运行库、容器、工作缓冲、校验和结果。`getrusage().ru_maxrss` 可能继承 fork 前 Python 的峰值，v1 报告该项无效，v2 已修正。
- logical record bytes 是软件记录访问计数，不能解释为 DRAM 物理流量。
- 当前为有明确未知边界的器件资源微基准，无真实网表拥塞/时序代价，也无 FPGA 实卡吞吐结论。
