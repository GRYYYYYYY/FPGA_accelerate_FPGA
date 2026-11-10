#!/usr/bin/env python3
"""Bounded seven-state encoding-mechanism regression; never run the full DUT here."""
import json
import os
import re
import subprocess
from pathlib import Path
from transform_hls_fsm_binary_v1 import transform
from check_hls_fsm_binary_v1 import check_delta
from check_vitis_kernel import digest, require
from run_compact_native_stack_recovery_v1 import atomic

ROOT = Path(__file__).resolve().parents[1]
BIN = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')


def original_module():
    lines = ['module fsm_original(input ap_clk, input ap_rst, input go, input hold, output [6:0] states, output datum);']
    for index in range(1,8):
        lines.append("parameter ap_ST_fsm_state"+str(index)+" = 7'd"+str(1<<(index-1))+';')
    lines += ['(* fsm_encoding = "none" *) reg [6:0] ap_CS_fsm;', 'reg [6:0] ap_NS_fsm;',
              'initial begin', "#0 ap_CS_fsm = 7'd1;", 'end']
    for index in range(1,8):
        lines += ['wire ap_CS_fsm_state'+str(index)+';',
                  'assign ap_CS_fsm_state'+str(index)+" = ap_CS_fsm[32'd"+str(index-1)+'];',
                  'assign states['+str(index-1)+'] = ap_CS_fsm_state'+str(index)+';']
    lines += ['assign datum = go ^ hold ^ ap_CS_fsm_state3;',
              'always @ (posedge ap_clk) begin', "    if (ap_rst == 1'b1) begin",
              '        ap_CS_fsm <= ap_ST_fsm_state1;', '    end else begin',
              '        ap_CS_fsm <= ap_NS_fsm;', '    end', 'end',
              'always @ (*) begin', '    case (ap_CS_fsm)']
    for index in range(1,8):
        lines += ['        ap_ST_fsm_state'+str(index)+' : begin',
                  "            if ((go == 1'b1) & (hold == 1'b0)) begin",
                  '                ap_NS_fsm = ap_ST_fsm_state'+str(index%7+1)+';',
                  '            end else begin',
                  '                ap_NS_fsm = ap_ST_fsm_state'+str(index)+';',
                  '            end', '        end']
    lines += ['        default : begin', "            ap_NS_fsm = 'bx;", '        end',
              '    endcase', 'end', 'endmodule']
    return '\n'.join(lines)+'\n'


TB = '''
module tb_fsm_binary;
reg clk=0, rst=1, go=0, hold=0;
wire [6:0] original_states, binary_states;
wire original_datum, binary_datum;
reg [6:0] coverage=0;
integer r,g,h,k,samples=0,cases=0;
fsm_original original(clk,rst,go,hold,original_states,original_datum);
fsm_binary candidate(clk,rst,go,hold,binary_states,binary_datum);
function automatic logic four(input integer value);
  case(value)
    0: four=1'b0;
    1: four=1'b1;
    2: four=1'bx;
    default: four=1'bz;
  endcase
endfunction
initial begin
  #2;
  if ({original_states,original_datum} !== {binary_states,binary_datum}) $fatal(1,"FSM_MAP_FAIL initial");
  for(r=0;r<4;r=r+1) for(g=0;g<4;g=g+1) for(h=0;h<4;h=h+1) begin
    rst=four(r);go=four(g);hold=four(h);cases=cases+1;
    for(k=0;k<20;k=k+1) begin
      #4;clk=1;
      #1;
      if ({original_states,original_datum} !== {binary_states,binary_datum})
        $fatal(1,"FSM_MAP_FAIL rst=%b go=%b hold=%b sample=%0d",rst,go,hold,samples);
      coverage=coverage|original_states;samples=samples+1;
      #5;clk=0;
    end
  end
  if (coverage !== 7'b1111111 || samples!=1280 || cases!=64) $fatal(1,"FSM_MAP_FAIL coverage");
  $display("FSM_MAP_PASS states=7 cases=64 samples=1280 coverage=%b",coverage);
  $finish;
end
initial begin #15000; $fatal(1,"FSM_MAP_TIMEOUT"); end
endmodule
'''


def main():
    output = ROOT/'data/derived/fsm_binary_four_state_regression_20261025_v1'
    output.mkdir(exist_ok=False)
    original = original_module()
    candidate, ledger = transform(original)
    mapping = check_delta(original, candidate, ledger)
    source = output/'comparison.sv'
    source.write_text('`timescale 1ns/1ps\n'+original+candidate.replace('module fsm_original(', 'module fsm_binary(', 1)+TB)
    atomic(output/'mechanism_ledger.json', ledger)
    prefix = ['timeout','--kill-after=5','90','prlimit','--as=8589934592:8589934592','--stack=67108864:67108864','--core=0:0','--','taskset','-c','118']
    commands = [prefix+[str(BIN/'xvlog'),'--sv',str(source)],
                prefix+[str(BIN/'xelab'),'work.tb_fsm_binary','-mt','off','--debug','off','-s','fsm_binary_mechanism'],
                prefix+[str(BIN/'xsim'),'fsm_binary_mechanism','-runall']]
    inputs = [source, Path(__file__).resolve(), ROOT/'scripts/transform_hls_fsm_binary_v1.py', ROOT/'scripts/check_hls_fsm_binary_v1.py', ROOT/'scripts/audit_hls_fsm_shape_v3.py']
    files = {str(path):digest(path) for path in inputs}
    atomic(output/'plan.json', dict(commands=commands, files=files, states=7, input_level_cases=64, samples=1280,
        scope='Synthetic seven-state encoding mechanism only; no full IP compilation or simulation', address_space_bytes=8*1024**3))
    env = {**os.environ, 'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1'}
    for index, command in enumerate(commands):
        with (output/(str(index)+'.log')).open('x') as log:
            code = subprocess.run(command,cwd=output,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
        path = output/(str(index)+'.log')
        atomic(output/(str(index)+'.receipt.json'),dict(command=command,exit_code=code,log_sha256=digest(path)))
        require(code==0 and not re.search(r'(?im)^\s*(?:ERROR|FATAL)\b|FSM_MAP_FAIL|FSM_MAP_TIMEOUT',path.read_text()), 'Mechanism regression failed stage '+str(index))
    text = (output/'2.log').read_text()
    require(text.splitlines().count('FSM_MAP_PASS states=7 cases=64 samples=1280 coverage=1111111')==1, 'Missing or duplicate complete regression acceptance')
    for path, checksum in files.items():
        require(digest(path)==checksum, 'Regression source changed')
    for path in output.iterdir():
        if path.name in ['plan.json','mechanism_ledger.json'] or path.name.endswith(('.receipt.json','.log')):
            files[str(path)]=digest(path)
    atomic(ROOT/'results/fsm_binary_four_state_regression_20261025_v1.json', dict(status='seven_state_encoding_mechanism_four_state_control_reset_and_outputs_regression_passed',
        states=7, input_level_cases=64, samples=1280, all_seven_states_observed=True, mapping=mapping, files=files,
        full_ip_verified=False, general_formal_equivalence_proven=False,
        limits=['Synthetic seven-state fixture, not the actual43-module candidate or full44-port kernel',
                'Crosses0/1/X/Z on reset/go/hold at clock-sampled observations, not every input history or glitch',
                'No illegal-state injection equivalence, timing signoff, memory reduction or acceleration claim']))
    print('Seven-state mechanism four-state regression passed:64 cases/1280samples')


if __name__=='__main__':
    main()
