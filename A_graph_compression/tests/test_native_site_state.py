"""Exact native/Python transaction snapshots, including failed replacements."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from site_resources import SiteState


@unittest.skipUnless(shutil.which('g++'),'g++ required')
class NativeSiteStateTests(unittest.TestCase):
    def test_shared_bits_exclusive_outputs_atomic_replace_and_release(self):
        # op, owner, signals, bits, categorical values, verified, unresolved
        actions=[
            ('R',1,[1],[(0,240,160)],[(1,7)],True,False),
            ('R',2,[2],[(0,240,160)],[(1,7)],True,False),
            ('R',3,[1],[],[],True,False),
            ('R',1,[3],[(0,240,176)],[],True,False),
            ('D',2),
            ('R',1,[3],[(0,240,176)],[],True,False),
            ('R',1,[4],[(0,16,16),(0,16,0)],[],True,False),
            ('R',3,[4],[(0,1,0)],[],True,False),
            ('R',3,[4],[],[(0,2)],True,False),
            ('R',3,[4],[],[],False,False),
            ('R',3,[4],[],[],True,True),
            ('R',3,[4],[(1,15,16)],[],True,False),
            ('R',3,[4],[],[(1,1),(1,2)],True,False),
            ('D',1),
            ('R',3,[1],[(1,(1<<64)-1,(1<<63)+1)],[(1,7)],True,False),
            ('R',8,[7],[],[],True,False),
            ('R',99,[7],[],[],True,False),
            ('R',3,[1,1],[(1,0,0)],[(1,7)],True,False)]
        state=SiteState(fixed_signals=[('r7',99)],fixed_bits=[('r0',15,5)],fixed_values=[('r0',1)])
        expected=[];lines=[str(len(actions))]
        for action in actions:
            op,net=action[:2];tokens=[op,str(net)];accepted=True
            try:
                if op=='D':state.release(net)
                else:
                    _,_,signals,bits,values,verified,unresolved=action
                    tokens.extend([str(int(verified)),str(int(unresolved)),str(len(signals)),*map(str,signals),str(len(bits))])
                    for row in bits:tokens.extend(map(str,row))
                    tokens.append(str(len(values)))
                    for row in values:tokens.extend(map(str,row))
                    payload={'signal_resources':['r'+str(r) for r in signals],
                             'configuration_bits':[('r'+str(r),m,v) for r,m,v in bits],
                             'configuration_values':[('r'+str(r),v) for r,v in values]}
                    if not verified:payload['status']='unverified'
                    if unresolved:payload['additional_requirements']=['unresolved']
                    state.replace(net,payload)
            except ValueError:accepted=False
            snapshot=[]
            for owner in sorted(state.signals.by_net):
                snapshot.append([owner,sorted(int(r[1:]) for r in state.signals.by_net[owner]),
                    sorted([int(r[1:]),m,v] for r,(m,v) in state.bits.by_net[owner].items()),
                    sorted([int(r[1:]),v] for r,v in state.values[owner].items())])
            expected.append({'accepted':accepted,'state':snapshot});lines.append(' '.join(tokens))
        with tempfile.TemporaryDirectory() as tmp:
            binary=Path(tmp)/'state'
            subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',
                str(ROOT/'tests/native_site_state_driver.cpp'),'-o',str(binary)],check=True)
            result=subprocess.run([str(binary)],input='\n'.join(lines)+'\n',text=True,capture_output=True,check=True)
        self.assertEqual(json.loads(result.stdout),expected)
        self.assertFalse(expected[3]['accepted'])
        self.assertEqual(expected[3]['state'],expected[2]['state'])


if __name__=='__main__':unittest.main()
