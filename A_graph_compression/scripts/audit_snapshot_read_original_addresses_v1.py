#!/usr/bin/env python3
"""Bind original pointer environments; preserve full vectors and avoid assuming batch semantics."""
import json
from pathlib import Path
import re
from check_vitis_kernel import digest,require

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
OUTPUT=ROOT/'results/snapshot_read_original_address_audit_20261029_v1.json'


def scalar(text,count):
    pattern=r'\[\[\[runtime\]\]\]\s*'+''.join(
        r'\[\[transaction\]\]\s*'+str(i)+r'\s+(0x[0-9a-fA-F]+)\s*\[\[/transaction\]\]\s*' for i in range(count))+r'\[\[\[/runtime\]\]\]\s*'
    match=re.fullmatch(pattern,text)
    require(match is not None,'Different scalar framing/transaction set')
    values=[int(v,16) for v in match.groups()]
    require(all(0<=v<2**64 for v in values),'Invalid pointer width')
    return values


def main():
    require(not OUTPUT.exists(),'Refuse overwrite')
    files={str(Path(__file__).resolve()):digest(__file__)}
    def load(path):
        files[str(path)]=digest(path);return json.loads(path.read_text())
    def bind(path,expected=None):
        actual=digest(path)
        if expected is not None:require(actual==expected,'Changed frozen evidence '+str(path))
        files[str(path)]=actual;return actual
    snapshot=BASE/'snapshot_rtl_local_project/solution/sim'
    parent=load(BASE/'snapshot_rtl_local_recovery/plan.json')
    original=ROOT/'data/derived/resident_snapshot_rtl_20261024_v1'
    snap_plan=load(original/'plan.json')
    candidate=BASE/'search_read_control_staging_cosim_project_v1/solution/sim'
    reference=ROOT/'build/search_packet_width64_rtl_20261025_v1/solution/sim'
    setup=load(ROOT/'results/search_read_control_staging_full_depth_setup_audit_20261025_v1.json')
    baseline=load(ROOT/'results/search_packet_width64_rtl_audit_20261025_v1.json')
    require(baseline['rtl_verified'] and baseline['cycles']==[2132461,12404],'Missing actual original search oracle')
    require(setup['transactions']==2 and setup['c_vector_files']==27 and len(setup['models'])==7,'Different read-control setup')
    scopes=[]
    for label,sim,source,top,count,bindings,aliases in [
        ('snapshot',snapshot,original/'source/search_resident_snapshot_top.cpp','search_resident_snapshot_top',30,snap_plan['files'],{'initial':'initial_r'}),
        ('read',candidate,BASE/'search_read_control_staging_hls_v1/source/search_kernel_top.cpp','search_kernel_top',2,setup['files'],{'image':'image_r','config':'config_r'})]:
        bind(source,bindings[str(source)])
        ports=re.findall(r'#pragma HLS INTERFACE m_axi port=(\w+) offset=slave bundle=(\w+) depth=(\d+)',source.read_text())
        require(len(ports)==13 and len({p[0] for p in ports})==13,'Different thirteen-pointer top interface')
        rows=[]
        for name,bundle,depth in ports:
            p=sim/'tv/cdatafile'/f'c.{top}.autotvin_{aliases.get(name,name)}.dat'
            expected=(parent['copied'] if label=='snapshot' else setup['files'])[str(p)]
            bind(p,expected);values=scalar(p.read_text(),count)
            rows.append(dict(port=name,bundle=bundle,declared_depth=int(depth),values=values,source=str(p)))
        tb=sim/'verilog'/f'{top}.autotb.v';bind(tb,(parent['copied'] if label=='snapshot' else setup['files'])[str(tb)])
        scopes.append(dict(label=label,transactions=count,pointers=13,pointer_vectors=rows,
                           zero_base_ports=[r['port'] for r in rows if all(v==0 for v in r['values'])]))
    actual={p.name:p for p in (candidate/'tv/cdatafile').glob('*.dat')}
    expected={p.name:p for p in (reference/'tv/cdatafile').glob('*.dat')}
    require(actual.keys()==expected.keys() and len(actual)==27,'Different complete read-control C-vector set')
    for name,p in actual.items():
        h=bind(p,setup['files'][str(p)])
        require(h==bind(expected[name],setup['files'][str(expected[name])]),'Full C-vector differs from accepted baseline')
        if str(expected[name]) in baseline['files']:require(h==baseline['files'][str(expected[name])],'Different accepted baseline vector')
    # Bind the relevant frozen algorithm sources for subsequent review. This
    # observation is not a formal proof that arbitrary pointer bases are legal.
    for folder,bindings,names in [(original/'source',snap_plan['files'],['search_resident_snapshot.hpp','search_key_words.hpp','search_node_occupancy.hpp','search_site_occupancy.hpp']),
                                  (BASE/'search_read_control_staging_hls_v1/source',setup['files'],['search_kernel.hpp'])]:
        for name in names:
            p=folder/name;bind(p,bindings[str(p)])
    for sim,bindings in [(candidate,setup['files']),(reference,baseline['files'])]:
        p=sim/'verilog/search_kernel_top.v';bind(p,bindings[str(p)])
    result=dict(status='original_snapshot13_and_read13_pointer_vectors_bound_full27_read_C_vectors_equal_actual_search_baseline',
                scopes=scopes,read_complete_c_vector_files=27,files=files,address_relocation_applied=False,
                full_snapshot_rtl_verified=False,staged_search_rtl_verified=False,
                decision='Retain each original environment and require all30/2 actual transactions and original complete output oracles.',
                limits=['Selected original source/vector/report bindings verified; this is not a re-audit of every inherited baseline artifact.',
                        'Zero base observations alone neither prove a null-control failure nor prove arbitrary-address equivalence.',
                        'Candidate full RTL remains required; no batch address wrapper is applied to these unrelated DUTs.'])
    with OUTPUT.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(result['status'])


if __name__=='__main__':main()
