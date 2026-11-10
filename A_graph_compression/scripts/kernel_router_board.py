#!/usr/bin/env python3
"""Run explicit platform-bound hybrid routing after full C-model integration verification."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import struct
import subprocess
import time
from check_vitis_kernel import digest,require
from vitis_board import kernel_evidence,verify_files,write_new
from check_kernel_router_board import audit

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--link',type=Path,required=True);p.add_argument('--device',required=True)
    p.add_argument('--execution',choices=['direct','expanded'],required=True);p.add_argument('--cpu',type=int,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--host-report',type=Path,default=ROOT/'data/derived/kernel_router_xrt_20261023_v1/report.json')
    p.add_argument('--cmodel-report',type=Path,default=ROOT/'results/kernel_router_integration_audit_20261023_v1.json')
    p.add_argument('--integration-plan',type=Path,default=ROOT/'data/derived/kernel_router_integration_20261023_v1/plan.json')
    a=p.parse_args();require(a.cpu in os.sched_getaffinity(0),'Requested host CPU unavailable')
    cm=json.loads(a.cmodel_report.read_text());ip=a.integration_plan.resolve()
    require(cm['status']=='four_full_router_vitis_abi_cmodel_conditions_independently_verified','Full C-model integration audit required')
    require(cm['files'].get(str(ip))==digest(ip),'Integration input plan differs');verify_files(cm['files'])
    inputs=json.loads(ip.read_text());verify_files(inputs['files'])
    host=json.loads(a.host_report.read_text())
    require(host['status']=='xrt_router_compiled_mock_exchange_and_shape_preflights_passed_no_hardware_execution'
            and host['no_cpu_kernel_symbols'],'Hardware runner preparation missing')
    verify_files({**host['files'],**host['generated']});binary=a.host_report.resolve().parent/'router'
    require(str(binary) in host['generated'],'Unbound hardware executable')
    ld=a.link.resolve();lp=ld/'plan.json';lr=ld/'receipt.json';link=json.loads(lp.read_text());receipt=json.loads(lr.read_text())
    require(receipt['status']=='linked' and receipt['exit_code']==0 and receipt['plan_sha256']==digest(lp)
            and receipt['log_sha256']==digest(ld/'link.log'),'Platform link incomplete or changed')
    verify_files(link['files']);xclbin=Path(receipt['xclbin']);require(digest(xclbin)==receipt['xclbin_sha256'],'xclbin changed')
    mode,memory=link['mode'],link['memory'];_,bundle,xo=kernel_evidence(link['kernel_report'],mode)
    require(link['command'][-1]==str(xo),'Linked XO differs from audited kernel')
    inp=inputs['inputs'][mode];config=inputs['configs'][mode]
    original=(bundle/mode/'board.txt').read_text().splitlines()[0].split()
    require([inp['image'],config]==original[:2],'Resident graph differs from audited kernel workload')
    cfg=struct.unpack('<32I',Path(config).read_bytes());out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    command=['taskset','-c',str(a.cpu),str(binary),inp['image'],inp['fixture'],inp['sites'],'4096','80','200000','8',
             a.execution,config,str(xclbin),a.device,memory,str(out/'transport')]
    files={**host['files'],**host['generated'],**link['files']}
    deps=[Path(__file__).resolve(),ROOT/'scripts/check_kernel_router_board.py',ROOT/'scripts/check_kernel_router.py',
          ROOT/'scripts/vitis_board.py',ROOT/'scripts/check_vitis_kernel.py',a.cmodel_report.resolve(),ip,a.host_report.resolve(),lp,lr,ld/'link.log',xclbin]
    deps.extend(Path(x) for x in [*inp.values(),config,inputs['references'][mode]])
    files.update({str(q):digest(q) for q in deps})
    write_new(out/'plan.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'owner_pid':os.getpid(),
        'files':files,'command':command,'mode':mode,'memory':memory,'execution':a.execution,'cpu':a.cpu,
        'reference':inputs['references'][mode],'node_count':cfg[2],
        'scope':'Full CPU routing through explicit real XRT adjacency, two batches, partial14-instance site model.'})
    before=time.monotonic_ns()
    with (out/'router.raw.json').open('x') as stdout,(out/'router.log').open('x') as stderr:
        child=subprocess.Popen(command,stdout=stdout,stderr=stderr)
        write_new(out/'submission.json',{'owner_pid':os.getpid(),'child_pid':child.pid,'command':command})
        code=child.wait()
    elapsed=(time.monotonic_ns()-before)/1e6;verify_files(files)
    write_new(out/'receipt.json',{'exit_code':code,'process_wall_ms':elapsed,'plan_sha256':digest(out/'plan.json'),
        'raw_sha256':digest(out/'router.raw.json'),'log_sha256':digest(out/'router.log')})
    require(code==0,'Hybrid hardware routing failed; inspect preserved outputs')
    checked=audit(out);write_new(out/'audit.json',checked)
    print(json.dumps({'status':checked['status'],'output':str(out)}))


if __name__=='__main__':main()
