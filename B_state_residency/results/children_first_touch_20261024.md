# 首次邻接过滤状态机及完整真实路由对照（2026-10-24）

新增 `hardware/search/children_machine.hpp` 将原 `getChildren` 首次过滤拆为原始边获取、排除判断、创建节点、类型/死端检查、输出与发布请求。`adapters/build_children_router.py` 仅替换该过滤段，保留首次缓存所有权、lazy fetch/intern和发布实现，并填补行数以保持标签采样的源码行号。原始源码及已有基线未修改。

单元结果 `children_unit_v4_20261024` 与 `audit_children_unit.py` passed：73728组flags/created/Laguna/prune/type/dead组合，加20000组多边序列，共 **93728组**。原始getChildren、排除及dead端函数逐字抽取作为golden；检查输出顺序、标签读取/创建事件、created/dead/rawFetched状态和fetch次数。覆盖0..18条边、重复子节点、自环、简化lazy/nonlazy与串行锁分支。全部93728组再次访问缓存，修改标签、created、属性、类型和prune后仍返回原列表且无过滤副作用；66841组空结果，8760组发生创建后丢弃节点。另验证错误phase、越界node拒绝与显式发布终态。

前三次单元构建未通过，目录 `children_unit_20261024`、`children_unit_v2_20261024`、`children_unit_v3_20261024` 保留。原因是测试脚手架缺RouteNodeType命名空间/NodeStatic别名，以及误用原文本字符偏移截取长度已变化的候选函数；最终按候选自己的结束标记抽取。算法helper没有因这些构建错误改动，不将失败构建计作语义验证。

完整真实结果 `children_real_20261024` 与 `audit_children_real.py` passed：使用同一9089009节点/40469536原始边输入、已验证bounded frontier和exclusion helper，完成 **570286次搜索、130334832次入队、12轮收敛、overused=0**。与冻结 `exclusion_real_20261024` 对照：路径结果逐字节一致，全部搜索元数据逐字节一致，已采集标签访问二进制一致。标签访问仍是原始抽样，不声称核对了每条完整运行标签访问；未增加硬件或速度结论。

关键语义：isExcluded通过后先getOrCreate，之后才检查INACCESSIBLE/deadEnd；重复child会观察更新后的created。结构any_alive计算先于排除，不能以过滤输出代替。首次缓存发布后不会因query/price/标签改变而重新过滤，空缓存也是有效缓存。这决定了后续硬件必须保存设计级过滤结果，不能把raw CSR或查询级标签present作为替代。接口和恢复边界见 [首次过滤契约](../hardware/CHILDREN_FIRST_TOUCH.md)。

证据绑定：helper SHA256 `2c81dcc34cf7ca50eca31354806a3e943517c3a271857590d4b62a4e19782ed3`；单元manifest `6c38e24f227497259aaa0a95d27ee0de32408c0a06d1d96f4af2df82e427b852`；完整真实manifest `d79a8a0bd96a6fb318244828d4700bfb219e2606f62bf4fa80c356136ed3f171`。生成器、helper、原函数片段、编译命令、binary、结果和采样记录均经审计绑定。runner/tool8353已经终态，不重投。

复核命令：`python3 scripts/audit_children_unit.py`、`python3 scripts/audit_children_real.py`。后续实现硬件请求/响应控制器及图/设计状态服务，然后接自动换页排除边引擎。当前没有首次过滤HLS/RTL、设备图读取、完整设备搜索或平台/板上结果，研究继续。
