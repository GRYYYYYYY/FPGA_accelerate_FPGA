from pathlib import Path
import hashlib,json,struct,mmap,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def f32(f):return struct.unpack('<f',struct.pack('<f',f))[0]
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 dep=ROOT/'results/graph_image_20261024';assert m['base_gate_sha256']==sha(dep/'source_bound_audit.json')and m['base_manifest_sha256']==sha(dep/'manifest.json')
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 source=(out/'sources/reference/trace.cpp').read_text();a=source.index('        st.shareWeight = std::pow(1.0f, cfg.shareExponent);');b=source.index('        st.earlyTermination = false;',a)
 assert (out/'sources/initializer.txt').read_text()==source[a:b]
 assert all(c['exit_code']==0 for c in m['commands']) and 'CONNECTION_STATE_EXPORT_PASS'in(out/'execute.log').read_text()
 table=(out/'connections.bin').read_bytes();layout=m['layout'];assert len(table)==layout['connections']*64
 # Decode the entire original RRT1 grammar independently, including connection identities.
 rrt=ROOT/'data/derived/logicnets_jscl.rrt'
 with rrt.open('rb')as f:
  data=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ);assert data[:4]==b'RRT1'
  wl=struct.unpack_from('<f',data,32)[0];exp_bits=struct.unpack_from('<I',data,36)[0];sll=struct.unpack_from('<i',data,60)[0]
  assert bits(wl)==layout['wl_bits']and exp_bits==layout['share_exponent_bits']and sll==layout['sll_length']
  pos=68;rows=struct.unpack_from('<i',data,pos)[0];pos+=4+rows*4;laguna=struct.unpack_from('<i',data,pos)[0];pos+=4
  if laguna:
   cols=struct.unpack_from('<i',data,pos)[0];pos+=4+cols*8+rows
  nodes=struct.unpack_from('<i',data,pos)[0];pos+=4;assert nodes==layout['nodes']
  edges=0
  for _ in range(nodes):
   count=struct.unpack_from('<i',data,pos+32)[0];assert 0<=count<=32;edges+=count;pos+=36+count*4
  nets=struct.unpack_from('<i',data,pos)[0];pos+=4;assert nets==layout['nets']
  directed=struct.unpack('<f',struct.pack('<I',layout['directed_bits']))[0]
  weights=[bits(1.0),bits(f32(1.0-f32(wl))),bits(f32(f32(wl)*directed)),0,0,sll]
  count=0;crosses=0
  for net in range(nets):
   num=struct.unpack_from('<i',data,pos+18)[0];pos+=22
   for _ in range(num):
    _,src,sink,na=struct.unpack_from('<4i',data,pos);pos+=16+na*4
    north,south=data[pos+10],data[pos+11];flags=(8 if north else 0)|(16 if south else 0);crosses+=bool(flags)
    nr=struct.unpack_from('<i',data,pos+13)[0];pos+=17+nr*4
    actual=struct.unpack_from('<16I',table,count*64)
    expected=(0x43505331,count,net,sink,src,*weights,flags,bits(wl),layout['directed_bits'],exp_bits,0)
    assert actual==expected,(count,actual,expected);count+=1
  assert pos==len(data)and count==layout['connections']==180326;data.close()
 tsv=[list(map(int,s.split()))for s in(out/'connections.tsv').read_text().splitlines()];assert len(tsv)==count
 for i,row in enumerate(tsv):
  words=struct.unpack_from('<16I',table,i*64);assert row==list(words[1:])
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'connections_checked':count,'all_RRT_nodes_skipped_by_exact_grammar':nodes,'edges':edges,'crossSLR_connections':crosses,'weight_words':weights[:3],'landmark_ready':False,'scope':'All real connection source/net/sink/cross flags independently decoded from RRT; initial non-timing State initializer extracted verbatim, nonzero WL/heuristic weights; not live route trace or landmark build.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
