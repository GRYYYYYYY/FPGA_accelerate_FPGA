"""Bind new address adaptation tests to frozen native endpoint/checker sources."""
from pathlib import Path
import json,hashlib,re
from make_address64_endpoint import render,testbench,ROOT
from make_address64_carry_tb import render as carry_testbench
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parent=ROOT/'results/record_epoch6_pilot_20261024';pp=parent/'manifest.json';pm=json.loads(pp.read_text());assert pm['status']=='passed'
 frozen=parent/'pilot/sources';expected={p.name:sha(p) for p in frozen.glob('*.sv') if not p.name.startswith('tb_')}
 summaries={}
 for name in ['address64_endpoint_v3_20261024','address64_carry_20261024']:
  out=ROOT/'results'/name;mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed'
  for case,row in m['cases'].items():
   assert row['status']=='passed' and row['parent_sha256']==sha(pp) and all(s['exit_code']==0 for s in row['commands'])
   files=[Path(x) for s in row['commands'] if s['stage']=='compile' for x in s['argv'] if x.endswith('.sv')]
   tb='tb_backing_base_config.sv' if case=='config' else ('tb_address64_endpoint_carry.sv' if 'carry' in name else 'tb_address64_endpoint.sv')
   need={'backing_base_config.sv',tb} if case=='config' else set(expected)|{'backing_base_config.sv','memory_scratch_endpoint_address64.sv',tb}
   assert {p.name for p in files}==need
   for p in files:
    assert sha(p)==next(h for n,h in row['sources'].items() if Path(n).name==p.name)
    if p.name in expected:assert sha(p)==expected[p.name]
    elif p.name=='memory_scratch_endpoint_address64.sv':assert p.read_text()==render()
    elif p.name=='tb_address64_endpoint.sv':assert p.read_text()==testbench()
    elif p.name=='tb_address64_endpoint_carry.sv':assert p.read_text()==carry_testbench()
    elif p.name=='backing_base_config.sv':assert sha(p)==sha(ROOT/'hardware/variants/address64'/p.name)
    else:assert sha(p)==sha(ROOT/'hardware/tb'/p.name)
   lp=out/case/'simulate.log';log=lp.read_text();assert sha(lp)==row['log_sha256'] and 'Fatal:' not in log and '$finish' in log
   if case=='config':assert 'BASE_CONFIG_PASS cases=4 invalid_alignment=1 overflow=1 high_address=1 exact_end=1 locked=1 reset=1' in log
   else:
    assert 'SMALL_STALLS_PASS cases=8 blocked_cycles=800' in log and 'SMALL_32SLOTS_PASS pages=32 fields=5 checkpoints=8 transfers=288 checks=1778 tag_wraps=4' in log
    if 'carry' in name:
     counts=dict((k,int(v)) for k,v in re.findall(r'(aw|ar)=(\d+)',re.search(r'^ADDRESS64_CARRY_PASS (.+)$',log,re.M)[1]));assert counts['aw']>0 and counts['ar']>0
   summaries[name+'/'+case]={'manifest_sha256':sha(mp),'log_sha256':sha(lp)}
 result={'status':'passed','parent_sha256':sha(pp),'cases':summaries,'scope':'config arithmetic, one-time lifetime lock and 32-slot high-address endpoint integration; not synthesis, routed timing, XRT, DMA submission or board validation','generator_sha256':sha(ROOT/'hardware/scripts/make_address64_endpoint.py'),'carry_generator_sha256':sha(ROOT/'hardware/scripts/make_address64_carry_tb.py')}
 (ROOT/'results/address64_endpoint_v3_20261024/source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('ADDRESS64_SOURCE_BOUND_AUDIT_PASS')
if __name__=='__main__':main()
