from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'tb_cost_state.sv').read_text().split(' integer fd,fo,',1)[0].replace('module tb_cost_state;','module tb_cost_state_boundaries;\nreg hold_ar=0,hold_aw=0,hold_w=0,inject_r=0,inject_b=0;wire raw_arready,raw_awready,raw_wready;')
s=s.replace('.MAX_CYCLES(2048)','.MAX_CYCLES(64)')
for channel in ['ar','aw','w']:
 s=s.replace('.'+channel+'valid(m_'+channel+'valid)','. '+channel+'valid(m_'+channel+'valid&&!hold_'+channel+')'.replace('. ','.'))
 s=s.replace('.'+channel+'ready(m_'+channel+'ready)','.'+channel+'ready(raw_'+channel+'ready)')
s=s.replace(".inject_r(1'b0)",'.inject_r(inject_r)').replace(".inject_b(1'b0)",'.inject_b(inject_b)')
s+=(HERE/'boundaries_body.inc').read_text()
for c in ['ar','aw','w']:s+='\nassign m_'+c+'ready=raw_'+c+'ready&&!hold_'+c+';'
s+='\nendmodule\n';(HERE/'tb_cost_state_boundaries.sv').write_text(s)
