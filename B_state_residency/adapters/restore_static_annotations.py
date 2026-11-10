"""Restore proved preprocessing-only static annotations; Vivado validation remains mandatory."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
from prepare_real import ROOT,RUNTIME,JAVA_BIN,sha


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset');parser.add_argument('logical',type=Path);parser.add_argument('original',type=Path)
    parser.add_argument('preprocessed',type=Path);parser.add_argument('routed',type=Path)
    args=parser.parse_args();directory=ROOT/'results'/('static_restore_'+args.dataset+'_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'));directory.mkdir()
    source=ROOT/'adapters/RestoreStaticAnnotations.java';jar=RUNTIME/'rapidwright.jar';classes=directory/'java';classes.mkdir()
    snapshot=directory/source.name;snapshot.write_text(source.read_text())
    record={'status':'building','dataset':args.dataset,'input_hashes':{str(p.resolve()):sha(p) for p in [args.logical,args.original,args.preprocessed,args.routed,source,jar]}}
    def save():(directory/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    save()
    try:
        cmd=[str(JAVA_BIN/'javac'),'-cp',str(jar),'-d',str(classes),str(snapshot)];record['build_command']=cmd
        with (directory/'build.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        cmd=['taskset','-c','24-31',str(JAVA_BIN/'java'),'-Xmx24g','-XX:ActiveProcessorCount=8','-cp',f'{classes}:{jar}',
             'RestoreStaticAnnotations',str(args.logical.resolve()),str(args.original.resolve()),str(args.preprocessed.resolve()),str(args.routed.resolve()),str(directory/'restored.phys'),str(directory/'restored.dcp')]
        record.update(status='running',command=cmd);save()
        with (directory/'restore.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,RAPIDWRIGHT_PATH=str(RUNTIME)),check=True,timeout=300)
        if 'B_STATIC_RESTORE_PASS' not in (directory/'restore.log').read_text():raise ValueError('No successful restoration receipt')
        record['status']='strict_physical_comparison_passed_vivado_pending'
        record['outputs']={str(p):sha(p) for p in [directory/'restored.phys',directory/'restored.dcp']}
    except Exception as error:
        record.update(status='failed',error=str(error));raise
    finally:save()
    print(directory,flush=True)


if __name__=='__main__':main()
