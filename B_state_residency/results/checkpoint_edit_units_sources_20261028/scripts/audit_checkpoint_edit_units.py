"""Check CP semantics, native-qualified cases and explicit generic counterexample."""
from pathlib import Path
import importlib.util
import json
import re
import struct
import sys
import zlib
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
assert m['status']=='observed'and not m['compile_only']
for rel,h in m['bound'].items():assert sha(p/'tools'/rel)==h==sha(ROOT/rel),rel
v=ROOT/'hardware/variants/checkpoint_edit_exclusion_v1'
spec=importlib.util.spec_from_file_location('cp_edit_tb',v/'build_tb.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
vm=json.loads((v/'manifest.json').read_text())
image=(p/'tools/query.bin').read_bytes();bm=json.loads((p/'tools/bundle_manifest.json').read_text())
assert sha(p/'tools/query.bin')==m['query_sha256']and sha(p/'tools/bundle_manifest.json')==m['bundle_manifest_sha256']
assert len(image)==40 and zlib.crc32(image)==bm['query_crc32']
words=list(struct.unpack('<10I',image));words[6]=5;words[7]=(words[7]&0xffffffc0)|23
converted=struct.pack('<10I',*words);target_crc=zlib.crc32(converted)
order=[(mode,suite)for mode in ['baseline','default','exclusive']for suite in ['checkpoint','rebase','native_cp','generic_overlap']]
assert [(c['mode'],c['suite'])for c in m['cases']]==order
observed={}
for c in m['cases']:
    mode,suite=c['mode'],c['suite'];name=f'{mode}_{suite}';d=p/name
    assert c['status']=='passed'
    assert sha(d/'query_lifecycle.sv')==c['rtl_sha256']==vm['sources']['query_lifecycle.sv']['baseline'if mode=='baseline'else'fixed']
    tb,top,trace,marker=b.build(ROOT,mode,suite)
    assert (d/'tb.sv').read_text()==tb and sha(d/'tb.sv')==c['tb_sha256']
    assert not re.search(r'\b(force|release)\s',tb)
    assert [x['stage']for x in c['commands']]==['compile','elaborate','simulate']
    for x in c['commands']:
        assert x['exit_code']==0 and sha(d/(x['stage']+'.stdout.log'))==x['log_sha256']
    log=(d/'simulate.log').read_text();assert sha(d/'simulate.log')==c['simulate_log_sha256']
    assert marker in log and 'Fatal:'not in log and 'ERROR:'not in log
    finish=re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)',log);assert len(finish)==1
    text=(d/trace).read_text();assert sha(d/trace)==c['trace_sha256']
    lines=[l.split()for l in text.splitlines()]
    result=dict(trace_sha256=sha(d/trace),finish=finish[0])
    if suite=='checkpoint':
        q=[l for l in lines if l[0]=='Q'];cp=[l for l in lines if l[0]=='CP']
        assert len(q)==14 and len(cp)==27
        assert [int(l[3])for l in q]==[0,0,1,0,1,1,0,1,1,1,1,1,0,1]
        assert [int(l[2])for l in cp]==[0,0,1]+[1]*11+[1,2,1,1,2,2,1,0,0,0,1,0,0]
        verdict=re.findall(r'QUERY_CHECKPOINT_PASS queries=(\d+) checkpoints=(\d+) cycles=(\d+)',log)
        assert len(verdict)==1 and tuple(map(int,verdict[0][:2]))==(14,27)and int(verdict[0][2])>0
        result.update(queries=14,checkpoints=27)
    else:
        replies=[l for l in lines if l[0]=='R']
        statuses=[int(l[2])for l in replies];floors=[int(l[4])for l in replies]
        if suite=='rebase':
            assert statuses==[1,1,1,1,1,2,2,0,0,1,1,2]
            assert floors==[0,0,0,0,0,0,0,1,1,1,1,0]
            assert re.findall(r'QUERY_REBASE_PASS checks=(\d+)',log)==['119']
            exports=[l for l in lines if l[0]=='M'];assert len(exports)==10
            assert [int(l[3],16)for l in exports]==words
            assert int(replies[7][3],16)==bm['query_crc32']and int(replies[8][3],16)==target_crc
        elif suite=='native_cp':
            assert statuses==[2,0,2]and floors==[0,1,1]
            assert [int(l[3],16)for l in replies]==[0,bm['query_crc32'],target_crc]
        else:
            assert statuses==([0]if mode=='exclusive'else[2])
            assert floors==([1]if mode=='exclusive'else[0])
            assert int(replies[0][3],16)==(bm['query_crc32']if mode=='exclusive'else 0)
        if suite in ['native_cp','generic_overlap']:
            monitor=[l for l in lines if l[0]=='CP_EDIT_MONITOR'];assert len(monitor)==1
            safe,edit,overlap=map(int,monitor[0][1:]);assert safe>0 and edit>0
            assert overlap==0 if suite=='native_cp'else overlap>0
            result['monitor']=dict(safe_busy=safe,edit_busy=edit,overlaps=overlap)
        result.update(statuses=statuses,floors=floors)
    observed[name]=result
for suite in ['checkpoint','rebase','native_cp','generic_overlap']:
    assert observed[f'baseline_{suite}']==observed[f'default_{suite}']
    if suite!='generic_overlap':assert observed[f'baseline_{suite}']==observed[f'exclusive_{suite}']
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),cases=observed,
    exact_trace_comparisons=7,generic_overlap_specialization_counterexample=True,scope=m['scope'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('CHECKPOINT_EDIT_UNITS_AUDITED cases=12 comparisons=7')
