# 有界探测的后备目录索引

新模块 `backing_frame_directory_indexed` 保留旧 `backing_frame_directory_lookup` 的全部公开命令、状态码、frame 地址、published、四槽租约与严格事务号语义。旧源码保持冻结。此模块尚未接入完整状态端点。

权威状态仍为按 frame 排列的 25bit owner/published BRAM。辅助索引只保存 epoch 与 frame，默认32768槽、最多64次线性探测、8位epoch；不会复制published或省略完整24bit owner比较。每个有效桶必须再读权威BRAM核对owner。哈希使用集合预实验中的32bit mixed32，以三步寄存状态计算；其资源和时序须实际综合验证。

看到空桶时，若本生命周期全部owner都有索引，可以确定不存在；否则必须顺序扫描权威目录。探测预算耗尽也必须扫描。真正不存在的新owner在有物理frame时仍能分配；若无索引槽则记录 `index_complete=0`，本生命周期之后所有索引未命中都扫描。不会把探测耗尽当作FULL，也不会因溢出重复分配。命中读取当前published，PIN/MEMORY_DONE不需要更新索引。

冷reset之后逐槽清零索引，完成前cmd_ready为0。epoch0无效；正常RECYCLE在租约全空且fence_retired条件满足时递增epoch，同时清分配范围和事务隔离。epoch全1时，RECYCLE必须等待全表清零后才返回成功，随后使用epoch1。清表每周期一个槽，默认32768周期；响应背压期间不接受命令。旧表项不会跨回绕复活。reset仍是整传输域的协调冷启动，不支持仅复位目录后接收旧总线响应。

支持参数：1≤INDEX_BITS≤31、1≤HASH_BITS≤24、1≤EPOCH_BITS≤16，1≤FRAMES≤2^INDEX_BITS，1≤PROBE_LIMIT≤2^HASH_BITS。参数组合由构建入口检查。保留单命令串行化、同步单读单写BRAM；不宣称最坏查询延迟恒定——安全回退上界仍随FRAMES增长。

验证应覆盖：与旧目录逐命令差分、强制碰撞和未索引owner重复查找/RESERVE、空桶后回退、FULL但已有owner仍可命中、published随WB撤销/提交、失败租约阻止回收、非法cookie/旧tx、价格/query隔离、响应背压、冷启动清表、至少两次epoch回绕及旧owner隔离。真实键集合只是额外的owner映射验证，不能代替真实页传输或完整路由回放。
