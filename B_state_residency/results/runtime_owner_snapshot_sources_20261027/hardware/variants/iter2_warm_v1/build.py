from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/iter2_lifecycle_full_v5/sources')
def make():
 for n in ['query_residency_system.sv','search_residency_system.sv','residency_system.sv']:
  s=(BASE/n).read_text();assert s.count('ENABLE_TEST_INJECTION=0')==1;s=s.replace('ENABLE_TEST_INJECTION=0','ENABLE_TEST_INJECTION=0,RESTORE_RECORDS=512')
  if n=='residency_system.sv':
   assert s.count('.MAX_RECORDS(512)')==1;s=s.replace('.MAX_RECORDS(512)','.MAX_RECORDS(RESTORE_RECORDS)')
  else:
   mod='search_residency_system'if n=='query_residency_system.sv'else'residency_system'
   start=s.index(mod+' #(');end=s.index(')inner('if n=='query_residency_system.sv'else')backend(',start)
   s=s[:end]+',.RESTORE_RECORDS(RESTORE_RECORDS)'+s[end:]
  (HERE/n).write_text(s)
if __name__=='__main__':make()
