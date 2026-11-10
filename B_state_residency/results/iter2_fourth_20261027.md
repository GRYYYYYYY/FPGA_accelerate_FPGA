# 自然第四条查询与最后owner释放（2026-10-27）

真实CPU query180330为iteration2、connection170791/net26422/source66893/sink6954。普通捕获与prepare ripup观察版的10份输出逐字节一致，完整路由结果哈希不变。两份独立事件/8叉heap/全9089009行状态审计通过：83poll、82expand、402candidate、231标签更新。231尚不是独立重算的cost次数。

实际旧路径和新回溯路径都是6954→990178→558358→265324→66893。准备阶段990178的最后一个本net引用1→0，occupancy1→0，primary owner变为-1；558358和265324分别refs4→3、5→4，occupancy保持2/1。源和sink的owner不被这条路径的ripup修改。本例没有overflow池新增或回收，原overflow完整字节保持不变。

独立q3提交→q4准备转换核对全部9089009行，精确应用q3三节点提交、q4原生拆线、旧target清理/新target设置和source push。只有6954/66893/151354/990178/990179五行变化，其余行及价格/overflow原字节不变。此前prepare审计只支持refs>1；本轮在独立脚本中增加仅限已证实的“唯一primary owner、occupancy1”释放规则，未修改旧冻结脚本，也不声称支持所有overflow owner排列。

两份捕获已归档并实际恢复，source-bound audit字节一致；恢复后的prepare和transition审计也重新生成且字节一致。证据在同名JSON，14文件源码冻结在iter2_fourth_sources_20261027/manifest.json。

后续接入需要保留q1/q2/q3，再处理q4历史路径，不能拿已有连接的槽代替它或直接装入prepared owner。当前尚无q4独立cost/filter oracle、四路径槽完整RTL、G4发布/恢复、板卡时序或性能证明。
