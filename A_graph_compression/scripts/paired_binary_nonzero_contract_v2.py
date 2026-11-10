"""Exact complete input and command contract for the two encoded full44 trials."""
import json
from pathlib import Path
import re
from check_vitis_kernel import digest,require
from check_hls_fsm_binary_v1 import check_delta
from check_compact_nonzero_axi_models_v1 import audit_model
from binary_nonzero_full44_prerequisites_v1 import CSR,COMPACT

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
PREP=ROOT/'data/derived/paired_binary_nonzero_entries_20261029_v2'
PREPORT=ROOT/'results/paired_binary_nonzero_entries_preparation_20261029_v2.json'
AS_BYTES=64*1024**3
STACK=64*1024**2
GUARD_FREE=16*1024**3
ERRORS=['ERROR:','Fatal:','FATAL_ERROR','runtime error:','A_RO_WRITE_VIOLATION','A_RO_UNKNOWN_ADDRESS','A_RO_UNSUPPORTED_BURST','Simulator command interrupted','engine not responding','unexpected manner']


def config(mode):
    require(mode in [0,1],'Unsupported graph mode')
    stem='compressed_batch_bus64' if mode==0 else 'compressed_batch_compact_bus64'
    return dict(mode=mode,label='csr' if mode==0 else 'compact',parent=BASE/(stem+'_rtl_guarded_v1'),trial=BASE/(stem+'_binary_nonzero_rtl_v2'),
                candidate=ROOT/'data/derived'/('hls_binary_fsm_candidate_20261025_v1' if mode==0 else 'hls_compact_binary_fsm_candidate_20261025_v1'),
                preflight=ROOT/'data/derived'/('compressed_bus64_dpi_models_preflight_20261025_v1' if mode==0 else 'compressed_compact_bus64_dpi_models_preflight_20261025_v1'),
                preaudit=ROOT/'results'/('compressed_bus64_dpi_storage_preflight_audit_20261025_v1.json' if mode==0 else 'compressed_compact_bus64_dpi_storage_preflight_audit_20261025_v1.json'),
                allocation=ROOT/'results'/(stem+'_cosim_allocations_20261025_v1.json'),
                setup=ROOT/'results/compressed_batch_bus64_full_depth_cosim_setup_20261025_v1.json' if mode==0 else BASE/'compressed_batch_compact_bus64_cosim_setup/setup.json',
                golden=BASE/(stem+'_cosim_setup'),output=ROOT/'results'/(CSR if mode==0 else COMPACT),encoded_modules=43 if mode==0 else 45)


def selected(relative):
    p=Path(relative)
    return ((len(p.parts)==2 and p.parts[0]=='verilog' and p.suffix in ['.v','.sv','.svh','.vh','.dat','.prj','.ini','.sh']) or
            p.parts[:2]==('tv','cdatafile') or p.parts[0]=='wrapc_pc')


def source_contract(mode):
    c=config(mode);files={}
    def load(path):
        files[str(path)]=digest(path);return json.loads(path.read_text())
    paired=load(ROOT/'results/paired_binary_nonzero_axi_preparation_20261029_v1.json');env=next(m for m in paired['modes'] if m['graph_mode']==mode)
    parent=load(c['parent']/'plan.json');candidate=load(c['candidate']/'plan.json');conversion=load(c['preflight']/'plan.json')
    preaudit=load(c['preaudit']);allocation=load(c['allocation']);setup=load(c['setup'])
    require(parent['transactions']==4 and parent['graph_mode']==mode and parent['allocation_sha256']==digest(c['allocation']),'Different guarded source scope')
    if mode==1:require(parent['setup_sha256']==digest(c['setup']),'Changed compact setup')
    require(len(candidate['modules'])==c['encoded_modules'] and len(conversion['models'])==len(preaudit['models'])==30,'Incomplete original encoding/storage matrix')
    for report in [preaudit,allocation,setup]:
        for p,h in report['files'].items():
            require(p not in files or files[p]==h,'Conflicting source evidence');files[p]=h
    changes={Path(r['original']).name:r for r in candidate['modules']}
    manifest={}
    for name,h in parent['copied_files'].items():
        relative=Path(name).relative_to(c['parent']/'sim')
        if not selected(relative):continue
        require(digest(name)==h,'Changed full original copied input')
        source=Path(name);kind='unchanged'
        if relative.parts[0]=='verilog' and source.name in changes:
            r=changes[source.name];require(digest(source)==digest(r['original']),'Different original encoded source');source=Path(r['candidate']);kind='encoded_dut'
            check_delta(Path(name).read_text(),source.read_text(),json.loads(Path(r['ledger']).read_text()))
            for p in [r['original'],r['candidate'],r['ledger']]:files[str(p)]=digest(p)
        manifest[str(relative)]=dict(source=str(source),sha256=digest(source),kind=kind,original=name,original_sha256=h)
        files[name]=h;files[str(source)]=digest(source)
    # The old copied_files ledger omits generated include headers even though
    # its copytree-based runner copied them. Bind the actual include closure,
    # requiring every added header to match the original HLS setup byte-for-byte.
    pending=[rel for rel in manifest if Path(rel).suffix in ['.v','.sv','.svh','.vh']];seen=set()
    while pending:
        rel=pending.pop()
        if rel in seen:continue
        seen.add(rel)
        for name in re.findall(r'`include\s+"([^\"]+)"',Path(manifest[rel]['source']).read_text()):
            require(Path(name).name==name,'Unsupported include path')
            include=str(Path(rel).parent/name)
            if include not in manifest:
                parent_header=c['parent']/'sim'/include;original_header=Path(setup['project'])/'solution/sim'/include
                require(parent_header.is_file() and original_header.is_file() and digest(parent_header)==digest(original_header),'Missing/changed original HLS include '+name)
                manifest[include]=dict(source=str(parent_header),sha256=digest(parent_header),kind='original_header',original=str(original_header),original_sha256=digest(original_header))
                files[str(parent_header)]=digest(parent_header);files[str(original_header)]=digest(original_header)
            pending.append(include)
    require(sum(m['kind']=='encoded_dut' for m in manifest.values())==c['encoded_modules'],'Incomplete encoded manifest')
    converted={m['bundle']:m for m in conversion['models']}
    for m in env['models']:
        name=Path(m['target']).name;old=c['parent']/'sim/verilog'/name;conv=converted[m['bundle']]
        require(digest(old)==conv['before_sha256'] and digest(m['source'])==conv['after_sha256'],'Different original DPI transformation')
        audit_model(Path(m['source']).read_text(),Path(m['target']).read_text(),m['bundle'])
        manifest['verilog/'+name]=dict(source=m['target'],sha256=digest(m['target']),kind='model',original=str(old),original_sha256=digest(old))
        for p in [str(old),m['source'],m['target']]:files[p]=digest(p)
    require(len(env['pointer_vectors'])==44,'Incomplete pointer set')
    for name,row in env['pointer_vectors'].items():
        rel=Path('tv/cdatafile')/Path(row['source']).name;record=manifest[str(rel)]
        require(record['original']==row['source'],'Wrong original pointer fixture')
        text=Path(row['target']).read_text();old=Path(row['source']).read_text()
        tokens=re.findall(r'0x[0-9a-fA-F]+',text)
        require(len(tokens)==4 and all(int(v,16)==row['original_address']+4096 for v in tokens),'Different relocated pointer values')
        require(re.sub(r'0x[0-9a-fA-F]+',lambda m:'0x'+format(int(m[0],16)-4096,'0'+str(len(m[0])-2)+'x'),text)==old,'Non-address pointer edit')
        record.update(source=row['target'],sha256=digest(row['target']),kind='pointer');files[row['target']]=digest(row['target'])
    expected={p.name for p in (c['candidate']/'verilog').iterdir() if p.is_file()}
    actual={Path(p).name for p in manifest if Path(p).parts[0]=='verilog' and Path(p).suffix in ['.v','.sv','.dat']}
    require(actual==expected,'Incomplete original candidate source/ROM matrix')
    # Verify every original RO guard remains inside the unchanged model body.
    inventory=load(ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json');ports={p['name']:p for p in inventory['ports']}
    expected_ro={ports[g['regions'][0]['name']]['bundle']:[r for r in g['regions'] if r['readonly']] for g in allocation['allocations'] if any(r['readonly'] for r in g['regions'])}
    require({m['bundle']:m['readonly'] for m in parent['models']}==expected_ro,'Partial readonly coverage')
    for m in parent['models']:
        name='AESL_axi_master_'+m['bundle']+'.v';text=(c['parent']/'sim/verilog'/name).read_text();original=Path(setup['project'])/'solution/sim/verilog'/name
        marker='\n// Independent conservative read-only AXI burst guard.\n'
        require(text.count(marker)==1 and text.split(marker)[0]+'endmodule'+text.rsplit('endmodule',1)[1]==original.read_text(),'Original model changed beyond RO guard')
        files[str(original)]=digest(original)
    for i in range(4):
        p=c['golden']/f'hls_{mode}_{i}.bin';require(p.stat().st_size==946498280 and setup['files'].get(str(p))==digest(p),'Changed full C golden');files[str(p)]=digest(p)
    for p,h in files.items():require(digest(p)==h,'Changed complete source proof '+p)
    return manifest,files,env


def commands(mode):
    c=config(mode);out=c['trial'];directory=out/'sim/verilog';pc=out/'sim/wrapc_pc'
    original=json.loads((c['parent']/'plan.json').read_text())['command']
    require(original[:3]==['/usr/bin/time','-v',str(BIN/'xelab')] and original[-4:]==['-mt','off','--O0','--stats'],'Different original compiler command')
    prefix=['prlimit','--stack='+str(STACK)+':'+str(STACK),'--core=0:0','--as='+str(AS_BYTES)+':'+str(AS_BYTES),'--','taskset','-c','122']
    return [dict(phase='xsc',command=prefix+[str(BIN/'xsc'),'--cppversion','14','--mt','off',str(ROOT/'hardware/sim/axi_dpi_memory_v1.cpp')],cwd=str(directory)),
            dict(phase='elaborate',command=prefix+original+['--timescale','1ns/1ps','--sv_lib','dpi','--sv_root','xsim.dir/work/xsc'],cwd=str(directory)),
            dict(phase='rtl',command=prefix+[str(BIN/'xsim'),'--noieeewarnings','search_batch_trace_top_v2','-tclbatch',str(out/'bounded.tcl')],cwd=str(directory)),
            dict(phase='postcheck',command=prefix+[str(pc/'cosim.pc.exe')],cwd=str(pc))]


def prepared(mode):
    report=json.loads(PREPORT.read_text())
    require(report['status']=='both_nonzero_encoded_full44_execution_entries_prepared_no_trial_started','Missing entry preparation')
    for p,h in report['files'].items():require(digest(p)==h,'Changed prepared source '+p)
    selected_mode=next(m for m in report['modes'] if m['graph_mode']==mode)
    require((selected_mode['transactions'],selected_mode['ports'],selected_mode['models'],selected_mode['pages'])==(4,44,30,4) and selected_mode['commands']==commands(mode),'Different prepared scope/commands')
    require(selected_mode['address_space_bytes']==AS_BYTES and selected_mode['runtime_guard_free_bytes']==GUARD_FREE and selected_mode['startup_gate_removed_by_user'],'Different resource policy')
    return selected_mode,report['files']
