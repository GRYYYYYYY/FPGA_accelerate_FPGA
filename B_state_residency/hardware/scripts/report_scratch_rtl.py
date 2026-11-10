"""Audit completed behavioral RTL and physical RAM synthesis evidence."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha


def audit(directory):
    directory=Path(directory).resolve();path=directory/'manifest.json';record=json.loads(path.read_text())
    if record['status']!='passed' or record['performance'] is not None:raise ValueError('Flow incomplete')
    for filename,digest in {**record['files'],**record['artifacts']}.items():
        if sha(filename)!=digest:raise ValueError('Bound artifact changed: '+filename)
        p=Path(filename)
        if p.suffix in ('.py','.sv','.xdc') and sha(directory/p.name)!=digest:
            raise ValueError('Frozen source snapshot changed')
    if [row['stage'] for row in record['commands']]!=['compile','elaborate','simulate','synthesize']:
        raise ValueError('Missing flow stage')
    if any(row['exit_code'] for row in record['commands']):raise ValueError('Flow stage failed')
    for row in record['commands']:
        text=(directory/(row['stage']+'.console.log')).read_text()
        if re.search(r'(?im)^\s*(ERROR|FATAL|Fatal):',text):raise ValueError('Unexpected tool/checker error')
    simulation=(directory/'simulate.log').read_text()
    markers=re.findall(r'TEST_PASS scratch_frame_store checks=(\d+) actual_commands=(\d+) stalled_cycles=(\d+)',simulation)
    if len(markers)!=1:raise ValueError('Missing/extra terminal PASS')
    if tuple(map(int,markers[0]))!=tuple(record['simulation'][key] for key in ('checks','actual_commands','stalled_cycles')):
        raise ValueError('Simulation evidence mismatch')
    synth=(directory/'synthesize.log').read_text()
    if 'synth_design completed successfully' not in synth or '0 Critical Warnings and 0 Errors' not in synth:
        raise ValueError('Synthesis incomplete or critical/error diagnostics present')
    if 'dissolved into registers' in synth:raise ValueError('RAM inference failed')
    rams=(directory/'ram_cells.txt').read_text().splitlines()
    if rams!=record['synthesis']['ram_cells'] or len(rams)!=2 or any(not line.endswith(' RAMB36E2') for line in rams):
        raise ValueError('Unexpected RAM mapping')
    utilization=(directory/'utilization.rpt').read_text()
    def used(label):
        match=re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*(\d+)\s*\|',utilization,re.M)
        if not match:raise ValueError('Missing utilization row '+label)
        return int(match[1])
    return dict(status='passed',manifest_sha256=sha(path),simulation=record['simulation'],
                utilization=dict(luts=used('CLB LUTs*'),registers=used('CLB Registers'),bram_tiles=used('Block RAM Tile')),
                warnings=[line for line in synth.splitlines() if line.startswith('WARNING:')],
                scope='Default 4-slot/64-node scratch storage primitive only. Clean authorization and finite token quarantine remain external. Behavioral simulation and synthesized resources, no post-route timing, DMA, board or acceleration claim.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path);args=parser.parse_args()
    result=audit(args.directory);(args.directory/'completion_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
