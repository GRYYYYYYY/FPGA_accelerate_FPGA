# 原始 VPR 模型适配入口

- `vpr_rrg.py`：XML → SQLite；保留节点/有向边/switch 身份、CHANZ 共享容量和原始 RC/延迟。
- `vpr_baseline.py`：原始 VPR 的串行 route-only 复现、哈希校验、原生与独立检查、失败留档。
- `route_audit.py`：来自相邻 `3D_FPGA_routing/scripts/check_route.py` 的固定快照，原路径/内容 SHA256 见 `configs/vpr.lock.json`；不跟随相邻项目更新。
- `experiment_plan.py`：本目录专用计划，区分已接入基线与计划变体。
- `common.py`：流式哈希和禁止覆盖的输出工具。

使用 `python3 scripts/run.py baseline` 或 `export-rrg --help`。输入、字段单位、验证覆盖和限制见 [INTERFACES.md](../INTERFACES.md)。此处没有 GPU、HLS 或修改版 VPR 路由器。
