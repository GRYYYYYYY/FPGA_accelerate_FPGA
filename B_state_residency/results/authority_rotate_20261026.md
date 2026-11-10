# 双槽authority组件与身份回退修复（2026-10-26）

选定authority_rotate_v6。新增checkpoint_authority_rotator，两个原生reader/GET codec共用串行只读AXI；配置处理阻止GET，准备完成未发布时服务旧槽。publish要求两槽物理和逻辑退休、无请求争用、外部许可，握手原子切换活动槽。配置/GET背压阻止发布，discard/abort不改活动身份。

真实反例v5_unfixed：SLVERR后rearm被取消，configured变0；旧包装器错误允许重新初绑，将已发布G2回退G1，未发生publish。唯一修复以保留的非零bound_generation判定身份已建立，不能再用configured。随后正常rearm仍回到原G2。

224次检查、28原生GET、7配置+2rearm、45个64B读beat、两次发布G1→G2→G4通过。原生布局失败2、配置取消3、真实R SLVERR错误9均有原生握手记录。独立namespace状态机核对C/K/L/F/P/X/A/Q/R，全部AXI地址/数据/status与两份真实完整owner图像重放一致，无写请求。旧失败与修复两归档实际恢复复审audit一致，当前源冻结results/authority_rotate_sources_20261026。

初始owner表已有其他net占用；warm相对初始仅六个目标资源变为ref1/occ1，其他字节完全保留。已有node0/net4754和六个目标资源已实际GET验证，按不同net计占用。开发审计中的“初始全零”假设已纠正。

这只是双槽读取基线选择组件，publish_permit尚由TB驱动，未接全系统lease/manifest授权与coordinator journal/config/path/query/label联合发布或恢复。G4复用同一warm owner图像，不是新捕获完整G4快照。未综合/时序/板卡或持久化anti-replay证明。

下一优先coordinator及有效配置的影子prepare/publish，再接真实lease形成同拍联合提交；之后验证换代后的warm恢复，尤其target reset后保存路径/序号等必须恢复完成再放行。运行中工作DDR快照生产、通用多net/overflow、价格/回绕/未知页/持久化/板卡仍缺。goal active。
