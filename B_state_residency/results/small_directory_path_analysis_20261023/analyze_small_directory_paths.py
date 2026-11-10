"""Extract routed max-path composition; no extrapolated Fmax or speedup."""
from pathlib import Path
import re,json,hashlib,csv
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/small_directory_path_analysis_20261023';out.mkdir()
 pair=ROOT/'results/rtl_small_codec_endpoint_timing_20261023';audit=json.loads((pair/'final_manifest.json').read_text());assert audit['audit_status']=='evidence_verified'
 result={'status':'verified_report_extraction','variants':{},'pair_manifest_sha256':sha(pair/'final_manifest.json'),'source_sha256':sha(Path(__file__)),'scope':'One routed run per configuration. Path composition is evidence, not a pipeline benefit prediction or platform Fmax.'}
 for name in ['dynamic','static']:
  p=pair/name/'timing_routed.rpt';assert sha(p)==audit['artifacts'][str(p.relative_to(pair))]
  text=p.read_text().split('Max Delay Paths',1)[1].split('Min Delay Paths',1)[0]
  blocks=re.split(r'(?=Slack \((?:MET|VIOLATED)\))',text)[1:];rows=[]
  for block in blocks:
   delay=re.search(r'Data Path Delay:\s+([\d.]+)ns\s+\(logic ([\d.]+)ns.*?route ([\d.]+)ns',block)
   if not delay:continue
   row={'source':re.search(r'Source:\s+(\S+)',block)[1],'destination':re.search(r'Destination:\s+(\S+)',block)[1],'delay_ns':float(delay[1]),'logic_ns':float(delay[2]),'route_ns':float(delay[3]),'logic_levels':int(re.search(r'Logic Levels:\s+(\d+)',block)[1])}
   row['route_fraction']=row['route_ns']/row['delay_ns'];rows.append(row)
  expected=[p for p in audit['variants'][name]['internal_paths'] if p['delay_type']=='max'];assert len(rows)==len(expected)==10
  for row,ref in zip(rows,expected):assert row['source']==ref['startpoint'] and row['destination']==ref['endpoint'] and abs(row['delay_ns']-float(ref['datapath_delay_ns']))<.0011
  result['variants'][name]=rows
 (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
 for n,rows in result['variants'].items():print(n,rows[0])
if __name__=='__main__':main()
