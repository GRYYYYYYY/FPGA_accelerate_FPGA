from pathlib import Path
import hashlib,json,sys,struct,math,mmap,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def fp(u):return struct.unpack('<f',struct.pack('<I',u))[0]
def bits(f):
 try:return struct.unpack('<I',struct.pack('<f',f))[0]
 except OverflowError:return 0xff800000 if f<0 else 0x7f800000
def f32(f):return fp(bits(f))
def signed(u):return u if u<0x80000000 else u-0x100000000
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for name,s in m['sources'].items():assert sha(out/'sources'/name)==s['sha256']==sha(Path(s['path']))
 for name,h in m['artifacts'].items():assert sha(out/name)==h
 original=ROOT/'results/graph_image_20261024/reference/trace.cpp';assert sha(original)==m['original_sha256'];s=original.read_text();a=s.index('        float distToCenter = std::abs(getEndTileXCoordinate(id) - nw.xCenter) +');b=s.index('        float biasCost',a)
 fragment=out/'sources/hls/cost_center/v1/original_center.inc';assert fragment.read_text()==s[a:b]and sha(fragment)==m['fragment_sha256']
 inputs=ROOT/'results/cost_state_inputs_20261025';im=json.loads((inputs/'manifest.json').read_text());assert im['status']=='passed'and sha(inputs/'manifest.json')==m['input_manifest_sha256']
 layout=im['cases']['real']['layout'];image=(inputs/'real/initial.bin').read_bytes();assert sha(inputs/'real/initial.bin')==im['cases']['real']['artifacts']['initial.bin'];expected_net=image[layout['nets_offset']:layout['nets_offset']+layout['net_count']*16]
 assert (out/'net_records.bin').read_bytes()==expected_net and sha(out/'net_records.bin')==m['net_sha256']
 rows=[];rejected=0
 for line in(out/'vectors.txt').read_text().splitlines():
  row=list(map(lambda x:int(x,16),line.split()));assert len(row)==6 and all(0<=v<=0xffffffff for v in row);x,y,cx,cy,status,result=row
  invalid=(cx&0x7f800000)==0x7f800000 or(cy&0x7f800000)==0x7f800000
  if invalid:assert(status,result)==(1,0);rejected+=1
  else:
   dx=abs(f32(f32(signed(x))-fp(cx)));dy=abs(f32(f32(signed(y))-fp(cy)));assert status==0 and result==bits(f32(dx+dy)),row
  rows.append(row)
 assert len(rows)==110397 and rejected==12054
 # Verify the real samples are the declared raw graph/net records, not a fixture substitution.
 graph=ROOT/'results/graph_image_20261024';gm=json.loads((graph/'manifest.json').read_text());ga=json.loads((graph/'source_bound_audit.json').read_text());assert ga['status']=='passed'and ga['manifest_sha256']==sha(graph/'manifest.json')
 start=82400;real=alternate=0
 with (graph/'nodes.rrt32').open('rb')as f:
  attrs=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
  for net in range(layout['net_count']):
   node=(net*65537+17)%layout['nodes'];offset=node*32;cx,cy=struct.unpack_from('<2I',expected_net,net*16);x,endy=struct.unpack_from('<hh',attrs,offset+14)
   assert rows[start][:4]==[x&0xffffffff,endy&0xffffffff,cx,cy];start+=1;real+=1
   if attrs[offset+8]==5:
    beginy=struct.unpack_from('<h',attrs,offset+12)[0];assert rows[start][:4]==[x&0xffffffff,beginy&0xffffffff,cx,cy];start+=1;alternate+=1
  attrs.close()
 assert start==len(rows)and real==27960 and alternate==37
 assert all(c['exit_code']==0 for c in m['commands'])and 'runtime error:'not in(out/'execute.log').read_text()
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':len(rows),'rejected_nonfinite_centers':rejected,'real_static_samples':real,'sll_alternate_y_samples':alternate,'scope':'CPU/native extracted float expression versus integer binary32 plus independent binary32-stage reconstruction. Real static value samples, not live route calls or post-prev service execution. Finite net centers only; no new HLS/RTL or joined cost-packet proof.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
