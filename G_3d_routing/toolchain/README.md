# 本地 VPR 运行依赖

原始 VPR 程序引用相邻项目的干净构建归档，SHA256 固定在 `configs/vpr.lock.json`。当前容器没有 TBB，首次启动失败记录保留在 `results/baseline_20261022T145539.324186Z/`。

使用 Ubuntu 22.04 jammy 官方 apt 索引下载 `libtbb12`、`libtbbmalloc2` 的 `2021.5.0-7ubuntu2` amd64 包，以 `dpkg-deb -x` 解包到 `runtime/`。包及库 SHA256 已写入锁文件，许可证位于解包后的 `runtime/usr/share/doc/`。未全局安装或修改相邻项目。

`baseline` 设置本地 `LD_LIBRARY_PATH`，启动前校验库并用 `ldd` 拒绝缺失依赖。一般系统 C/C++/Tcl/zlib/OpenMP 运行库仍取自当前 Ubuntu；解析路径记入批次环境。跨机器迁移时需重新建立输入引用并记录新环境，不要改写历史结果。
