#!/usr/bin/env python3
"""Plot the six audited supplemental order permutations separately from original7."""
import argparse
import base64
from collections import Counter
import csv
import html
import itertools
import json
from pathlib import Path
import statistics
import sys
from check_vitis_kernel import digest, require
from check_training_order_control_v1 import summarize

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT/'results/training_order_control_audit_20261029_v1.json'
PROOF = ROOT/'results/training_order_control_integrity_20261030_v1.json'
CONDITIONS = ['csr/direct', 'compact/expanded', 'compact/direct']
COLORS = ['#356b9e', '#2d8b75', '#b95c39']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'results/figures/training_order_control_20261030_v1')
    out = parser.parse_args().output.resolve(); require(not out.exists(), 'Refuse overwrite')
    report = json.loads(REPORT.read_text()); proof = json.loads(PROOF.read_text())
    require(report['status'] == 'all_six_order_permutations_18_complete_training_inclusive_workers_independently_audited' and
            (report['completed_blocks'],report['completed_workers']) == (6,18), 'Incomplete supplemental experiment')
    require(proof['status'] == 'six_permutation_cpu_final_report_and_all_block_bindings_independently_rehashed' and
            proof['report_sha256'] == digest(REPORT), 'Wrong integrity gate')
    files = dict(proof['files'])
    for name, checksum in files.items(): require(digest(name) == checksum, 'Changed original evidence '+name)
    summary, paired = summarize(report['workers'])
    require(summary == report['summaries'] and paired == report['paired_comparisons'], 'Different recomputed statistics')
    orders = report['orders']
    require(len(orders) == 6 and set(map(tuple,orders)) == set(itertools.permutations(range(3))), 'Incomplete balanced orders')
    require(all(Counter(order.index(i) for order in orders) == {0:2,1:2,2:2} for i in range(3)), 'Unbalanced positions')
    lookup = {(w['repeat'], w['condition']['mode']+'/'+w['condition']['execution']):w for w in report['workers']}
    require(len(lookup) == 18, 'Missing/duplicate workers')
    rows = []
    for block, order in enumerate(orders):
        for index, condition in enumerate(CONDITIONS):
            w = lookup[block,condition]
            rows.append(dict(block=block+1, condition=condition, position=order.index(index)+1,
                             application_seconds=w['application_wall_ms']/1000,
                             worker_process_seconds=w['worker_process_wall_ms']/1000))
    ratios = [dict(block=i+1, numerator=p['numerator'], denominator=p['denominator'], elapsed_ratio=v)
              for p in paired for i,v in enumerate(p['ratios_by_repeat'])]
    out.mkdir(parents=True)
    def csv_write(name, data):
        with (out/name).open('x',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    csv_write('workers.csv', rows); csv_write('paired_ratios.csv', ratios)
    csv_write('execution_order.csv', [dict(block=i+1, first=CONDITIONS[o[0]], second=CONDITIONS[o[1]], third=CONDITIONS[o[2]]) for i,o in enumerate(orders)])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    import numpy
    fig, axes = plt.subplots(1,2,figsize=(11,5.3))
    fig.subplots_adjust(left=.08,right=.98,bottom=.25,top=.80,wspace=.32)
    for i,c in enumerate(CONDITIONS):
        values=[r['application_seconds'] for r in rows if r['condition']==c]
        axes[0].scatter([i+(b-2.5)*.05 for b in range(6)],values,color=COLORS[i],s=30)
        median=statistics.median(values);axes[0].plot([i-.25,i+.25],[median,median],color=COLORS[i],lw=3)
        axes[0].annotate(f'{median:,.1f} s',(i,median),xytext=(0,12),textcoords='offset points',ha='center',fontsize=9)
    axes[0].set_xticks(range(3),['CSR\ndirect','Compact\nexpanded','Compact\ndirect'])
    axes[0].set_ylim(0,1800);axes[0].set_ylabel('Application elapsed time (s)');axes[0].set_title('All 18 workers; bars mark medians')
    for p in paired:
        color=COLORS[CONDITIONS.index(p['numerator'])]
        axes[1].plot(range(1,7),p['ratios_by_repeat'],'o-',color=color,label=p['numerator'])
        axes[1].axhline(p['median_paired_ratio'],color=color,linestyle=':',lw=1)
    axes[1].axhline(1,color='#555',ls='--',lw=1);axes[1].set_ylim(.8,1.6);axes[1].set_xticks(range(1,7))
    axes[1].set_xlabel('Paired block');axes[1].set_ylabel('Elapsed ratio to CSR / direct');axes[1].legend(frameon=False)
    axes[1].set_title('Six within-block ratios per comparison')
    for ax in axes:ax.grid(axis='y',alpha=.2)
    fig.suptitle('Supplemental CPU order control: six permutations, kept separate from original seven blocks',fontsize=11)
    fig.text(.08,.07,'Each worker includes fresh preparation and TWO complete 1,062-net batches; compact includes template training.\nShared host/cache; 14-site model. No cold-cache, confidence-interval or causal-effect claim.\nExcludes acquisition, device transfer and physical readback. These are CPU results, not FPGA speedups.',fontsize=8.5)
    for ext in ['png','svg','pdf']:fig.savefig(out/('application_and_ratios.'+ext),dpi=180)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.5));fig.subplots_adjust(left=.12,right=.98,bottom=.20,top=.87)
    ax.imshow(orders,cmap=ListedColormap(COLORS),vmin=0,vmax=2,aspect='auto')
    for i,order in enumerate(orders):
        for j,index in enumerate(order):ax.text(j,i,CONDITIONS[index],ha='center',va='center',color='white',fontsize=10)
    ax.set_xticks(range(3),['First','Second','Third']);ax.set_yticks(range(6),range(1,7));ax.set_ylabel('Block')
    ax.set_title('Verified six-permutation execution order')
    fig.text(.12,.055,'Each condition occurs twice at each position. Balanced order does not isolate shared-host or cache effects.',fontsize=8)
    for ext in ['png','svg','pdf']:fig.savefig(out/('execution_order.'+ext),dpi=180)
    plt.close(fig)
    analysis=dict(status='six_permutation_CPU_supplement_plotted_without_pooling', rows=rows, paired_comparisons=paired,
                  orders=orders, limitations=report['limitations'], experiment_complete=False)
    (out/'analysis.json').write_text(json.dumps(analysis,indent=2)+'\n')
    body='<meta charset="utf-8"><title>CPU 顺序控制补充实验</title><style>body{font:16px/1.6 sans-serif;max-width:1100px;margin:30px auto}img{max-width:100%}</style><h1>CPU 顺序控制补充实验</h1><p>6 组、18 次完整运行；六种排列各一次，与原 7 组分别报告。完整 FPGA 实验尚未完成。</p>'
    for p in paired:body+=f'<p>{html.escape(p["numerator"])} / CSR 配对应用耗时比中位数：<b>{p["median_paired_ratio"]:.6f}</b>。小于 1 表示应用耗时较少。</p>'
    for name in ['application_and_ratios.png','execution_order.png']:
        body+='<img alt="'+name+'" src="data:image/png;base64,'+base64.b64encode((out/name).read_bytes()).decode()+'">'
    body+='<p>每次包含新输入准备和两批各1062网路由；compact还包含新训练。共享主机、页缓存未隔离，仅覆盖14站点模型。位置均衡不是冷缓存控制；不推断因果效应或FPGA加速。计时不含采集、板卡传输或物理读回。</p><p>图表重读完整绑定证据并重算统计，没有重新执行完整语义审核。</p>'
    (out/'report.html').write_text(body)
    (out/'requirements.txt').write_text(f'matplotlib=={matplotlib.__version__}\nnumpy=={numpy.__version__}\n')
    for p in [REPORT, PROOF, Path(__file__).resolve(), ROOT/'scripts/check_training_order_control_v1.py', *out.iterdir()]:files[str(p)]=digest(p)
    manifest=dict(status=analysis['status'],files=files,rows=dict(workers=18,ratios=12,orders=6),
                  reproduction_command=[sys.executable,str(Path(__file__).resolve()),'--output','NEW_OUTPUT_DIRECTORY'],
                  dependencies='/tmp/A_graph_compression_recovery_20261025_v1/plot_dependencies_v1',experiment_complete=False)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(out)


if __name__ == '__main__':main()
