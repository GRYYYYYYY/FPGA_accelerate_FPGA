#!/usr/bin/env python3
"""Exercise the production address guard across widths, bursts and rejection cases."""
import json
import os
from pathlib import Path
import subprocess
import time

from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
BIN = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')


def execute(directory, phase, arguments, expected=None):
    command = ['timeout', '--kill-after=5', '90', 'prlimit', '--as=8589934592:8589934592',
               '--stack=67108864:67108864', '--core=0:0', '--', *arguments]
    start = time.monotonic()
    with (directory/(phase+'.log')).open('x') as log:
        rc = subprocess.run(command, cwd=directory, env={**os.environ, 'LD_PRELOAD': '/lib/x86_64-linux-gnu/libudev.so.1'},
                            stdout=log, stderr=subprocess.STDOUT).returncode
    log = directory/(phase+'.log'); text = log.read_text(errors='replace')
    receipt = dict(command=command, exit_code=rc, elapsed_seconds=time.monotonic()-start,
                   expected_failure=expected, log_sha256=digest(log))
    (directory/(phase+'.receipt.json')).write_text(json.dumps(receipt, indent=2)+'\n')
    if expected:
        require(rc in [0, 1] and expected in text and 'UNEXPECTED_ACCEPTANCE' not in text and 'Fatal:' in text,
                'Did not reject exactly as expected: '+phase)
    else:
        require(rc == 0 and not any(x in text for x in ['ERROR:', 'FATAL', 'Fatal:', 'UNEXPECTED_ACCEPTANCE']), 'Failed '+phase)
    return text


def main():
    out = ROOT/'data/derived/axi_rebase_guard_regression_20261029_v2'; out.mkdir(exist_ok=False)
    guard = ROOT/'hardware/vitis/axi_model_rebase_guard_v1.sv'
    lines = ['`timescale 1ns/1ps', 'module guard_tb;',
             'reg clk=0; always #5 clk=~clk;',
             'reg [4:0] awvalid=0, arvalid=0; reg awready=1, arready=1;',
             'reg [63:0] awaddr=4096, araddr=4096;',
             'reg [7:0] awlen=0, arlen=0; reg [2:0] awsize=0, arsize=0;',
             'reg [1:0] awburst=1, arburst=1; integer test_case=0, w, k, samples=0;',
             'reg [63:0] offset;']
    for i, width in enumerate([32, 64, 128, 256, 512]):
        lines += [f'a_axi_model_rebase_guard_v1 #(.DEPTH(4096),.DATA_BITS({width})) g{i}(',
                  f'.clk(clk),.awvalid(awvalid[{i}]),.awready(awready),.awaddr(awaddr),.awlen(awlen),.awsize(awsize),.awburst(awburst),',
                  f'.arvalid(arvalid[{i}]),.arready(arready),.araddr(araddr),.arlen(arlen),.arsize(arsize),.arburst(arburst));']
    lines += ['initial begin', 'if (!$value$plusargs("CASE=%d",test_case)) test_case=0;',
              'if (test_case==0) begin',
              '  for(w=0;w<5;w=w+1) begin',
              '    for(k=0;k<128;k=k+1) begin',
              '      @(negedge clk); awsize=w+2;arsize=w+2; awlen=k%16;arlen=k%16;',
              '      offset=((k*17)%32)*(64\'d1<<(w+2));',
              '      awaddr=4096+offset;araddr=4096+offset;awvalid=1<<w;arvalid=1<<w;',
              '      @(negedge clk); awvalid=0;arvalid=0;samples=samples+2;',
              '    end',
              '    @(negedge clk); awburst=0;arburst=0;awlen=255;arlen=255;',
              '    awaddr=4096+4095*(64\'d1<<(w+2));araddr=awaddr;awvalid=1<<w;arvalid=1<<w;',
              '    @(negedge clk);awvalid=0;arvalid=0;samples=samples+2;',
              '    @(negedge clk);awsize=0;arsize=0;awburst=1;arburst=1;awlen=0;arlen=0;',
              '    awaddr=4096+4095;araddr=awaddr;awvalid=1<<w;arvalid=1<<w;',
              '    @(negedge clk);awvalid=0;arvalid=0;samples=samples+2;',
              '  end',
              '  @(negedge clk);awready=0;arready=0;awvalid=31;arvalid=31;awaddr=64\'hx;araddr=64\'hz;',
              '  @(negedge clk);awvalid=0;arvalid=0;',
              '  if(samples!=1300)$fatal(1,"WRONG_SAMPLE_COUNT");',
              '  $display("A_REBASE_GUARD_PASS widths=5 accepted_requests=1300 stalled_unknown=1");$finish;',
              'end else begin',
              '  @(negedge clk);awsize=6;arsize=6;awaddr=4096;araddr=4096;',
              '  case(test_case)']
    cases = [
        ('below_aw', 'awvalid=16;awaddr=4095;', 'A_REBASE_BELOW_BASE'),
        ('below_ar', 'arvalid=16;araddr=0;', 'A_REBASE_BELOW_BASE'),
        ('end_aw', 'awvalid=16;awaddr=4096+4096*64;', 'A_REBASE_MODEL_RANGE'),
        ('end_ar', 'arvalid=16;araddr=4096+4096*64;', 'A_REBASE_MODEL_RANGE'),
        ('burst_tail_aw', 'awvalid=16;awaddr=4096+4095*64;awlen=1;', 'A_REBASE_MODEL_RANGE'),
        ('burst_tail_ar', 'arvalid=16;araddr=4096+4095*64;arlen=1;', 'A_REBASE_MODEL_RANGE'),
        ('max_aw', "awvalid=16;awaddr=64'hffffffffffffffff;", 'A_REBASE_MODEL_RANGE'),
        ('max_ar', "arvalid=16;araddr=64'hffffffffffffffff;", 'A_REBASE_MODEL_RANGE'),
        ('unknown_aw', "awvalid=16;awaddr=64'hx;", 'A_REBASE_UNKNOWN'),
        ('unknown_ar', "arvalid=16;araddr=64'hz;", 'A_REBASE_UNKNOWN'),
        ('unknown_len', "awvalid=16;awlen=8'hx;", 'A_REBASE_UNKNOWN'),
        ('unknown_size', "arvalid=16;arsize=3'bx;", 'A_REBASE_UNKNOWN'),
        ('unknown_burst', "awvalid=16;awburst=2'bz;", 'A_REBASE_UNKNOWN'),
        ('size_aw', 'awvalid=16;awsize=7;', 'A_REBASE_SIZE'),
        ('size_ar', 'arvalid=16;arsize=7;', 'A_REBASE_SIZE'),
        ('wrap_aw', 'awvalid=16;awburst=2;', 'A_REBASE_BURST'),
        ('reserved_ar', 'arvalid=16;arburst=3;', 'A_REBASE_BURST'),
        ('cross_4k_aw', 'awvalid=16;awaddr=4096+4032;awlen=1;', 'A_REBASE_4K'),
        ('cross_4k_ar', 'arvalid=16;araddr=4096+4032;arlen=1;', 'A_REBASE_4K'),
        ('narrow_cell_end', 'awvalid=16;awaddr=4096+4096;awsize=0;', 'A_REBASE_MODEL_RANGE'),
    ]
    lines += [str(i)+': begin '+code+' end' for i, (_, code, _) in enumerate(cases, 1)]
    lines += ['default: $fatal(1,"BAD_CASE");', 'endcase',
              '#20;$display("UNEXPECTED_ACCEPTANCE");$finish;', 'end', 'end',
              'initial begin #100000;$fatal(1,"GUARD_TIMEOUT");end', 'endmodule']
    tb = out/'guard_tb.sv'; tb.write_text('\n'.join(lines)+'\n')
    files = {str(p): digest(p) for p in [guard, tb, Path(__file__).resolve()]}
    (out/'plan.json').write_text(json.dumps(dict(files=files, accepted_requests=1300, rejected_cases=cases), indent=2)+'\n')
    execute(out, 'xvlog', [str(BIN/'xvlog'), '--sv', str(guard), str(tb)])
    execute(out, 'xelab', [str(BIN/'xelab'), 'work.guard_tb', '-mt', 'off', '--debug', 'off', '--timescale', '1ns/1ps', '-s', 'guard'])
    text = execute(out, 'positive', [str(BIN/'xsim'), 'guard', '-runall', '-testplusarg', 'CASE=0'])
    require(text.count('A_REBASE_GUARD_PASS widths=5 accepted_requests=1300 stalled_unknown=1') == 1, 'Incomplete positive matrix')
    for i, (name, _, error) in enumerate(cases, 1):
        execute(out, name, [str(BIN/'xsim'), 'guard', '-runall', '-testplusarg', 'CASE='+str(i)], error)
        print(name, 'rejected', flush=True)
    for p, h in files.items(): require(digest(p) == h, 'Guard source changed')
    for p in out.iterdir():
        if p.is_file() and (p.name.endswith(('.log', '.receipt.json')) or p.name == 'plan.json'): files[str(p)] = digest(p)
    result = dict(status='rebase_guard_1300_accepted_requests_and20_invalid_handshakes_verified',
                  files=files, accepted_requests=1300, rejected_cases=[dict(name=n, expected=e) for n, _, e in cases],
                  full_kernel_verified=False, limits=['Guard only; real original memory-model payload and readonly behavior tested separately.',
                                                     'The guard validates the actual generated model cell indexing, not a new general-purpose AXI memory implementation.'])
    target = ROOT/'results/axi_rebase_guard_regression_20261029_v2.json'
    with target.open('x') as f: json.dump(result, f, indent=2); f.write('\n')
    print(result['status'])


if __name__ == '__main__': main()
