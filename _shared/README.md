# 公共实验支撑

`python/` 只有标准库 CLI 与小型有向最短路参考，供七个目录复用。它不是通用 FPGA 路由器。

`assets/gpu_router_original/` 是从用户 ZIP 的 rapidwright_code.zip 原样提取的 44 个文件（约 2.7 MB）。原始运行时包、器件数据库与基准未展开。提取文件 SHA256 在 `assets/gpu_router_provenance.json`，不依赖临时目录。

`sources.json` 登记所有原始材料，路径相对工作区根目录。RouterAcc 源码与 PDF 保留在原位置。`project_catalog.json` 是创建时的方向快照；各目录后续研究以自己的配置与文档为准。

`schemas/result.schema.json` 描述 CPU 合成检查结果；性能字段必须为空。真实基准接入时另建结果协议，避免混淆仿真、模型估计与实卡实测。

七个目录配置、数据清单和结果均独立。修改共享 Python 工具后，运行 `python3 scripts/check_all.py` 检查全部方向；不要为一个方向默默改变其他方向的语义。
