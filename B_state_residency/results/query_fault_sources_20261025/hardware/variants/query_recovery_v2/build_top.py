"""Narrow retirement fix; retain all original ports and production instances."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def make():
    s=(ROOT/'hardware/variants/query_lifecycle_v1/query_residency_system.sv').read_text()
    old='f_normal_retired&&f_backend_idle&&f_all_drained&&!ss_busy&&!rc_busy'
    new='f_normal_retired&&f_backend_idle&&f_all_drained&&!ss_busy&&(!rc_busy||(rc_fault&&f_phase==6))'
    assert s.count(old)==1
    return s.replace(old,new)
if __name__=='__main__':(Path(__file__).parent/'query_residency_system.sv').write_text(make())
