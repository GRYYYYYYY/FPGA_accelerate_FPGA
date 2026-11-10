from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 names=['route_checkpoint_unit_v5','route_checkpoint_unit32_v2','route_checkpoint_synth_v1','route_checkpoint_unit_v6','route_checkpoint_unit32_v3','route_checkpoint_synth_v2','route_checkpoint_unit_v7','route_checkpoint_unit32_v4','route_checkpoint_synth_v3','route_checkpoint_unit_v8','route_checkpoint_unit32_v5']
 audits={};receipts={}
 for n in names:
  p=ROOT/'results'/n;a=json.loads((p/'source_bound_audit.json').read_text());r=json.loads((ROOT/'results'/(n+'_restore_20261025.json')).read_text());assert a['status']==r['status']=='passed' and a['manifest_sha256']==sha(p/'manifest.json') and r['audit_byte_identical'] and r['audit_sha256']==sha(p/'source_bound_audit.json');audits[n]=a;receipts[n]=r
 syn={str(i):audits['route_checkpoint_synth_v'+str(i)]['utilization']for i in [1,2,3]};assert syn['3']['LUT']==min(v['LUT']for v in syn.values())
 selected='route_checkpoint_unit_v8';core=ROOT/'hardware/variants/route_checkpoint_v1/route_commit_controller.sv';assert sha(core)==sha(ROOT/'results'/selected/'sources/route_commit_controller.sv')
 comparison=ROOT/'results/route_checkpoint_index_comparison_20261025.json';assert json.loads(comparison.read_text())['status']=='passed'
 coverage=ROOT/'results/checkpoint_coverage_20261025.json';cv=json.loads(coverage.read_text());assert cv['status']=='incomplete' and len(cv['obligations'])==8
 old=json.loads((ROOT/'results/route_commit_20261025.json').read_text())['synthesis'];assert old['files']['sources/route_commit_controller.sv']==sha(ROOT/'results'/selected/'sources/base_controller.sv')
 # Remove only the task-created convenience backup; measured candidates remain
 # fully frozen in the verified result archives and source closure below.
 backup=ROOT/'hardware/variants/route_checkpoint_v1/build_fixed_slot.py'
 if backup.exists():backup.unlink()
 frozen=ROOT/'results/route_checkpoint_sources_20261025';assert not frozen.exists();frozen.mkdir()
 files=list((ROOT/'hardware/variants/route_checkpoint_v1').glob('*.py'))+list((ROOT/'hardware/variants/route_checkpoint_v1').glob('*.sv'))+[ROOT/'hardware/variants/route_checkpoint_v1/CONTRACT.md']
 files += [ROOT/'scripts'/n for n in ['run_route_checkpoint.py','prepare_route_checkpoint_synth.py','audit_route_checkpoint.py','audit_route_checkpoint_extended.py','audit_route_checkpoint_synth.py','analyze_checkpoint_coverage.py','summarize_route_checkpoint.py','archive_offer_result.py','restore_offer_result.py','verify_search_retire_restore.py']]
 files += [ROOT/'results'/n/'sources/build.py'for n in ['route_checkpoint_unit_v5','route_checkpoint_unit_v6','route_checkpoint_unit_v7']]
 files += [ROOT/'results'/selected/'sources/base_controller.sv',ROOT/'results'/selected/'sources/base_tb.sv']
 hashes={}
 for p in files:
  n=str(p.relative_to(ROOT));q=frozen/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);hashes[n]=sha(q)
 (frozen/'manifest.json').write_text(json.dumps({'status':'frozen','files':hashes,'dependencies':'CPU q1/q2 captured states and prior verified controller baseline remain in their existing verified archives; each new unit archive freezes actual label inputs.'},indent=2)+'\n')
 restored=sum(r['files']for r in receipts.values());delta={k:syn['3'][k]-old['utilization'][k]for k in syn['3']};saved=syn['1']['LUT']-syn['3']['LUT']
 report=dict(status='component_verified',full_checkpoint_status='incomplete',selected_implementation='serial duplicate comparison (candidate3)',selected_unit=['route_checkpoint_unit_v8','route_checkpoint_unit32_v5'],unit_checks_per_capacity={'route':31,'checkpoint':27},synthesis_candidates=syn,original_controller_utilization=old['utilization'],selected_delta_from_original_controller=delta,selected_LUT_saving_from_candidate1=saved,selected_LUT_saving_percent=100*saved/syn['1']['LUT'],actual_restored_files=restored,archives=len(names),source_files=len(hashes),source_manifest_sha256=sha(frozen/'manifest.json'),coverage_sha256=sha(coverage),event_comparison_sha256=sha(comparison),results={n:{'audit_sha256':sha(ROOT/'results'/n/'source_bound_audit.json'),'receipt':str(ROOT/'results'/(n+'_restore_20261025.json'))}for n in names},limitations='Component only. Real CPU paths/label inputs with registered mock owner/label services; cp_safe/topology/matching owner snapshot trusted. No system integration, full checkpoint, power-loss persistence, board performance or timing closure.')
 (ROOT/'results/route_checkpoint_20261025.json').write_text(json.dumps(report,indent=2)+'\n')
 text=f'''# 保存连接路径的 checkpoint 组件验证（2026-10-25）

发现并补齐了一类完整checkpoint缺口：原控制器reset会清除已提交连接的保存路径，恢复owner和标签后仍无法正确ripup。隔离组件新增固定格式导出、CRC32校验、暂存语义检查及双slot原子导入，保留原基线。

组件用两条真实CPU路径验证保存、控制器复位、恢复和共享ripup：554512、263946的引用计数从2降1再降0，ripup不读取label。owner/label仍是注册mock；这不等于真实AXI或完整系统checkpoint已完成。

每种8/32容量均通过31项路由检查及27项checkpoint检查，保留原25项回归。覆盖CRC/order/last、8种语义损坏、失败替换保持已发布路径、部分输入取消、导出背压期间丢失权限、部分暂存bank reset、空图像、普通请求退休。额外合成满长度路径覆盖最后一节点及重复检测；其拓扑有效性不在该组件验证范围。独立审计重算CRC并恢复owner操作序列。默认图像78字/312字节。

| 实现 | LUT | FF | 结果 |
|---|---:|---:|---|
| 算术索引、并行去重 | {syn['1']['LUT']:g} | {syn['1']['FF']:g} | 保留参考 |
| 固定slot选择、并行去重 | {syn['2']['LUT']:g} | {syn['2']['FF']:g} | LUT增加928，负结果保留 |
| 逐对去重扫描 | {syn['3']['LUT']:g} | {syn['3']['FF']:g} | 当前选择 |

三者默认32节点组件U280 OOC均零latch/blackbox/BRAM/DSP。三者两容量的完整单元事件流字节一致，表示这些场景语义保持，不是周期或穷举等价。第三版较首版减少{saved:g} LUT（{100*saved/syn['1']['LUT']:.3f}%）。原无checkpoint控制器为2144 LUT/2924 FF，新增功能仍增加{delta['LUT']:g} LUT/{delta['FF']:g} FF，开销较高，尚不适合宣称系统收益。后续考虑缓存元数据、减少暂存多读口及双bank BRAM结构，须再实测。

逐对扫描以较多校验周期换取比较器减少；最坏两slot校验约2×((7+P)+P×(P-1)/2)，P=32时1070个扫描周期，另加流传输和背压。此为结构上限说明，不是板卡实测。

{len(names)}个结果归档共{restored}文件已实际恢复并重审，audit逐字节一致，{len(hashes)}源文件冻结；源、输入、三个综合版本与负结果保留。

完整checkpoint尚缺什么：

1. 将路径接口接入route adapter和统一系统围栏，以实际AXI owner及标签同时保存/复位/恢复，验证无并发更新。
2. 用同一checkpoint身份绑定owner primary/pool/allocator、design创建/children cache、history/价格、标签页/目录和配置描述；当前authority仍q1六行、标签328条外部可信流。
3. 恢复query last_sequence、epoch及成功/尝试版本下限；当前last_sequence随reset清零，只有恢复路径不能防止旧序号重新接受。
4. 明确frontier/递归/在途查询的重启边界或完整序列化，落实全局原子发布；未知页默认值/旧prev语义、价格真实变更、回绕/容量回收与耐掉电仍缺。

逐项源证据及八类状态义务见`checkpoint_coverage_20261025.json`，协议及运行命令见`hardware/variants/route_checkpoint_v1/CONTRACT.md`。当前外层cp_safe、拓扑与owner快照一致性仍由可信调用方保证，没有系统集成、place/route/Fmax或板卡结论。研究goal继续active。
'''
 (ROOT/'results/route_checkpoint_20261025.md').write_text(text)
 prefix=f'''# 保存路径checkpoint组件通过，完整checkpoint继续推进（2026-10-25，优先历史）

详见 results/route_checkpoint_20261025.md/.json、checkpoint_coverage_20261025.json 和 hardware/variants/route_checkpoint_v1/CONTRACT.md。新增两slot路径CRC32导出、逐项/逐对语义校验和原子导入；8/32容量各31路由+27checkpoint检查，真实CPU两同网路径在控制器reset后恢复并ripup共享refs2→1→0，未读label。注册mock后端，尚未接真实AXI/统一围栏，cp_safe和同一owner快照由调用方保证。

三组件OOC LUT12897/13825/12061，选逐对扫描5751FF，零latch/blackbox/BRAM/DSP。固定slot选择负结果保留；较首版减836LUT，但较原2144LUT控制器仍增9917，资源开销较高。三版本两容量事件字节一致，另增满长度合成边界检查；非周期等价/系统资源/板卡性能证明。11归档373文件实际恢复复审一致，{len(hashes)}源冻结。

下一优先优化暂存多读口开销并接入系统围栏/真实AXI一致保存恢复；完整checkpoint必须覆盖owner/allocator、design/cache、history/价格、labels/目录、配置、journal和query序号/版本下限。last_sequence当前reset清零，不能只恢复路径；frontier重启边界、未知页/旧prev、真实价格/回绕/容量/耐掉电/板卡仍缺。原研究目标保持，goal active。以下保留历史。

'''
 assert restored==373
 for name in ['AGENTS.md','NEXT_STEPS.md','README.md','EXPERIMENTS.md','INTERFACES.md']:
  p=ROOT/name;p.write_text(prefix+p.read_text())
 print(json.dumps({'status':'component_verified','full_checkpoint':'incomplete','archives':len(names),'restored_files':restored,'sources':len(hashes),'LUT':syn['3']['LUT'],'FF':syn['3']['FF']}))
if __name__=='__main__':main()
