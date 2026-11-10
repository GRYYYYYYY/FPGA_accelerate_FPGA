"""Export a copied, RTL-verified 2022.2 component without changing original projects."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
HLS=ROOT.parent.parent.parent/'Xilinx/Vitis_HLS/2022.2/bin/vitis_hls'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--component',choices=['node_occupancy','site_request'],required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--cpu',type=int,default=115);a=p.parse_args()
    # Explicit installation path; independent of the repository nesting.
    hls=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')
    component=a.component;top='search_'+component+'_top';out=a.output.resolve()
    version='v3' if component=='node_occupancy' else 'v2'
    rtl=ROOT/'results'/f'{component}_rtl_audit_20261024_{version}.json';r=json.loads(rtl.read_text())
    require(r['status']==f'production_{component}_full_depth_'+('28' if component=='node_occupancy' else '34')+'_transactions_rtl_verified','RTL gate missing')
    for path,h in r['files'].items():require(digest(path)==h,'Changed RTL evidence '+path)
    original=ROOT/'build'/f'{component}_hls_20261024_v1'
    out.mkdir(parents=True,exist_ok=False);project=out/'project'
    shutil.copytree(original,project,ignore=lambda path,names:[n for n in names if Path(path)==original/'solution' and n in ['sim','csim']])
    syn={}
    for path in (original/'solution/syn').rglob('*'):
        if path.is_file():
            copied=project/path.relative_to(original);require(digest(path)==digest(copied),'Changed synthesis copy')
            syn[str(path)]=digest(path);syn[str(copied)]=digest(copied)
    xo=out/(top+'.xo');flow=out/'export.tcl'
    flow.write_text('cd {'+str(out)+'}\nopen_project project\nopen_solution solution\nexport_design -format xo -rtl verilog -output {'+str(xo)+'}\nputs RESIDENT_XO_EXPORT_COMPLETE\nexit\n')
    files={str(path):digest(path) for path in [rtl,flow,Path(__file__).resolve(),ROOT/'scripts/check_vitis_kernel.py']}
    command=['taskset','-c',str(a.cpu),str(hls),'-f',str(flow)]
    plan=dict(component=component,top=top,files=files,synthesis=syn,command=command,project=str(project),xo=str(xo))
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',stage='export')
    def update():
        temp=out/'state.tmp';temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(out/'state.json')
    update()
    try:
        with (out/'export.log').open('x') as log:
            child=subprocess.Popen(command,cwd=out,env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1'},stdout=log,stderr=subprocess.STDOUT)
            state['child_pid']=child.pid;update();code=child.wait()
        (out/'receipt.json').write_text(json.dumps(dict(command=command,exit_code=code,log_sha256=digest(out/'export.log')),indent=2)+'\n')
        text=(out/'export.log').read_text();require(code==0 and 'ERROR:' not in text and 'RESIDENT_XO_EXPORT_COMPLETE' in text and xo.is_file(),'XO export failed; retained without retry')
        for path,h in {**files,**syn}.items():require(digest(path)==h,'Synthesis/input changed during export '+path)
        state.update(status='complete',stage='exported_pending_archive_abi_audit');update()
        print(state['stage'],xo)
    except BaseException as e:
        state.update(status='failed',error=str(e));update();raise


if __name__=='__main__':main()
