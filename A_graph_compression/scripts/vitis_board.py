#!/usr/bin/env python3
"""Link an audited XO to an explicit platform, or execute its bound XRT host.

No platform/device is guessed. Existing result directories are never reused.
"""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
from check_vitis_kernel import digest,require
from check_vitis_readback import audit as readback_audit

ROOT=Path(__file__).resolve().parents[1]
VPP=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis/2022.2/bin/v++')

def write_new(path,data):
    with Path(path).open('x') as f:json.dump(data,f,indent=2);f.write('\n')

def verify_files(files):
    for name,value in files.items():require(digest(name)==value,'Bound input changed: '+name)

def kernel_evidence(path,mode):
    path=Path(path).resolve();report=json.loads(path.read_text())
    require(report['status']=='verified_vitis_xo_not_platform_linked','Kernel audit not passed')
    verify_files(report['artifacts'])
    bundle=Path(report['bundle']);plan_path=bundle/'plan.json';plan=json.loads(plan_path.read_text())
    require(digest(plan_path)==report['plan_sha256'],'Kernel plan changed')
    verify_files({**plan['files'],**plan['generated']})
    xo=Path(report['modes'][mode]['xo']);require(str(xo) in report['artifacts'],'Unbound kernel object')
    return report,bundle,xo

def link(a):
    report,bundle,xo=kernel_evidence(a.kernel_report,a.mode)
    platform=a.platform.resolve();require(platform.is_file() and platform.suffix=='.xpfm','Explicit installed .xpfm required')
    config=ROOT/'hardware/vitis'/('hbm.cfg' if a.memory=='HBM[0]' else 'ddr.cfg')
    require(VPP.is_file(),'Vitis2022.2 linker unavailable')
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    command=[str(VPP),'--link','--target','hw','--platform',str(platform),'--config',str(config),
             '--kernel_frequency','200','--temp_dir',str(out/'tmp'),'--log_dir',str(out/'logs'),
             '--report_dir',str(out/'reports'),'-o',str(out/'graph.xclbin'),str(xo)]
    bound={str(p):digest(p) for p in [Path(__file__).resolve(),a.kernel_report.resolve(),platform,config,xo]}
    plan={'created_utc':datetime.now(timezone.utc).isoformat(),'mode':a.mode,'memory':a.memory,
          'kernel_report':str(a.kernel_report.resolve()),'platform':str(platform),'command':command,'files':bound,
          'scope':'Platform hardware link only; no board performance or power.'}
    write_new(out/'plan.json',plan)
    env=os.environ.copy();env['LD_PRELOAD']='/lib/x86_64-linux-gnu/libudev.so.1'
    with (out/'link.log').open('x') as log:
        result=subprocess.run(command,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT)
    verify_files(bound)
    xclbin=out/'graph.xclbin';complete=result.returncode==0 and xclbin.is_file()
    receipt={'status':'linked' if complete else 'failed','exit_code':result.returncode,'plan_sha256':digest(out/'plan.json'),
             'log_sha256':digest(out/'link.log'),'xclbin':str(xclbin),'xclbin_sha256':digest(xclbin) if xclbin.is_file() else None}
    write_new(out/'receipt.json',receipt);require(complete,'Platform link failed; inspect preserved log')
    print(json.dumps(receipt))

def run(a):
    link_dir=a.link.resolve();receipt=json.loads((link_dir/'receipt.json').read_text());plan=json.loads((link_dir/'plan.json').read_text())
    require(receipt['status']=='linked' and receipt['exit_code']==0,'Platform link not complete')
    require(receipt['plan_sha256']==digest(link_dir/'plan.json') and receipt['log_sha256']==digest(link_dir/'link.log'),'Link evidence changed')
    verify_files(plan['files']);xclbin=Path(receipt['xclbin']);require(digest(xclbin)==receipt['xclbin_sha256'],'xclbin changed')
    mode,memory=plan['mode'],plan['memory'];report,bundle,xo=kernel_evidence(plan['kernel_report'],mode)
    host_report=a.host_report.resolve();host=json.loads(host_report.read_text())
    require(host['status']=='compiled_offline_contract_verified','Host preparation not passed');verify_files(host['artifacts'])
    executable=Path(host['executable']);manifest=bundle/mode/'board.txt'
    require(0<a.repetitions<=100,'Invalid repetitions')
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    bound={str(p):digest(p) for p in [Path(__file__).resolve(),host_report,executable,manifest,xclbin,link_dir/'plan.json',link_dir/'receipt.json',link_dir/'link.log']}
    command=[str(executable),str(xclbin),a.device,mode,memory,str(manifest),str(out/'readback'),str(a.repetitions)]
    write_new(out/'plan.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'command':command,'files':bound,
        'mode':mode,'memory':memory,'repetitions':a.repetitions,'manifest':str(manifest),
        'limitations':['No full-router offload or power capture.','Guard transfers, validation and export are included in host application wall time.']})
    with (out/'host.log').open('x') as log:
        result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    verify_files(bound)
    write_new(out/'receipt.json',{'exit_code':result.returncode,'status':'host_complete' if result.returncode==0 else 'failed',
                                 'plan_sha256':digest(out/'plan.json'),'log_sha256':digest(out/'host.log')})
    require(result.returncode==0,'Board execution failed; inspect preserved log')
    checked=readback_audit(out/'readback',manifest,a.repetitions,mode,memory)
    checked['launcher_evidence']={str(p):digest(p) for p in [out/'plan.json',out/'receipt.json',out/'host.log']}
    checked['status']='verified_bound_hardware_adjacency_readback'
    write_new(out/'audit.json',checked)
    print(json.dumps({'status':checked['status'],'batches':len(checked['batches']),'output':str(out)}))

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    l=sub.add_parser('link');l.add_argument('--kernel-report',type=Path,required=True);l.add_argument('--platform',type=Path,required=True)
    l.add_argument('--mode',choices=['csr','compact'],required=True);l.add_argument('--memory',choices=['DDR[0]','HBM[0]'],required=True)
    l.add_argument('--output',type=Path,required=True);l.set_defaults(function=link)
    r=sub.add_parser('run');r.add_argument('--link',type=Path,required=True);r.add_argument('--host-report',type=Path,required=True)
    r.add_argument('--device',required=True);r.add_argument('--repetitions',type=int,default=7);r.add_argument('--output',type=Path,required=True);r.set_defaults(function=run)
    a=p.parse_args();a.function(a)

if __name__=='__main__':main()
