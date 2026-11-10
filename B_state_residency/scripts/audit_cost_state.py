from pathlib import Path
import hashlib,json,sys,struct,math,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,s in m['sources'].items():assert sha(out/'sources'/n)==s['sha256']==sha(Path(s['path']))
 inp=ROOT/'results/cost_state_inputs_20261025';im=json.loads((inp/'manifest.json').read_text());assert im['status']=='passed'and sha(inp/'manifest.json')==m['input_manifest_sha256']
 for n,h in im['sources'].items():assert sha(inp/'sources'/n)==h
 assert sha(ROOT/'data/derived/logicnets_jscl.rrt')==im['input_rrt_sha256']
 def fbits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
 real=inp/'real';layout=im['cases']['real']['layout'];image=(real/'initial.bin').read_bytes();n=layout['nodes'];po=layout['prices_offset'];no=layout['nets_offset']
 assert image[:n*4]==struct.pack('<I',fbits(1))*n and not any(image[n*4:po])and not any(image[po+1024:no])
 factor=struct.unpack('<f',struct.pack('<I',layout['initial_factor_bits']))[0]
 expected_prices=[fbits(1 if i==0 else 1+i*factor)for i in range(256)];assert list(struct.unpack_from('<256I',image,po))==expected_prices
 nets=list(struct.iter_unpack('<ffii',image[no:no+layout['net_count']*16]));assert len(nets)==27960 and sum(r[2]for r in nets)==180326 and all(math.isfinite(x)and math.isfinite(y)and fanout>0 and hpwl>0 for x,y,fanout,hpwl in nets)
 counts={}
 for case,cm in m['cases'].items():
  d=out/case;ic=im['cases'][case];assert cm['status']=='passed'and all(r['exit_code']==0 for r in cm['commands'])
  for name,h in ic['artifacts'].items():assert sha(inp/case/name)==h
  for name,h in cm['artifacts'].items():assert sha(d/name)==h
  assert sha(d/'state.bin')==ic['artifacts']['expected.bin']and(d/'observed.txt').read_bytes()==(inp/case/'expected.txt').read_bytes()
  expected=json.loads((inp/case/'transactions.json').read_text());actual=[];reads=writes=bs=0;pending_read=None;pending_b=False
  for line in(d/'axi.txt').read_text().splitlines():
   r=line.split();op=r[0]
   if op=='A':assert pending_read is None and not pending_b and r[2]=='1';pending_read=int(r[1],16)
   elif op=='R':
    address=int(r[1],16);assert pending_read==address and r[3]=='0';pending_read=None;reads+=1;actual.append(['R',address,int(r[2],16).to_bytes(64,'little').hex()])
   elif op=='W':assert not pending_b and pending_read is None;pending_b=True;writes+=1;actual.append(['W',int(r[1],16),int(r[2],16),int(r[3],16)])
   elif op=='B':assert pending_b and r[1]=='0';pending_b=False;bs+=1
   else:raise AssertionError(op)
  assert pending_read is None and not pending_b and actual==expected
  status_counts={}
  for line in(d/'observed.txt').read_text().splitlines():
   status=line.split()[2];status_counts[status]=status_counts.get(status,0)+1
  count={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])};assert count['reads']==reads==ic['read_transactions']and count['writes']==writes==bs==ic['write_transactions']and count['commands']==ic['commands']and count['version']==18
  count['status_counts']=status_counts;counts[case]=count
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'counts':counts,'real_initial_history_words_checked':n,'real_initial_prices_checked':256,'real_initial_net_records_checked':len(nets),'real_net_fanout_sum':180326,'scope':'Standalone actual AXI design-level store: all R/W bytes and strobes, complete backing images, echo/backpressure, query/host edit fences, publish generation18 and stale generation2 with same low4 tag. Actual CPU initial import; scripted later edits, no route update arithmetic, candidate/cost/pager joins, faults/reload or synthesis proof.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
