# 共享访问接入真实占用后端（2026-10-24）

已将实际AXI owner_state_store和完整身份桥接入访问驻留组合，替换kind4/6返回模型。标签、图/坐标和占用均为实际设备RTL；主机引用操作与整个child判定互斥。契约见[ACCESS_OWNER_CONTRACT](../hardware/ACCESS_OWNER_CONTRACT.md)。metadata生产、真实设计导入/提交、完整search及板上仍未完成。

## 实际联调与独立审计

`access_owner_v3_20261024`三组全部passed，227.209s/exit0。输入与旧模型阶段相同，主机通过真正INC/DEC把当前child的同net引用及其他net占用调整到fixture值；每次CLOSE后GET确认仍保持。不同connection只清查询标签，不清设计占用。

| 项目 | 合成 | 真实图 | 单槽抽样 |
|---|---:|---:|---:|
| child判定 | 11664 | 512 | 614 |
| 实际HLS调用 | 51549 | 1756 | 2727 |
| 动态服务 | 39885 | 1244 | 2113 |
| 实际owner GET | 4970 | 59 | 249 |
| host owner命令 | 55248 | 2557 | 2963 |
| owner AXI读 | 169135 | 7408 | 9184 |
| owner AXI写 | 78526 | 3693 | 4329 |
| host owner被禁止的拍数 | 2114190 | 65553 | 130665 |
| 总仿真周期 | 9279444 | 423370 | 471217 |

独立审计维护node→net→引用数ledger，逐项核对全部host操作、kind4/6值和query关闭后持久状态；原HLS、图/表、native完整payload/presence及标签后备的全部检查沿用并通过。新增重放全部owner R/W，并检查最终primary/pool/allocator及所有活动/空闲链，没有用fixture布尔直接代替设备读取。真实图owner后备包含全N节点零区，不能只检查少数当前child记录。

合成11类服务全覆盖；真实512样本仍没有SLR请求，不外推为真实跨SLR路由。总周期含主机fixture准备、额外实际AXI服务和人为背压，不能与先前模型周期比较为硬件加速。

## 身份与错误边界

`owner_bridge_v3_20261024`passed：15检查/12错误案例/177周期。完整七部分身份在接受后快照，后续输入改变不影响回显；错误cookie/状态、query/price/lock漂移、非法owner/kind、超时、late abort、host逻辑拒绝和无归属raw响应均检查。

`access_owner_boundaries_v3_20261024`passed：4种实际整合故障、5次正常恢复、2099921周期；42 owner读/9写/B，Rerr1/Berr1、9次显式整设计重载。覆盖owner读错误、暂停AR后abort保持VALID并排空、owner回复暴露后abort、host owner写B失败。raw_busy排空后才能恢复，B错误不作回滚假设。

完整默认目录8次逐地址扫描，每次262144项；fixture8在host B故障后早停并重载，不声称完成那次扫描。最长服务等待262083拍，区别于完整初始化工作量；owner准备期间已有后台清零重叠。正常恢复均检查action1/bits0/7步/6服务及CLOSE后owner count0/occ1。

## 保留的负例

- `access_owner_20261024`：顶层生成器在access_pending声明前使用，编译失败。v2调整声明使用顺序；未改变算法。
- `access_owner_v2_20261024`：新variant未带access_dispatch依赖，elaborate失败。v3补入与原v3逐字节相同的dispatch后通过。
- `owner_bridge_20261024`：测试在撤下raw valid的同delta采样组合fault，110ns误判；v2等待稳定后继续。
- `owner_bridge_v2_20261024`：host测试同delta改lock并等待旧ready，已握手却继续等待，50us watchdog。v3仅修测试驱动采样，桥RTL不变。
- `access_owner_boundaries_20261024`：初始复位到setup才拉高，15ns触发未初始化监测；v2从测试开始断言rst。
- `access_owner_boundaries_v2_20261024`：故障和恢复已通过，但把旧cold剩余等待作为新阈值，262083低于任意阈值262100。v3直接监测完整目录逐地址清零，验证8次262144项；没有修改RTL或放宽业务门禁。

## 完整默认综合

`access_owner_synthesis_20261024/final_audit.json` passed：24634LUT、20366FF、375BRAM、3DSP、713CARRY8；零URAM/latch/组合环，LUTLP-1/check_timing loops均0。完整默认163840帧/HASH18的access HLS、dispatch、坐标/分页标签、身份桥及实际owner AXI一起综合；442.241s/exit0/checksumcd394aad/history103。

历史接口约100KiB截断，原receipt保留，同时按唯一ACCESS_OWNER_SYNTH_BEGIN/DONE从会话日志提取完整full_synthesis.log，逐行绑定审计通过。没有ALLOW_COMBINATORIAL_LOOPS豁免。3603输入/1998输出缺平台delay，HD.CLK_SRC未设，尚未布局布线；外部owner后备不计入375BRAM。这是综合资源及功能/结构终态，不是板上时序或速度。

下一步从实际children/design store生成一致Config14快照，合并初始created、持续dead状态及静态类型/flags，然后接geometry/cost、Frontier/递归/回溯提交。当前eager序列化图类型与loader一致；未来lazy JNI的exclusive sink type覆盖必须另行处理，不能假设一切运行时type永远静态。

## 驻留复用边界观测

`owner_reuse_20261024/analysis.json`绑定功能gate和原始源后，按每条真实owner命令的allocator首读划分AXI记录：三组access内部同一child重复owner GET均为0，不能宣称加一个仅限access的重复读取缓存就有收益。原evaluateCostAndPush会再读count；当前允许通过且已经有owner快照的child为合成2232、真实51、压力113。若未来在access→cost之间保留原owner读取的count/occupancy并保持设计只读锁，则对应的重复GET条件读事务为6796/161/350，64B读字节434944/10304/22400。

这些是尚未接入cost的条件机会，不是实测cost流量或加速。当前锁在access最终回复退休时结束，不能直接延长快照有效期；必须延伸所有权或引入可靠设计修改版本，不能因query2/price4数字相同就假定占用未变。metadata生产与完整cost接入仍优先。

功能manifest `80e4a5b5f859e517c5ba7d8b1be71bd520a1b04cec7eaa8d451af4aaf1527f63`，整合边界manifest `34bc5059a9c381ecbbb57bb15592b682454796df05a1ab280161ce46379a2d7b`，综合审计SHA256 `a7b5e49a3debf85770501ab9bf0413813deb44e2fd66695852fd722f0cf51a39`。本阶段所有作业均已终态，B147904空闲。
