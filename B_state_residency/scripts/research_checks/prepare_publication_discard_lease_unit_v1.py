"""Build actual two-module arbitrary-input phase-specific lease proof."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');p=B/'ka_publication_discard_lease_unit_v1';assert not p.exists();p.mkdir();S=B/'stage_static_cp_shadow_system_v6/sources'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ports(text):
 header=text.split('(',1)[1].split(');',1)[0];out=[];direction=None;width=''
 for chunk in header.split(','):
  chunk=chunk.strip();match=re.fullmatch(r'(input|output)\s+(?:wire|reg)?\s*(\[[^\]]+\])?\s*(\w+)',chunk)
  if match:direction,width,name=match.groups();width=width or ''
  else:assert re.fullmatch(r'\w+',chunk),chunk;name=chunk
  assert direction;out.append((name,direction,width))
 return out
sources={};decl=['reg past_valid=0;','wire pc_owned,jp_owned;','(* anyseq *) reg rst,other_command_busy;'];instances=[]
for file,instance,prefix in [('checkpoint_lease_guard.sv','lease','lease_'),('checkpoint_publish_barrier.sv','publication','pub_')]:
 text=(S/file).read_text();(p/file).write_text(text);sources[str(S/file)]=sha(S/file);sources[str(p/file)]=sha(p/file);connections=[]
 for name,direction,width in ports(text):
  if name=='clk':expression='clk'
  elif name=='rst':expression='rst'
  elif name=='owned':expression='pc_owned' if instance=='lease' else 'jp_owned'
  elif instance=='publication' and name=='lease_owned':expression='pc_owned'
  elif instance=='lease' and name=='command_busy':expression='(other_command_busy||jp_owned)'
  else:
   expression=prefix+name;decl.append(('(* anyseq *) reg ' if direction=='input' else 'wire ')+(width+' ' if width else '')+expression+';')
  connections.append('.'+name+'('+expression+')')
 instances.append(file[:-3]+' '+instance+'('+',\n'.join(connections)+');')
h='module ka_publication_discard_lease_unit(input wire clk);\n'+'\n'.join(decl)+'\n'+'\n'.join(instances)+'''\ninitial assume(rst);
always @(posedge clk)begin
 past_valid<=1;
 if(past_valid && !rst && pub_discard_valid!=0)begin
  assert(pc_owned);
  assert(jp_owned);
 end
 cover(past_valid && !rst && pub_discard_valid!=0 && pc_owned);
 cover(past_valid && !rst && jp_owned && !pc_owned);
end
endmodule
''';(p/'harness.sv').write_text(h);v=R/'hardware/variants/ka_publication_discard_lease_unit_v1';v.mkdir();(v/'harness.sv').write_text(h)
pr={'status':'prepared_original_two_module_discard_phase_lease_proof','source_sha256':sources,'harness_sha256':sha(p/'harness.sv'),'scope':'Complete original modules, all metadata/health/command/response inputs arbitrary. Only actual shared reset/clock and query command_busy OR jp_owned connection retained. Discard qualifier target, no assumption publication-owned implies lease-owned.'};(p/'projection.json').write_text(json.dumps(pr,indent=2)+'\n');print(p)
