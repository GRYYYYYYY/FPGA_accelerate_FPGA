"""Nine bounded native coordinator tests: default compatibility and exclusive contract."""
from pathlib import Path
import importlib.util, json, shutil, subprocess, sys, time
from run_checkpoint_authority import ROOT, sha

p = Path(sys.argv[1]).resolve()
variant = ROOT / 'hardware/variants/recovery_backend_loops_v1'
spec = importlib.util.spec_from_file_location('backend_builder', variant / 'build.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
base, fixed = b.sources(False), b.sources(True)
template = ROOT / 'hardware/variants/multi_owner_recovery_v1/tb_capacity_bound.sv'
s = template.read_text()
s = b.replace_once(s, 'module tb_capacity_bound;', 'module tb_backend_contract;')
s = s.replace('a_rsp_valid', 'a_pending').replace('o_rsp_valid', 'o_pending')
s = b.replace_once(s, ' recovery_coordinator dut(', ''' wire a_reply=a_pending||(EARLY==1&&a_valid);
 wire o_reply=o_pending||(EARLY==2&&o_valid);
 recovery_coordinator PARAMS dut(''')
s = b.replace_once(s, '.a_pending(a_pending)', '.a_rsp_valid(a_reply)')
s = b.replace_once(s, '.o_pending(o_pending)', '.o_rsp_valid(o_reply)')
s = b.replace_once(s, '.a_rsp_cookie(a_rsp_cookie)', '.a_rsp_cookie(a_pending?a_rsp_cookie:a_cookie)')
s = b.replace_once(s, '.o_rsp_cookie(o_rsp_cookie)', '.o_rsp_cookie(o_pending?o_rsp_cookie:o_cookie)')
s = b.replace_once(s,
 '   if(rsp_status!=3||rsp_cookie!=32\'h1001||rsp_corrected||journal_count!=1||permit_work||!fault||caps!=2||gets!=2||authority!=2)$fatal(1,"unavailable capacity did not fail closed within one extra pass");',
 '''   if(rsp_status!=EXPECTED_STATUS||rsp_cookie!=32'h1001||rsp_corrected||journal_count!=1||permit_work||!fault)
    $fatal(1,"contract status/retirement mismatch");
   if(EXPECTED_STATUS==3&&(caps!=2||gets!=2||authority!=2))$fatal(1,"capacity bound changed");
   if(EXPECTED_STATUS==6&&(caps!=0||authority!=1||gets!=(EARLY==2)))$fatal(1,"contract refusal not immediate");''')
s = b.replace_once(s, '  $display("CAPACITY_BOUND_PASS refusals=%0d gets=%0d authority=%0d journal=%0d",caps,gets,authority,journal_count);$finish;',
 '''  $display("BACKEND_CONTRACT_PASS status=%0d refusals=%0d gets=%0d authority=%0d journal=%0d",rsp_status,caps,gets,authority,journal_count);$finish;''')
s = b.replace_once(s, '\nendmodule', '''
 always @(posedge clk)if(!rst)begin
  if(a_valid&&!a_pending)$display("EVENT %0t A_REQUEST %0d %0d",$time,a_node,a_cookie);
  if(a_reply&&a_rsp_ready)$display("EVENT %0t A_REPLY %0d",$time,a_pending?a_rsp_cookie:a_cookie);
  if(o_valid&&!o_pending)$display("EVENT %0t O_REQUEST %0d %0d",$time,o_op,o_cookie);
  if(o_reply&&o_rsp_ready)$display("EVENT %0t O_REPLY %0d %0d",$time,o_status,o_pending?o_rsp_cookie:o_cookie);
 end
endmodule''')
p.mkdir()
(p / 'sources').mkdir()
shutil.copyfile(Path(__file__), p / 'runner.py')
shutil.copyfile(template, p / 'sources/template.sv')
for mode, source in [('baseline', base), ('fixed', fixed)]:
    (p / 'sources' / (mode + '.sv')).write_text(source['recovery_coordinator.sv'])
(p / 'sources/tb_template.sv').write_text(s)
m = dict(status='running', runner_sha256=sha(p / 'runner.py'),
    builder_sha256=sha(variant / 'build.py'), template_path=str(template),
    sources={f.name:sha(f) for f in (p / 'sources').iterdir()}, cases={},
    scope='Native coordinator with modeled authority/owner callbacks and one real journal key. Permanent CAPACITY refusal, two-pass bound, held completion and closed work. Default mode preserves request-cycle replies. Exclusive mode rejects deliberately violated interface assumptions. Not native reader/fence or full-root structural proof.')
def save():
    (p / 'manifest.json').write_text(json.dumps(m, indent=2, sort_keys=True) + '\n')
binpath = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
save()
try:
    for mode in ['baseline', 'default', 'exclusive']:
        for early in [0, 1, 2]:
            name = mode + '_' + str(early)
            d = p / name
            d.mkdir()
            tb = s.replace('EARLY', str(early)).replace('EXPECTED_STATUS', str(6 if mode == 'exclusive' and early else 3))
            tb = tb.replace('PARAMS', '#(.EXCLUSIVE_BACKEND_RESPONSES(1))' if mode == 'exclusive' else '')
            (d / 'tb.sv').write_text(tb)
            (d / 'run.tcl').write_text('run 20us\nquit\n')
            source = p / 'sources' / ('baseline.sv' if mode == 'baseline' else 'fixed.sv')
            commands = [('compile', [binpath/'xvlog', '--sv', source, d/'tb.sv']),
                ('elaborate', [binpath/'xelab', 'tb_backend_contract', '-s', 'test', '--debug', 'typical', '--mt', '2']),
                ('simulate', [binpath/'xsim', 'test', '--tclbatch', 'run.tcl', '--log', 'simulate.log'])]
            c = dict(status='running', mode=mode, early=early, commands=[], tb_sha256=sha(d/'tb.sv'))
            m['cases'][name] = c
            save()
            for stage, argv in commands:
                argv = list(map(str, argv))
                start = time.monotonic()
                with (d/(stage+'.stdout.log')).open('w') as f:
                    r = subprocess.run(argv, cwd=d, stdout=f, stderr=subprocess.STDOUT, timeout=120)
                c['commands'].append(dict(stage=stage, argv=argv, exit_code=r.returncode, elapsed_s=time.monotonic()-start))
                save()
                assert r.returncode == 0, (name, stage)
            log = (d/'simulate.log').read_text()
            assert 'BACKEND_CONTRACT_PASS' in log and '$finish called' in log and 'Fatal:' not in log, name
            c['status'] = 'observed'
            save()
            print(name, 'observed', flush=True)
    m['status'] = 'observed'
except Exception as e:
    m.update(status='failed', error=repr(e))
    raise
finally:
    m['artifacts']={str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*'))
        if f.is_file() and f.suffix in ['.log','.tcl','.sv']}
    save()
print('RECOVERY_BACKEND_NATIVE_OBSERVED')
