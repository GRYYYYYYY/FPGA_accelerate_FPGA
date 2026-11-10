# 运行中owner增量快照及G2 warm联动通过（2026-10-27）

详见results/runtime_owner_snapshot_20261027.json、hardware/variants/owner_snapshot_writer_v1/CONTRACT.md及hardware/variants/iter2_runtime_owner_v1/CONTRACT.md。选定full_v4/pressure_v4与unit_v3。新增incremental_owner_snapshot及owner_snapshot_checkpoint_adapter；现有路由/恢复生产层级沿用已审计基线。

候选owner只预装原始G1基线副本，不再装前轮prepared G2图像。实际query180327提交和历史路径ripup的6次owner AW被RTL跟踪，去重为4条64B脏行（339193/558358/265324/990179所在行；包含最终回到基线的行）。原生PC lease下，从当前working DDR真实读取4条、写候选4条并回读4条验证，形成真实完成回执；新RTL适配层在命令/复制/回复保持时封锁lease释放和发布许可，回复消费后才提供jp_manifest_ready。之后实际authority/config/coordinator共同发布G2/CP18，继续q180328第二owner-B故障、G2两键refs1/3修正、822标签/path/query恢复及attempt4重试，无工作DDR重装/外部cold reset。

32槽/单槽均通过：新增第9路AXI逐字节核对源4读/目标4写/目标4读（256B写入），完整146284032B候选等于真实CPU prepared态；原有8AXI、13个工作owner记录写、31个snapshot读beat与完整working owner/全部822标签及3MB backing重放通过。故障前/重试q180328各114poll/113expand/564candidate/302cost匹配CPU，第一query仍171/170/849/421，最后两路径共存、ledger180328/storage4/2/4。

单元11事务/66次保持检查覆盖零脏行、去重、命令锁存、无lease、源R/目标B在途取消与真实退休、源R错、目标B错、回读R错、dirty满表、源B错、地址重叠。独立重放10R/5W，含2个R错误与1个B错误；失败不产生有效回执。初始完整层级两次未通过编译仅为TB声明/拼接问题，v3为门控封装前开发例，正式证据为采用独立RTL适配层的v4。三归档均实际恢复重审audit逐字节一致。源冻结results/runtime_owner_snapshot_sources_20261027（22文件）。

限制必须保留：初始准确G1 clone及可信epoch设置仍是外部前提；单一已观察owner写者、dirty表64行满则拒绝、固定G1/G2布局与namespace接线。源B错误会使当前累积epoch失效，尚无恢复后重新arm/基线轮转。复制主口通过共享实际文件模拟第二个一致DDR端口，未实现板卡互连。标签仍依赖CPU保守822未来读闭包和外部历史路径；不是全状态运行中snapshot writer、硬件目录导出、全图未知页初始化、持久化认证/floor、任意变价、综合时序或板卡收益证明。

下一优先补齐实际目录/标签导出以减少CPU闭包前提，并建立owner增量epoch的原生换代/错误后rearm契约；继续真实overflow分配/回收的完整系统验证。不要将本例4条copy行推广成任意全图dirty容量或板卡加速比。研究继续，goal active。

以下保留历史。

