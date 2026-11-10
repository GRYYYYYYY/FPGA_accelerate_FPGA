# 同网分支共享引用与ripup

扩展已通过的同实例双查询TB。首次回溯时保存真实q1内部路径节点；q2搜索末态再从实际prev回溯保存q2路径。后续提交/ripup使用已保存connection路径，不从可能被后续搜索改写的全局prev重新推导旧路径。

四阶段：0仅q1已提交；1提交q2的6内部节点；2拆除q1的6内部节点；3拆除q2的6内部节点。每阶段通过真实owner GET检查两保存路径的全部12条引用（10个不同节点，共享2节点）。第二分支提交后，共享refs=2/occupancy=1；首分支拆掉后仍refs=1/occupancy=1；两分支都拆掉后内部节点回到空owner。源/汇不在提交或ripup循环中。全部owner请求等待成功回复再推进。

独立审计从两CPU末态快照还原两条路径，以初始owner图像构造四份全图预期，逐个owner B提交边界6/12/18/24重建并核对完整图像。另使用独立捕获的原Router sequence3准备态全9089009节点owner字段确认第二分支提交结果。主AXI重放仍核验全部读值/WSTRB/B及最终owner文件。label/design/history不随ripup清空。

同实例无额外reset/config/导入，保持32槽/单槽双查询全部成本/ACK/标签验证。生产RTL不改。回溯/提交/ripup由TB经真实接口调度，不是可综合控制器；价格/epoch切换、unknown-page、多net并发及板卡不覆盖。各阶段owner基本计数而非运行时间收益是本次验证重点。
