"""Copy six immutable old-host KA review archives to persistent shared storage."""
from pathlib import Path
import datetime
import importlib.util
import json
import os
import re
import shlex
import sys
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, '/tmp/B_state_residency_recovery_20261102/remote_status_python_v1')
import websocket

PROBE = "import runpy,sys; sys.path.insert(0,'/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/scripts/research_checks'); runpy.run_path('/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/scripts/research_checks/copy_shadow_authority_core_remote_v1.py',run_name='__main__')"


def main():
    helper = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/codex/home/skills/inspire-gpu-submit/scripts/inspire_gpu.py')
    spec = importlib.util.spec_from_file_location('inspire_helper', helper)
    api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)
    notebook = '24b4a633-9ad2-4133-9174-cfc8cd109508'
    access = api.run_qz(['notebook', 'GetNotebookAccessUrl', '--data', json.dumps({'notebook_id': notebook})])['Result']
    u = urllib.parse.urlsplit(access['jupyter_url'])
    assert u.scheme == 'https' and u.hostname == 'nat2-notebook-inspire.sii.edu.cn'
    for key in ['no_proxy', 'NO_PROXY']:
        os.environ[key] = ','.join(filter(None, [os.environ.get(key, ''), u.hostname]))
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
    terminal_receipt=ROOT/'results/shadow_authority_core_copy_v1_terminal_20261102.json'
    assert not terminal_receipt.exists()
    terminal_receipt.write_text(json.dumps({'notebook_id':notebook,'terminal_name':name,'created_for':'shadow_authority_core_copy_v1','closed':False})+'\n')
    ws = None
    output = ''
    report = None
    try:
        ws_url = urllib.parse.urlunsplit(('wss', u.netloc, path + '/terminals/websocket/' + urllib.parse.quote(name, safe=''), '', ''))
        ws = websocket.create_connection(ws_url, timeout=8, header=['Authorization: token ' + token],
                                         origin='https://' + u.netloc, http_no_proxy=[u.hostname])
        ws.send(json.dumps(['stdin', 'python3 -c ' + shlex.quote(PROBE) + '\n']))
        deadline = time.monotonic() + 300
        while time.monotonic() < deadline:
            try:
                frame = json.loads(ws.recv())
            except websocket.WebSocketTimeoutException:
                continue
            if frame[0] == 'stdout':
                output += frame[1]
                match = re.search(r'KA_REVIEWS_COPIED:(\{[^\r\n]*\})', output)
                if match:
                    try:
                        report = json.loads(match.group(1))
                    except json.JSONDecodeError:
                        continue
                    break
        (ROOT / 'results/shadow_authority_core_copy_v1_transcript_20261102.txt').write_text(output)
        if report is None:
            print('REMOTE_TRANSCRIPT_TAIL', repr(output[-1800:]))
        assert report is not None, 'No complete remote process snapshot received'
    finally:
        if ws is not None:
            ws.close()
        request('/api/terminals/' + urllib.parse.quote(name, safe=''), 'DELETE')
        terminal_receipt.write_text(json.dumps({'notebook_id':notebook,'terminal_name':name,'created_for':'shadow_authority_core_copy_v1','closed':True})+'\n')
    report.update(notebook_id=notebook, temporary_inspection_terminal_closed=True,
                  transport='authenticated Jupyter terminal; direct verified TLS; credentials not recorded')
    out = ROOT / 'results/shadow_authority_core_copy_20261102.json'
    assert not out.exists()
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status':'authority_core_provenance_copied','archives':len(report['archives']),'temporary_inspection_terminal_closed':True}))


if __name__ == '__main__':
    main()
