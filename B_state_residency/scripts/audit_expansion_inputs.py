from pathlib import Path
import hashlib,json,struct
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=ROOT/'results/expansion_inputs_20261024';graph=ROOT/'results/graph_image_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 gm=json.loads((graph/'manifest.json').read_text());assert sha(graph/'manifest.json')==m['graph_manifest_sha256']and sha(graph/'source_bound_audit.json')==m['graph_audit_sha256']
 assert sha(ROOT/'data/derived/logicnets_jscl.rrt')==gm['input_sha256']
 for name,digest in m['sources'].items():assert sha(out/'sources'/name)==digest
 for name,digest in m['artifacts'].items():assert sha(out/name)==digest
 assert all(x['exit_code']==0 for x in m['commands'])
 source=(graph/'reference/trace.cpp').read_text()
 edits=[('void getOrCreate(int id) { created[id] = 1; }','void getOrCreate(int id) { created[id] = 1; note_create(id); }',1),('int child = childIds[n.childStart + k];','int child = childIds[n.childStart + k]; note_position(k);',1),('out->push_back(child);','out->push_back(child); note_emit(child);',2)]
 for old,new,count in edits:assert source.count(old)==count;source=source.replace(old,new)
 assert source==(out/'sources/reference/oracle_trace.cpp').read_text()
 data=(graph/'design_suffix.rrtbin').read_bytes();assert sha(graph/'design_suffix.rrtbin')==gm['artifacts']['design_suffix.rrtbin'];pos=0
 def take(fmt):
  nonlocal pos
  vals=struct.unpack_from('<'+fmt,data,pos);pos+=struct.calcsize('<'+fmt);return vals
 nets,=take('i');sinks=set();connections=0;nodes=gm['nodes']
 for ni in range(nets):
  xc,yc,hp,size,src,count=take('ffhiii');assert count>=0
  for ci in range(count):
   conn,source,sink,na=take('iiii');assert na>=0 and 0<=source<nodes and -1<=sink<nodes
   if sink>=0:sinks.add(sink)
   for _ in range(na):
    a,=take('i');assert -1<=a<nodes
    if a>=0:sinks.add(a)
   x0,x1,y0,y1,hp,north,south,routed,nr=take('hhhhhBBBi');assert nr>=0
   for _ in range(nr):a,=take('i');assert 0<=a<nodes
   connections+=1
 assert pos==len(data)and sinks==set(map(int,(out/'sink_nodes.txt').read_text().split()))
 c=json.loads((out/'coverage.json').read_text());assert (nets,connections,len(sinks))==(c['nets'],c['connections'],c['sinks'])
 initial=bytearray(((nodes*16+63)//64)*64)
 for n in sinks:struct.pack_into('<I',initial,n*16,8)
 assert hashlib.sha256(initial).hexdigest()==sha(out/'initial_design.bin')
 prefix=(graph/'config_prefix.rrtbin').read_bytes();rows,=struct.unpack_from('<i',prefix,68);laguna,=struct.unpack_from('<i',prefix,72+4*rows);assert laguna==c['has_laguna']
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'nets':nets,'connections':connections,'sink_nodes':len(sinks),'has_laguna':laguna,'initial_design_sha256':sha(out/'initial_design.bin'),'scope':'Full real sink initialization independently decoded and checked against original Router loader. Expansion oracle is original getChildren with observer-only hooks, paged labels, and explicit control/write commands; no full routing invocation.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
