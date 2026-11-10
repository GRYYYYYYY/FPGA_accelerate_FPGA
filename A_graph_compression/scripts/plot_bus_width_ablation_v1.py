#!/usr/bin/env python3
"""Export source-bound CSVs and figures; separate HLS estimates from routed results."""
import csv
import importlib.metadata
import json
import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from check_vitis_kernel import digest,require

ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'results/figures/bus_width_ablation_20261025_v1';out.mkdir(parents=True,exist_ok=False)
    paths=[ROOT/'results/compressed_batch_bus_width_ablation_20261025_v1.json',
           ROOT/'results/search_packet_width64_physical_audit_20261025_v2.json',
           ROOT/'results/search_kernel_physical_csr_audit_20261024_v1.json']
    ablation,current,baseline=[json.loads(p.read_text()) for p in paths]
    rows=ablation['rows'];require([r['configuration'] for r in rows]==['default','packet64','all64'],'Different ablation matrix')
    require(all(r['pointer_count']==44 and r['declared_payload_bytes']==946497192 for r in rows),'Different full44 payload')
    with (out/'integrated_hls.csv').open('x',newline='') as f:
        writer=csv.writer(f);writer.writerow(['configuration','stage','LUT','FF','estimated_clock_ns','effective_budget_ns','budget_gap_ns'])
        for r in rows:writer.writerow([r['configuration'],'HLS_estimate',r['resources']['LUT'],r['resources']['FF'],r['estimated_clock_ns'],3.65,r['effective_clock_budget_gap_ns']])
    routed=[baseline['modes']['csr']['stages']['routed'],current['stages']['routed']]
    with (out/'search_core_postroute.csv').open('x',newline='') as f:
        writer=csv.writer(f);writer.writerow(['configuration','stage','LUT','FF','setup_WNS_ns'])
        for name,r in zip(['default','packet64'],routed):writer.writerow([name,'Vivado_postroute_OOC',r['resources']['LUT'],r['resources']['FF'],r['timing']['setup']['slack_ns']])
    plt.rcParams.update({'font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    colors=['#7b8794','#4c78a8','#2a9d8f']
    fig,axes=plt.subplots(1,2,figsize=(10,4.2),layout='constrained')
    labels=['Default','Packet cap 64','All caps 64']
    bars=axes[0].bar(labels,[r['resources']['LUT']/1e6 for r in rows],color=colors)
    axes[0].bar_label(bars,fmt='%.3f',padding=3);axes[0].set_ylim(0,2.3)
    axes[0].axhline(1.303680,color='#b44c43',linestyle='--',label='Whole-device LUT reference')
    axes[0].set_ylabel('Estimated LUTs (millions)');axes[0].legend(fontsize=8)
    bars=axes[1].bar(labels,[r['estimated_clock_ns'] for r in rows],color=colors)
    axes[1].bar_label(bars,fmt='%.3f',padding=3);axes[1].set_ylim(0,5.3)
    axes[1].axhline(3.65,color='#b44c43',linestyle='--',label='Effective HLS budget: 3.650 ns')
    axes[1].set_ylabel('Estimated clock period (ns)');axes[1].legend(fontsize=8)
    fig.suptitle('Integrated full44 batch: HLS estimates only\nAll three configurations miss the effective clock budget',fontsize=12)
    for suffix in ['png','svg','pdf']:fig.savefig(out/('integrated_hls.'+suffix),dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9,4.2),layout='constrained')
    labels=['Default','Packet cap 64']
    bars=axes[0].bar(labels,[r['resources']['LUT']/1000 for r in routed],color=colors[:2])
    axes[0].bar_label(bars,fmt='%.3f',padding=3);axes[0].set_ylim(0,125)
    axes[0].set_ylabel('Post-route LUTs (thousands)')
    bars=axes[1].bar(labels,[r['timing']['setup']['slack_ns'] for r in routed],color=colors[:2])
    axes[1].bar_label(bars,fmt='%.3f',padding=3);axes[1].axhline(0,color='#b44c43',linestyle='--')
    axes[1].set_ylim(-1.65,.2);axes[1].set_ylabel('Post-route setup WNS (ns)')
    fig.suptitle('Search-only CSR core: Vivado 2022.2 OOC post-route\nBoth miss timing; DRC/methodology gates are not all clear',fontsize=12)
    for suffix in ['png','svg','pdf']:fig.savefig(out/('search_core_postroute.'+suffix),dpi=180)
    plt.close(fig)
    caption='''# Bus-width ablation figure scope

`integrated_hls` compares the same integrated full44 batch at HLS synthesis only.
The all64 setting retains native 32-bit ports. It reduces the LUT estimate by
77.4807%, but its 3.715 ns clock estimate still exceeds the 3.650 ns effective
budget by 0.065 ns. Falling below a whole-device LUT reference does not establish
platform fit; shell resources and mapped implementation remain unverified.

`search_core_postroute` is a separate, smaller search-only CSR design. Its LUT
count changes from 105,963 to 81,235 and WNS from -1.389 ns to -0.382 ns. Both
designs still miss timing; neither is presented as an accepted platform design.
These figures do not compare resource counts across the two integration scopes.

No board throughput, bandwidth, power, acceleration, or statistical error bars
are inferred from these deterministic synthesis/implementation reports. Source
audits are recorded in manifest.json; plotting does not re-run semantic audits.
'''
    (out/'CAPTION.md').write_text(caption)
    packages={p:importlib.metadata.version(p) for p in ['matplotlib','numpy','contourpy','cycler','fonttools','kiwisolver','packaging','pillow','pyparsing','python-dateutil','six']}
    (out/'requirements.txt').write_text(''.join(f'{k}=={v}\n' for k,v in sorted(packages.items())))
    files={str(p):digest(p) for p in [*paths,Path(__file__).resolve(),*out.iterdir()] if p.is_file()}
    report=dict(status='source_bound_hls_and_postroute_ablation_figures_exported_separate_scopes',files=files,packages=packages,
                limits=['Existing audit metadata visualized, no new synthesis, RTL or board result',
                        'HLS timing and physical setup WNS are distinct quantities'])
    temporary=out/'manifest.tmp'
    with temporary.open('x') as f:json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,out/'manifest.json');print(out)
if __name__=='__main__':main()
