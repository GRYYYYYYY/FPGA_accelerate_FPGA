"""Four-path controller and parameterized export observer component checks."""
from pathlib import Path
import json, shutil, struct, subprocess, sys, time
from run_checkpoint_authority import ROOT, BIN, sha

out = Path(sys.argv[1]).resolve()
mode = sys.argv[2] if len(sys.argv) > 2 else 'path'
assert mode in ['path', 'export']
out.mkdir(); src = out / 'sources'; src.mkdir()
variant = ROOT / 'hardware/variants/path_capacity_v1'
test_variant = ROOT / 'hardware/variants/four_path_v1'
base = out.parent / 'third_warm_full_v2'
third = out.parent / 'followup_iter2_fourth_v1'
assert json.loads((base / 'source_bound_audit.json').read_text())['status'] == 'passed'
assert json.loads((third / 'source_bound_audit.json').read_text())['status'] == 'passed'
if mode == 'path':
    rtl, tb, top = 'route_commit_controller.sv', 'tb_path_capacity.sv', 'tb_path_capacity'
    shutil.copyfile(test_variant / tb, src / tb)
    trace = [t.split() for t in (base/'full/natural_trace.txt').read_text().splitlines()]
    image = [int(t[4],16) for t in trace if t[0]=='THIRD_PATH_WORD' and t[2]=='1']
    assert len(image)==117
    prep = json.loads((third / 'prepare_trace_audit.json').read_text())
    path = prep['path_sink_to_source']
    assert path == [6954, 990178, 558358, 265324, 66893]
    image += [1, 3, 26422, 66893, 6954, 0x9abcdef0, 0x12345678] + path[1:-1] + [0] * 29
    (out / 'image.txt').write_text(''.join(f'{w:08x}\n' for w in image))
    labels = []
    with (third / 'search_final_nodes.u32').open('rb') as f:
        for node in path:
            f.seek(node * 44); u = struct.unpack('<11I', f.read(44))
            payload = sum(u[k] << (32 * j) for j, k in enumerate([0, 1, 3, 4, 5]))
            labels.append(f'{node} {payload:040x}\n')
    (out / 'labels.txt').write_text(''.join(labels))
    plus = ['--testplusarg', 'image=' + str(out / 'image.txt'), '--testplusarg', 'labels=' + str(out / 'labels.txt')]
elif mode == 'query':
    rtl, tb, top = 'query_lifecycle.sv', 'tb_query_lifecycle.sv', 'tb_query_lifecycle'
    original = ROOT / 'hardware/variants/query_lifecycle_v1' / tb
    shutil.copyfile(original, src / 'original_tb.sv')
    s = original.read_text().replace('[1:0]route_slots', '[2:0]route_slots')
    s = s.replace('reg cmd_valid=0,cmd_slot=0;', 'reg cmd_valid=0;reg[1:0]cmd_slot=2;')
    s = s.replace('query_lifecycle #(.MAX_CYCLES(300))dut(.*);', '''query_lifecycle #(.PATH_SLOTS(3),.MAX_CYCLES(300))dut(.*,
 .cp_rebase(1'b0),.cp_rebase_permit(1'b0),.cp_source_version(32'd0),.cp_source_query(2'd0),.cp_source_price(4'd0),
 .active_generation(64'h100000003),.cp_valid(1'b0),.cp_restore(1'b0),.cp_safe(1'b1),.cp_ready(),.cp_busy(),
 .cp_expected_crc(32'd0),.cp_rsp_valid(),.cp_rsp_ready(1'b1),.cp_status(),.cp_crc(),
 .cp_s_valid(1'b0),.cp_s_ready(),.cp_s_index(32'd0),.cp_s_data(32'd0),.cp_s_last(1'b0),
 .cp_m_valid(),.cp_m_ready(1'b1),.cp_m_index(),.cp_m_data(),.cp_m_last());''')
    s = s.replace('route_payload[65:34]', 'route_payload[66:35]').replace('route_payload[97:66]', 'route_payload[98:67]')
    s = s.replace('route_payload[161:130]', 'route_payload[162:131]').replace('route_packet[33:2]', 'route_packet[34:3]')
    s = s.replace('route_packet[1]', 'route_packet[2:1]').replace('cmd_slot=0;', 'cmd_slot=2;').replace('route_slots=1;', 'route_slots=4;')
    s = s.replace("cmd_route_cookie=32'hdeadbeef;", "cmd_route_cookie=32'hdeadbeef;cmd_slot=0;")
    s = s.replace('  $fclose(events);', '  reset_case;cmd_slot=3;launch(27);finish(1,0);if(service_count||searches||routes)$fatal(1,"invalid slot side effects");\n  $fclose(events);')
    (src / tb).write_text(s)
    plus = []
else:
    rtl, tb, top = 'export_manifest.sv', 'tb_export_manifest.sv', 'tb_export_manifest'
    original = ROOT / 'hardware/variants/owner_g3_publish_v1' / tb
    s = original.read_text()
    shutil.copyfile(original, src / 'original_tb.sv')
    if mode == 'export':
        s = s.replace('selected_query=3,active_slots=3;', 'selected_query=3;reg[3:0]active_slots=15;')
        s = s.replace('active_slots=3;', 'active_slots=15;').replace('pw[0:77]', 'pw[0:155]')
        s = s.replace('export_manifest dut', 'export_manifest #(.PATH_SLOTS(4)) dut')
        s = s.replace('i<78', 'i<156').replace('i==77', 'i==155').replace('s<2', 's<4')
        s = s.replace('s?67922:204279', 's==3?6954:(s==2?151354:(s?67922:204279))')
        s = s.replace('mode==2&&i==5', 'mode==2&&i==122').replace('mode==3&&i==20', 'mode==3&&i==137')
        s = s.replace('path_last=i==155;', 'path_last=i==155||(mode==4&&i==116);')
        s = s.replace('path_last);@(negedge clk);', 'path_last);@(negedge clk);if(mode==4&&i==116)break;')
        s = s.replace('  $display("EXPORT_MANIFEST_PASS', '''  setup;labels;pw[118]=33;paths(0);ck(fault&&!manifest_ready,"fourth slot length");state_line(14);pw[118]=3;
  setup;labels;paths(4);ck(fault&&!manifest_ready,"old three-slot stream rejected");state_line(15);
  $display("EXPORT_MANIFEST_PASS''')
    (src / tb).write_text(s)
    plus = ['--testplusarg', 'trace=' + str(out / 'events.txt')]
shutil.copyfile(variant / rtl, src / rtl)
shutil.copyfile(variant / 'build.py', src / 'build.py')
shutil.copyfile(Path(__file__), src / 'runner.py')
(out / 'run.tcl').write_text('run 2ms\nquit\n')
m = dict(status='running', mode=mode, sources={p.name: sha(p) for p in src.iterdir()},
         input_audits={str(p): sha(p / 'source_bound_audit.json') for p in [base, third]},
         commands=[], scope='Component-only. Native path controller, CPU q4 backtrace and captured G3 prefix; registered mock owner/label services. Export observer unit uses synthetic handshake callbacks. No full q4 RTL or DDR/warm proof.')
def save():
    (out / 'manifest.json').write_text(json.dumps(m, indent=2) + '\n')
save()
try:
    for stage, args in [
        ('compile', [BIN / 'xvlog', '--sv', src / rtl, src / tb]),
        ('elaborate', [BIN / 'xelab', top, '-s', 'slots', '--debug', 'typical', '--mt', '2']),
        ('simulate', [BIN / 'xsim', 'slots', '--tclbatch', 'run.tcl', '--testplusarg', 'events=' + str(out / 'events.txt'), *plus])]:
        argv = list(map(str, args)); start = time.monotonic()
        with (out / (stage + '.log')).open('w') as f:
            r = subprocess.run(argv, cwd=out, stdout=f, stderr=subprocess.STDOUT, timeout=180)
        m['commands'].append(dict(stage=stage, argv=argv, exit_code=r.returncode, elapsed_s=time.monotonic()-start)); save()
        assert r.returncode == 0, stage
    log = (out / 'simulate.log').read_text()
    marker = 'PATH_CAPACITY_PASS' if mode == 'path' else 'QUERY_LIFECYCLE_PASS' if mode == 'query' else 'EXPORT_MANIFEST_PASS'
    assert marker in log and 'Fatal:' not in log and '$finish called' in log
    m['status'] = 'observed'
except Exception as e:
    m.update(status='failed', error=repr(e)); raise
finally:
    m['artifacts'] = {p.name: sha(p) for p in out.iterdir() if p.is_file() and p.name != 'manifest.json'}
    save()
print('PATH_CAPACITY_UNIT_OBSERVED', mode)
