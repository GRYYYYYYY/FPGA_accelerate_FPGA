#!/usr/bin/env python3
"""Reuse reviewed synthesis with a full44-port TB; prepare, do not claim RTL pass."""
import json
import os
import resource
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def same_bytes(a,b):
    require(a.stat().st_size==b.stat().st_size,'Snapshot length differs')
    with a.open('rb') as left,b.open('rb') as right:
        while True:
            x=left.read(8388608);y=right.read(8388608);require(x==y,'Full CPU/HLS snapshot bytes differ')
            if not x:break

def main():
    review_path=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_compact_hls_review.json');review=json.loads(review_path.read_text())
    require(review['status']=='compressed_batch_trace_compact_integrated_control_csim_synthesis_verified_rtl_pending','Missing synthesis gate')
    cpu_path=ROOT/'results/compressed_batch_rtl_full_depth_cpu_20261025_v1.json';cpu=json.loads(cpu_path.read_text());require(cpu['ports']==44 and cpu['transactions_per_mode']==4,'Missing full-depth CPU gate')
    for p,h in {**review['files'],**cpu['files']}.items():require(digest(p)==h,'Changed reviewed input '+p)
    require(shutil.disk_usage('/tmp').free>128*1024**3,'Insufficient local setup space')
    out=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_compact_cosim_setup');project=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_compact_cosim_project');out.mkdir(exist_ok=False);require(not project.exists(),'Existing project; do not repeat')
    original=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_compact_hls_project');old_source=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_compact_hls/source')
    source=out/'source';shutil.copytree(old_source,source);tb=source/'test_compressed_batch_rtl_full_depth.cpp';shutil.copyfile(ROOT/'hardware/vitis'/tb.name,tb)
    shutil.copytree(original,project,ignore=lambda p,n:[x for x in n if Path(p)==original/'solution' and x in ['sim','csim']])
    app=project/'hls.app';xml=ET.parse(app);files=xml.getroot().findall('files/file');tbs=[f for f in files if f.attrib.get('tb')=='1'];require(len(tbs)==1,'Unexpected TB list');require(tbs[0].attrib['name']==str(old_source/'test_compressed_batch_rtl_full_depth.cpp'),'Different original TB')
    tbs[0].attrib['name']=str(tb);xml.write(app,encoding='utf-8',xml_declaration=True);initial=out/'initial.hls.app';shutil.copyfile(app,initial)
    synthesis={}
    for p in (original/'solution/syn').rglob('*'):
        if p.is_file():
            q=project/p.relative_to(original);require(digest(q)==digest(p),'Different synthesis clone');synthesis[str(p)]=digest(p);synthesis[str(q)]=digest(q)
    flow=out/'prepare.tcl';flow.write_text('cd {'+str(project.parent)+'}\nopen_project {'+project.name+'}\nopen_solution solution\ncsim_design -clean\nputs FULL44_BATCH_CSIM_COMPLETE\ncosim_design -rtl verilog -trace_level none -setup\nputs FULL44_BATCH_COSIM_SETUP_COMPLETE\nexit\n')
    inputs={str(p):digest(p) for p in [review_path,cpu_path,flow,initial,Path(__file__).resolve(),ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json']}
    inputs.update({str(p):digest(p) for p in source.iterdir() if p.is_file()})
    command=['prlimit','--stack=67108864:67108864','--','taskset','-c','123','/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls','-f',str(flow)]
    (out/'plan.json').write_text(json.dumps(dict(files=inputs,synthesis=synthesis,command=command,project=str(project),original_project=str(original),cpu_reference=str(Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_rtl_tb_cpu_v2')),transactions=4,graph_mode=1,rtl_simulated=False),indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',stage='full_depth_csim_and_cosim_setup')
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    save();pointer=ROOT/'data/derived/compressed_batch_compact_cosim_setup_20261025_v1';pointer.mkdir(exist_ok=False);(pointer/'location.json').write_text(json.dumps(dict(bundle=str(out),project=str(project),owner_pid=os.getpid(),local_storage_ephemeral=True),indent=2)+'\n')
    env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_BATCH_RTL_SNAPSHOT_PREFIX':str(out/'hls')}
    try:
        with (out/'prepare.log').open('x') as log:
            child=subprocess.Popen(command,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_FSIZE,(8589934592,8589934592)));state['child_pid']=child.pid;save();code=child.wait()
        (out/'prepare.receipt.json').write_text(json.dumps(dict(command=command,exit_code=code,log_sha256=digest(out/'prepare.log')),indent=2)+'\n')
        text=(out/'prepare.log').read_text();require(code==0 and 'ERROR:' not in text and 'FULL44_BATCH_COSIM_SETUP_COMPLETE' in text,'Full-depth setup failed')
        require('FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=1 ports=44 transactions=4' in text,'Missing44 port snapshots')
        for p,h in {**inputs,**synthesis}.items():require(digest(p)==h,'Setup changed reviewed source/RTL')
        for transaction in range(4):same_bytes(out/f'hls_1_{transaction}.bin',Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_rtl_tb_cpu_v2')/f'cpu_1_{transaction}.bin')
        directory=project/'solution/sim/verilog';top='search_batch_trace_top_v2'
        require(re.search(r'parameter AUTOTB_TRANSACTION_NUM = 4;', (directory/(top+'.autotb.v')).read_text()),'Wrong generated transaction count')
        for p in (original/'solution/syn/verilog').glob('*.v'):require(digest(directory/p.name)==digest(p),'Generated simulation RTL differs')
        setup_files={}
        for parent in [directory,project/'solution/sim/tv/cdatafile']:
            for p in parent.iterdir():
                if p.is_file() and p.suffix in ['.v','.sv','.dat','.tcl','.sh','.prj','.ini']:setup_files[str(p)]=digest(p)
        for p in [project/'solution/sim/wrapc_pc/cosim.pc.exe',project/'solution/sim/wrapc_pc'/('apatb_'+top+'.cpp'),app]:setup_files[str(p)]=digest(p)
        report=dict(status='full44_depth_four_transaction_csim_snapshots_and_cosim_setup_verified_rtl_pending',files={**inputs,**synthesis,**setup_files},project=str(project),transactions=4,mode='compact',rtl_simulated=False,limits=['Unchanged synthesis; no new csynth required or claimed','Complete CPU/HLS port payloads match, but xelab/xsim/original RTL postcheck not yet executed','Logical4-node synthetic routing; full declared pointer depths, not a full production traffic run','RTL const-region AXI-write integrity needs generated-model monitoring; host readonly snapshots alone do not prove it'])
        for p in [out/'plan.json',out/'prepare.log',out/'prepare.receipt.json',*[out/f'hls_1_{i}.bin' for i in range(4)]]:report['files'][str(p)]=digest(p)
        with (out/'setup.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
        state.update(status='complete',stage='full_depth_setup_verified_rtl_execution_pending');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
