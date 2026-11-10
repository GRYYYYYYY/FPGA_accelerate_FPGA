"""Prepare only133 matched production sources after actual full-system acceptance."""
from pathlib import Path
import json
import shutil
import sys
from config_native_publication_synth_common_v1 import ROOT,TARGET,REFERENCE,VARIANT,sha,evidence


def main():
    p=Path(sys.argv[1]).resolve();assert p==TARGET and not p.exists()
    rm,ra,fm,fa,proof=evidence()  # Never read a live/restoring candidate root before the accepted freeze.
    changes={}
    for name in ['config_restore_controller.sv','residency_system.sv']:
        changes[name]=dict(original_sha256=rm['sources'][name],candidate_sha256=sha(VARIANT/'fixed'/name),path=str(VARIANT/'fixed'/name))
    p.mkdir();src=p/'sources';src.mkdir();(p/'bound').mkdir();sources={}
    for name,digest in rm['sources'].items():
        origin=REFERENCE/'sources'/name;assert sha(origin)==digest
        dest=src/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(origin,dest);sources[name]=digest
    for name,entry in changes.items():shutil.copyfile(entry['path'],src/name);sources[name]=sha(src/name)
    for name in rm['rtl']:assert sources[name]==fm['sources'][name]['sha256']
    for file in src.rglob('*.dat'):shutil.copyfile(file,p/file.name)
    prep='prepare_config_native_publication_synth_v1.py';shutil.copyfile(Path(__file__),src/prep);sources[prep]=sha(src/prep)
    tcl=(REFERENCE/'synth.tcl').read_text().replace(str(REFERENCE),str(p));(p/'synth.tcl').write_text(tcl)
    shutil.copyfile(REFERENCE/'clock.xdc',p/'clock.xdc')
    assert tcl.count('read_verilog -sv ')==133 and 'config_restore_controller_observer.sv' not in tcl
    for i,(source,digest) in enumerate(proof.items()):
        name=f'{i:02d}_{Path(source).name}';shutil.copyfile(source,p/'bound'/name)
        assert sha(p/'bound'/name)==digest
    bound={f'{i:02d}_{Path(source).name}':dict(source=source,sha256=digest) for i,(source,digest) in enumerate(proof.items())}
    m=dict(status='prepared',sources=sources,rtl=rm['rtl'],parameters=rm['parameters'],part=rm['part'],
        reference=str(REFERENCE),reference_audit_sha256=sha(REFERENCE/'source_bound_audit.json'),
        tcl_sha256=sha(p/'synth.tcl'),xdc_sha256=sha(p/'clock.xdc'),clock_period_ns=10,
        production_changes=changes,native_publication_evidence=proof,bound=bound,
        scope='Two-source native feedback publication candidate on preferred CP OOC baseline. Same133 compiled production sources/U280/top parameters/10ns XDC; all4 verification sources excluded. Matched full-system actual restore required. Timing is pre-placement with unspecified IO; no physical or board claim.')
    (p/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    print('NATIVE_PUBLICATION_SYNTH_PREPARED',len(m['rtl']),len(changes),'production sources only')


if __name__=='__main__':main()
