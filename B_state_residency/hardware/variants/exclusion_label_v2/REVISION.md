# v2：同拍故障可见性

CONTRACT.md 保留 v1 的通用协议。v2 将 fault 输出改为「锁存故障 OR 当前服务故障/非预期回复」，使接收方在同一拍 ready/valid 接收之前就能看见中止；内部 stopped 寄存器继续锁存故障，已提供的回复数据保持稳定。

v1 首轮1024项矩阵通过，但增强测试在462741ns发现成功回复等待接收时注入故障，fault 输出需等下一拍才可见。负例保存在 results/exclusion_label_samecycle_negative_20261024；编译/展开成功，仿真明确 Fatal。不是工具故障。v2使用完全相同的增强测试，另验证同边同phase的前次token不能满足新请求。禁止使用v1通过结果作为最终验收。

fault 是同步协议中的组合可见故障指示，外部输入必须与clk同步；未验证跨时钟域。TOKEN_BITS=32生产配置、3位耗尽配置，其余限制沿用CONTRACT.md。
