"""Freeze one restored full-system query specialization replay, not timing acceptance."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT,sha

p=Path('/tmp/B_state_residency_offer_20261025/query_native_system_crc_pressure_v1')
mp=p/'manifest.json';ap=p/'source_bound_audit.json'
m=json.loads(mp.read_text());a=json.loads(ap.read_text())
rp=ROOT/'results/query_native_system_crc_pressure_v1_restore_20261025.json';r=json.loads(rp.read_text())
assert m['status']=='observed'and a['status']==r['status']=='passed'and r['audit_byte_identical']
assert a['manifest_sha256']==sha(mp)and r['audit_sha256']==sha(ap)
assert len(a['exact_comparisons'])==27
q=a['query_interface_exclusion']
assert q['cycles']>0 and q['service_req']==q['service_rsp']>0 and q['search_req']==q['search_rsp']>0 and q['route_req']==q['route_rsp']>0
report=ROOT/'results/query_native_system_crc_20261028.json';assert not report.exists()
report.write_text(json.dumps(dict(status='one_full_system_query_specialization_case_passed',audit=a,restoration=r,
    full_matrix_complete=False,full_root_loops=None,timing_qualified=False,
    scope='Actual query service/search/route interfaces on the restored real four-query CRC pressure system. Two production overlays, 27 exact outputs and finish cycle. Matched synthesis and other behavioral cases remain separate.'),indent=2,sort_keys=True)+'\n')
md=ROOT/'results/query_native_system_crc_20261028.md';assert not md.exists()
md.write_text(f'''# Query接口互斥候选完整CRC压力例通过

在十源已审计native retirement基线上仅覆盖query_lifecycle与query root两源，默认通用协议保留、实际root启用互斥特化；时序块未改。完整四查询CRC压力例27份输出及结束时间{a['finish_time']}与已恢复参考逐字节/周期一致。

实际query控制器端口观测{q['cycles']}周期，service请求/回复{q['service_req']}/{q['service_rsp']}，search {q['search_req']}/{q['search_rsp']}，route {q['route_req']}/{q['route_rsp']}，三对READY/reply VALID互斥检查通过且各计数非零平衡。原有backend/capture检查保留，没有强制DUT或改写刺激/日志。

独立审计及{r['files']}文件归档实际恢复通过，audit逐字节一致；相关源码、工具和报告冻结。CPU数值/AXI/最终DDR结论通过相同输出观察继承，非任意输入证明。

仅此完整CRC压力例；其他容量/故障场景和匹配新OOC尚待验证。旧十源矩阵及旧零环综合网表不自动证明这个新候选的完整矩阵或时序。固定价格/history、可信初始快照、持久化floor/认证、自然overflow、物理实现和板卡范围限制保留。
''')
f=ROOT/'results/query_native_system_crc_sources_20261028';assert not f.exists();f.mkdir();files={}
def copy(src,rel):
    dst=f/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    assert sha(dst)==sha(src);files[str(rel)]=dict(source=str(src),sha256=sha(dst))
for n,e in m['sources'].items():
    src=p/'sources'/n;assert sha(src)==e['sha256'];copy(src,Path('sources')/n)
for n in ['manifest.json','source_bound_audit.json']:copy(p/n,Path('reports')/n)
for src in [report,md,rp]:copy(src,Path('reports')/src.name)
for n in ['run_query_native_system.py','audit_query_native_system.py','freeze_query_native_system.py','run_checkpoint_authority.py']:
    copy(ROOT/'scripts'/n,Path('scripts')/n)
v=ROOT/'hardware/variants/query_native_system_v1'
for n in ['build.py','CONTRACT.md','tb_query_fault.sv']:
    copy(v/n,Path('variant')/n)
for mode in ['baseline','fixed']:
    for n in ['query_lifecycle.sv','query_residency_system.sv']:copy(v/mode/n,Path('variant')/mode/n)
(f/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,full_matrix_complete=False,timing_qualified=False),indent=2,sort_keys=True)+'\n')
print('QUERY_NATIVE_SYSTEM_FROZEN',len(files),'files')
