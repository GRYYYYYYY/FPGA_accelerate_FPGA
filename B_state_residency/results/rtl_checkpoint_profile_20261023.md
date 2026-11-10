# Checkpoint分阶段周期观察

被动wrapper实例化已冻结的四页五字段测试，不驱动或修改测试/DUT。原221检查、8checkpoint、36传输、4tag回绕及结束354420ns完全一致；compile/elaborate/simulate和runner61139均exit0。数据来自公开命令握手、响应和端点状态采样，CSV逐条记录，不是排程估计。

8次checkpoint接受到首次成功响应25–29周期，均值26.375；到host消费响应29–33周期，均值30.375，差值固定4周期是原测试台响应背压。各阶段平均周期：BEGIN发送1/等待4.625，排空等待2.75，FINISH发送1/等待4.625，目录操作发送1/等待5，恢复QUERY发送1/等待4.375。逐条核对阶段周期和+1（接受命令采样边沿）等于响应延迟。

范围：4帧/3位事务与代次/1位tag，非零query/price，周期性调度停顿；开始checkpoint前脏页已写回、驻留槽已释放。此处不包括前置写回/释放、后续缺页、全量真实查询、跨域网络、完整路由或实卡时间。不能把这个小样本均值直接外推为全38查询开销或性能保证。

证据rtl_checkpoint_profile_20261023/manifest.json（SHA256 `a8d8d96a2280b74e2227d8a344435a2704b8dccaad1b528f173f0ec796caa83f`）、checkpoint_cycles.csv、profile_audit.json和冻结源。审计同时核对原多页测试RTL/TB哈希、计数和结束时间。全38输入生成与自动衔接流程独立继续，未修改其冻结源码。
