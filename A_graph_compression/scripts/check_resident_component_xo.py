"""Verify exported archive RTL provenance and actual pointer/control ABI."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest,require
from resident_router_memory_plan import component_source
ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    b=a.bundle.resolve();require(not a.output.exists(),'Existing XO audit')
    plan=json.loads((b/'plan.json').read_text());state=json.loads((b/'state.json').read_text());receipt=json.loads((b/'receipt.json').read_text())
    require(state['status']=='complete' and state['stage']=='exported_pending_archive_abi_audit','Export incomplete')
    require(receipt['exit_code']==0 and receipt['command']==plan['command'] and receipt['log_sha256']==digest(b/'export.log'),'Invalid export receipt')
    for path,h in {**plan['files'],**plan['synthesis']}.items():require(digest(path)==h,'Changed export dependency '+path)
    top=plan['top'];src=ROOT/'hardware/vitis'/f'{top}.cpp';args=component_source(src,top)
    original=Path(plan['project'])/'solution/syn/verilog'
    expected={p.name:digest(p) for p in original.iterdir() if p.suffix in ('.v','.dat')}
    abi=[];members={}
    with ZipFile(plan['xo']) as z:
        require(len(z.namelist())==len(set(z.namelist())),'Duplicate archive entry')
        xmls=[n for n in z.namelist() if n.endswith('/kernel.xml')];require(len(xmls)==1,'Unexpected kernel XML count')
        kernel=ET.fromstring(z.read(xmls[0])).find('kernel')
        require(kernel is not None and kernel.get('name')==top and kernel.get('hwControlProtocol')=='ap_ctrl_chain','Wrong kernel/control protocol')
        actual={Path(n).name:n for n in z.namelist() if '/hdl/verilog/' in n and Path(n).suffix in ('.v','.dat')}
        require(set(actual)==set(expected),'Exported RTL/data member set differs')
        for name,h in expected.items():
            require(hashlib.sha256(z.read(actual[name])).hexdigest()==h,'Exported RTL/data byte mismatch '+name)
            members[actual[name]]=h
        ports={x.get('name'):x for x in kernel.findall('ports/port')};observed=kernel.findall('args/arg')
        require(len(observed)==len(args),'Argument count mismatch')
        used=[]
        for arg,x in zip(args,observed):
            port='M_AXI_'+arg['bundle'].upper();offset=int(x.get('offset'),0)
            require(x.get('name')==arg['name'] and int(x.get('id'))==arg['id'] and x.get('port')==port,'Pointer argument identity mismatch')
            require(x.get('type')=='void*' and int(x.get('addressQualifier'))==1 and int(x.get('size'),0)==int(x.get('hostSize'),0)==8 and int(x.get('hostOffset'),0)==0,'Pointer ABI mismatch')
            require(offset>=16 and offset%4==0 and all(offset+8<=lo or offset>=hi for lo,hi in used),'Invalid/overlapping register offsets')
            used.append((offset,offset+8));require(ports[port].get('mode')=='master','Wrong memory port mode')
            abi.append(dict(**arg,control_offset=offset,axi_width=int(ports[port].get('dataWidth'))))
        require(set(ports)=={'S_AXI_CONTROL',*['M_AXI_'+x['bundle'].upper() for x in args]},'Unexpected XML ports')
        require(ports['S_AXI_CONTROL'].get('mode')=='slave' and max(hi for _,hi in used)<=int(ports['S_AXI_CONTROL'].get('range'),0),'Control range insufficient')
        members[xmls[0]]=hashlib.sha256(z.read(xmls[0])).hexdigest()
    files=[b/'plan.json',b/'state.json',b/'receipt.json',b/'export.log',Path(plan['xo']),src,Path(__file__).resolve(),ROOT/'scripts/resident_router_memory_plan.py',ROOT/'scripts/check_vitis_kernel.py']
    report=dict(status='rtl_verified_component_xo_archive_and_control_abi_independently_verified',component=plan['component'],
                files={str(p):digest(p) for p in files},archive_members=members,arguments=abi,platform_linked=False,device_executed=False,
                limitations=['Archive provenance and control ABI only; no platform link, memory group compatibility, device allocation, timing or throughput evidence.'])
    with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],len(abi))


if __name__=='__main__':main()
