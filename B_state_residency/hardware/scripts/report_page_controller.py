"""Audit controller XSim sessions, frozen vectors, and completed project synthesis.

Run only after the standalone checkpoint report has finished; no synthesis or
simulation is launched by this auditor. Original failures remain as artifacts.
"""
import json
from pathlib import Path
import re
import sys
from make_controller_vectors import sha, ROOT


def audit(out):
    out=out.resolve();sources=json.loads((out/'source_manifest.json').read_text())
    vectors=json.loads((out/'vectors/vectors_manifest.json').read_text())
    if sources['status']!='frozen' or vectors['status']!='passed':raise ValueError('Inputs incomplete')
    for name,digest in sources['files'].items():
        if sha(name)!=digest or sha(out/'sources'/Path(name).relative_to(ROOT))!=digest:
            raise ValueError('Source changed: '+name)
    for name,digest in vectors['files'].items():
        if sha(name)!=digest:raise ValueError('Vector or trace changed: '+name)
    sim=(out/'simulation_session.log').read_text()
    if '\0' in sim or re.search(r'(?im)^\s*(ERROR|FATAL|Fatal):',sim):raise ValueError('Simulation transcript corrupt/failed')
    matches=re.findall(r'TEST_PASS scratch_page_controller tx_bits=(\d+) gen_bits=(\d+) checks=(\d+) stalls=(\d+)',sim)
    if len(matches)!=2:raise ValueError('Missing/duplicate terminal simulation verdict')
    sims={}
    for name,match in zip(('boundaries','actual'),matches):
        tx,gen,checks,stalls=map(int,match);ref=vectors['cases'][name]
        if (tx,gen,checks,stalls)!=(ref['tx_bits'],ref['generation_bits'],ref['commands'],4*((ref['commands']+12)//13)):
            raise ValueError('Partial/wrong stimulus '+name)
        top='tb_controller_small' if name=='boundaries' else 'tb_controller_actual'
        elaborate=(out/('small_sim' if name=='boundaries' else 'actual_sim')/'elaborate.log').read_text()
        if f'Built simulation snapshot {top}_behav' not in elaborate:raise ValueError('No elaboration terminal')
        sims[name]=dict(ref,checks=checks,stalled_cycles=stalls)
    if sim.count("'compile' step finished")!=2 or sim.count("'elaborate' step finished")!=2 or sim.count('XSim completed.')!=2:
        raise ValueError('Incomplete simulation stages')
    if set(vectors['cases']['boundaries']['status_counts'])!=set(map(str,range(8))):raise ValueError('Status scenarios absent')
    if sims['actual']['actual']['queries']!=19 or sims['actual']['actual']['field_accesses']!=56588:
        raise ValueError('Wrong real query coverage')
    run=out/'project/b_page_controller.runs/synth_1'
    if not (run/'.vivado.end.rst').exists() or (run/'.vivado.error.rst').exists():raise ValueError('Synthesis run not complete')
    synth=(run/'runme.log').read_text()
    if 'synth_design completed successfully' not in synth or '0 Critical Warnings and 0 Errors' not in synth:
        raise ValueError('Missing synthesis success')
    if re.search(r'(?im)^\s*(ERROR|CRITICAL WARNING):',synth) or 'dissolved into registers' in synth:
        raise ValueError('Synthesis error or failed memory mapping')
    receipt=json.loads((out/'checkpoint_report_receipt.json').read_text())
    report=(out/'checkpoint_report.log').read_text()
    if receipt['exit_code']!=0 or 'B_CONTROLLER_REPORT_PASS ram_cells=2' not in report:
        raise ValueError('Checkpoint reporting incomplete')
    rams=(out/'ram_cells.txt').read_text().splitlines()
    if len(rams)!=2 or any(not x.endswith(' RAMB36E2') for x in rams):raise ValueError('Unexpected RAM mapping')
    util=(out/'utilization.rpt').read_text()
    def used(label):
        match=re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*(\d+)\s*\|',util,re.M)
        if not match:raise ValueError('Missing resource '+label)
        return int(match[1])
    artifacts=[out/p for p in ('source_manifest.json','vectors/vectors_manifest.json','simulation_session.log',
          'checkpoint_report.tcl','checkpoint_report.log','checkpoint_report_receipt.json','utilization.rpt',
          'ram_cells.txt','process_receipt.json','hs_err_pid1998871.log')]
    artifacts.extend(run/p for p in ('runme.log','scratch_page_controller.tcl','scratch_page_controller.dcp','.vivado.end.rst'))
    artifacts.extend(out/p/'elaborate.log' for p in ('small_sim','actual_sim'))
    record=dict(status='passed',performance=None,toolchain='Vivado/XSim 2022.2',part='xcu280-fsvh2892-2L-e',
        simulation=sims,utilization=dict(luts=used('CLB LUTs*'),registers=used('CLB Registers'),latches=used('Register as Latch'),bram_tiles=used('Block RAM Tile')),
        ram_cells=rams,warnings=[line for line in synth.splitlines() if line.startswith('WARNING:')],
        files={**sources['files'],**vectors['files'],str(Path(__file__).resolve()):sha(__file__)},
        artifacts={str(p):sha(p) for p in artifacts},
        scope='Controller plus scratch RAM; 3-bit boundary / 16-bit actual-value simulation and synthesized resources. COMPLETE and remote-drain attestations still trusted external interfaces; no address-pool RTL, remote fence queue, AXI/DDR/HBM DMA, timing closure, cold-to-warm recovery, board run or speed result.',
        tool_incident='MCP parent1998871 aborted at launch_runs; existing child2223090 retained until completion. Checkpoint read with local batch, no duplicate synthesis. Small/actual simulate.log empty/NUL, full clean Vivado simulation_session.log is authoritative.')
    return record

if __name__=='__main__':
    out=Path(sys.argv[1]);record=audit(out)
    dest=out/'manifest.json'
    if dest.exists() and json.loads(dest.read_text())!=record:raise ValueError('Do not overwrite differing evidence')
    dest.write_text(json.dumps(record,indent=2)+'\n')
    summary=dict(status='passed',manifest_sha256=sha(dest),simulation={k:{x:v[x] for x in ('checks','stalled_cycles')} for k,v in record['simulation'].items()},utilization=record['utilization'],scope=record['scope'])
    (out/'completion_audit.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
