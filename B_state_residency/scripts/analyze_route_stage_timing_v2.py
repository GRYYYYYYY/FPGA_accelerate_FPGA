"""Index every reported combinational cell, including LUT and MUX levels."""
from pathlib import Path
from collections import Counter, defaultdict
import json
import re
from run_checkpoint_authority import ROOT, sha


def parse_report(text):
    starts = list(re.finditer(r'^Slack \(', text, re.M))
    assert starts, 'No timing path'
    block = text[starts[0].start():starts[1].start() if len(starts)>1 else len(text)]

    def field(pattern):
        match = re.search(pattern, block, re.M)
        assert match, pattern
        return match

    slack = float(field(r'^Slack \([^)]+\)\s*:\s*(-?[\d.]+)ns')[1])
    source = field(r'^\s+Source:\s+(\S+)')[1]
    destination = field(r'^\s+Destination:\s+(\S+)')[1]
    delay = field(r'Data Path Delay:\s+([\d.]+)ns\s+\(logic\s+([\d.]+)ns.*?route\s+([\d.]+)ns')
    levels = field(r'Logic Levels:\s+(\d+)\s+\(([^)]+)\)')
    entries = re.findall(r'([A-Z][A-Z0-9_]*)=(\d+)', levels[2])
    assert ' '.join(f'{name}={count}' for name,count in entries) == levels[2].strip()
    declared = {name:int(count) for name,count in entries}
    assert len(declared) == len(entries) and sum(declared.values()) == int(levels[1])
    rows = []
    for match in re.finditer(r'^\s+([A-Z][A-Z0-9_]*)\s+\(Prop_([^)]+)\)\s+([\d.]+)\s+([\d.]+)\s+([rf])\s+(\S+)\s*$', block, re.M):
        rows.append(dict(type=match[1], arc=match[2], delay_ns=float(match[3]),
                         arrival_ns=float(match[4]), edge=match[5], pin=match[6],
                         cell=match[6].rsplit('/',1)[0]))
    # These three restored fixtures launch at FDRE/C. Reject another format
    # explicitly instead of dropping an unrecognised launch or logic row.
    assert rows and rows[0]['type']=='FDRE' and rows[0]['arc']=='FDRE_C_Q'
    launch, cells = rows[0], rows[1:]
    assert launch['cell'] == source.rsplit('/',1)[0]
    assert len(cells)==int(levels[1]) and dict(Counter(x['type'] for x in cells))==declared, 'Incomplete combinational cell rows'
    assert abs(sum(x['delay_ns'] for x in rows)-float(delay[2]))<0.02, 'Logic delay mismatch'
    luts = [x for x in cells if re.fullmatch(r'LUT[1-6]',x['type'])]
    nets = []
    for match in re.finditer(r'^\s+net \(fo=(\d+), ([^)]+)\)\s+([\d.]+)\s+([\d.]+)\s+(\S+)\s*$', block, re.M):
        nets.append(dict(fanout=int(match[1]),placement=match[2],delay_ns=float(match[3]),
                         arrival_ns=float(match[4]),name=match[5]))
    unplaced = [n for n in nets if n['placement']=='unplaced']
    assert len(unplaced)==len(cells)+1, 'Incomplete data-net rows'
    assert abs(sum(n['delay_ns'] for n in unplaced)-float(delay[3]))<0.02, 'Net delay mismatch'
    groups = defaultdict(lambda:dict(levels=0,logic_delay_ns=0.0))
    segments = []
    for cell in cells:
        hierarchy = cell['cell'].rsplit('/',1)[0]
        groups[hierarchy]['levels'] += 1
        groups[hierarchy]['logic_delay_ns'] += cell['delay_ns']
        if not segments or segments[-1]['hierarchy']!=hierarchy:
            segments.append(dict(hierarchy=hierarchy,levels=0))
        segments[-1]['levels'] += 1
    return dict(source=source,destination=destination,slack_ns=slack,
                data_delay_ns=float(delay[1]),logic_delay_ns=float(delay[2]),
                estimated_net_delay_ns=float(delay[3]),logic_levels=len(cells),
                lut_levels=len(luts),primitive_counts=declared,launch_cell=launch,
                logic_cells=cells,luts=luts,ordered_hierarchy_segments=segments,
                hierarchy_totals=dict(groups),unplaced_data_nets=unplaced,
                highest_fanout_unplaced_nets=sorted(unplaced,key=lambda n:n['fanout'],reverse=True)[:10])


def main():
    base = Path('/tmp/B_state_residency_offer_20261025')
    gate = json.loads((base/'route_stage_synth_followup_v1/manifest.json').read_text())
    assert gate['status']=='observed' and gate['stage']=='complete'
    p = base/'route_stage_synth_v1'
    m = json.loads((p/'manifest.json').read_text())
    a = json.loads((p/'source_bound_audit.json').read_text())
    rp = ROOT/'results/route_stage_synth_v1_restore_20261025.json'
    r = json.loads(rp.read_text())
    assert m['status']=='observed' and a['status']==r['status']=='passed' and r['audit_byte_identical']
    assert a['manifest_sha256']==sha(p/'manifest.json') and r['audit_sha256']==sha(p/'source_bound_audit.json')
    assert a['check_timing_counts']['loops']==0 and not a['timing_loop_warnings']
    report = p/'timing_synth.rpt'
    assert sha(report)==a['artifact_sha256'][report.name]
    result = parse_report(report.read_text())
    assert result['slack_ns']==a['preplacement_wns_ns']
    result.update(status='source_bound_worst_setup_path_navigation',analyzer_sha256=sha(Path(__file__)),
                  audit_sha256=sha(p/'source_bound_audit.json'),restore_receipt_sha256=sha(rp),
                  report_sha256=sha(report),
                  scope='Literal first/worst setup path of the restored matched OOC report. All declared combinational cells are counted, including MUX levels. Hierarchy groupings are navigation, not RTL proof. Data-net delays are unplaced estimates; clock nets tagged unset are excluded. No physical or board-speed extrapolation.')
    for label,filename,digest in [
        ('path_area_reference','route_path_timing_path_20261029.json',m['reference_audit_sha256']),
        ('cp_timing_reference','checkpoint_edit_timing_path_20261028.json',m['cp_timing_reference']['audit_sha256'])]:
        path = ROOT/'results'/filename
        baseline = json.loads(path.read_text())
        assert baseline['audit_sha256']==digest
        comparison = dict(baseline_source=baseline['source'],baseline_destination=baseline['destination'],
                          baseline_slack_ns=baseline['slack_ns'],baseline_logic_levels=baseline['logic_levels'],
                          same_endpoint_names=result['source']==baseline['source'] and result['destination']==baseline['destination'],
                          slack_delta_ns=result['slack_ns']-baseline['slack_ns'],
                          logic_level_delta=result['logic_levels']-baseline['logic_levels'],
                          logic_delay_delta_ns=result['logic_delay_ns']-baseline['logic_delay_ns'],
                          estimated_net_delay_delta_ns=result['estimated_net_delay_ns']-baseline['estimated_net_delay_ns'],
                          scope='Each design worst reported path; different endpoints are not same-path causal evidence. Logic levels include all reported combinational primitives. Unplaced estimates do not establish physical frequency.')
        result[label] = dict(analysis_sha256=sha(path),comparison=comparison)
    out = ROOT/'results/route_stage_timing_path_20261029.json'
    assert not out.exists()
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('ROUTE_STAGE_TIMING_PATH_INDEXED',result['logic_levels'],'logic levels',result['lut_levels'],'LUT levels','WNS',result['slack_ns'])


if __name__=='__main__':
    main()
