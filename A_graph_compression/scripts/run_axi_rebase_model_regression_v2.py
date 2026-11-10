#!/usr/bin/env python3
"""Compare unchanged full-depth model instances with wrapped instances on all4 pages."""
import json
from pathlib import Path
import re
import shutil

from check_vitis_kernel import digest, require
from prepare_compact_nonzero_axi_models_v1 import interface
from run_axi_rebase_guard_regression_v2 import execute, BIN

ROOT = Path(__file__).resolve().parents[1]
SELECTED = ['completion_mem', 'state_mem', 'site_scratch_mem', 'node_meta_mem', 'tree_meta_mem', 'batch_input_mem']


def parameter_number(value):
    match = re.fullmatch(r"32'd\s*(\d+)", value.strip())
    require(match is not None, 'Unexpected generated numeric parameter')
    return int(match[1])


def testbench(original, bundle):
    module, ports, parameters, declarations = interface(original, bundle)
    values = dict(parameters); width = parameter_number(values[bundle+'_DATA_BITWIDTH'])
    depth = parameter_number(values[bundle+'_mem_depth']); pre = 'TRAN_'+bundle+'_'
    lines = ['`timescale 1ns/1ps', 'module model_tb;']
    lines += ['parameter '+n+' = '+v+';' for n, v in parameters]
    lines += [f'localparam BITS={width}, DEPTH={depth}, BYTES={width//8}, SIZE={width.bit_length()-4};']
    outputs = []; inputs = []
    for decl in declarations:
        name = re.search(r'(\w+)\s*;$', decl)[1]
        if decl.startswith('input'):
            inputs.append(name); lines.append(decl.replace('input', 'reg', 1))
        else:
            outputs.append(name)
            for prefix in ['ref_', 'dut_']:
                lines.append(re.sub(r'\b'+name+r'\b', prefix+name, decl.replace('output', 'wire', 1)))
    lines += ['integer tx, j, received, requests=0, response_samples=0, test_case=0;', 'always #5 clk=~clk;']
    for ref in [True, False]:
        connections = []
        for p in ports:
            if p in outputs: expression = ('ref_' if ref else 'dut_')+p
            elif not ref and p in [pre+'AWADDR', pre+'ARADDR']: expression = p+"+64'd4096"
            elif ref and p == pre+'AWVALID': expression = '(test_case==0 ? '+p+" : 1'b0)"
            else: expression = p
            connections.append('.'+p+'('+expression+')')
        lines += [('REF_'+module if ref else module)+(' reference_model (' if ref else ' candidate_model ('),
                  '    '+',\n    '.join(connections)+'\n);']
    # Every non-address output must agree at each observed cycle, including stalled responses.
    lines += ['always @(negedge clk) begin #1;', 'if(reset===1 && test_case==0) begin',
              '  if ({'+','.join('ref_'+p for p in outputs)+'} !== {'+','.join('dut_'+p for p in outputs)+'})',
              '    $fatal(1,"MODEL_RESPONSE_DIFF");',
              '  response_samples=response_samples+1;', 'end', 'end']
    lines += ['task read_words(input [63:0] address,input [7:0] length); begin',
              f'  @(negedge clk); {pre}ARADDR=address;{pre}ARLEN=length;{pre}ARSIZE=SIZE;{pre}ARBURST=1;{pre}ARVALID=1;{pre}RREADY=1;',
              f'  @(posedge clk);while(dut_{pre}ARREADY!==1)@(posedge clk);',
              f'  @(negedge clk);{pre}ARVALID=0;received=0;',
              '  while(received<=length) begin @(posedge clk);',
              f'    if(dut_{pre}RVALID===1 && {pre}RREADY===1) begin',
              f'      if(dut_{pre}RRESP!==0 || dut_{pre}RLAST!==(received==length) || (^dut_{pre}RDATA)===1\'bx)$fatal(1,"BAD_READ_RESPONSE");',
              '      received=received+1;', '    end', '  end',
              f'  @(negedge clk);{pre}RREADY=0;requests=requests+1;', 'end endtask']
    lines += ['task write_word(input [63:0] address,input [7:0] value,input [BYTES-1:0] mask); begin',
              f'  @(negedge clk);{pre}WSTRB=mask;{pre}AWADDR=address;{pre}AWLEN=0;{pre}AWSIZE=SIZE;{pre}AWBURST=1;{pre}AWVALID=1;{pre}BREADY=1;',
              f'  @(posedge clk);while(dut_{pre}AWREADY!==1)@(posedge clk);',
              f'  @(negedge clk);{pre}AWVALID=0;{pre}WVALID=1;{pre}WLAST=1;{pre}WSTRB=mask;',
              f'  for(j=0;j<BYTES;j=j+1){pre}WDATA[j*8+:8]=value;',
              f'  @(posedge clk);while(dut_{pre}WREADY!==1)@(posedge clk);',
              f'  @(negedge clk);{pre}WVALID=0;{pre}WLAST=0;',
              f'  @(posedge clk);while(dut_{pre}BVALID!==1)@(posedge clk);',
              f'  if(dut_{pre}BRESP!==0)$fatal(1,"BAD_WRITE_RESPONSE");',
              f'  @(negedge clk);{pre}BREADY=0;requests=requests+1;', 'end endtask']
    lines += ['initial begin']+['  '+p+'=0;' for p in inputs]
    lines += ['  if(!$value$plusargs("CASE=%d",test_case))test_case=0;',
              '  repeat(5)@(negedge clk);reset=1;',
              '  for(tx=0;tx<4;tx=tx+1) begin',
              '    @(negedge clk);ready=1;@(negedge clk);ready=0;repeat(3)@(negedge clk);']
    if bundle == 'batch_input_mem':
        lines += ["    if(test_case==1)write_word(0,8'hff,{BYTES{1'b1}});",
                  "    if(test_case==2)write_word(0,8'hff,{BYTES{1'b0}});",
                  '    if(test_case!=0)begin $display("UNEXPECTED_ACCEPTANCE");$finish;end',
                  '    read_words(0,1);']
    else:
        lines += ['    read_words(0,DEPTH>3?3:DEPTH-1);',
                  "    write_word(0,8'ha0+tx,{BYTES{1'b1}});", '    read_words(0,0);',
                  "    write_word((DEPTH-1)*BYTES,8'h50+tx,{BYTES/2{2'b01}});", '    read_words((DEPTH-1)*BYTES,0);',
                  "    write_word(0,8'hff,{BYTES{1'b0}});"]
    lines += ['    repeat(4)@(negedge clk);done=1;@(negedge clk);done=0;repeat(4)@(negedge clk);',
              '  end', f'  if(requests!={4 if bundle == "batch_input_mem" else 24} || response_samples<100)$fatal(1,"INCOMPLETE_MODEL_TEST");',
              f'  $display("MODEL_REBASE_PASS bundle={bundle} width={width} depth={depth} pages=4 requests=%0d samples=%0d",requests,response_samples);',
              '  $finish;', 'end', 'initial begin #200000;$fatal(1,"MODEL_TEST_TIMEOUT");end', 'endmodule']
    return '\n'.join(lines)+'\n', width, depth


def transactions(path, width, depth):
    raw = path.read_bytes(); word_bytes = width//8
    if raw.startswith(b'[[[runtime]]]'):
        lines = raw.decode().splitlines(); at = 1; rows = []
        for tx in range(4):
            require(re.fullmatch(r'\[\[transaction\]\]\s+'+str(tx), lines[at]) is not None, 'Wrong text transaction')
            at += 1; row = []
            for _ in range(depth):
                require(re.fullmatch('0x[0-9a-fA-F]+', lines[at]) is not None, 'Unknown/malformed data')
                value = int(lines[at], 16); require(value < 1 << width, 'Word too wide'); row.append(value); at += 1
            require(lines[at] == '[[/transaction]]', 'Wrong text boundary'); at += 1; rows.append(row)
        require(lines[at:] in [[], ['[[[/runtime]]]']], 'Extra text data')
        return rows
    stride = 8+depth*word_bytes
    require(len(raw) in [stride*4, stride*4+8], 'Wrong complete binary size')
    rows = []
    for tx in range(4):
        start = stride*tx; require(int.from_bytes(raw[start:start+8], 'big') == depth, 'Wrong binary depth')
        rows.append([int.from_bytes(raw[i:i+word_bytes], 'big') for i in range(start+8, start+stride, word_bytes)])
    require(raw[stride*4:] in [b'', bytes.fromhex('5a5aa5a50f0ff0f0')], 'Wrong binary EOF')
    return rows


def main():
    out = ROOT/'data/derived/axi_rebase_model_regression_20261029_v2'; out.mkdir(exist_ok=False)
    proof_path = ROOT/'results/compact_nonzero_axi_models_structure_audit_20261029_v1.json'
    proof = json.loads(proof_path.read_text())
    require(proof['status'] == 'all30_original_model_bodies_and_complete_address_wrapper_connections_independently_verified', 'Missing structure audit')
    for p, h in proof['files'].items(): require(digest(p) == h, 'Frozen wrapper changed')
    prepared = json.loads((ROOT/'results/compact_nonzero_axi_models_preparation_20261029_v1.json').read_text())
    models = {m['bundle']: m for m in prepared['models']}; guard = Path(prepared['guard_source'])
    files = {str(proof_path): digest(proof_path), str(Path(__file__).resolve()): digest(__file__), str(guard): digest(guard),
             str(ROOT/'scripts/run_axi_rebase_guard_regression_v2.py'): digest(ROOT/'scripts/run_axi_rebase_guard_regression_v2.py')}
    records = []
    for bundle in SELECTED:
        row = models[bundle]; original = Path(row['source']); wrapper = Path(row['target'])
        directory = out/bundle/'sim/verilog'; directory.mkdir(parents=True)
        cdata = directory.parent/'tv/cdatafile'; cdata.mkdir(parents=True)
        rtldata = directory.parent/'tv/rtldatafile'; rtldata.mkdir()
        src = original.parent.parent/'tv/cdatafile'/('c.search_batch_trace_top_v2.autotvin_'+bundle+'.dat')
        shutil.copyfile(src, cdata/src.name); require(digest(src) == digest(cdata/src.name), 'C input copy differs')
        text = original.read_text()
        ref = text.replace('module AESL_axi_master_'+bundle, 'module REF_AESL_axi_master_'+bundle, 1)
        if '"../tv/rtldatafile/rtl.search_' in ref:
            ref = ref.replace('"../tv/rtldatafile/rtl.search_', '"../tv/rtldatafile/ref.search_', 1)
        (directory/'reference.v').write_text(ref)
        tb, width, depth = testbench(text, bundle); (directory/'model_tb.sv').write_text(tb)
        for p in [src, cdata/src.name, original, wrapper, directory/'reference.v', directory/'model_tb.sv']: files[str(p)] = digest(p)
        execute(directory, 'xvlog', [str(BIN/'xvlog'), '--sv', str(guard), str(wrapper), 'reference.v', 'model_tb.sv'])
        execute(directory, 'xelab', [str(BIN/'xelab'), 'work.model_tb', '-mt', 'off', '--debug', 'off', '--timescale', '1ns/1ps', '-s', 'model'])
        log = execute(directory, 'positive', [str(BIN/'xsim'), 'model', '-runall', '-testplusarg', 'CASE=0'])
        require(log.count('MODEL_REBASE_PASS bundle='+bundle+' ') == 1, 'Incomplete model regression')
        record = dict(bundle=bundle, data_bits=width, depth=depth, pages=4, response_cycles_compared=True)
        if bundle == 'batch_input_mem':
            for case in [1, 2]:
                execute(directory, 'readonly_'+str(case), [str(BIN/'xsim'), 'model', '-runall', '-testplusarg', 'CASE='+str(case)], 'A_RO_WRITE_VIOLATION')
            record['readonly_write_and_zero_strobe_rejected'] = True
        else:
            a = rtldata/('ref.search_batch_trace_top_v2.autotvout_'+bundle+'.dat')
            b = rtldata/('rtl.search_batch_trace_top_v2.autotvout_'+bundle+'.dat')
            before = transactions(cdata/src.name, width, depth)
            expected = [list(row) for row in before]
            for tx, values in enumerate(expected):
                values[0] = int.from_bytes(bytes([0xa0+tx])*(width//8), 'little')
                last = bytearray(values[-1].to_bytes(width//8, 'little'))
                for lane in range(0, width//8, 2): last[lane] = 0x50+tx
                values[-1] = int.from_bytes(last, 'little')
            require(transactions(a, width, depth) == expected, 'Original model differs from independent complete output oracle')
            require(transactions(b, width, depth) == expected and digest(a) == digest(b), 'Relocated complete outputs differ')
            files[str(a)] = digest(a); files[str(b)] = digest(b)
            record.update(all_output_words_verified=depth*4, output_bytes=a.stat().st_size)
        for p in directory.iterdir():
            if p.is_file() and p.name.endswith(('.log', '.receipt.json')): files[str(p)] = digest(p)
        records.append(record); print(bundle, 'verified', flush=True)
    for name, h in files.items(): require(digest(name) == h, 'Regression evidence changed')
    report = dict(status='six_original_full_depth_models_all4pages_rebased_response_payload_and_readonly_regression_verified',
                  files=files, models=records, full_kernel_verified=False,
                  limits=['Six real generated models covering32/64/128/256/512-bit buses and readonly protection; all30 wrapper structures audited separately.',
                          'Original model capacities,4pages,full input files and every output word retained for these representative models.',
                          'No full4tx/44-pointer DUT execution or physical/board claim.'])
    target = ROOT/'results/axi_rebase_model_regression_20261029_v2.json'
    with target.open('x') as f: json.dump(report, f, indent=2); f.write('\n')
    print(report['status'])


if __name__ == '__main__': main()
