"""Record the verified local loop fix without claiming full-system closure."""
from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha

p=Path('/tmp/B_state_residency_offer_20261025/capture_loops_component_v1')
m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
rpath=ROOT/'results/capture_loops_component_v1_restore_20261025.json';r=json.loads(rpath.read_text())
assert a['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json')
assert r['status']=='passed'and r['audit_byte_identical']and r['audit_sha256']==sha(p/'source_bound_audit.json')
result=dict(status='component_passed_full_system_pending',audit=a,restoration=r,
    integration_runs=['capture_loops_system_on_full_v1','capture_loops_system_crc_pressure_v1'],
    remaining=['Full real-system regression including normal on/off and both capacities, cancel/CRC noncold retry',
               'Recovery REARM/authority/owner and other full-root feedback regions',
               'Full-root zero-loop DRC/check_timing and physical timing/board validation'])
target=ROOT/'results/capture_loops_component_20261027.json';assert not target.exists()
target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
md='''# 查询展开组件组合环修复通过，完整系统仍待验证

使用已审计真实query root的原生recursive_candidate_controller、expansion_capture、children_frames。三组件切片DEPTH16/CAPACITY4、4272端口位、外部物理expander/metadata/access接口保留。Vivado2022.2实际综合：基线LUTLP-1报告3个LUT形成一个区域，check_timing报告一个环；候选两类检查均零环，零latch/blackbox。没有waiver、false-path或降低实验时钟。

候选只改两源：root VALID由准入条件产生，不再依赖下游READY；无效root本地status1拒绝且不要求下游ready。capture发出独立pop intent，pop_ready仍负责frame_done资格。frames原字节不变；没有撤销物理已发出的请求，abort后仍等待原生生产者退休。

基线在“先看到VALID才给READY”的接收端前16周期无受理；候选低ready时保持请求，随后仅一次受理、空查询完成保持/退休，通过18项检查；无效root在ready0时本地拒绝，无物理请求副作用。

两版各运行原有七场景递归控制回归，以及正常嵌套和九类失败/取消/溢出/身份错误/保持边界的capture回归。独立CPU递归遍历核对76条事件；capture核对14条事件。旧有用例两版事件顺序和结束时刻精确相同（3786ns、2580ns）。独立枚举128组二态输入，求解旧pop反馈方程并核对候选的可观察ready、push、result和实际pop握手相等；这是局部布尔等价检查，不是完整RTL形式证明。

216文件归档实际恢复后重新审计，audit逐字节相同。源码、检查工具与报告另行冻结。完整系统capture_loops_system_on_full_v1及capture_loops_system_crc_pressure_v1已经启动，只替换上述两份生产源，预期与已独立审计的真实四查询参考在全部12AXI、native事件/周期、最终DDR及恢复流上逐字节相同；尚未完成或通过该验证。脚本run_capture_loop_system.py与audit_capture_loop_system.py为新集成工具，后者尚待终态实际执行。

本组件范围没有恢复coordinator/authority/owner连接。原完整query root的20环不因本组件通过而消失；下一继续隔离REARM/ready/fault反馈并进行完整层级综合检查。既有固定价格/history、外部初始快照、持久化floor/认证、自然overflow新增回收、板卡收益等研究缺口保留。
'''
(ROOT/'results/capture_loops_component_20261027.md').write_text(md)
freeze=ROOT/'results/capture_loops_component_sources_20261027';freeze.mkdir()
files={}
def copy(src,rel):
    q=freeze/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,q)
    assert sha(q)==sha(src);files[str(rel)]=dict(source=str(src),sha256=sha(q))
for name,e in m['sources'].items():
    assert sha(p/'sources'/name)==e['sha256'];copy(p/'sources'/name,Path('sources')/name)
for name in ['run_capture_loop_component.py','audit_capture_loop_component.py','freeze_capture_loop_component.py',
             'run_checkpoint_authority.py','archive_offer_result.py','restore_offer_result.py','verify_search_retire_restore.py']:
    copy(ROOT/'scripts'/name,Path('scripts')/name)
for mode in ['baseline','fixed']:
    for name in ['synth.tcl','loops.rpt','check_timing.rpt','facts.txt','utilization.rpt']:
        copy(p/mode/'synth'/name,Path('reports')/mode/name)
for name in ['manifest.json','source_bound_audit.json']:copy(p/name,Path('reports')/name)
for name in ['capture_loops_component_20261027.json','capture_loops_component_20261027.md','capture_loops_component_v1_restore_20261025.json']:
    copy(ROOT/'results'/name,Path('reports')/name)
(freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,scope='Passed native component only; full-system integration runner/auditor remain under development and are not frozen here.'),indent=2,sort_keys=True)+'\n')
print('CAPTURE_COMPONENT_FROZEN',len(files))
