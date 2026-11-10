"""Compile-only preflight or gated twelve-case checkpoint specialization tests."""
from pathlib import Path
import argparse
import importlib.util
import json
import re
import shutil
import struct
import subprocess
import time
import zlib
from run_checkpoint_authority import ROOT,BIN,sha

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
    parser=argparse.ArgumentParser();parser.add_argument('output');parser.add_argument('--compile-only',action='store_true');args=parser.parse_args()
    if not args.compile_only:
        q=json.loads(Path('/tmp/B_state_residency_offer_20261025/query_native_matrix_queue_v1/manifest.json').read_text())
        assert q['status']=='observed'and q['stage']=='complete','existing query matrix owns behavioral simulation slot'
    assert int(Path('/sys/fs/cgroup/memory.current').read_text())<=int(Path('/sys/fs/cgroup/memory.max').read_text())*.75
    out=Path(args.output).resolve();out.mkdir();tools=out/'tools';tools.mkdir()
    v=ROOT/'hardware/variants/checkpoint_edit_exclusion_v1'
    b=load(v/'build_tb.py','cp_edit_tb');source_builder=load(v/'build.py','cp_edit_sources')
    for mode in ['baseline','fixed']:
        for n,s in source_builder.sources(mode=='fixed').items():assert (v/mode/n).read_text()==s
    bundle=Path('/tmp/B_state_residency_offer_20261025/bundle_capture_v3/full_5/bundle')
    bm=json.loads((bundle/'manifest.json').read_text());image=(bundle/'query.bin').read_bytes()
    assert len(image)==40 and bm['query_words']==10 and zlib.crc32(image)==bm['query_crc32']
    paths=[Path(__file__),v/'build.py',v/'build_tb.py',v/'manifest.json',
           ROOT/'hardware/variants/query_checkpoint_v1/tb_query_checkpoint.sv',ROOT/'hardware/variants/query_warm_rebase_v1/tb_rebase.sv']
    bound={}
    for src in paths:
        rel=src.relative_to(ROOT);dst=tools/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);bound[str(rel)]=sha(src)
    shutil.copyfile(bundle/'manifest.json',tools/'bundle_manifest.json');(tools/'query.bin').write_bytes(image)
    m=dict(status='running',compile_only=args.compile_only,cases=[],bound=bound,query_sha256=sha(tools/'query.bin'),
           bundle_manifest_sha256=sha(tools/'bundle_manifest.json'),scope='Unmodified checkpoint/rebase compatibility scenarios plus separate native permission-loss and generic overlap scenarios. Modeled backend unit verification only; no full-system or timing proof.')
    def save():(out/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    save()
    try:
        for mode in ['baseline','default','exclusive']:
            for suite in ['checkpoint','rebase','native_cp','generic_overlap']:
                for rel,h in bound.items():assert sha(ROOT/rel)==h==sha(tools/rel)
                name=f'{mode}_{suite}';d=out/name;d.mkdir()
                src=v/('baseline'if mode=='baseline'else'fixed')/'query_lifecycle.sv';shutil.copyfile(src,d/'query_lifecycle.sv')
                tb,top,trace,marker=b.build(ROOT,mode,suite);(d/'tb.sv').write_text(tb)
                (d/'query.hex').write_text(''.join(f'{w:08x}\n'for w, in struct.iter_unpack('<I',image)))
                (d/'run.tcl').write_text('run 2ms\nquit\n')
                c=dict(mode=mode,suite=suite,status='running',top=top,trace=trace,marker=marker,commands=[],rtl_sha256=sha(d/'query_lifecycle.sv'),tb_sha256=sha(d/'tb.sv'))
                m['cases'].append(c);save()
                commands=[('compile',[BIN/'xvlog','--sv','query_lifecycle.sv','tb.sv']),('elaborate',[BIN/'xelab',top,'-s','cp_edit','--debug','typical','--mt','2'])]
                if not args.compile_only:commands.append(('simulate',[BIN/'xsim','cp_edit','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','events='+str(d/'events.txt')]))
                for stage,argv in commands:
                    start=time.monotonic()
                    with(d/(stage+'.stdout.log')).open('w')as log:proc=subprocess.run(list(map(str,argv)),cwd=d,stdout=log,stderr=subprocess.STDOUT,timeout=180)
                    c['commands'].append(dict(stage=stage,argv=list(map(str,argv)),exit_code=proc.returncode,elapsed_s=time.monotonic()-start,log_sha256=sha(d/(stage+'.stdout.log'))));save()
                    assert proc.returncode==0,(name,stage)
                if args.compile_only:c['status']='elaborated_not_simulated'
                else:
                    log=(d/'simulate.log').read_text();assert marker in log and '$finish called'in log and 'Fatal:'not in log and 'ERROR:'not in log
                    c.update(status='passed',trace_sha256=sha(d/trace),simulate_log_sha256=sha(d/'simulate.log'))
                save();print(name,c['status'],flush=True)
        if not args.compile_only:
            comparisons=[]
            for suite in ['checkpoint','rebase','native_cp','generic_overlap']:
                trace='events.txt'if suite=='checkpoint'else'native.txt'
                assert (out/f'baseline_{suite}'/trace).read_bytes()==(out/f'default_{suite}'/trace).read_bytes()
                comparisons.append([f'baseline_{suite}',f'default_{suite}'])
                if suite!='generic_overlap':
                    assert (out/f'baseline_{suite}'/trace).read_bytes()==(out/f'exclusive_{suite}'/trace).read_bytes()
                    comparisons.append([f'baseline_{suite}',f'exclusive_{suite}'])
            m['exact_trace_comparisons']=comparisons
        m['status']='elaborated_not_simulated'if args.compile_only else'observed'
    except Exception as e:m.update(status='failed',error=repr(e));raise
    finally:save()
    print('CHECKPOINT_EDIT_UNITS_TERMINAL',m['status'],flush=True)
if __name__=='__main__':main()
