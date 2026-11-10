#!/usr/bin/env python3
"""One owner: wait for the live pilot, validate its receipt, then launch the frozen matrix."""
import argparse
from datetime import datetime,timezone
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha
from research_matrix import save,validate_plan


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('pilot',type=Path);parser.add_argument('--config',type=Path,required=True)
    args=parser.parse_args();pilot=args.pilot.resolve();config_path=args.config.resolve()
    lock=(ROOT/'results/research_stage2_chain.lock').open('a+')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    directory=ROOT/'results'/('research_chain_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'));directory.mkdir()
    record={'status':'binding_pilot','pid':os.getpid(),'pilot':str(pilot),'config_template':str(config_path),'config_template_sha256':sha(config_path),
            'tool_sha256':sha(__file__),'owner':'current chain only','recovery':'none; no automatic resubmission','started_utc':datetime.now(timezone.utc).isoformat()}
    manifest=directory/'manifest.json'
    def persist():save(manifest,record)
    persist()
    try:
        initial=json.loads((pilot/'manifest.json').read_text());pid=initial['runner_pid'];proc=Path(f'/proc/{pid}')
        if initial['status']=='running':
            if not proc.exists() or Path(os.readlink(proc/'cwd'))!=ROOT:raise RuntimeError('Pilot receipt has no matching live process')
            birth=(proc/'stat').read_text().split()[21]
            record.update(status='waiting_for_live_pilot',pilot_pid=pid,pilot_process_birth=birth);persist()
            while proc.exists():
                fields=(proc/'stat').read_text().split()
                if fields[21]!=birth:raise RuntimeError('Pilot PID was reused')
                if fields[2]=='Z':break
                current=json.loads((pilot/'manifest.json').read_text())
                if current['status']=='failed':raise RuntimeError('Pilot failed; matrix not submitted')
                time.sleep(10)
        current=json.loads((pilot/'manifest.json').read_text())
        if current['status']!='passed' or len(current['runs'])!=len(current['schedule']) or not all(r.get('verified') for r in current['runs']):
            raise RuntimeError('Pilot has no complete successful receipt; no matrix submitted')
        config=json.loads(config_path.read_text());validate_plan(config)
        for dataset in config['datasets']:
            rows=[r for r in current['runs'] if r['dataset']==dataset['id']]
            if not rows:continue
            refs={}
            for mode in ('serial','batch'):
                values={r['result_sha256'] for r in rows if r['mode']==mode}
                if len(values)!=1:raise RuntimeError('Pilot result disagreement')
                refs[mode]=values.pop()
            if not any(r['variant']=='original' and r['mode']=='serial' for r in rows):raise RuntimeError('No original baseline in new-dataset pilot')
            dataset['reference_results']=refs
        if sha(config_path)!=record['config_template_sha256']:raise RuntimeError('Queued config changed')
        frozen=directory/'matrix_config.json';save(frozen,config)
        record.update(status='launching_matrix',pilot_final_manifest_sha256=sha(pilot/'manifest.json'),frozen_config=str(frozen));persist()
        output=directory/'matrix';command=[sys.executable,str(ROOT/'scripts/research_matrix.py'),'--config',str(frozen),'--output',str(output)]
        record['command']=command
        with (directory/'matrix_console.log').open('w') as log:
            process=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            record.update(status='matrix_running',matrix_pid=process.pid,matrix_directory=str(output));persist()
            code=process.wait()
        receipt=json.loads((output/'manifest.json').read_text())
        record.update(exit_code=code,status='passed' if code==0 and receipt['status']=='passed' else 'failed')
        if record['status']!='passed':raise RuntimeError('Matrix failed; inspect preserved console and receipt')
    except Exception as error:
        record['status']='failed';record['error']=str(error);raise
    finally:
        record['finished_utc']=datetime.now(timezone.utc).isoformat();persist()
    print(directory,flush=True)


if __name__=='__main__':main()
