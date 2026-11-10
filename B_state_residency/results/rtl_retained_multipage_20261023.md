# Checkpoint多页/五字段验证

冻结RTL不改。新测试复用原公开接口、独立AXI字节模型及端点顺序断言，使用四个后备页、全部四个驻留槽，query=2、price=9。每页节点0和63均写入五字段；包含NaN位模式、符号位、全位模式及8位目标字段。先完成四页写回与释放，再执行8次checkpoint，每次重用generation0和transaction0..3，经AXI逐页读回并核对所有字段；公共checkpoint携带不同身份参数，内部仍恢复原身份。

XSim编译/展开/模拟均exit0，runner48726 exit0。221检查、36次完整页传输、8checkpoint、4次1位fence tag回绕，结束354420ns；四页owner保持，原始21-beat页面字节检查与重建的136位字段值一致。测试期望来自独立构造的字段位模式，不读取DUT内存作为期望。

证据目录rtl_retained_multipage_20261023，manifest SHA256 `7157b1b2aa8221796beb04d690f68f2e6ab5c7c7e6118092be2701a3039c1d02`，completion_audit、完整日志和冻结源码。仍为定向行为测试，不代替全38真实查询回放、布局布线或实卡。

新增audit_checkpoint_vectors.py逐查询对照前轮独立planner的累计访问、读写、BIND/RELEASE、WB/RF和checkpoint数。全量生成中的前29查询已核对一致（7,127,089字段、1,380,406传输），status=verified_partial_receipts，未当作全量通过。生成完成后必须不带--progress运行以核对完整向量文件哈希和终态，再启动RTL。
