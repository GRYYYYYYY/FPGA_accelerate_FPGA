"""59 bounded controls for three explicit payload contracts; no real DUT/netlist."""
from pathlib import Path
import json,os,re,shutil,subprocess
from host_edit_system_common_v1 import ROOT,BASE,sha,read,identity
from config_native_publication_synth_common_v1 import BIN,wait_preserving,memory_admission
from run_shadow_cp_protocol_controls_v5 import CASES as CP_CASES,model as cp_model,harness as cp_harness

EXTRA=[('stall_flip','DATA_FLIP_STALL','DATA_MISMATCH phase=0 ready=0'),('active_flip','DATA_FLIP_ACTIVE','DATA_MISMATCH'),('edge_flip','EDGE_ONLY_FLIP','DATA_MISMATCH phase=1 ready=1'),('data_x','DATA_X_BOTH','DATA_UNKNOWN'),('data_z','DATA_Z_BOTH','DATA_UNKNOWN'),('valid_x','VALID_X_BOTH','VALID_UNKNOWN'),('valid_z','VALID_Z_BOTH','VALID_UNKNOWN'),('idle_valid_x','IDLE_VALID_X_BOTH','VALID_UNKNOWN'),('idle_valid_z','IDLE_VALID_Z_BOTH','VALID_UNKNOWN'),('valid_drop','VALID_DROP','VALID_MISMATCH'),('meta_flip','META_FLIP','META_MISMATCH'),('meta_x','META_X_BOTH','META_UNKNOWN'),('meta_z','META_Z_BOTH','META_UNKNOWN'),('ready_x','READY_X','READY'),('no_stream','NO_STREAM','PROTOCOL_COVERAGE_MISSING'),('no_transfers','NO_TRANSFERS','PROTOCOL_COVERAGE_MISSING'),('no_stalls','NO_STALLS','PROTOCOL_COVERAGE_MISSING')]
CP_EXTRA=[('cp_data_z','DATA_Z_BOTH','CP_DATA_UNKNOWN'),('cp_valid_z','VALID_Z_BOTH','CP_VALID_UNKNOWN'),('cp_idle_valid_z','IDLE_VALID_Z_BOTH','CP_VALID_UNKNOWN'),('cp_meta_x','CP_META_X_BOTH','CP_META_UNKNOWN'),('cp_meta_z','CP_META_Z_BOTH','CP_META_UNKNOWN'),('cp_ready_x','CP_READY_X','CP_READY_UNKNOWN')]
CASES=list(CP_CASES)+CP_EXTRA+[(group.lower()+'_'+name,group+'_'+define,group+'_'+failure) for group in ['KA','PW'] for name,define,failure in EXTRA]+[(n,n.upper(),'KA_DATA_MISMATCH') for n in ['ka_node_only_flip','ka_net_only_flip']]


def model(ports,gate):
    s=cp_model(ports,gate)
    # Extend legacy CP X controls to Z and unknown metadata without changing
    # the observer's unchanged CP task body.
    idle="32'h00000000" if gate else "32'hxxxxxxxx"
    needle="`ifdef DATA_X_BOTH\nassign cp_m_data=stream_valid?32'hxxxxxxxx:"+idle+";"
    assert s.count(needle)==1
    s=s.replace(needle,needle+"\n`elsif DATA_Z_BOTH\nassign cp_m_data=stream_valid?32'hzzzzzzzz:"+idle+";")
    needle="`ifdef VALID_X_BOTH\nassign cp_m_valid=(counter>=12)?1'bx:stream_valid;"
    assert s.count(needle)==1
    s=s.replace(needle,needle+"\n`elsif VALID_Z_BOTH\nassign cp_m_valid=(counter>=12)?1'bz:stream_valid;\n`elsif IDLE_VALID_Z_BOTH\nassign cp_m_valid=(counter==1)?1'bz:stream_valid;")
    needle='`ifdef META_FLIP\n'
    assert s.count(needle)==1
    s=s.replace(needle,"`ifdef CP_META_X_BOTH\nassign cp_m_index=stream_valid?'x:word_index;\n`elsif CP_META_Z_BOTH\nassign cp_m_index=stream_valid?'z:word_index;\n`elsif META_FLIP\n")
    extra='''reg[31:0]ka_index,pw_index;
`ifdef KA_NO_STREAM
wire ka_stream=1'b0;
`else
wire ka_stream=(counter>=10&&ka_index<5);
`endif
`ifdef PW_NO_STREAM
wire pw_stream=1'b0;
`else
wire pw_stream=(counter>=10&&pw_index<5);
`endif
`ifdef KA_NO_TRANSFERS
wire ka_ready=1'b0;
`elsif KA_NO_STALLS
wire ka_ready=1'b1;
`elsif KA_READY_X
wire ka_ready=(counter>=12)?1'bx:cp_m_ready;
`else
wire ka_ready=cp_m_ready;
`endif
always @(posedge clk)begin
 if(k_cold_rst)begin ka_index<=0;pw_index<=0;end
 else begin
  if(ka_stream&&ka_ready)ka_index<=ka_index+1;
  if(pw_stream&&p_m_wready)pw_index<=pw_index+1;
 end
end
reg ka_edge_fault=0,pw_edge_fault=0;
always @(negedge clk)begin if(ka_stream&&ka_ready)begin #4.999;ka_edge_fault=1;end else ka_edge_fault<=0;end
always @(negedge clk)begin if(pw_stream&&p_m_wready)begin #4.999;pw_edge_fault=1;end else pw_edge_fault<=0;end
always @(posedge clk)begin ka_edge_fault<=0;pw_edge_fault<=0;end
'''
    s=s.replace('reg[31:0]counter,sampled,word_index;','reg[31:0]counter,sampled,word_index;\n'+extra,1)
    replacements={}
    for tag,key,valid,ready,index,fields in [('KA','ka','k_a_valid','ka_ready','ka_index',[('k_a_node',32,"32'ha0000000"),('k_a_net',32,"32'hb0000000")]),('PW','pw','p_m_wvalid','p_m_wready','pw_index',[('p_m_wdata',512,"512'hc0000000")])]:
        raw=key+'_stream';drop=f'({raw}&&{index}!=2)' if gate else raw
        replacements[valid]=f'''`ifdef {tag}_VALID_X_BOTH
assign {valid}=(counter>=12)?1'bx:{raw};
`elsif {tag}_VALID_Z_BOTH
assign {valid}=(counter>=12)?1'bz:{raw};
`elsif {tag}_IDLE_VALID_X_BOTH
assign {valid}=(counter==1)?1'bx:{raw};
`elsif {tag}_IDLE_VALID_Z_BOTH
assign {valid}=(counter==1)?1'bz:{raw};
`elsif {tag}_VALID_DROP
assign {valid}={drop};
`else
assign {valid}={raw};
`endif'''
        for field,width,prefix in fields:
            base=f'({prefix}+{index})';idle="'0" if gate else "'x"
            # Mutate both node/net for data faults; either mismatch must reject.
            stall=f"({base}^(!{ready}?{width}'h1:{width}'h0))" if gate else base
            active=f"({base}^(({index}==2)?{width}'h1:{width}'h0))" if gate else base
            edge=f"({base}^({key}_edge_fault?{width}'h1:{width}'h0))" if gate else base
            replacements[field]=f'''`ifdef {tag}_DATA_X_BOTH
assign {field}={raw}?'x:{idle};
`elsif {tag}_DATA_Z_BOTH
assign {field}={raw}?'z:{idle};
`elsif {tag}_DATA_FLIP_STALL
assign {field}={raw}?{stall}:{idle};
`elsif {tag}_DATA_FLIP_ACTIVE
assign {field}={raw}?{active}:{idle};
`elsif {tag}_EDGE_ONLY_FLIP
assign {field}={raw}?{edge}:{idle};
`else
assign {field}={raw}?{base}:{idle};
`endif'''
        if tag=='KA':
            for field,_,_ in fields:
                define='KA_NODE_ONLY_FLIP' if field=='k_a_node' else 'KA_NET_ONLY_FLIP'
                expression=f"(32'h{'a' if field=='k_a_node' else 'b'}0000000+ka_index)"
                wrong=f"({expression}^((ka_index==2)?32'h1:32'h0))" if gate else expression
                replacements[field]=f"`ifdef {define}\nassign {field}=ka_stream?{wrong}:"+("'0" if gate else "'x")+";\n`else\n"+replacements[field]+"\n`endif"
        field='k_a_cookie' if tag=='KA' else 'p_m_wstrb';width=32 if tag=='KA' else 64
        normal=f"({width}'h11110000+{index})" if tag=='KA' else "64'hffffffffffffffff"
        flip=f"({normal}^(({raw}&&{index}==2)?{width}'h1:{width}'h0))" if gate else normal
        replacements[field]=f'''`ifdef {tag}_META_FLIP
assign {field}={flip};
`elsif {tag}_META_X_BOTH
assign {field}={raw}?'x:{normal};
`elsif {tag}_META_Z_BOTH
assign {field}={raw}?'z:{normal};
`else
assign {field}={normal};
`endif'''
    replacements.update(k_a_ready='assign k_a_ready=ka_ready;',k_a_checkpoint="assign k_a_checkpoint=32'd17;",k_a_design="assign k_a_design=64'h1234;",p_m_wlast='assign p_m_wlast=(pw_index==4);')
    for name,new in replacements.items():
        pattern=r'^assign '+name+r'=.*;$';s,n=re.subn(pattern,lambda _:new,s,flags=re.M);assert n==1,(name,n)
    return s


def harness(ports):
    s=cp_harness(ports)
    s=s.replace(cp_model(ports,False),model(ports,False),1).replace(cp_model(ports,True),model(ports,True),1)
    needle='reg cold=1;reg[31:0]stream=0;reg ready=0;'
    additions='''
`ifdef CP_READY_X
reg cp_ready_fault=0;initial begin #170;cp_ready_fault=1;end
wire c_ready=cp_ready_fault?1'bx:ready;
`else
wire c_ready=ready;
`endif
`ifdef PW_NO_TRANSFERS
wire p_ready=1'b0;
`elsif PW_NO_STALLS
wire p_ready=1'b1;
`elsif PW_READY_X
reg pw_ready_fault=0;initial begin #170;pw_ready_fault=1;end
wire p_ready=pw_ready_fault?1'bx:ready;
`else
wire p_ready=ready;
`endif'''
    assert s.count(needle)==1;s=s.replace(needle,needle+additions)
    assert s.count('.cp_m_ready(ready)')==1;s=s.replace('.cp_m_ready(ready)','.cp_m_ready(c_ready)')
    assert s.count(".p_m_wready('0)")==1;s=s.replace(".p_m_wready('0)",'.p_m_wready(p_ready)')
    return s


def main():
    p=BASE/'shadow_payload_contract_controls_v1';assert not p.exists() and not os.environ.get('LD_PRELOAD')
    variant=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v5';vm=read(variant/'manifest.json')
    assert vm['unconditional_outputs']==342 and vm['cp_task_body_unchanged']
    shadow=variant/'shadow.sv';assert sha(shadow)==vm['files']['shadow.sv']
    ports=read(ROOT/'results/stage_static_cp_port_schema_20261030.json')['ports'];source=harness(ports)
    p.mkdir();m=dict(status='running',stage='wait_memory',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),runner_sha256=sha(__file__),checker_sha256=sha(shadow),checker_manifest_sha256=sha(variant/'manifest.json'),cases={},planned_cases=len(CASES),scope='59 bounded fake-model controls only; three legal independent five-beat streams, idle X/0, stalls and NBA sampling. No real FPGA netlist.')
    def save():
        q=p/'manifest.pending.json';q.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');q.replace(p/'manifest.json')
    save()
    try:
        memory_admission(m,save)
        for mode,define,expected in CASES:
            d=p/mode;d.mkdir();(d/'control.sv').write_text(source);shutil.copyfile(shadow,d/'shadow.sv');(d/'run.tcl').write_text('run 2us\nquit\n')
            c=dict(status='running',expected=expected,commands=[],inputs={n:sha(d/n) for n in ['control.sv','shadow.sv','run.tcl']});m['cases'][mode]=c;save()
            compiler=[str(BIN.parent/'xvlog'),'--sv','-d','SHADOW_NETLIST_TOP=protocol_gate']
            if define:compiler+=['-d',define]
            phases=[('compile',compiler+['shadow.sv','control.sv']),('elaborate',[str(BIN.parent/'xelab'),'tb_candidate_offer','stage_static_cp_shadow','-s','control','--O0','--mt','2']),('simulate',[str(BIN.parent/'xsim'),'control','-tclbatch','run.tcl'])]
            for stage,argv in phases:
                for n,h in c['inputs'].items():assert sha(d/n)==h
                m['stage']=mode+'_'+stage;save()
                with (d/(stage+'.stdout.log')).open('w') as log:
                    child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT);m['active_process']=dict(pid=child.pid,start_ticks=identity(child.pid));save();code=wait_preserving(child,600,m,save)
                m.pop('active_process',None);c['commands'].append(dict(stage=stage,argv=argv,exit_code=code,stdout_sha256=sha(d/(stage+'.stdout.log'))));save();assert code==0,(mode,stage)
            log=(d/'simulate.stdout.log').read_text();assert expected in log,(mode,log[-1800:])
            if mode in ['matching','ready_nba']:assert 'Fatal:' not in log and 'PAYLOAD_GROUP_PASS group=KA' in log and 'PAYLOAD_GROUP_PASS group=PW' in log
            else:assert 'Fatal:' in log and 'FULL_SHADOW_PROTOCOL_PASS' not in log
            c['status']='observed';save();print('PAYLOAD_CONTROL_OBSERVED',mode,flush=True)
        m.update(status='observed',stage='complete',full_system_functional_netlist_validated=False)
    except Exception as error:m.update(status='failed',error=repr(error));raise
    finally:save()


if __name__=='__main__':main()
