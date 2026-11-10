"""Mutations must not pass the independent decoder/semantic checker."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import check_native_site_routing as verifier

class FakeImage:
    nodes=[(0,),(1,)]
    tiles=[(2,)]
    str_offsets=list(range(7))
    def __init__(self,path):pass
    def text(self,n):return ['n0','n1','tile','pip','up','down'][n]
    def numeric_neighbors(self,n):return [(1,0,3,4,5,0,0)] if n==0 else []
    def attrs(self,n):return {'IS_PSEUDO':'1'}

class NativeSiteVerifierTests(unittest.TestCase):
    def test_decoder_and_mutation_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);directory=root/'experiment';directory.mkdir()
            folder=root/'data/derived/native_site_csr_inputs_20261023_v1';folder.mkdir(parents=True)
            fixture=root/'routing';fixture.mkdir()
            manifest={'queries':1,'image':str(root/'image.agr'),'routing_fixture':str(fixture/'routing.txt')}
            symbols={'resources':['bel/O6','bel/INIT'],'values':['D6'],'requirements':{'tile/pip':
                {'signal_resources':[0],'configuration_bits':[[1,3,1]],'configuration_values':[]}}}
            queries=[{'net_id':0,'net':'q','source':0,'sinks':[1]}]
            for path,value in ((folder/'manifest.json',manifest),(folder/'symbols.json',symbols),(fixture/'queries.json',queries)):
                path.write_text(json.dumps(value))
            plan={'cache_rows':4096,'max_iterations':80,'max_expansions':200000,'present_cap':8,'cpu':1,'owner_pid':123}
            command=[str(root/'build/native_site_20261023_v1'),manifest['image'],manifest['routing_fixture'],str(folder/'sites.txt'),'4096','80','200000','8']
            (directory/'csr.submission.json').write_text(json.dumps({'command':command,'cpu':1,'owner_pid':123}))
            (directory/'csr.log').write_text('done\n')
            demands=[[0],[[1,3,1]],[]]
            connection={'status':'found','cost':1,'expanded':1,'blocked':0,'unknown_sources':[],'unknown_pips':[]}
            raw={'scope':'tested_site_instances_only','status':'routed','routes':[{'net':0,'complete':True,'nodes':[0,1],
                'edges':[[0,1,0,3,4,5,0,0]],'demands':demands}],
                'iterations':[{'conflicts':[],'site_conflicts':[],'incomplete':[],'connections':[[connection]]}],
                'preparation_ms':1,'route_ms':2,'cache_hits':0,'cache_misses':1}
            decoded=[['bel/O6'],[['bel/INIT',3,1]],[]]
            reference={'status':'routed','routes':{'q':{'source':'n0','sinks':['n1'],'nodes':['n0','n1'],
                'edges':[{'src':'n0','dst':'n1','pip':'tile/pip','src_wire':'tile/up','dst_wire':'tile/down','direction':'forward'}],'complete':True}},
                'site_demands':{'q':decoded},'iterations':[{'iteration':0,'conflicts':{},'site_conflicts':[],
                'incomplete_nets':[],'outcomes':[{'net':'q','connections':[dict(connection,target='n1')]}]}]}
            def publish(value,hash_ok=True):
                path=directory/'csr.raw.json';path.write_text(json.dumps(value))
                (directory/'csr.receipt.json').write_text(json.dumps({'exit_code':0,'output_sha256':verifier.digest(path) if hash_ok else 'bad'}))
            with patch.object(verifier,'ROOT',root),patch.object(verifier,'PackedGraph',FakeImage):
                publish(raw)
                result=verifier.check_mode(directory,'csr',plan,reference)
                self.assertEqual(result['pips'],1)
                self.assertEqual(result['connections_checked'],1)
                mutations={}
                r=deepcopy(raw);r['routes'][0]['edges'][0][6]=1;mutations['attribute']=r
                r=deepcopy(raw);r['routes'][0]['edges'][0][7]=1;mutations['direction']=r
                r=deepcopy(raw);r['routes'][0]['demands'][1][0][2]=0;mutations['site_bits']=r
                r=deepcopy(raw);r['routes'].append(deepcopy(r['routes'][0]));mutations['duplicate_net']=r
                r=deepcopy(raw);r['routes'][0]['nodes']=[-1,1];mutations['negative_id']=r
                r=deepcopy(raw);r['iterations'][0]['connections'][0][0]['cost']=2;mutations['cost']=r
                r=deepcopy(raw);r['iterations'][0]['connections'][0][0]['unknown_pips']=[[0,3]];mutations['unknowns']=r
                r=deepcopy(raw);r['iterations'][0]['conflicts']=[[0,[0]]];mutations['conflicts']=r
                for name,value in mutations.items():
                    with self.subTest(name=name):
                        publish(value)
                        with self.assertRaises(ValueError):verifier.check_mode(directory,'csr',plan,reference)
                publish(raw,False)
                with self.assertRaises(ValueError):verifier.check_mode(directory,'csr',plan,reference)

if __name__=='__main__':unittest.main()
