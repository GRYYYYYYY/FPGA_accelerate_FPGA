"""Prepare the matched bypass-off OOC without changing any production source."""
from pathlib import Path
import copy,json,shutil,sys
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();ref=p.parent/'native_retirement_synth_v1'
rm=json.loads((ref/'manifest.json').read_text());ra=json.loads((ref/'source_bound_audit.json').read_text())
receipt=ROOT/'results/native_retirement_synth_v1_restore_20261025.json';rr=json.loads(receipt.read_text())
assert rm['status']=='observed'and ra['status']==rr['status']=='passed'and rr['audit_byte_identical']
assert ra['manifest_sha256']==sha(ref/'manifest.json')and rr['audit_sha256']==sha(ref/'source_bound_audit.json')
assert ra['check_timing_counts']['loops']==0 and rm['parameters']['ENABLE_RESTORE_SEED_BYPASS']==1
current=int(Path('/sys/fs/cgroup/memory.current').read_text());limit=int(Path('/sys/fs/cgroup/memory.max').read_text())
assert current*4<=limit*3,'defer new synthesis until memory admission is below75%'
p.mkdir();src=p/'sources';src.mkdir();sources={}
for n,h in rm['sources'].items():
    origin=ref/'sources'/n;assert sha(origin)==h
    dest=src/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(origin,dest);sources[n]=h
for f in src.rglob('*.dat'):shutil.copyfile(f,p/f.name)
tcl=(ref/'synth.tcl').read_text().replace(str(ref),str(p))
assert tcl.count('ENABLE_RESTORE_SEED_BYPASS=1')==1
tcl=tcl.replace('ENABLE_RESTORE_SEED_BYPASS=1','ENABLE_RESTORE_SEED_BYPASS=0',1)
(p/'synth.tcl').write_text(tcl);shutil.copyfile(ref/'clock.xdc',p/'clock.xdc')
shutil.copyfile(Path(__file__),src/'prepare_native_off.py');sources['prepare_native_off.py']=sha(src/'prepare_native_off.py')
parameters=copy.deepcopy(rm['parameters']);parameters['ENABLE_RESTORE_SEED_BYPASS']=0
m=dict(status='prepared',sources=sources,rtl=rm['rtl'],parameters=parameters,part=rm['part'],
    reference=str(ref),reference_audit_sha256=sha(ref/'source_bound_audit.json'),reference_restore_sha256=sha(receipt),
    only_parameter_changed='ENABLE_RESTORE_SEED_BYPASS',tcl_sha256=sha(p/'synth.tcl'),xdc_sha256=sha(p/'clock.xdc'),
    clock_period_ns=10,memory_admission=dict(current_bytes=current,limit_bytes=limit,fraction=0.75),
    scope='Same ten-source-repaired implementation and133 production RTL, same part/clock/Tcl. Only ENABLE_RESTORE_SEED_BYPASS=1 to0 differs. Off-mode structure and matched resource/timing estimates must be measured; no physical timing or board-speed claim.')
(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
print('NATIVE_OFF_SYNTH_PREPARED',len(m['rtl']),'production changes=0 generic changes=1')
