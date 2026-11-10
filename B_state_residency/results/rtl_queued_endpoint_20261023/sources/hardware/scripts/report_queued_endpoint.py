"""Audit successful endpoint simulations/synthesis and deliberate guard failures."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def audit(out):
    sources=json.loads((out/'source_manifest.json').read_text())
    extra=json.loads((out/'verification_sources.json').read_text())
    files={**sources['files'],**extra['files']}
    for name,digest in files.items():
        if sha(name)!=digest or sha(out/'sources'/Path(name).relative_to(ROOT))!=digest:raise ValueError('Source changed '+name)
    vectors=ROOT/'results/rtl_page_controller_20261023/vectors/vectors_manifest.json'
    v=json.loads(vectors.read_text())
    for name,digest in v['files'].items():
        if sha(name)!=digest:raise ValueError('Inherited actual vector evidence changed')
    files.update(v['files']);files[str(vectors)]=sha(vectors)
    sim=(out/'simulation_session.log').read_text()
    if '\0' in sim or re.search(r'(?im)^\s*(ERROR|FATAL|Fatal):',sim):raise ValueError('Positive simulation failed/corrupt')
    m=re.findall(r'TEST_PASS queued_scratch_endpoint small=(\d+) tag_bits=(\d+) checks=(\d+) actual_commands=(\d+) stalls=(\d+) retries=(\d+) wraps=(\d+)',sim)
    if [tuple(map(int,row)) for row in m]!=[(1,1,2267,0,1638,0,24),(0,2,472689,472689,145440,0,4)]:raise ValueError('Wrong/incomplete functional runs')
    order=re.findall(r'TEST_PASS queued_ordering checks=(\d+) stalled_cycles=(\d+) request_full=(\d+) work_full=(\d+) response_full=(\d+)',sim)
    if len(order)!=1 or tuple(map(int,order[0]))!=(6144,46060,61627,58328,34799):raise ValueError('Incomplete ordering pressure')
    if sim.count("'compile' step finished")!=3 or sim.count("'elaborate' step finished")!=3 or sim.count('XSim completed.')!=3:raise ValueError('Incomplete stages')
    for name in ('small','actual','ordering'):
        log=(out/(name+'_sim')/'elaborate.log').read_text()
        if f'Built simulation snapshot tb_queued_{name}_behav' not in log:raise ValueError('Missing elaboration '+name)
    guards_path=out/'negative_guards/manifest.json';guards=json.loads(guards_path.read_text())
    expected={'ignore_old_responses','ignore_duplicate_acks','ignore_queued_work','ignore_same_cycle_ingress','seal_with_live_lease'}
    if guards['status']!='passed' or set(guards['mutations'])!=expected:raise ValueError('Incomplete negative guards')
    for name,digest in guards['files'].items():
        if sha(name)!=digest:raise ValueError('Negative test input changed')
    wrapper=(ROOT/'hardware/rtl/queued_scratch_endpoint.sv').read_text()
    for name,row in guards['mutations'].items():
        d=out/'negative_guards'/name
        if row['status']!='expected_failure_observed':raise ValueError('Mutation was not rejected')
        if (d/'queued_scratch_endpoint.sv').read_text()!=wrapper.replace(row['removed'],row['replacement']):raise ValueError('More than declared mutation')
        if [r['stage'] for r in row['commands']]!=['compile','elaborate','simulate'] or any(r['exit_code'] for r in row['commands'][:2]):raise ValueError('Mutation failed before simulation')
        log=(d/'simulate.log').read_text();fatal=[x for x in log.splitlines() if x.startswith('Fatal:')]
        if fatal!=[row['causal_failure']] or row['expected_failure'] not in fatal[0] or 'TEST_PASS' in log:raise ValueError('Wrong guard failure')
        for path,digest in row['artifacts'].items():
            if sha(path)!=digest:raise ValueError('Negative artifact changed')
    synthdir=out/'synthesis';receipt=json.loads((synthdir/'receipt.json').read_text());synth=(synthdir/'synthesize.log').read_text()
    if receipt['exit_code']!=0 or receipt['driver_sha256']!=sha(ROOT/'hardware/scripts/synthesize_queued_endpoint.py') or receipt['tcl_sha256']!=sha(synthdir/'synthesize.tcl'):raise ValueError('Synthesis command changed/failed')
    if 'synth_design completed successfully' not in synth or '0 Critical Warnings and 0 Errors' not in synth or 'B_QUEUED_SYNTH_PASS ram_cells=2' not in synth:raise ValueError('Incomplete synthesis')
    if re.search(r'(?im)^\s*(ERROR|CRITICAL WARNING):',synth) or 'RAM "data_reg" dissolved' in synth:raise ValueError('Synthesis errors/RAM failure')
    rams=(synthdir/'ram_cells.txt').read_text().splitlines()
    if len(rams)!=2 or any(not r.endswith(' RAMB36E2') for r in rams):raise ValueError('Unexpected page memory mapping')
    util=(synthdir/'utilization.rpt').read_text()
    def used(label):
        m=re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*(\d+)\s*\|',util,re.M)
        if not m:raise ValueError('Missing resource '+label)
        return int(m[1])
    artifacts=[out/p for p in ('source_manifest.json','verification_sources.json','simulation_session.log','negative_guards/manifest.json')]
    artifacts += [synthdir/p for p in ('synthesize.tcl','synthesize.log','receipt.json','utilization.rpt','ram_cells.txt','queued_scratch_endpoint.dcp','console.log')]
    artifacts += [out/(name+'_sim')/'elaborate.log' for name in ('small','actual','ordering')]
    return dict(status='passed',performance=None,toolchain='Vivado/XSim 2022.2',part='xcu280-fsvh2892-2L-e',
        simulation=dict(boundary_checks=2267,tag1_fences=48,tag1_wraps=24,actual_commands=472689,actual_field_accesses=56588,actual_queries=19,tag2_fences=19,tag2_wraps=4,
                        ordering_checks=6144,ordering_stalls=46060,ordering_full_cycles=dict(request=61627,work=58328,response=34799)),
        guard_failures={k:v['causal_failure'] for k,v in guards['mutations'].items()},
        utilization=dict(luts=used('CLB LUTs*'),lut_as_memory=used('LUT as Memory'),registers=used('CLB Registers'),latches=used('Register as Latch'),bram_tiles=used('Block RAM Tile')),
        ram_cells=rams,warnings=[x for x in synth.splitlines() if x.startswith('WARNING:')],files=files,
        artifacts={str(p):sha(p) for p in artifacts},scope='Closed single-clock endpoint queues only. No externally supplied drain booleans, but COMPLETE persistence remains an adapter contract. No hidden-producer/multi-clock/AXI outstanding proof, backing-address pool RTL, DDR/HBM DMA, formal proof, placed timing or acceleration result.')
if __name__=='__main__':
    out=Path(sys.argv[1]).resolve();record=audit(out);dest=out/'manifest.json'
    if dest.exists() and json.loads(dest.read_text())!=record:raise ValueError('Existing evidence differs')
    dest.write_text(json.dumps(record,indent=2)+'\n')
    summary={k:record[k] for k in ('status','simulation','utilization','scope')};summary['manifest_sha256']=sha(dest)
    (out/'completion_audit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
