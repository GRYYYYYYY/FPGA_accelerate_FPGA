# 新按需路径的G2 runtime snapshot与warm恢复

完整正常两查询已去除初始未来标签闭包，不要再回退到822 imports或插入中间host final读来凑齐标签。

下一优先在label_source_crc/runtime_label_snapshot完整链中启用本七层变体与真实baseline reader：

0. 新baseline AXI是第九路，目前顶层旧8路physical-drained并未自动覆盖它。将reader idle/实际AR-R在途责任纳入PC lease、恢复/target-reset退休条件；验证abort期间不清请求归属，不屏蔽VALID伪造排空。普通成功例一一消费全部781回执不代表故障窗口通用安全。
1. q180327后仅777已用标签/389页；使用实际PC lease + native control(1) flush、目录扫描和真实DDR导出动态count/CRC。不能套旧822/403断言或CPU warm标签文件；容量1024可容777，但必须以原生count和回执验证。
2. 接实际owner dirty-line copy、G2三方共同发布，选定源path/query仍实际导出并核对CRC/floor180327。q2新增4个record按需从immutable G1 baseline取值，先证明已修改记录不会被覆盖。
3. 第二q2 owner-B故障后从G2 authority修复，再恢复实际777流而非旧822流；三回执/退休/最终消费后放行。target_reset会重新OPEN，baseline permit/epoch需明确绑定源数据和恢复目标namespace；不得把新价格号当作任意重定价有效。
4. 重试q2后会重新加载4个缺失记录，最终781标签需对原CPU；原有页状态/空页全部重放。read-seed dirty位、故障中事务退休仍需保留；禁止重新加载working DDR或用预构造答案补数据。

随后做CRC失败、更高attempt重试等新路径恢复回归，再owner baseline epoch轮转/真实overflow生命周期、综合时序/板卡与认证。

默认回归开发历史：default_full_v1在0ps因runner移除了disabled旧TB仍需的imports参数失败；v2只为disabled模式恢复该参数。启用模式的命令行与TB均没有imports入口。
