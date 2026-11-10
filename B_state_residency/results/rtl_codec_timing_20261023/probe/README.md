# 设备枚举与内存分配兼容性诊断

两次 Vivado 2022.2 在 route_design 完成路由后、写最终报告之前异常退出。栈共同经过 libudev 的 realloc、设备枚举、libXil_lmgr11、GetRegInfoWebTalk。此证据不能独自证明完整根因。

本目录 C 程序只调用真实 libudev 的枚举与释放函数，无设备写入，无许可API、身份替换或枚举stub。它链接 Vivado 自带 libtcmalloc，并使用 RTLD_DEEPBIND 加载 libudev，构造分配器作用域冲突诊断。默认进程 exit=-6、realloc(): invalid pointer；只为子进程设置 LD_PRELOAD=/lib/x86_64-linux-gnu/libc.so.6 后 exit=0、scan_return=0。该诊断模型不是对Vivado内部dlopen标志的直接观测。

编译：

```sh
cc udev_allocator_probe.c -o udev_allocator_probe -Wl,--no-as-needed -L/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/lib/lnx64.o -Wl,-rpath,/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/lib/lnx64.o -l:libtcmalloc.so.4 -ldl
./udev_allocator_probe
LD_PRELOAD=/lib/x86_64-linux-gnu/libc.so.6 ./udev_allocator_probe
```

`probe.log` 的 config_webtalk -info 确认用户及安装均已禁用WebTalk。没有修改设置。AMD文档说明该命令控制用户/安装范围，因此本轮只读取其状态：[config_webtalk](https://docs.amd.com/r/2021.1-English/ug835-vivado-tcl-commands/config_webtalk)。

实际Vivado兼容性重跑位于 ../libc_batch/。环境覆盖与系统libc哈希保存在 launch.json/process_result.json。未修改Vivado安装、全局环境或其他会话。独立诊断只能支持兼容性假设；实现是否成功以最终退出码、报告、检查点及审计为准。
