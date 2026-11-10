"""Resident CPU execution of the exact HLS C++ decoder ABI.

This is a C-model integration provider, not FPGA/XRT execution or board timing.
Buffers and metadata caches are host allocations. Calls are single-threaded.
"""
import ctypes as C
import importlib.util
from pathlib import Path

from search_experiment import IncompleteDomain,edge_order


class HlsCModel:
    execution_kind='native_cpu_execution_of_hls_c_model'

    def __init__(self,reader,library,fixed_mode,image_capacity_words):
        if reader.mode!=fixed_mode:raise ValueError('C-model representation mismatch')
        root=Path(__file__).resolve().parents[1]
        spec=importlib.util.spec_from_file_location('_hls_fixture_contract',root/'hardware/hls/prepare_fixtures.py')
        host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
        host.IMAGE_DEPTH=image_capacity_words
        config=host.descriptor(reader)
        self.reader=reader
        self.known_sources={reader.text(reader.nodes[node][0]) for node,_,_ in reader.roots}
        self.ids={reader.text(node[0]):i for i,node in enumerate(reader.nodes)}
        self.image=(C.c_uint32*(len(reader.data)//4)).from_buffer_copy(reader.data)
        self.config=(C.c_uint32*32)(*config)
        self.requests=(C.c_uint32*1)()
        self.output=(C.c_uint32*(8*host.MAX_DEGREE))()
        self.result=(C.c_uint32*3)()
        self.written=C.c_uint32();self.failed=C.c_uint32()
        self.library=C.CDLL(str(Path(library).resolve()))
        word=C.POINTER(C.c_uint32)
        self.kernel=self.library.graph_expand
        self.kernel.argtypes=[word,word,word,word,word,C.c_uint32,C.c_uint32,word,word]
        self.kernel.restype=None
        self._strings={};self._attributes={};self._pips={}
        self.calls=self.unknown_calls=self.returned_records=0

    def text(self,index):
        if index not in self._strings:self._strings[index]=self.reader.text(index)
        return self._strings[index]

    def neighbors(self,node):
        if node not in self.ids:raise IncompleteDomain(node)
        index=self.ids[node];self.requests[0]=index
        self.kernel(self.image,self.config,self.requests,self.output,self.result,1,len(self.output),
                    C.byref(self.written),C.byref(self.failed))
        self.calls+=1
        start,degree,status=self.result
        if status==1:
            if (start,degree,self.written.value,self.failed.value)!=(0,0,0,1):raise ValueError('Malformed unknown result')
            self.unknown_calls+=1;raise IncompleteDomain(node)
        if status or start or degree!=self.written.value or self.failed.value:
            raise ValueError('HLS C-model decoder error: '+str(status))
        pairs=[]
        for i in range(degree):
            src,dst,tile,pip,up,down,attr,direction=self.output[8*i:8*i+8]
            if src!=index or direction>1:raise ValueError('Invalid HLS output identity/direction')
            tn=self.text(self.reader.tiles[tile][0]);un=tn+'/'+self.text(up);dn=tn+'/'+self.text(down)
            sw,dw=(dn,un) if direction else (un,dn)
            edge={'src':node,'dst':self.text(self.reader.nodes[dst][0]),'pip':tn+'/'+self.text(pip),
                  'src_wire':sw,'dst_wire':dw,'direction':'reverse' if direction else 'forward'}
            key=(tile,pip,up,down,attr)
            if key not in self._pips:
                if attr not in self._attributes:self._attributes[attr]=self.reader.attrs(attr)
                self._pips[key]={'up_wire':un,'down_wire':dn,'attributes':{**self._attributes[attr],'TILE':tn}}
            pairs.append((edge,self._pips[key]))
        self.returned_records+=degree
        return sorted(pairs,key=edge_order)
