"""Prepare matched checkpoint-edit OOC only after restored full-system audit."""
from pathlib import Path
import importlib.util,json,shutil,sys
from run_checkpoint_authority import ROOT,sha
p=Path(sys.argv[1]).resolve();ref=p.parent/'route_path_synth_v1'
assert int(Path('/sys/fs/cgroup/memory.current').read_text())<=int(Path('/sys/fs/cgroup/memory.max').read_text())*.75
rm=json.loads((ref/'manifest.json').read_text());ra=json.loads((ref/'source_bound_audit.json').read_text())
assert rm['status']=='observed'and ra['status']=='passed'and ra['manifest_sha256']==sha(ref/'manifest.json')
assert ra['check_timing_counts']['loops']==0
receipt=ROOT/'results/route_path_synth_v1_restore_20261025.json';rr=json.loads(receipt.read_text())
assert rr['status']=='passed'and rr['audit_byte_identical']and rr['audit_sha256']==sha(ref/'source_bound_audit.json')
full=p.parent/'route_stage_system_crc_pressure_v1'
fm=json.loads((full/'manifest.json').read_text());fa=json.loads((full/'source_bound_audit.json').read_text())
frp=ROOT/'results/route_stage_system_crc_pressure_v1_restore_20261025.json';fr=json.loads(frp.read_text())
assert fm['status']=='observed'and fa['status']==fr['status']=='passed'and fr['audit_byte_identical']
assert fa['manifest_sha256']==sha(full/'manifest.json')and fr['audit_sha256']==sha(full/'source_bound_audit.json')
assert len(fa['exact_comparisons'])==27
variant=ROOT/'hardware/variants/route_stage_system_v1';builder=variant/'build.py'
spec=importlib.util.spec_from_file_location('query_native_system_builder',builder);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
fixed,evidence=b.sources(p.parent/'route_path_system_crc_pressure_v1')
baseline={n:(b.PARENT/'baseline'/n).read_text() for n in b.NAMES}
assert set(fixed)==set(b.NAMES)
changes={}
assert len(rm['rtl'])==133
for n in rm['rtl']:
    expected=sha(b.PARENT/'fixed'/n)if n in fixed else rm['sources'][n]
    assert sha(full/'sources'/n)==fm['sources'][n]['sha256']==expected,n
for n in fixed:
    assert (ref/'sources'/n).read_text()==baseline[n]==(b.PARENT/'baseline'/n).read_text()
    assert (b.PARENT/'fixed'/n).read_text()==fixed[n]
    changes[n]=dict(original_sha256=sha(ref/'sources'/n),candidate_sha256=sha(b.PARENT/'fixed'/n),path=str(b.PARENT/'fixed'/n))
evidence.update(reference_restore_sha256=sha(receipt),full_system_audit_sha256=sha(full/'source_bound_audit.json'),full_system_restore_sha256=sha(frp))
cp_ref=p.parent/'checkpoint_edit_synth_v1'
cp_m=json.loads((cp_ref/'manifest.json').read_text());cp_a=json.loads((cp_ref/'source_bound_audit.json').read_text())
cp_rp=ROOT/'results/checkpoint_edit_synth_v1_restore_20261025.json';cp_r=json.loads(cp_rp.read_text())
assert cp_m['status']=='observed' and cp_a['status']==cp_r['status']=='passed'
assert cp_a['manifest_sha256']==sha(cp_ref/'manifest.json') and cp_r['audit_byte_identical']
assert cp_r['audit_sha256']==sha(cp_ref/'source_bound_audit.json') and cp_a['check_timing_counts']['loops']==0
assert cp_m['rtl']==rm['rtl'] and cp_m['parameters']==rm['parameters'] and cp_m['part']==rm['part']
assert (cp_ref/'clock.xdc').read_bytes()==(ref/'clock.xdc').read_bytes()
cp_evidence=dict(root=str(cp_ref),audit_sha256=sha(cp_ref/'source_bound_audit.json'),restore_sha256=sha(cp_rp))
p.mkdir()
src = p / 'sources'
src.mkdir()
sources = {}
for n, h in rm['sources'].items():
    origin = ref / 'sources' / n
    assert sha(origin) == h
    dest = src / n
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(origin, dest)
    sources[n] = h
for n, c in changes.items():
    shutil.copyfile(c['path'], src / n)
    sources[n] = sha(src / n)
for f in src.rglob('*.dat'):
    shutil.copyfile(f, p / f.name)
(p / 'synth.tcl').write_text((ref / 'synth.tcl').read_text().replace(str(ref), str(p)))
shutil.copyfile(ref / 'clock.xdc', p / 'clock.xdc')
shutil.copyfile(Path(__file__), src / 'prepare_route_stage.py')
sources['prepare_route_stage.py'] = sha(src / 'prepare_route_stage.py')
m=dict(status='prepared',sources=sources,rtl=rm['rtl'],parameters=rm['parameters'],part=rm['part'],
    reference=str(ref),reference_audit_sha256=sha(ref/'source_bound_audit.json'),tcl_sha256=sha(p/'synth.tcl'),
    xdc_sha256=sha(p/'clock.xdc'),clock_period_ns=10,production_changes=changes,route_stage_evidence=evidence,
    scope='Two-source same-cycle stage-write factoring on the restored path area branch; cumulative changed production file set remains eleven. Same133 RTL/U280/parameters/10ns clock. Matched full-system CRC pressure audit and restoration required; no physical or board timing claim.')
m['cp_timing_reference']=cp_evidence
(p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
print('ROUTE_STAGE_SYNTH_PREPARED',len(m['rtl']),len(changes))
