# 同网双查询连续仿真

一次配置/复位/标签导入后，在同一实例执行logicnets首query（conn16506/net2717/source65185/sink150697/sequence1），经真实标签回溯、host owner提交和target/source准备后执行同网query2（conn16497/sink128009/sequence2）。价格及存储epoch保持不变；搜索sequence为独立32bit值。

初次只导入328条CPU联合工作集记录，全部内容来自q1初态，不能预装q2标签。首查询实际POLL/target完成后读取328条q1末态；从实际prev沿150697回到65185，逐次真实host标签读取决定下一节点。只对6内部路径节点发owner INC并等待成功响应，源/汇不提交。再发5次标签字段写：旧target=0、新target=1、source lb/upstream=0、visited=2。328条q2准备态读取全部评分通过后，从实际heap重新seed source并搜索q2。q2路径尚未提交。

没有第二次reset/配置/图像或标签导入，没有CPU提供的path地址表驱动回溯，也没有用q2 owner图像替换内存。q2 CPU snapshot只用于比较；cost/candidates/polls文件仅评分。首查询的created/children缓存、标签与实际owner提交持续保留；没有query2前的全量缓存清除。

预期两query共116POLL/114expand/447decision/293cost-OFFER/879标签ACK，7prev跳转、6owner INC，q1和q2各328末态记录及中间328准备态记录。32槽/单槽各自完整运行。

回溯和准备仍由SystemVerilog TB任务驱动，通过真实标签/owner服务接口，不是可综合自主backtrace/commit控制器。CPU预知工作集、未知页初始化、跨价格更新/epoch回绕、q2提交/后续ripup、其他net并发及板卡未覆盖。不得把本例称为生产完整路由器。
