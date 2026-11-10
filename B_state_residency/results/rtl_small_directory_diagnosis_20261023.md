# 小页目录变异提前失败诊断

独立重建对照 results/rtl_small_directory_diagnosis_20261023，runner30591 exit0：

|输入|xelab选项|观测|
|---|---|---|
|原始目录和原测试|无debug|check97首次MEMORY_DONE报STALE|
|仅丢checkpoint allocation变异|--debug typical|checkpoint lost allocation（目标断言）|
|同一变异|无debug|同样check97提前STALE|

原始先导使用--debug typical且完整328检查通过。此次仅改变展开选项已复现差异，不能把无debug提前失败归因为目标变异；也尚不足以认定具体优化器缺陷，需进一步最小复现/调度检查。未修改RTL或TB来消除现象。

全部三变异用与先导一致的--debug typical重跑：results/rtl_small_directory_mutants_v2_20261023，runner67949 exit0，manifest 35f76f5c9b341273fcfebf7556d96e0e90bc9266fae51f5b8b25d599e4f338f1。owner截断、槽位别名在对应检查失败；丢后备状态在checkpoint lost allocation明确检出。原始无debug失败保留不覆盖。

查阅AMD [UG900 xelab选项](https://docs.amd.com/r/2023.1-English/ug900-vivado-logic-simulation/xelab-xvhdl-and-xvlog-xsim-Command-Options)说明typical提供line/wave调试能力；该文档并未确认本例缺陷或修复。官方支持搜索未找到精确对应AR，不宣称无已知问题。当前MCP未提供doc_search工具，使用官方网页检索。

新增make_small_services.py导出backing_page_service_small和record_backing_service_small：27位owner、32租约、72位cookie、3位offset，接新codec/AXI/目录。服务层目前未编译或仿真；下一步全链记录服务测试，仍保留目录无debug差异为未解决工具/调度事项。
