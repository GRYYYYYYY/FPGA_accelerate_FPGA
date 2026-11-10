#!/usr/bin/env python3
"""Render all 21 audited full CPU runs, including their actual execution order."""
import argparse
import base64
from collections import Counter
import csv
import html
import importlib.metadata
import json
import math
from pathlib import Path
import statistics
import sys

from check_vitis_kernel import digest,require
from check_source_to_route_training_statistics_v2 import summarize,check_sequence
from supervise_search_axi_dpi_v3 import atomic

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'results/source_to_route_training_statistics_audit_20261027_v2.json'
INTEGRITY=ROOT/'results/source_to_route_training_statistics_integrity_20261029_v1.json'
CONDITIONS=['csr/direct','compact/direct','compact/expanded']
LABELS=['CSR / direct','Compact / direct','Compact / expanded']
COLORS=['#356b9e','#b95c39','#2d8b75']


def read_evidence():
    report=json.loads(REPORT.read_text());proof=json.loads(INTEGRITY.read_text())
    require(report['status']=='complete_source_to_route_statistics_audited' and report['completed_workers']==21,'Incomplete CPU result')
    require(proof['status']=='training_inclusive_seven_blocks_all_artifact_hashes_reread_and_statistics_recomputed' and proof['report_sha256']==digest(REPORT),'Wrong integrity evidence')
    files={**proof['files'],str(REPORT):digest(REPORT),str(INTEGRITY):digest(INTEGRITY)}
    for path,h in files.items():require(digest(path)==h,'Changed CPU evidence '+path)
    summaries,paired=summarize(report['workers'])
    require(summaries==report['summaries']==proof['summaries'] and paired==report['paired_comparisons']==proof['paired_comparisons'],'Changed paired statistics')
    paths=[Path(p) for p in report['artifacts'] if p.endswith('/plan.json')]
    require(len(paths)==1,'Ambiguous statistics plan')
    plan_path=paths[0];plan=json.loads(plan_path.read_text());base=plan_path.parent
    previous_end=0;orders=[];positions={};lookup={(w['repeat'],w['condition']['mode']+'/'+w['condition']['execution']):w for w in report['workers']}
    for repeat,order in enumerate(plan['block_orders']):
        submissions={};receipts={};block=base/f'block_{repeat:03d}'
        audit=json.loads((block/'audit.json').read_text())
        require(audit['status']=='all_source_to_route_integration_trials_audited' and audit['completed_workers']==3,'Partial block audit')
        for index,condition in enumerate(plan['conditions']):
            require(audit['summaries'][index]=={k:v for k,v in lookup[repeat,condition['mode']+'/'+condition['execution']].items() if k!='repeat'},'Worker differs from block evidence')
            for suffix,dest in [('submission',submissions),('receipt',receipts)]:
                path=block/f'worker_{index:03d}.{suffix}.json'
                require(audit['artifacts'][str(path)]==digest(path),'Unbound actual execution receipt')
                files[str(path)]=digest(path);dest[index]=json.loads(path.read_text())
        previous_end=check_sequence(order,submissions,receipts,plan['owner_pid'],plan['cpu'],previous_end)
        labels=[plan['conditions'][index]['mode']+'/'+plan['conditions'][index]['execution'] for index in order]
        orders.append(dict(block=repeat+1,position_1=labels[0],position_2=labels[1],position_3=labels[2]))
        for position,label in enumerate(labels):positions[repeat,label]=position+1
    require(len(orders)==7,'Incomplete execution matrix')
    rows=[]
    for repeat in range(7):
        for condition in CONDITIONS:
            w=lookup[repeat,condition];stages=w['stage_ms'];total=w['application_wall_ms'];native=stages['native_process_ms']
            require(0<native<total and all(type(v) in [int,float] and math.isfinite(v) and v>=0 for v in stages.values()),'Invalid stage timer')
            residual=total-sum(stages.values());require(residual>=0,'Overlapping stage accounting')
            rows.append(dict(block=repeat+1,condition=condition,execution_position=positions[repeat,condition],
                application_seconds=total/1000,worker_process_seconds=w['worker_process_wall_ms']/1000,
                cpu_router_subprocess_seconds=native/1000,outside_cpu_router_subprocess_seconds=(total-native)/1000,
                training_load_fit_freeze_seconds=sum(stages[k] for k in ['training_load_ms','training_fit_ms','training_freeze_ms'])/1000,
                unassigned_application_seconds=residual/1000))
    ratios=[dict(block=i+1,condition=p['numerator'],denominator=p['denominator'],elapsed_ratio=value) for p in paired for i,value in enumerate(p['ratios_by_repeat'])]
    table=[]
    for condition in CONDITIONS:
        records=[r for r in rows if r['condition']==condition];values=[r['application_seconds'] for r in records]
        table.append(dict(condition=condition,n=7,application_median_seconds=statistics.median(values),application_min_seconds=min(values),application_max_seconds=max(values),
          application_mean_seconds=statistics.mean(values),cpu_router_subprocess_mean_seconds=statistics.mean(r['cpu_router_subprocess_seconds'] for r in records),
          outside_cpu_router_subprocess_mean_seconds=statistics.mean(r['outside_cpu_router_subprocess_seconds'] for r in records),
          training_load_fit_freeze_median_seconds=statistics.median(r['training_load_fit_freeze_seconds'] for r in records)))
    counts={c:dict(sorted(Counter(positions[r,c] for r in range(7)).items())) for c in CONDITIONS}
    before=sum(positions[r,'compact/direct']<positions[r,'compact/expanded'] for r in range(7))
    return files,report,proof,rows,ratios,orders,table,dict(position_counts=counts,compact_direct_before_expanded_blocks=before,blocks=7,cpu=plan['cpu'],seed=plan['seed'])


def export_csv(path,rows):
    with path.open('x',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'results/figures/training_inclusive_cpu_20261029_v1')
    args=parser.parse_args();out=args.output.resolve();require(not out.exists(),'Refuse overwrite')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    files,report,proof,rows,ratios,orders,table,order_audit=read_evidence()
    out.mkdir(parents=True)
    for name,data in [('workers.csv',rows),('paired_ratios.csv',ratios),('execution_order.csv',orders),('summary.csv',table)]:export_csv(out/name,data)
    plt.rcParams.update({'font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11,4.9));fig.subplots_adjust(left=.08,right=.98,bottom=.24,top=.80,wspace=.32)
    for index,condition in enumerate(CONDITIONS):
        values=[r['application_seconds'] for r in rows if r['condition']==condition]
        offsets=[(r-3)*.035 for r in range(7)]
        axes[0].scatter([index+o for o in offsets],values,color=COLORS[index],s=32,zorder=3)
        med=statistics.median(values);axes[0].plot([index-.24,index+.24],[med,med],color=COLORS[index],lw=3)
        axes[0].annotate(f'{med:,.1f} s',(index,med),xytext=(0,13),textcoords='offset points',ha='center',fontsize=9)
    axes[0].set_xticks(range(3),['CSR\ndirect','Compact\ndirect','Compact\nexpanded']);axes[0].set_ylabel('Application elapsed time (s)');axes[0].set_ylim(0,1800);axes[0].set_title('All 21 complete workers; bars mark medians')
    for condition,color in zip(CONDITIONS[1:],COLORS[1:]):
        data=[r for r in ratios if r['condition']==condition]
        values=[r['elapsed_ratio'] for r in data]
        axes[1].plot(range(1,8),values,'o-',color=color,lw=1.4,ms=5,label=condition.replace('/',' / '))
        axes[1].axhline(statistics.median(values),color=color,ls=':',lw=1)
    axes[1].axhline(1,color='#555555',ls='--',lw=1);axes[1].set_ylim(.80,1.60);axes[1].set_xticks(range(1,8));axes[1].set_xlabel('Paired block');axes[1].set_ylabel('Elapsed ratio to CSR / direct');axes[1].set_title('Matched blocks; lower values take less time');axes[1].legend(frameon=False,fontsize=8)
    for ax in axes:ax.grid(axis='y',alpha=.2)
    fig.suptitle('CPU experiment: fresh training + captured-graph conversion + two full routing batches',fontsize=12,y=.96)
    fig.text(.08,.075,'Each worker routes 1,062 nets twice. Compact training uses 3,761 sources and reproduces 440 frozen templates.\nShared host/cache; partial 14-site model. Excludes Vivado acquisition, device transfer and physical readback.\nSeven observed points per condition; observed ranges are not confidence intervals. This is not FPGA performance.',fontsize=8.4)
    for ext in ['png','svg','pdf']:fig.savefig(out/('application_and_paired_ratios.'+ext),dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,5.2));fig.subplots_adjust(left=.08,right=.98,bottom=.25,top=.80,wspace=.36)
    outside=[r['outside_cpu_router_subprocess_mean_seconds'] for r in table];native=[r['cpu_router_subprocess_mean_seconds'] for r in table]
    axes[0].bar(range(3),outside,color='#aaaeb3',label='Outside CPU router subprocess')
    axes[0].bar(range(3),native,bottom=outside,color=COLORS,label='CPU router subprocess (two batches)')
    for i,r in enumerate(table):axes[0].text(i,r['application_mean_seconds']+24,f"{r['application_mean_seconds']:,.1f}",ha='center',fontsize=9)
    axes[0].set_xticks(range(3),['CSR\ndirect','Compact\ndirect','Compact\nexpanded']);axes[0].set_ylabel('Mean application elapsed time (s)');axes[0].set_ylim(0,1800);axes[0].set_title('Additive means from per-worker timers');axes[0].legend(frameon=False,fontsize=7.6,loc='upper left');axes[0].grid(axis='y',alpha=.2)
    matrix=[[CONDITIONS.index(row[f'position_{pos}']) for pos in [1,2,3]] for row in orders]
    axes[1].imshow(matrix,cmap=ListedColormap(COLORS),vmin=0,vmax=2,aspect='auto')
    short=['CSR direct','Compact direct','Compact expanded']
    for r,row in enumerate(matrix):
        for c,value in enumerate(row):axes[1].text(c,r,short[value],ha='center',va='center',fontsize=7.4,color='white')
    axes[1].set_xticks(range(3),['First','Second','Third']);axes[1].set_yticks(range(7),range(1,8));axes[1].set_ylabel('Block');axes[1].set_xlabel('Verified execution position');axes[1].set_title('Actual randomized order is unbalanced')
    fig.suptitle('Cost accounting and execution-order limits',fontsize=12,y=.96)
    fig.text(.08,.075,'Stage plot uses arithmetic means, not sums of stage medians. The CPU subprocess includes its own setup, routing and export.\nCompact/direct ran before compact/expanded in every block; CSR was first in 2 blocks and last in 5.\nOrder and cache carryover are not isolated. These observed differences do not establish an order-independent causal effect.',fontsize=8.4)
    for ext in ['png','svg','pdf']:fig.savefig(out/('cost_and_execution_order.'+ext),dpi=180)
    plt.close(fig)
    direct=report['paired_comparisons'][0];expanded=report['paired_comparisons'][1]
    analysis=dict(status='all21_audited_cpu_measurements_visualized_with_actual_execution_order',summaries=table,paired_comparisons=report['paired_comparisons'],execution_order_audit=order_audit,
       experiment_complete=False,board_or_fpga_speedup_claimed=False,source_semantics_reexecuted=False,
       limitations=proof['limits']+['The actual fixed-seed schedule is unbalanced: compact/direct precedes compact/expanded in all seven blocks; CSR is first twice and last five times. Order/cache carryover is not isolated.',
       'Stage chart uses additive means. No sum of stage medians is presented as an application total.',
       'No significance test or confidence interval is claimed from seven shared-host blocks. Every paired observation is retained.',
       'Plots rehash bound artifacts and recompute summary/paired/order arithmetic; they do not rerun the full routing semantic oracle.'])
    atomic(out/'analysis.json',analysis)
    def figure(name):
        raw=base64.b64encode((out/name).read_bytes()).decode('ascii');return '<img alt="'+name+'" src="data:image/png;base64,'+raw+'">'
    def esc(x):return html.escape(str(x))
    body='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>含训练的 CPU 路由实验实测结果</title><style>body{font:16px/1.6 sans-serif;max-width:1100px;margin:40px auto;padding:0 20px;color:#17212b}img{max-width:100%;height:auto}table{border-collapse:collapse;width:100%}th,td{padding:9px;border-bottom:1px solid #ddd;text-align:left}code{overflow-wrap:anywhere}h1{font-size:28px}</style><body>'
    body+='<h1>含训练的 CPU 路由实验实测结果</h1><p>实验结果补充，2026-10-29。完整 FPGA 实验尚未完成。</p>'
    body+='<p>21 个完整 worker、7 个配对组、3 个条件。每次从捕获图重新生成输入，并执行两批各 1,062 网的完整路由；两种 compact 条件均先用原 3,761 个训练源重新训练并精确复现 440 个冻结模板。所有原完整结果审核已通过。</p>'
    body+=f'<p>配对耗时比中位数：compact/direct 相对 CSR/direct 为 <strong>{direct["median_paired_ratio"]:.6f}</strong>，耗时增加 {(direct["median_paired_ratio"]-1)*100:.2f}%；compact/expanded 为 <strong>{expanded["median_paired_ratio"]:.6f}</strong>，耗时减少 {(1-expanded["median_paired_ratio"])*100:.2f}%。这是包含两批路由的 CPU 应用耗时观察，不能解释为 FPGA 加速。</p>'
    body+='<table><tr><th>条件</th><th>次数</th><th>应用中位数 / 秒</th><th>观测范围 / 秒</th></tr>'
    for r in table:body+=f'<tr><td>{esc(r["condition"])}</td><td>7</td><td>{r["application_median_seconds"]:.3f}</td><td>{r["application_min_seconds"]:.3f} – {r["application_max_seconds"]:.3f}</td></tr>'
    body+='</table>'+figure('application_and_paired_ratios.png')
    body+='<h2>执行顺序限制</h2><p>重新核对全部 21 份提交及退出回执后，实际顺序只有两种：CSR→compact/direct→compact/expanded（2 组），compact/direct→compact/expanded→CSR（5 组）。因此 compact/direct 在全部 7 组中先于 compact/expanded，CSR 从未处于第二位。随机顺序没有形成位置均衡；共享页缓存和前一个 worker 的影响未被隔离。结果不能支持与执行顺序无关的因果结论，也不能据此声称有冷缓存收益。</p>'
    body+=figure('cost_and_execution_order.png')
    body+='<h2>测量边界与复现</h2><p>计时包含 compact 新训练、捕获 TSV 转换、完整输入生成与两批 CPU 路由；不含 Vivado 采集、板卡传输和物理读回。前置完整性检查与事后语义审核位于 application 计时外、worker process wall 内。路由资源模型仅覆盖 14 个已物理验证的站点实例；未知资源没有据此扩大授权。内存继承峰值未作为独立 native-only 峰值画图。</p><p>图表显示全部观察值和配对比。观测范围不是置信区间；没有显著性或总体加速推断。阶段图使用逐 worker 差值的算术均值，使各段可相加；没有相加不同阶段的中位数。</p>'
    body+='<p>同目录包含 workers.csv（21 行）、paired_ratios.csv（14 行）、execution_order.csv（7 行）、summary.csv（3 行）、analysis.json、PNG/SVG/PDF 与 manifest.json。重建命令记录在 manifest 中，必须指定不存在的新输出目录。</p><p>原始统计报告 SHA256：<code>'+digest(REPORT)+'</code>；完整证据复核报告 SHA256：<code>'+digest(INTEGRITY)+'</code>。</p></body></html>'
    (out/'report.html').write_text(body)
    packages={n:importlib.metadata.version(n) for n in ['matplotlib','numpy']}
    (out/'requirements.txt').write_text(''.join(f'{k}=={v}\n' for k,v in packages.items()))
    for p in [Path(__file__).resolve(),ROOT/'scripts/check_source_to_route_training_statistics_v2.py',*out.iterdir()]:
        if p.is_file():files[str(p)]=digest(p)
    atomic(out/'manifest.json',dict(status=analysis['status'],files=files,packages=packages,rows=dict(workers=21,paired_ratios=14,execution_order=7,summary=3),
      reproduction_command=[sys.executable,str(Path(__file__).resolve()),'--output','NEW_OUTPUT_DIRECTORY'],
      existing_plot_dependencies='/tmp/A_graph_compression_recovery_20261025_v1/plot_dependencies_v1',experiment_complete=False))
    print(out)

if __name__=='__main__':main()
