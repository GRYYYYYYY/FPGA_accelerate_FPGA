#!/usr/bin/env python3
"""Export paired HLS estimates and a separate measured OOC timing comparison."""
import csv,json,importlib.metadata
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from check_vitis_kernel import digest,require
from run_compact_native_stack_recovery_v1 import atomic
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'results/figures/csr_compact_and_physopt_20261025_v1';out.mkdir(parents=True,exist_ok=False)
    names=['compressed_batch_synthesis_review_20261025_v1','compressed_batch_compact_synthesis_review_20261025_v1','compressed_batch_bus64_synthesis_review_20261025_v1','compressed_batch_compact_bus64_synthesis_review_20261025_v1','search_kernel_physical_csr_audit_20261024_v1','search_packet_width64_physical_audit_20261025_v2','search_packet64_physopt_audit_20261025_v1','compressed_batch_csr_compact_global64_comparison_20261025_v1']
    paths=[ROOT/'results'/(n+'.json') for n in names];reports=[json.loads(p.read_text()) for p in paths]
    hls=[]
    for label,mode,r in zip(['Default','Default','Global cap 64','Global cap 64'],['CSR','Compact','CSR','Compact'],reports[:4]):
        require(len(r['source_arguments'])==45 and sum(a['pointer'] for a in r['source_arguments'])==44 and not r['rtl_verified'],'Wrong integrated scope')
        hls.append(dict(configuration=label,mode=mode,LUT=r['resources']['LUT'],FF=r['resources']['FF'],estimated_clock_ns=r['estimated_clock_ns'],effective_budget_ns=3.65,stage='HLS_estimate'))
    routed=[reports[4]['modes']['csr']['stages']['routed'],reports[5]['stages']['routed']]
    physical=[dict(configuration=n,LUT=r['resources']['Total LUTs'],FF=r['resources']['FFs'],WNS_ns=r['timing']['setup']['slack_ns'],stage='search_CSR_OOC_postroute') for n,r in zip(['Default','Packet cap 64'],routed)]
    r=reports[6];require(r['route']['nets with routing errors']==0 and not r['quality_gates']['internal_timing_met'],'Wrong physical result')
    physical.append(dict(configuration='Packet64 + physopt',LUT=r['resources']['Total LUTs'],FF=r['resources']['FFs'],WNS_ns=r['after']['setup']['slack_ns'],stage='search_CSR_OOC_postroute'))
    for name,rows in [('integrated_hls.csv',hls),('search_postroute.csv',physical)]:
        with (out/name).open('x',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    plt.rcParams.update({'font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    colors=['#406c9b','#ce8054'];fig,axes=plt.subplots(1,2,figsize=(9.5,4.4),layout='constrained')
    for i,mode in enumerate(['CSR','Compact']):
        rows=[r for r in hls if r['mode']==mode];xs=[x+(i-.5)*.34 for x in [0,1]]
        b=axes[0].bar(xs,[r['LUT']/1e6 for r in rows],width=.32,label=mode,color=colors[i]);axes[0].bar_label(b,fmt='%.3f',padding=3)
        b=axes[1].bar(xs,[r['estimated_clock_ns'] for r in rows],width=.32,label=mode,color=colors[i]);axes[1].bar_label(b,fmt='%.3f',padding=3)
    for ax in axes:ax.set_xticks([0,1],['Default','Global cap 64'])
    axes[0].set_ylabel('Estimated LUTs (millions)');axes[0].set_ylim(0,2.3);axes[0].legend()
    axes[1].set_ylabel('Estimated clock period (ns)');axes[1].set_ylim(0,5.2);axes[1].axhline(3.65,color='#a43b3b',ls='--',label='Effective budget: 3.650 ns');axes[1].legend(fontsize=8)
    fig.suptitle('Integrated full44 batch: paired HLS estimates\nBoth graph modes miss the effective clock budget',fontsize=12)
    for extension in ['png','svg','pdf']:fig.savefig(out/('integrated_paired_hls.'+extension),dpi=180)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.4,4.5),layout='constrained');b=ax.bar([r['configuration'] for r in physical],[r['WNS_ns'] for r in physical],color=['#7b8794','#406c9b','#4a9682']);ax.bar_label(b,fmt='%.3f',padding=4);ax.axhline(0,color='#a43b3b',ls='--');ax.set_ylim(-1.65,.15);ax.set_ylabel('Post-route setup WNS (ns)');ax.set_title('Search-only CSR: Vivado 2022.2 OOC post-route\nAll three miss timing; DRC/methodology gates remain uncleared')
    for extension in ['png','svg','pdf']:fig.savefig(out/('search_postroute_timing.'+extension),dpi=180)
    plt.close(fig)
    (out/'CAPTION.md').write_text('Integrated charts show HLS estimates for two graph modes under default and global64 interface settings, at unchanged full44 capacity. Global64 retains native32 interfaces. These are not mapped platform resources. The separate search-only CSR timing chart shows actual OOC routed results; the physopt trial improves WNS by66ps to-0.316ns but fails timing, DRC and methodology acceptance. Do not compare resources across integration scopes or infer board throughput, bandwidth, power or acceleration. Source audits are visualized; semantic auditors are not rerun by plotting.\n')
    packages={n:importlib.metadata.version(n) for n in ['matplotlib','numpy']};(out/'requirements.txt').write_text(''.join(f'{k}=={v}\n' for k,v in packages.items()))
    files={str(p):digest(p) for p in [*paths,Path(__file__).resolve(),*out.iterdir()] if p.is_file()};atomic(out/'manifest.json',dict(status='paired_hls_and_separate_postroute_figures_exported_all_sources_bound',files=files,packages=packages,board_speedup_claimed=False));print(out)
if __name__=='__main__':main()
