from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def generate(s):
 s=s.replace('tb_record_backing_service_retained','tb_record_backing_service_small').replace('record_backing_service_retained #','record_backing_service_small #')
 for a,b in [('[23:0] cmd_owner','[26:0] cmd_owner'),('[63:0] cmd_cookie','[71:0] cmd_cookie'),('[63:0] rsp_cookie','[71:0] rsp_cookie'),('[63:0] token','[71:0] token'),('[63:0] make_cookie','[71:0] make_cookie'),('[63:0] result','[71:0] result'),('[5:0] record_in_offset','[2:0] record_in_offset'),('[5:0] record_out_offset','[2:0] record_out_offset'),('[3:0] leased','[31:0] leased'),('[166:0] saved_record','[163:0] saved_record'),('reg [63:0] offset_coverage=0,cookie;','reg [63:0] offset_coverage=0;reg [71:0] cookie;'),('fixtures[0:1343]','fixtures[0:191]'),('write_words[0:20]','write_words[0:2]'),('record_fixtures[0:4095]','record_fixtures[0:511]'),('cookie[58]','cookie[64]'),('token[58]','token[64]'),('result[25:2]','result[31:5]'),('result[41:26]','result[47:32]'),('result[57:42]','result[63:48]'),('result[58]','result[64]'),('result[1:0]','result[4:0]'),('1344','192'),('input_count!=64','input_count!=8'),('write_beats>=21','write_beats>=3'),('write_beats!=21','write_beats!=3'),('active_page*21','active_page*3'),('m_awlen>20','m_awlen>2'),('m_arlen>20','m_arlen>2'),('write_count>20','write_count>2'),('n<64','n<8'),('page_value*64','page_value*8'),('i>=64','i>=8'),('i!=64','i!=8'),('i[5:0]','i[2:0]'),('(fr*21)%64','(fr*3)%64'),("(64'd1<<26)","(72'd1<<32)"),('pages=64 records=4096','pages=64 records=512'),('test_slot<4','test_slot<32'),('test_slot=3;','test_slot=31;'),('txid=txid+4','txid=txid+32'),('(1<<(test_slot+1))',"(64'd1<<(test_slot+1))"),('(1<<test_slot)',"(64'd1<<test_slot)"),('fr=j>=6?3:0','fr=j>=6?21:0'),('words<4','words<22'),('transfer_page(3,1,0,0,1)','transfer_page(21,1,0,0,1)'),('k<63','k<7'),('record_fixtures[64+k]','record_fixtures[8+k]'),('feed_record(62,record_fixtures[127])','feed_record(6,record_fixtures[15])'),('record_fixtures[64]','record_fixtures[8]'),("(512'd1<<200)","(512'd1<<144)"),('memory[20]','memory[2]'),("(512'd1<<224)","(512'd1<<328)")]:
  assert a in s,a;s=s.replace(a,b)
 # Exercise owner bits above the original 24-bit domain.
 s=s.replace("24'h100000","27'h7000000").replace("24'h10003f","27'h700003f").replace("24'h200000","27'h6000000")
 return s
if __name__=='__main__':
 p=ROOT/'hardware/tb/tb_record_backing_service_small.sv';s=generate((ROOT/'hardware/tb/tb_record_backing_service_retained.sv').read_text())
 if p.exists():assert p.read_text()==s
 else:p.write_text(s)
