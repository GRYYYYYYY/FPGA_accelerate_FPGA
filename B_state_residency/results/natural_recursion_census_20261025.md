# 两个真实设计的自然递归普查（2026-10-25，优先历史）

完整原始串行搜索的观测普查和独立审计已通过；机器证据 results/natural_recursion_census_20261025.json，由 scripts/summarize_natural_recursion_census.py 汇总。

| 真实设计 | 查询次数 | 扩展次数 | push次数 | lookahead | 最大观测深度 |
| --- | --- | --- | --- | --- | --- |
| logicnets_jscl | 570286 | 47721796 | 130334832 | 0 | 1 |
| vtr_mcml | 718921 | 198273738 | 390136023 | 0 | 1 |

合计1289207查询、245995534扩展、520470855次push，全部found/routed，无abort。两个设计使用同一观测二进制，分别12轮/48轮收敛到overused=0；最终完整路由文件各自与冻结原串行基线逐字节相同。没有修改原图去制造递归。全部观测State profile的cross=0、landmark=0；结论仅限这两个设计及当前串行配置，不能推断其他器件/跨SLR场景不会递归。

观测源码删去新增观测后可逐字恢复冻结原始源码。正负合成对照使用同一header及同一原Router：Laguna正例lookahead=1、剩余兄弟=1、深度2；负例lookahead=0、深度1，故计数器具备实际递归触发覆盖。审计逐行检查34字段、query序列、每轮查询数、push总量及 expansions=pops-found-aborted+lookahead，未截断普查。审计脚本 audit_natural_recursion_census_v1.py 保留首次logicnets已冻结审计版本；通用 audit_natural_recursion_census.py 供MCML使用，其第三参数指向第一个普查目录绑定相同对照源码。

结果链接 results/natural_census_v1、natural_census_controls_v1、natural_mcml_census_v1；三个完整归档位于 results/offer_archives_20261025，同名JSON为恢复索引，分别18/10/18文件。实际移开三个scratch目录后恢复并核验全部成员，重新汇总应与恢复前逐字节一致；凭据 results/natural_recursion_restore_20261025.json。不存在GPU/FPGA实测加速结论，观测运行时间不作为性能基准。

下一优先工作改为采集自然普通查询的真实根前快照和逐候选事件，而不是继续寻找本配置未触发的递归。logicnets首选attempt1、connection_index16506/id37267、net2717、source65185、sink150697、fanout257：72扩展/172push，initial_queue=1、targets=1、最大raw/filtered degree8。MCML首选attempt1、connection_index89391：81扩展/179push。须在原ripup/prolog/prepare后的实际时刻保存State、bbox、标签、owner/history/价格和队列；真实队列长度用queue.sz，不能用底层h.size()。首查询present_factor bits为1056964608，不能从迭代日志推断时刻价格。

尚未输出这些自然查询的可重放状态快照、逐child事件或新RTL oracle；既有1216-parent脚本向量与合成递归矩阵不能充当自然轨迹金标准。接下来研究query级State驻留/重复准备，保留合成递归正确性覆盖；跨价格版本标签有效性、真实owner生命周期、完整搜索/回溯/提交与板卡性能仍待完成。研究goal active。

