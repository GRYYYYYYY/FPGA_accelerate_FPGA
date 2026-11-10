from pathlib import Path
import json,shutil
from run_checkpoint_authority import ROOT,sha

def main():
 scratch=Path('/tmp/B_state_residency_offer_20261025');names=['query_checkpoint_v6','query_checkpoint_development_20261025','query_checkpoint_synth_v1','query_checkpoint_base_synth_v1'];evidence={}
 for n in names:
  p=scratch/n;a=json.loads((p/'source_bound_audit.json').read_text());r=json.loads((ROOT/'results'/f'{n}_restore_20261025.json').read_text());assert a['status']==r['status']=='passed'and r['audit_byte_identical']and sha(p/'source_bound_audit.json')==r['audit_sha256'];evidence[n]={'audit':a,'restore':r}
 frozen=ROOT/'results/query_checkpoint_sources_20261025';frozen.mkdir();sources={}
 paths=list((ROOT/'hardware/variants/query_checkpoint_v1').glob('*'))+[ROOT/'scripts'/n for n in ['run_query_checkpoint.py','audit_query_checkpoint.py','prepare_query_checkpoint_synth.py','audit_query_checkpoint_synth.py','audit_query_checkpoint_development.py','report_query_checkpoint.py','run_checkpoint_authority.py']]
 for p in paths:
  if p.is_file():shutil.copyfile(p,frozen/p.name);sources[str(p.relative_to(ROOT))]=sha(p)
 baseline=scratch/'authority_query_v4/sources/query_lifecycle.sv';shutil.copyfile(baseline,frozen/'baseline_query_lifecycle.sv');bs=sha(baseline);assert bs==evidence['query_checkpoint_v6']['audit']['baseline_sha256']
 (frozen/'manifest.json').write_text(json.dumps({'status':'passed','sources':sources,'baseline':{'path':str(baseline),'frozen':'baseline_query_lifecycle.sv','sha256':bs}},indent=2)+'\n')
 coverage={'status':'incomplete','validated':['native query ledger export/import of sequence_seen,sequence and context/dirty state','40-byte identity-bound canonical CRC32 image, strict stream and atomic publish','same-lifetime sequence rollback and clean-over-dirty rollback rejected','cold reset then trusted image import rejects consumed sequence','empty image, sequence exhaustion, drift/permission/cancel/backpressure and staged failure'], 'missing':['full-query AXI/system lease integration of this new interface','single checkpoint descriptor binds owner/path/labels/design/history/price/config/journal/query ledger','snapshot rotation and warm nonzero-owner full-query recovery','durable recovery-attempt version/query lower bounds across cold reset','external boot admission fence until every state restore completes','unknown pages/stale prev/frontier policy, epoch rollover and real price changes','authenticated/immutable snapshots, durable atomic publication and board performance'], 'prior_integrated_query':'results/authority_query_20261025.json','distinction':'Version/query/price equality in this component is not durable recovery-attempt monotonicity. Cold-reset local floors do not prevent an older trusted same-generation image.'}
 util=evidence['query_checkpoint_synth_v1']['audit']['utilization'];base=evidence['query_checkpoint_base_synth_v1']['audit']['utilization'];files=sum(e['restore']['files']for e in evidence.values());delta={k:util[k]-base[k]for k in util}
 report={'status':'passed','research_goal':'active','selected':'query_checkpoint_v6','evidence':evidence,'coverage':coverage,'component_utilization':util,'baseline_utilization':base,'delta':delta,'archive_files':files,'frozen_source_files':len(sources)+1,'sources':sources,'baseline_sha256':bs,'basic_check':'python3 scripts/run.py check passed'}
 (ROOT/'results/query_checkpoint_20261025.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'results/query_checkpoint_coverage_20261025.json').write_text(json.dumps(coverage,indent=2)+'\n')
 md=f'''# 查询序号与上下文 checkpoint 组件（2026-10-25）

选定 query_checkpoint_v6，原生 query_lifecycle 新增10字/40字节CRC32图像，保存sequence_seen、last_sequence、上下文design/version/query/price和label_state_dirty，并绑定调用方active_generation。原控制器冷复位将last_sequence清零，路径checkpoint也未保存该状态；测试先展示冷复位后未导入即接受旧序号2，再验证导入后序号2/1被拒绝且没有任何后端请求，更大序号3正常完成。

14次原生查询、27次checkpoint检查，7次冷复位。正常查询走注册service/search/route模型，每次实际7/1/1请求；拒绝查询三个后端请求数均0。checkpoint期间不接受普通命令且没有后端请求，回复与导出背压保持。空图像、最大序号ffffffff耗尽、CRC、magic/format/design/generation高32位/version/query/price/保留位、seen/sequence规范、index/last、部分导入权限丢失、generation漂移和取消导出均验证。源码/实际命令和S/M流由独立Python状态机核验，CRC由zlib计算；失败不替换已发布ledger。

导入只在完整接收且CRC/身份/语义通过后，单沿发布所有ledger。当前已见序号不能回退；已有dirty不能被旧clean图像清除。后者是实际测试发现的反例：query_checkpoint_v2在新负例中返回0而预期1，旧clean导入使dirty丢失；已修复并保存失败源/日志。开发包另保留5个中间版本：v4行为测试通过，但ENV监视在DONE退休期用下一编号记录，被首次独立审计拒绝；选定监视排除DONE，未掩盖数据面差异。

固定格式：magic51435031、格式1、design低/高、generation低/高、version、query/price/seen/dirty打包、last_sequence、保留0。未见序号时last_sequence必须0，已见时非零。generation/design/version非零；version/query/price与active相等，非全局单调恢复下限。CRC是传输校验，不是认证。已有sequence上下文与active不一致时导出拒绝，避免用当前上下文覆盖旧上下文。

Vivado2022.2 U280 原生组件OOC：{int(util['LUT'])}LUT/{int(util['FF'])}FF/0BRAM/0DSP；原控制器{int(base['LUT'])}LUT/{int(base['FF'])}FF，增{int(delta['LUT'])}LUT/{int(delta['FF'])}FF。两者均零latch/blackbox。64.022s与36.391s为工具执行时间，不能解释为硬件性能；无完整系统资源/时序/板卡收益。两个临时MCP会话已关闭。

四归档{files}文件均实际移走原目录、解压并独立复审，审计JSON逐字节一致；{len(sources)+1}当前源/依赖（含原控制器）冻结于results/query_checkpoint_sources_20261025。基础check通过，旧完整查询/公共基线保持不变。完整机器证据见query_checkpoint_20261025.json；CONTRACT位于hardware/variants/query_checkpoint_v1。

运行：`python3 hardware/variants/query_checkpoint_v1/build.py`，`python3 scripts/run_query_checkpoint.py /tmp/B_state_residency_offer_20261025/新目录`，`python3 scripts/audit_query_checkpoint.py 同目录`。综合入口prepare_query_checkpoint_synth.py，新模块或追加--base比较原控制器。

尚未将新接口接入完整query top；真实AXI证据仍属于上一轮不含该接口的authority_query系统。cp_safe和active_generation由可信调用方保证，必须先恢复匹配的owner/path/labels等全部状态并持有排他许可。恢复启动还必须持续关闭admit，直到所有匹配状态和ledger恢复完成；单靠cp_valid不能消除复位至导入前窗口。组件冷复位也会清本地单调下限，因此不阻止更早的可信同代图像重放。恢复协调器attempt_version/query下限没有序列化，本轮只恢复query ledger及上下文。

下一优先统一checkpoint描述/发布/快照轮换，把该ledger与路径、owner、labels/目录、design/history/价格、配置/journal绑定，再接完整系统冷恢复门控并验证warm非零owner。未知页/旧prev/frontier、实际价格变化/epoch回绕、容量与序号耗尽换代、耐掉电、认证/不可变和板卡仍缺。研究目标保持active。
'''
 (ROOT/'results/query_checkpoint_20261025.md').write_text(md)
 prefix=f'''# 查询序号checkpoint组件通过（2026-10-25，优先历史）

详见 results/query_checkpoint_20261025.md/.json、query_checkpoint_coverage_20261025.json 和 hardware/variants/query_checkpoint_v1/CONTRACT.md。新增原生query_lifecycle的10字CRC32快照，保存sequence_seen/last_sequence、design/version/query/price与dirty，绑定generation64。14查询/27checkpoint、实际S/M流和独立状态机/zlib审核通过；冷复位未导入会接受旧序号，正确导入后拒绝且无后端请求。

CRC/身份/规范/次序/last、部分导入、权限/漂移、背压取消、空图像/序号耗尽和原子发布验证。真实旧clean导入清dirty反例已修复：同生命周期sequence及dirty不能回退。开发失败/监视编号审计失败保留。原生组件OOC {int(util['LUT'])}LUT/{int(util['FF'])}FF，比原{int(base['LUT'])}/{int(base['FF'])}增{int(delta['LUT'])}/{int(delta['FF'])}，均0BRAM/DSP/latch/blackbox。四归档{files}文件实际恢复复审一致，{len(sources)+1}当前源冻结。

本轮后端为注册mock，新接口尚未接完整query/AXI；上一轮完整系统基线保持。version/query/price只做上下文相等，恢复协调器attempt下限仍未序列化；cold-reset本地floor不能阻止更早可信图像重放。恢复前必须外层admit门控到全部同代状态恢复完毕。下一优先统一描述/发布/快照轮换及完整冷恢复集成，再warm非零owner；未知页/旧prev/frontier、价格/回绕/容量/耐掉电/板卡仍缺。goal active。以下保留历史。

'''
 for name in ['AGENTS.md','README.md','NEXT_STEPS.md','EXPERIMENTS.md','INTERFACES.md']:
  p=ROOT/name;p.write_text(prefix+p.read_text())
 print(json.dumps({'status':'passed','archives':4,'archive_files':files,'frozen_sources':len(sources)+1,'utilization':util,'delta':delta}))
if __name__=='__main__':main()
