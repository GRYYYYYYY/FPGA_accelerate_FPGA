#!/usr/bin/env python3
"""Observe the existing conversion owner, then independently audit all 14 trials."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from check_packed_conversion import digest
from real_experiment import write_new
ROOT=Path(__file__).resolve().parents[1]
EXPERIMENT=ROOT/'data/derived/packed_conversion_statistics_20261023_v1'
STATE=ROOT/'results/packed_conversion_audit_pipeline_20261023_v1.json'
REPORT=ROOT/'results/packed_conversion_statistics_audit_20261023_v1.json'


def identity(pid):
    try:
        fields=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
        return None if fields[0]=='Z' else fields[19]
    except FileNotFoundError:return None


def main():
    plan_path=EXPERIMENT/'plan.json';plan=json.loads(plan_path.read_text());pid=plan['owner_pid'];start=identity(pid)
    if start and b'packed_conversion_benchmark.py' not in Path(f'/proc/{pid}/cmdline').read_bytes():raise ValueError('Wrong conversion process')
    checker=ROOT/'scripts/check_packed_conversion.py'
    files={str(p):digest(p) for p in (Path(__file__),checker,plan_path,ROOT/'scripts/real_experiment.py')}
    state={'owner_pid':os.getpid(),'conversion_owner_pid':pid,'conversion_start_ticks':start,'status':'waiting_existing_conversion','files':files}
    write_new(STATE,state)
    def save(**changes):
        state.update(changes);tmp=STATE.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(STATE)
    try:
        while start is not None and identity(pid)==start:time.sleep(15)
        for path,value in files.items():
            if digest(path)!=value:raise ValueError('Audit dependency changed')
        final=json.loads((EXPERIMENT/'report.json').read_text())
        if final['workers']!=14 or final['status']!='all_regenerated_images_byte_identical':raise ValueError('Conversion incomplete')
        command=[sys.executable,'-u',str(checker),str(EXPERIMENT),'--output',str(REPORT)]
        child=subprocess.Popen(command);save(status='auditing',child_pid=child.pid)
        code=child.wait()
        if code:raise RuntimeError('Independent conversion audit failed: '+str(code))
        verified=json.loads(REPORT.read_text())
        if verified['status']!='complete_conversion_matrix_independently_audited':raise ValueError('Audit incomplete')
        save(status='complete',report_sha256=digest(REPORT))
    except BaseException as error:
        save(status='failed',error=str(error));raise


if __name__=='__main__':main()
