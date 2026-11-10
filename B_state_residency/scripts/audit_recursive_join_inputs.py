from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
def f(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for g,b in [('sources',out/'sources'),('artifacts',out)]:
  for n,h in m[g].items():assert sha(b/n)==h,n
 assert len(m['commands'])==2 and all(c['exit_code']==0 for c in m['commands'])
 base=ROOT/'results/recursion_order_20261025';assert sha(base/'source_bound_audit.json')==m['base_audit_sha256']
 src=out/'sources';observer=(src/'cost_observer.txt').read_text();assert (src/'joined.cpp').read_text().replace(observer,'',1)==(base/'sources/immediate.cpp').read_text()
 a=(base/'sources/case.cpp').read_text();b=(src/'case.cpp').read_text();assert a[a.index(' Router r;'):a.index(' r.exploreAndExpand(st,0);')].strip()==b[b.index(' Router r;'):b.index(' uint32_t qw[16]')].strip()
 assert a[a.index(' r.exploreAndExpand(st,0);'):]==b[b.index(' r.exploreAndExpand(st,0);'):]
 log=(out/'execute.log').read_text().splitlines();assert [l for l in log if not l.startswith('C ')]==(base/'immediate_execute.log').read_text().splitlines()
 rows=[l.split()for l in(out/'cost_vectors.txt').read_text().splitlines()];assert len(rows)==2
 upstream=0.0;est=f(.8);wl=f(1-est);expected=[]
 for parent,child in [(0,1),(1,2)]:
  nodecost=f(1+f(child/10));partial=f(f(upstream+nodecost)+wl);h=f(est*(4-child));total=f(partial+h)
  packet=[bits(1),0,bits(1),bits(1),bits(1),1,bits(float(child)),10,bits(upstream),bits(wl),1,bits(est),4-child,0,0]+[0]*8
  result=[bits(1),bits(nodecost),bits(partial),bits(h),bits(total)];expected.append((parent,child,packet,result));upstream=partial
 for row,(p,c,packet,result)in zip(rows,expected):assert list(map(int,row[:2]))==[p,c] and list(map(lambda t:int(t,16),row[2:]))==packet+result
 mapping=[0,8,16,24,32];offsets=[0];edges=[];attrs=[];design=[]
 for n in range(33):
  active=n in mapping;i=mapping.index(n)if active else 0;edges+={0:[8,16],8:[16]}.get(n,[]);offsets.append(len(edges));flags=(1|(2 if i==0 else 0))if active else 0
  attrs.append(struct.pack('<iiBBhhhhhIii',i,i,12,flags,i,0,i,0,1,bits(1),i,-1));design.append(struct.pack('<4I',int(active),0,0,0))
 for n,data,size in [('offsets.u32le',struct.pack('<34I',*offsets),192),('edges.u32le',struct.pack('<3I',*edges),64),('nodes.rrt32',b''.join(attrs),1088),('design.bin',b''.join(design),576)]:assert (out/n).read_bytes()==data+bytes(size-len(data))
 ed=bytearray((out/'design.bin').read_bytes());struct.pack_into('<4I',ed,0,5,2,3,0);struct.pack_into('<4I',ed,128,5,1,1,0);assert (out/'expected_design.bin').read_bytes()==ed
 assert (out/'owners.bin').read_bytes()==bytes(640)
 cost=bytearray(1280)
 for i in range(33):struct.pack_into('<I',cost,i*4,bits(1))
 for i in range(256):struct.pack_into('<I',cost,192+4*i,bits(1))
 struct.pack_into('<4I',cost,1216,0,0,1,10);assert (out/'cost.bin').read_bytes()==cost
 qw=[0x43505331,0,0,32,0,bits(1),bits(wl),bits(est),0,0,60,0,bits(est),bits(1),bits(2),0];assert (out/'connections.bin').read_bytes()==struct.pack('<16I',*qw)
 labels=[l.split()for l in(out/'final_labels.txt').read_text().splitlines()];assert len(labels)==5
 expected_labels={n:[0,0,0xffffffff,0,0]for n in mapping}
 for (p,c,packet,result)in expected:expected_labels[c*8]=[result[4],result[2],p*8,77,0]
 assert {int(t[0]):[int(w,16)for w in t[1:]]for t in labels}==expected_labels
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'original_recursive_source_recovered':True,'physical_mapping':mapping,'actual_CPU_cost_words':56,'scope':m['scope']}
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
