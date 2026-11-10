# 真实相邻查询的owner连续准备通过（2026-10-27）

详见results/iter2_continuous_20261027.json与hardware/variants/iter2_continuous_v1/CONTRACT.md。32槽/单槽均原生执行query180327、171poll/170expand/849candidate/421cost，验证822标签，保留已提交slot0与sequence180327。真实PC lease导出原路径镜像，保留slot0原字节，导入由隔离原CPU观察的下一连接旧路径67922→990179→558358→265324→66893到slot1，释放lease后由原生route controller拆线。三个内部DEC为990179 refs2→1/occ2、558358 refs4→3/occ2、265324 refs5→4/occ1。无工作DDR重装/冷复位。

独立审计全部9089009节点主owner与下一CPU prepared状态、overflow保持及完整146284032B图像、六次真实owner记录写、822标签/全部3MB backing及8AXI重放。最终slot0保留、slot1清理、journal四键、storage3/1/3、sequence180327。生产RTL未改。

下一query180328独立cost302项及过滤/闭包584条通过，584为现有822的子集；标签差异仅source序号与两个target标记。原CPU插桩全路由哈希与十份查询文件一致，真实旧路径追踪揭示此前仅看558358/265324会漏掉990179的DEC。

本轮只证明owner准备连续性，历史路径仍由已观察CPU轨迹供给；尚未执行下一source/target准备、query180328搜索、G2三方发布或其故障恢复。无运行中快照writer/全局cache/变价/持久化认证/综合时序/板卡收益结论。源冻结results/iter2_continuous_sources_20261027，研究继续，goal active。

以下保留历史。

