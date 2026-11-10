"""Replace test data storage with a sequential reader; keep all DUT checks."""
from pathlib import Path
from make_indexed_endpoint import transform

ROOT = Path(__file__).resolve().parents[2]


def generate():
    text = (ROOT / 'hardware/tb/tb_memory_endpoint_indexed.sv').read_text()
    text = transform(text, [
        ('module memory_endpoint_indexed_test #(parameter integer SMALL=0);',
         'module memory_endpoint_stream_test #(parameter integer SMALL=0,REPLAY_FRAMES=512,REPLAY_INDEX=9,EXPECT_COMMANDS=77099,EXPECT_TRANSFERS=6086,EXPECT_QUERIES=19);', 1),
        ('TB_FRAMES=SMALL?4:512,TB_INDEX=SMALL?2:9;', 'TB_FRAMES=SMALL?4:REPLAY_FRAMES,TB_INDEX=SMALL?2:REPLAY_INDEX;', 1),
        ('reg [511:0] raw_expected[0:127805];', 'integer page_fd,page_rc,page_sequence=0;reg [511:0] extra_page_word;', 1),
        ('initial begin #1500000000;$fatal(1,"memory endpoint watchdog");end',
         'initial begin #500000000000;$fatal(1,"memory endpoint watchdog");end', 1),
        ('$readmemh(pages_path,raw_expected);fd=$fopen(vectors_path,"r");if(!fd)$fatal(1,"cannot open vectors");',
         'page_fd=$fopen(pages_path,"r");if(!page_fd)$fatal(1,"cannot open expected pages");\n'
         '            fd=$fopen(vectors_path,"r");if(!fd)$fatal(1,"cannot open vectors");', 1),
        ('for(n=0;n<21;n=n+1)expected[n]=raw_expected[vpage_index*21+n];',
         '''if(vpage_index!=page_sequence)$fatal(1,"expected page sequence changed");
                    for(n=0;n<21;n=n+1)begin
                        page_rc=$fscanf(page_fd,"%h\\n",expected[n]);
                        if(page_rc!=1)$fatal(1,"truncated expected page");
                    end
                    page_sequence=page_sequence+1;''', 1),
        ('$fclose(fd);\n            if(vector_count!=77099 || completed_transfers!=6086 || completed_fences!=19',
         '''$fclose(fd);
            page_rc=$fscanf(page_fd,"%h",extra_page_word);
            if(page_rc!=-1 || page_sequence!=EXPECT_TRANSFERS)$fatal(1,"unexpected page suffix or missing transfer");
            $fclose(page_fd);
            if(vector_count!=EXPECT_COMMANDS || completed_transfers!=EXPECT_TRANSFERS || completed_fences!=EXPECT_QUERIES''', 1),
        ('vector_count=vector_count+1;',
         '''vector_count=vector_count+1;
                if(vo==11)$display("STREAM_QUERY_DONE queries=%0d commands=%0d transfers=%0d time_ns=%0t",completed_fences,vector_count,completed_transfers,$time);''', 1),
        ('module tb_memory_endpoint_indexed_small;memory_endpoint_indexed_test #(.SMALL(1)) test();endmodule\nmodule tb_memory_endpoint_indexed_actual;memory_endpoint_indexed_test #(.SMALL(0)) test();endmodule',
         '''module tb_memory_endpoint_stream_small;memory_endpoint_stream_test test();endmodule
module tb_memory_endpoint_stream_large;
    memory_endpoint_stream_test #(.REPLAY_FRAMES(23405),.REPLAY_INDEX(15),.EXPECT_COMMANDS(3286037),.EXPECT_TRANSFERS(414485),.EXPECT_QUERIES(7)) test();
endmodule''', 1)])
    return text


if __name__ == '__main__':
    target = ROOT / 'hardware/tb/tb_memory_endpoint_stream.sv'
    if target.exists():
        raise FileExistsError(target)
    target.write_text(generate())
