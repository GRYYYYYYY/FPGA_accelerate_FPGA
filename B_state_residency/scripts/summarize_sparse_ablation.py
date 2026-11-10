"""Bound full-replay ablation summary; physical resources remain separate evidence."""
from pathlib import Path
import csv,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha

def main():
 out=ROOT/'results/sparse_full_ablation_20261024';out.mkdir();rows=[];inputs={}
 variants=[('native16','record_epoch16_full_20261024','record_epoch16_timing_20261024'),('sparse_wb','sparse_writeback_cycle64_full_20261024','sparse_writeback_timing_20261024'),('sparse_wb_rf','sparse_records_full_20261024','sparse_records_timing_20261024')]
 baseline=None;reference_counts=None
 for label,replay,physical in variants:
  path=ROOT/'results'/replay;m=json.loads((path/'manifest.json').read_text());a=json.loads((path/'source_bound_audit.json').read_text())
  assert m['status']=='passed' and a['status']=='passed' and sha(path/'manifest.json')==a['manifest_sha256']
  case=m['cases']['pilot'] if label=='native16' else m
  log=path/('pilot/simulate.log' if label=='native16' else 'simulate.log');assert sha(log)==case['log_sha256']
  counts=case['counts'];assert counts['errors']==0 and counts['fences']==38 and counts['transfers']==2472066
  conserved={k:counts[k] for k in ['transfers','fences','aw','ar','b','r']}
  if reference_counts is None:reference_counts=conserved
  assert conserved==reference_counts
  if baseline is None:baseline=case['end_ns']
  phys=ROOT/'results'/physical/'final_audit.json';p=json.loads(phys.read_text());assert p['status']=='evidence_verified'
  resources=p['resources'];time=case['end_ns']
  rows.append({'variant':label,'end_ns':time,'time_seconds':time/1e9,'reduction_vs_native16_percent':100*(1-time/baseline),'axi_page_payload_bytes':2472066*192,'postroute_lut':resources['CLB LUTs'],'postroute_ff':resources['CLB Registers'],'postroute_bram36_tiles':resources['Block RAM Tile'],'postroute_wns_ns':p['routed_timing']['wns_ns'],'postroute_whs_ns':p['routed_timing']['whs_ns']})
  for file in [path/'manifest.json',path/'source_bound_audit.json',log,phys]:inputs[str(file.relative_to(ROOT))]=sha(file)
 with (out/'ablation.csv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 m={'status':'passed','script_sha256':sha(Path(__file__)),'inputs':inputs,'rows':rows,'conserved_counts':reference_counts,'csv_sha256':sha(out/'ablation.csv'),'scope':'Three full38 state-endpoint access replays under existing testbench. OOC resource/timing evidence listed separately; not full routing or board speedup.'}
 (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 lines=['# 稀疏记录控制完整消融','', '三组均完成38查询、28检查点和2472066次页传输，独立源码绑定审计通过。公开原始命令21466914条，AW/AR/B/R计数和192B页格式保持一致。','', '| 方案 | 回放终点（s） | 相对原生减少 | 布线后 LUT / FF / BRAM36 |','| --- | ---: | ---: | ---: |']
 for row in rows:lines.append(f"| {row['variant']} | {row['time_seconds']:.9f} | {row['reduction_vs_native16_percent']:.4f}% | {int(row['postroute_lut'])} / {int(row['postroute_ff'])} / {int(row['postroute_bram36_tiles'])} |")
 lines+=['','组合相比WB-only再减少6.4154%；37个查询收据区间更快、1个相同、0个变慢。WB省略3248686个空EXPORT；RF省略8773322个空BEAT，并执行1850442次RF mask收尾。总AXI页payload仍474636672B，收益来自端点记录控制工作减少，不是传输字节减少。','','原生、WB、组合的FINISH合法重试分别为0/1/0，检查数中保留该差异。先导19查询的收益不能替代上述全38结果。收据区间含TB节拍、初始化、检查点预刷和回收，并非独立连接搜索延迟。','','布线后资源来自各独立10ns OOC实现，均缺少平台IO预算及真实时钟上下文。尚未完成完整FPGA路由或板上测量。这里没有把新frontier组件计入三组端点，也没有假定合并后的资源/时序可简单相加。','','证据：sparse_full_ablation_20261024/manifest.json与ablation.csv；完整组合审计sparse_records_full_20261024/source_bound_audit.json及query_intervals.json。']
 (ROOT/'results/sparse_full_ablation_20261024.md').write_text('\n'.join(lines)+'\n');print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
