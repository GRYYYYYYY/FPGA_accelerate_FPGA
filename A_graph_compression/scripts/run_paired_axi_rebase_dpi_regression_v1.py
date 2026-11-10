#!/usr/bin/env python3
"""Compare real native models against both frozen DPI-plus-rebase environments."""
import json
from pathlib import Path
import re
import shutil
from check_vitis_kernel import digest,require
from run_axi_rebase_guard_regression_v3 import execute,BIN
from run_axi_rebase_model_regression_v3 import testbench,transactions,SELECTED
from transform_axi_memory_dpi_v2 import transform

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')


def main():
    out=ROOT/'data/derived/paired_axi_rebase_dpi_regression_20261029_v1'
    target=ROOT/'results/paired_axi_rebase_dpi_regression_20261029_v1.json'
    require(not out.exists() and not target.exists(),'Refuse overwrite')
    sp=ROOT/'results/paired_binary_nonzero_axi_structure_audit_20261029_v1.json';structure=json.loads(sp.read_text())
    require(structure['status']=='both_encoded_modes_complete_nonzero_address_environment_structure_independently_verified','Missing structure audit')
    for p,h in structure['files'].items():require(digest(p)==h,'Changed accepted structure input')
    prep_path=ROOT/'results/paired_binary_nonzero_axi_preparation_20261029_v1.json';prep=json.loads(prep_path.read_text())
    files={str(sp):digest(sp),str(prep_path):digest(prep_path)}
    guard=Path(prep['guard_source']);cpp=ROOT/'hardware/sim/axi_dpi_memory_v1.cpp'
    for p in [guard,cpp,Path(__file__).resolve(),ROOT/'scripts/run_axi_rebase_guard_regression_v3.py',ROOT/'scripts/run_axi_rebase_model_regression_v3.py',ROOT/'scripts/transform_axi_memory_dpi_v2.py']:
        files[str(p)]=digest(p)
    out.mkdir();build=out/'dpi';build.mkdir()
    execute(build,'xsc',[str(BIN/'xsc'),'--cppversion','14',str(cpp)])
    library=build/'xsim.dir/work/xsc/libdpi.so';require(library.is_file(),'Missing actual DPI library');files[str(library)]=digest(library)
    records=[]
    for mode in prep['modes']:
        label=mode['label'];parent=BASE/('compressed_batch_bus64_rtl_guarded_v1' if mode['graph_mode']==0 else 'compressed_batch_compact_bus64_rtl_guarded_v1')
        old=json.loads((parent/'plan.json').read_text());models={m['bundle']:m for m in mode['models']}
        files[str(parent/'plan.json')]=digest(parent/'plan.json')
        for bundle in SELECTED:
            m=models[bundle];original=parent/'sim/verilog'/('AESL_axi_master_'+bundle+'.v');wrapped=Path(m['target'])
            original_text=original.read_text();converted,_=transform(original_text)
            require(converted==Path(m['source']).read_text(),'DPI model differs from exact original storage-only conversion')
            directory=out/label/bundle/'sim/verilog';directory.mkdir(parents=True)
            cdata=directory.parent/'tv/cdatafile';cdata.mkdir(parents=True);rdata=directory.parent/'tv/rtldatafile';rdata.mkdir()
            source=parent/'sim/tv/cdatafile'/('c.search_batch_trace_top_v2.autotvin_'+bundle+'.dat')
            require(digest(source)==old['copied_files'][str(source)],'Changed full C payload')
            shutil.copyfile(source,cdata/source.name);require(digest(source)==digest(cdata/source.name),'Different copied C payload')
            reference=original_text.replace('module AESL_axi_master_'+bundle,'module REF_AESL_axi_master_'+bundle,1)
            reference=reference.replace('"../tv/rtldatafile/rtl.search_','"../tv/rtldatafile/ref.search_',1)
            (directory/'reference.v').write_text(reference)
            tb,width,depth=testbench(original_text,bundle)
            if bundle=='batch_input_mem':
                require(tb.count('read_words(0,1);')==1 and depth<=256,'Unexpected readonly test shape')
                tb=tb.replace('read_words(0,1);','read_words(0,DEPTH-1);')
            (directory/'model_tb.sv').write_text(tb)
            for p in [source,cdata/source.name,original,Path(m['source']),wrapped,directory/'reference.v',directory/'model_tb.sv']:files[str(p)]=digest(p)
            execute(directory,'xvlog',[str(BIN/'xvlog'),'--sv',str(guard),str(wrapped),'reference.v','model_tb.sv'])
            execute(directory,'xelab',[str(BIN/'xelab'),'work.model_tb','-mt','off','--debug','off','--timescale','1ns/1ps','--sv_lib','dpi','--sv_root',str(library.parent),'-s','model'])
            log=execute(directory,'positive',[str(BIN/'xsim'),'model','-runall','-testplusarg','CASE=0'])
            require(log.count('SELECTED_CASE=0\n')==1 and log.count('MODEL_REBASE_PASS bundle='+bundle+' ')==1,'Wrong/missing positive execution')
            registration=re.findall(r'A_DPI_REGISTER id=(\d+) name=(\S+) bits=(\d+) depth=(\d+) pages=(\d+)',log)
            require(registration==[('0','model_tb.candidate_model.original_model',str(width),str(depth),'4')],'Missing/wrong actual full DPI allocation')
            record=dict(graph_mode=mode['graph_mode'],bundle=bundle,data_bits=width,depth=depth,pages=4,
                        native_reference=True,dpi_registration_verified=True,response_cycles_compared=True)
            if bundle=='batch_input_mem':
                for case in [1,2]:
                    negative=execute(directory,'readonly_'+str(case),[str(BIN/'xsim'),'model','-runall','-testplusarg','CASE='+str(case)],'A_RO_WRITE_VIOLATION')
                    require(negative.count('SELECTED_CASE='+str(case)+'\n')==1 and 'MODEL_REBASE_PASS' not in negative,'Wrong readonly case selected')
                record.update(readonly_full_page_words_read=depth*4,readonly_write_and_zero_strobe_rejected=True)
            else:
                before=transactions(cdata/source.name,width,depth);expected=[list(row) for row in before]
                for tx,row in enumerate(expected):
                    row[0]=int.from_bytes(bytes([0xa0+tx])*(width//8),'little');last=bytearray(row[-1].to_bytes(width//8,'little'))
                    for lane in range(0,width//8,2):last[lane]=0x50+tx
                    row[-1]=int.from_bytes(last,'little')
                a=rdata/('ref.search_batch_trace_top_v2.autotvout_'+bundle+'.dat');b=rdata/('rtl.search_batch_trace_top_v2.autotvout_'+bundle+'.dat')
                require(transactions(a,width,depth)==expected,'Native full output differs from independent data oracle')
                require(transactions(b,width,depth)==expected and digest(a)==digest(b),'DPI-plus-rebase complete outputs differ')
                files[str(a)]=digest(a);files[str(b)]=digest(b);record['all_output_words_verified']=depth*4
            for p in directory.iterdir():
                if p.is_file() and p.name.endswith(('.log','.receipt.json')):files[str(p)]=digest(p)
            records.append(record);print(label,bundle,'native_vs_dpi_rebase_verified',flush=True)
    for p in build.iterdir():
        if p.is_file() and p.name.endswith(('.log','.receipt.json')):files[str(p)]=digest(p)
    for p,h in files.items():require(digest(p)==h,'Changed DPI regression evidence')
    report=dict(status='both_modes_six_full_depth_models_native_vs_dpi_rebase_all4pages_verified',files=files,models=records,
                graph_modes=[0,1],models_per_mode=6,full_kernel_verified=False,
                limits=['12 real native/DPI model comparisons; no reduced depths/pages or changed payloads.',
                        'Thirty model structures per mode are audited separately; full4tx/44-pointer DUT execution is still required.',
                        'No new production RTL, FPGA synthesis, physical timing, board or performance result.'])
    with target.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],len(records))


if __name__=='__main__':main()
