from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=ROOT/'hardware/variants/label_baseline_system_v1'
PARENTS=['query_residency_system.sv','search_residency_system.sv','residency_system.sv']
def make():
 out={}
 for name in PARENTS:
  s=(BASE/name).read_text().replace('input wire baseline_permit,','input wire baseline_retired,\ninput wire baseline_permit,',1)
  if name!='residency_system.sv':s=s.replace('.baseline_permit(baseline_permit),','.baseline_retired(baseline_retired),.baseline_permit(baseline_permit),',1)
  else:
   s=s.replace('assign f_backend_idle=as_backend_idle&&as_retired;', 'assign f_backend_idle=as_backend_idle&&as_retired&&(!ENABLE_BASELINE||baseline_retired);')
   s=s.replace('assign f_all_drained=as_drained&&', 'assign f_all_drained=(!ENABLE_BASELINE||baseline_retired)&&as_drained&&')
  out[name]=s
 return out
if __name__=='__main__':
 for n,s in make().items():(HERE/n).write_text(s)
