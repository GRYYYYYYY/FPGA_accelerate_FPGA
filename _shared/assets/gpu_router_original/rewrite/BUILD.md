# 编译与使用说明

本包为 **C++ JNI 加速版 PartialRouter** 的必须源码（不含 `jars/`、`data/`、`devices/`、`_work/`）。
运行还需 RapidWright 依赖 jar、器件库，以及 `devices/xcvu13p.{rdv,atc}`（可与运行时包一起解压到同一目录树）。

## 目录结构（解压后）

```
rewrite/
├── BUILD.md                 # 本说明
├── run2.sh / run.sh         # 批量跑测示例
├── cpp_router/
│   ├── CMakeLists.txt
│   ├── src/                 # C++ / CUDA 路由核
│   └── include/
└── RapidWright/
    ├── bin/rapidwright      # 启动脚本（PartialRouter → C++ JNI）
    └── src/com/xilinx/rapidwright/
        ├── rwroute/RW*.java # 新增/修改的 Java 类
        └── edif/EDIFNetlist.java
```

完整可运行树还需（来自运行时环境或 `rapidwright_runtime.zip`）：

```
rewrite/
├── devices/xcvu13p.rdv
├── devices/xcvu13p.atc
├── cpp_router/build/libRWRouteCppJni.so   # 编译后生成
└── RapidWright/
    ├── bin/com/...          # 已编译 class（或自行 javac）
    ├── jars/
    └── data/
```

## 环境要求

| 依赖 | 说明 |
|------|------|
| JDK 8+（推荐 11） | `javac` / `java`，且需 `jni.h`（`$JDK/include`） |
| CMake ≥ 3.13、g++（C++17） | 编译 `libRWRouteCppJni.so` |
| CUDA Toolkit（可选） | 有 `nvcc` 时编入 GPU 路径；没有则 CPU-only |
| libstdc++ | 若 `.so` 链到 conda 的 libstdc++，设 `LD_LIBRARY_PATH` |
| 大内存 | 生成 `.rdv` 约需 `-Xmx110g`；日常跑测视用例而定 |

`CMakeLists.txt` 默认 `JDK_HOME=/home/zhlin/jdk11`，其他机器请用 `-DJDK_HOME=...` 覆盖。

## 1. 编译 C++ JNI 库

```bash
ROOT=/path/to/rewrite          # 解压后的 rewrite 根目录
JDK_HOME=${JDK_HOME:-$HOME/jdk11}   # 改成你的 JDK 路径

mkdir -p "$ROOT/cpp_router/build"
cd "$ROOT/cpp_router/build"
cmake .. -DJDK_HOME="$JDK_HOME"
make -j"$(nproc)" RWRouteCppJni

# 产物：
ls -lh "$ROOT/cpp_router/build/libRWRouteCppJni.so"
```

无 CUDA 时会提示 CPU-only，仍可正常跑（`RW_GPU_FLOOD` 无设备时会回退）。

## 2. 编译 Java 类

需已有 `RapidWright/jars/` 与现有 `RapidWright/bin/`（官方 class）。在 `RapidWright` 目录：

```bash
cd "$ROOT/RapidWright"
CP="bin:$(echo jars/*.jar | tr ' ' ':')"

# 主路径（加速入口）
javac -source 8 -target 8 -cp "$CP" -d bin \
  src/com/xilinx/rapidwright/rwroute/RWRouteCppJni.java \
  src/com/xilinx/rapidwright/rwroute/RWRouteCppProblemExport.java \
  src/com/xilinx/rapidwright/rwroute/RWRouteCppVerify.java \
  src/com/xilinx/rapidwright/rwroute/RWRouteCppCheck.java \
  src/com/xilinx/rapidwright/rwroute/RWRouteNodeGraphCache.java \
  src/com/xilinx/rapidwright/rwroute/RWRoute.java \
  src/com/xilinx/rapidwright/rwroute/RWRouteConfig.java \
  src/com/xilinx/rapidwright/edif/EDIFNetlist.java

# 可选：生成器件数据用
javac -source 8 -target 8 -cp "$CP" -d bin \
  src/com/xilinx/rapidwright/rwroute/RWDeviceCompactExport.java \
  src/com/xilinx/rapidwright/rwroute/RWAttrCompact.java
```

## 3. 器件数据（`.rdv` / `.atc`）

启动脚本默认顺序：环境变量 `RWDEV_RDV`/`RWDEV_ATC` → `rewrite/devices/` → `/tmp/`。

若已有文件，放到：

```bash
mkdir -p "$ROOT/devices"
# 将 xcvu13p.rdv / xcvu13p.atc 放入 devices/
```

或一次性生成（需很大堆内存）：

```bash
cd "$ROOT/RapidWright"
./bin/rapidwright --gen-device
# 默认写到 devices/（若目录可写）或按脚本逻辑输出；也可用：
# java -Xmx110g -cp "bin:jars/*" com.xilinx.rapidwright.rwroute.RWDeviceCompactExport <part> <out.rdv>
# java -Xmx32g  -cp "bin:jars/*" com.xilinx.rapidwright.rwroute.RWAttrCompact <part> <out.atc>
```

## 4. 使用（跑 PartialRouter）

在 **`RapidWright` 目录**下执行（相对路径的 DCP 相对当前工作目录解析）：

```bash
cd "$ROOT/RapidWright"

# 推荐：走加速启动脚本（自动加载 .so 与 devices/）
./bin/rapidwright com.xilinx.rapidwright.rwroute.PartialRouter \
  /path/to/in_partial_routed.dcp \
  /path/to/out_rw_routed.dcp \
  --nonTimingDriven \
  [--lutPinSwapping]

# 批量示例见仓库根目录 run2.sh / run.sh（请按实际 case 路径修改）
```

等价环境变量方式（不经脚本时）：

```bash
export RWDEV=1
export RWDEV_RDV="$ROOT/devices/xcvu13p.rdv"
export RWDEV_ATC="$ROOT/devices/xcvu13p.atc"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:+$LD_LIBRARY_PATH:}$ROOT/cpp_router/build"
# 若需要 conda 的 libstdc++：
# export LD_LIBRARY_PATH="$HOME/miniconda3/lib:$LD_LIBRARY_PATH"

java -cp "bin:jars/*" -Djava.library.path="$ROOT/cpp_router/build" \
  com.xilinx.rapidwright.rwroute.RWRouteCppJni \
  in.dcp out.dcp --nonTimingDriven [--lutPinSwapping]
```

常用环境变量：

| 变量 | 含义 |
|------|------|
| `RWDEV_RDV` / `RWDEV_ATC` | 器件文件路径 |
| `RW_GPU_FLOOD` | 默认 `1`；无 GPU 时自动回退 CPU |
| `RW_JVM_ARGS` | 传给 JVM 的额外参数（如 `-Xmx64g`） |
| `RW_VERIFY` | 设 `0` 可关闭输出 DCP 自检 |

## 5. 参数说明

- 多数大 case：`--nonTimingDriven`
- 部分 case（如 THEIA / RLE 等）：可加 `--lutPinSwapping`
- 注意：部分 case 上 `--lutPinSwapping` 会在后处理失败（RapidWright 原有限制）；启动脚本会自动去掉该选项重试一次

## 6. 自检清单

```bash
# 源码 / 产物
ls "$ROOT/cpp_router/build/libRWRouteCppJni.so"
ls "$ROOT/RapidWright/bin/rapidwright"
ls "$ROOT/devices/xcvu13p.rdv" "$ROOT/devices/xcvu13p.atc"

# 原生依赖
ldd "$ROOT/cpp_router/build/libRWRouteCppJni.so"   # 不应有 not found
which java && java -version
```

## 本包包含的源码文件

- `cpp_router/CMakeLists.txt`、`cpp_router/src/*`、`cpp_router/include/*`
- `cpp_router/fpgaif/*`、`cpp_router/capnp_gen/*`（可选 FPGAIF 前端，主路径不需要）
- `RapidWright/bin/rapidwright`
- `RapidWright/src/.../rwroute/RW*.java` 等新增/修改类
- `RapidWright/src/.../edif/EDIFNetlist.java`
- `run.sh`、`run2.sh`
