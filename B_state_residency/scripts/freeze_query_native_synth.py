"""Freeze restored matched OOC results while keeping timing acceptance unresolved."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT,sha

p=Path('/tmp/B_state_residency_offer_20261025/query_native_synth_v1')
mp=p/'manifest.json';ap=p/'source_bound_audit.json'
m=json.loads(mp.read_text());a=json.loads(ap.read_text())
rp=ROOT/'results/query_native_synth_v1_restore_20261025.json';r=json.loads(rp.read_text())
assert a['status']==r['status']=='passed'and r['audit_byte_identical']
assert a['manifest_sha256']==sha(mp)and r['audit_sha256']==sha(ap)
ref=Path(m['reference']);ra=json.loads((ref/'source_bound_audit.json').read_text())
assert sha(ref/'source_bound_audit.json')==m['reference_audit_sha256']
delta={k:a['utilization'][k]-ra['utilization'][k]for k in ['LUT','FF','BRAM','DSP','URAM']}
report=ROOT/'results/query_native_synth_20261028.json';assert not report.exists()
report.write_text(json.dumps(dict(status='matched_ooc_artifacts_restored',audit=a,restoration=r,
    reference_audit_sha256=sha(ref/'source_bound_audit.json'),utilization_delta_candidate_minus_reference=delta,
    preplacement_wns_delta_ns=a['preplacement_wns_ns']-ra['preplacement_wns_ns'],
    timing_qualified=False,full_behavior_matrix_complete=False,
    scope='Query lifecycle and integrated root specialization only on the matched ten-source OOC baseline; full CRC pressure and native tests separate. Same133 production RTL, parameters, U280 and10ns constraints. No placed/routed or board conclusion.'),indent=2,sort_keys=True)+'\n')
md=ROOT/'results/query_native_synth_20261028.md';assert not md.exists()
md.write_text(f'''# Query接口互斥候选同源OOC复查

query_native_synth_v1在已恢复native_retirement_synth_v1上仅覆盖query_lifecycle与root两源；133生产RTL与已通过完整CRC压力例逐文件一致，器件/参数/U280/10ns/Tcl保持匹配。没有合成TB监视器或新增IO约束。

check_timing组合环{a['check_timing_counts']['loops']}，LUTLP-1区域LUT计数{a['drc_loop_cell_counts']}，自动切环警告{len(a['timing_loop_warnings'])}。候选布局前WNS {a['preplacement_wns_ns']}ns，参考{ra['preplacement_wns_ns']}ns。存在环或自动切断时，slack不能证明时序有效性。

候选LUT {a['utilization']['LUT']}、FF {a['utilization']['FF']}、BRAM {a['utilization']['BRAM']}、DSP {a['utilization']['DSP']}；候选减参考的差值{delta}。零latch/blackbox检查由独立审计提供。

产物审计、{r['files']}文件归档实际恢复和audit字节一致通过。design_acceptance={a['design_acceptance']}，timing_qualified=false。未布局net估计、缺少真实IO/时钟位置及物理实现条件，不能换算成板卡频率或收益。新候选完整行为矩阵尚未执行，只有独立CRC压力例/原生12例证据。
''')
f=ROOT/'results/query_native_synth_sources_20261028';assert not f.exists();f.mkdir();files={}
def copy(src,rel):
    dst=f/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    assert sha(src)==sha(dst);files[str(rel)]=dict(source=str(src),sha256=sha(dst))
for n,h in m['sources'].items():
    src=p/'sources'/n;assert sha(src)==h;copy(src,Path('sources')/n)
for src in [mp,ap,rp,report,md,ref/'source_bound_audit.json']:
    rel=Path('reports')/('reference_audit.json'if src.parent==ref else src.name);copy(src,rel)
for n in ['prepare_query_native_synth.py','audit_query_native_synth.py','freeze_query_native_synth.py',
          'run_restore_seed_synth.py','inspect_restore_seed_synth.py','analyze_restore_seed_loops.py','audit_restore_seed_diagnostics.py','run_checkpoint_authority.py']:
    copy(ROOT/'scripts'/n,Path('scripts')/n)
for variant in ['query_native_system_v1','query_native_exclusion_v1']:
    v=ROOT/'hardware/variants'/variant
    for n in ['build.py'if variant=='query_native_system_v1'else'manifest.json','CONTRACT.md']:
        copy(v/n,Path('variants')/variant/n)
    for mode in ['baseline','fixed']:
        for n in ['query_lifecycle.sv','query_residency_system.sv']:copy(v/mode/n,Path('variants')/variant/mode/n)
(f/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,timing_qualified=False),indent=2,sort_keys=True)+'\n')
print('QUERY_NATIVE_SYNTH_FROZEN',len(files),'files')
