from pathlib import Path
import json,hashlib,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,s in m['sources'].items():assert sha(out/'sources'/n)==s['sha256']==sha(Path(s['path']))
 for n,d in m['artifacts'].items():assert sha(out/n)==d
 assert all(r['exit_code']==0 for r in m['commands'])
 functional=ROOT/'results/cost_state_20261025';fm=json.loads((functional/'manifest.json').read_text());fg=json.loads((functional/'source_bound_audit.json').read_text());assert fg['status']=='passed'and fg['manifest_sha256']==sha(functional/'manifest.json')
 assert sha(out/'sources/cost_state_store.sv')==fm['sources']['cost_state_store.sv']['sha256']
 initial=ROOT/'results/cost_state_inputs_20261025/synthetic/initial.bin';original=initial.read_bytes();assert sha(initial)==m['initial_sha256']==sha(out/'state.bin')
 mem=bytearray(original);reloads=reads=writes=bs=r_errors=b_errors=0;pending_r=None;pending_b=False;failed_b_changed=False
 written={2:(68,0x41000000),4:(8,0x40400000),5:(124,0x40800000)}
 for line in(out/'axi.txt').read_text().splitlines():
  r=line.split();op=r[0]
  if op=='N':assert pending_r is None and not pending_b;reloads+=1;assert int(r[1])==reloads;mem=bytearray(original)
  elif op=='A':assert pending_r is None and not pending_b and r[2]=='1';pending_r=int(r[1],16)
  elif op=='R':
   address=int(r[1],16);offset=address-0x1fffff000;assert pending_r==address and 0<=offset<=4032
   assert int(r[2],16).to_bytes(64,'little')==mem[offset:offset+64];pending_r=None;reads+=1
   assert int(r[3])==(2 if reloads==1 else 0);r_errors+=r[3]!='0'
  elif op=='W':
   assert pending_r is None and not pending_b and reloads in written
   offset,value=written[reloads];address=int(r[1],16);mask=int(r[2],16);data=int(r[3],16).to_bytes(64,'little');assert address==0x1fffff000+(offset&~63)and mask==15<<(offset%64)
   assert int.from_bytes(data[offset%64:offset%64+4],'little')==value
   for j in range(64):
    if mask&(1<<j):mem[(offset&~63)+j]=data[j]
   pending_b=True;writes+=1
  elif op=='B':
   assert pending_b;pending_b=False;bs+=1;assert int(r[1])==(2 if reloads==2 else 0);b_errors+=r[1]!='0'
   if r[1]!='0':assert mem!=original and int.from_bytes(mem[68:72],'little')==0x41000000;failed_b_changed=True
  else:raise AssertionError(op)
 assert pending_r is None and not pending_b and reloads==10 and reads==5 and writes==bs==3 and r_errors==b_errors==1 and failed_b_changed
 log=(out/'simulate.log').read_text();assert 'Fatal:'not in log and m['result']in log and '$finish called'in log
 count={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',m['result'])};assert count=={'checks':99,'errors':9,'reloads':10,'reads':5,'writes':3,'bs':3,'cycles':306}
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'counts':count,'r_errors':r_errors,'b_errors':b_errors,'failed_B_changed_backing':True,'same_functional_RTL':True,'scope':'Actual standalone cost-state AXI: R/B errors, AR/AW/W retained on abort, early logical error retirement vs physical drain, timeout, query drift, edit/query violation, full version exhaustion and explicit new-design backing reload recovery. Not joined cost/search or arbitrary protocol corruption coverage.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
