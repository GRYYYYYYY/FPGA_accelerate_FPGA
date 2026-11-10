# 保留目录原语：兼容性与故障回归

独立XSim六组测试完成，runner exit0。旧小规模向量1460条中，10条原先检查opcode6为BAD；新模块将6定义为RECYCLE_TX，因此明确排除这10条，其余1450条原始命令及期望值不变，与原线性目录逐响应差分通过。旧大规模66261条向量全部原样通过独立oracle，包括真实最大键集与对抗碰撞。新模块沿用全部索引、权威owner和发布位检查。

这不是全部旧接口行为不变：opcode6的定义有意改变。排除的原行号及全文记录在manifest；opcode7仍非法。新opcode6由上一轮1006命令/40次回收先导覆盖。

四项独立故障变体均成功编译/展开，并由运行期预期断言检出，无PASS标记：

- skip_id_reset：Fatal: status check=45 op=1 got=5 expected=0
- drop_allocation：Fatal: retained allocation
- ignore_leases：Fatal: status check=25 op=6 got=0 expected=2
- ignore_fence：Fatal: status check=30 op=6 got=0 expected=2

只修改结果目录内的故障源码副本。工作区RTL与已通过源码hash不变；small/large测试台仅替换被测module名。large关闭线性参考，ref_cycles是原测试台镜像计数，manifest已设null，不能解释为基线时间。

证据 `results/rtl_retained_directory_regression_20261023/manifest.json`，SHA256 `0ceb1ab33bddcfe568d1d0852bd67a75a681a2fdffc2b5177abc8199d7278dac`，以及completion_audit。无完整端点checkpoint、综合或实卡证明。
