"""Use the user's authenticated notebook access to read original process identities."""
from pathlib import Path
import datetime
import importlib.util
import json
import re
import shlex
import sys
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, '/tmp/B_state_residency_recovery_20261102/remote_status_python_v1')
import websocket

PROBE = r'''
from pathlib import Path
import os,json,datetime
expected={1293430:'1664575051',1309736:'1664579699',2565424:'1663666192',3013336:'1663807268',1719618:'1664702242'}
names=['ka_active_configured_formal_v1','ka_retired_configured_formal_v1','ka_as_lease_staging_exclusion_formal_v1','ka_as_lease_recover_gate_fault_v1','ka_publication_release_full_rtl_v2']
host=Path('/proc/sys/kernel/hostname').read_text().strip()
assert host=='fpgaacc1--cfc8cd109508-jnnrja5s7q',host
def process(pid):
 p=Path('/proc')/str(pid)
 try:
  s=(p/'stat').read_text().rsplit(')',1)[1].split()
  return {'pid':pid,'state':s[0],'start_ticks':s[19],'cpu_ticks':int(s[11])+int(s[12]),'rss_pages':int(s[21])}
 except FileNotFoundError:return {'pid':pid,'missing':True}
original=[]
for pid,start in expected.items():
 r=process(pid);r['expected_start_ticks']=start;r['original_identity_present']=r.get('start_ticks')==start;original.append(r)
base=Path('/tmp/B_state_residency_offer_20261025');manifests={}
for n in names:
 p=base/n/'manifest.json'
 if p.exists():
  m=json.loads(p.read_text());manifests[n]={k:m.get(k) for k in ['status','stage','runner_pid','runner_start_ticks','active_process','memory_observation']}
  a=m.get('active_process')
  if a:manifests[n]['active_process_now']=process(a['pid'])
 else:manifests[n]={'missing':True}
skip={os.getpid(),os.getppid()};matches=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit() or int(p.name) in skip:continue
 try:
  args=(p/'cmdline').read_bytes().split(b'\0')
  # Match executable/argument paths, not an ancestor shell's echoed probe text.
  selected=[n for n in names if any(a.startswith(b'/') and str(base/n).encode() in a for a in args)]
  selected+=['full_probe_runner'] if any(a.rsplit(b'/',1)[-1]==b'run_publication_release_full_rtl_v2.py' for a in args) else []
  if selected:matches.append(dict(process(int(p.name)),matched_runs=selected))
 except (FileNotFoundError,ProcessLookupError):pass
cg=Path('/sys/fs/cgroup');stats=dict(x.split() for x in (cg/'memory.stat').read_text().splitlines())
report={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hostname':host,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'pid_namespace':os.readlink('/proc/self/ns/pid'),'original_processes':original,'manifests':manifests,'matching_original_run_processes':matches,'memory_current_bytes':int((cg/'memory.current').read_text()),'memory_max':(cg/'memory.max').read_text().strip(),'memory_anon_bytes':int(stats['anon']),'memory_file_bytes':int(stats['file']),'memory_events':(cg/'memory.events').read_text(),'inspection':'Read-only proc and original manifests; original processes not signalled or modified.'}
print('OLD_BACKEND_SNAPSHOT:'+json.dumps(report))
'''


def main():
    helper = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/codex/home/skills/inspire-gpu-submit/scripts/inspire_gpu.py')
    spec = importlib.util.spec_from_file_location('inspire_helper', helper)
    api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)
    notebook = '24b4a633-9ad2-4133-9174-cfc8cd109508'
    access = api.run_qz(['notebook', 'GetNotebookAccessUrl', '--data', json.dumps({'notebook_id': notebook})])['Result']
    u = urllib.parse.urlsplit(access['jupyter_url'])
    assert u.scheme == 'https' and u.hostname == 'nat2-notebook-inspire.sii.edu.cn'
    token = urllib.parse.parse_qs(u.query)['token'][0]
    path = u.path.removesuffix('/lab')
    base = urllib.parse.urlunsplit((u.scheme, u.netloc, path, '', ''))
    # The configured proxy breaks this notebook TLS route; direct TLS was verified.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def request(suffix, method='GET', payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(base + suffix, data=data, method=method,
                                     headers={'Authorization': 'token ' + token, 'Content-Type': 'application/json'})
        with opener.open(req, timeout=15) as response:
            body = response.read()
            return json.loads(body) if body else None

    created = request('/api/terminals', 'POST', {})
    name = created['name']
    ws = None
    output = ''
    report = None
    try:
        ws_url = urllib.parse.urlunsplit(('wss', u.netloc, path + '/terminals/websocket/' + urllib.parse.quote(name, safe=''), '', ''))
        ws = websocket.create_connection(ws_url, timeout=8, header=['Authorization: token ' + token],
                                         origin='https://' + u.netloc, http_no_proxy=[u.hostname])
        ws.send(json.dumps(['stdin', 'python3 -c ' + shlex.quote(PROBE) + '\n']))
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            try:
                frame = json.loads(ws.recv())
            except websocket.WebSocketTimeoutException:
                continue
            if frame[0] == 'stdout':
                output += frame[1]
                match = re.search(r'(?m)^OLD_BACKEND_SNAPSHOT:(\{[^\r\n]*\})\r?$', output)
                if match:
                    report = json.loads(match.group(1))
                    break
        assert report is not None, 'No complete remote process snapshot received'
    finally:
        if ws is not None:
            ws.close()
        request('/api/terminals/' + urllib.parse.quote(name, safe=''), 'DELETE')
    report.update(notebook_id=notebook, temporary_inspection_terminal_closed=True,
                  transport='authenticated Jupyter terminal; direct verified TLS; credentials not recorded')
    out = ROOT / 'results/old_host_original_jobs_live_check_20261102.json'
    assert not out.exists()
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
