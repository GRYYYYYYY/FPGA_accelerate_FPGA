`timescale 1ns/1ps
// Immutable lossless CSR + 32-byte attributes; one request and one AXI beat in flight.
module graph_static_reader(
    input wire clk,rst,
    input wire cfg_valid,output wire cfg_ready,
    input wire [63:0] cfg_offsets_base,cfg_edges_base,cfg_attrs_base,
    input wire [31:0] cfg_nodes,cfg_edges,
    output reg cfg_rsp_valid,input wire cfg_rsp_ready,output reg [2:0] cfg_status,
    output reg configured,
    input wire req_valid,output wire req_ready,input wire [1:0] req_op,
    input wire [31:0] req_cookie,req_node,req_index,
    output wire rsp_valid,input wire rsp_ready,output reg [3:0] rsp_status,
    output reg [31:0] rsp_cookie,rsp_parent,rsp_index,rsp_node,rsp_start,rsp_count,
    output reg [255:0] rsp_attrs,output wire fault,
    output reg [63:0] m_araddr,output wire [7:0] m_arlen,output wire [2:0] m_arsize,
    output wire [1:0] m_arburst,output wire [3:0] m_arid,
    output wire m_arvalid,input wire m_arready,
    input wire [511:0] m_rdata,input wire [3:0] m_rid,input wire [1:0] m_rresp,
    input wire m_rlast,m_rvalid,output wire m_rready
);
    localparam [1:0] IDLE=0,ADDRESS=1,DATA=2,REPLY=3;
    localparam [1:0] OFF_FIRST=0,OFF_SECOND=1,EDGE=2,ATTR=3;
    reg [1:0] state,kind;
    reg stopped,edge_request,attr_half;
    reg [3:0] word_offset;
    reg [63:0] offsets_base,edges_base,attrs_base;
    reg [31:0] nodes,edges,source_node,source_index,start_offset,degree,selected_node;
    wire [64:0] offsets_bytes=(({33'b0,cfg_nodes}+65'd1)*65'd4+65'd63)&~65'd63;
    wire [64:0] edges_bytes=({33'b0,cfg_edges}*65'd4+65'd63)&~65'd63;
    wire [64:0] attrs_bytes=({33'b0,cfg_nodes}*65'd32+65'd63)&~65'd63;
    wire [64:0] offsets_last={1'b0,cfg_offsets_base}+offsets_bytes-1'b1;
    wire [64:0] edges_last={1'b0,cfg_edges_base}+(edges_bytes==0?65'd1:edges_bytes)-1'b1;
    wire [64:0] attrs_last={1'b0,cfg_attrs_base}+attrs_bytes-1'b1;
    wire overlap=(cfg_offsets_base<=attrs_last[63:0]&&cfg_attrs_base<=offsets_last[63:0])||
        (edges_bytes!=0&&((cfg_edges_base<=offsets_last[63:0]&&cfg_offsets_base<=edges_last[63:0])||
                         (cfg_edges_base<=attrs_last[63:0]&&cfg_attrs_base<=edges_last[63:0])));
    wire unexpected=m_rvalid&&state!=DATA&&!(state==ADDRESS&&m_arready);
    assign fault=!rst&&(stopped||unexpected);
    assign cfg_ready=!rst&&!fault&&!configured&&!cfg_rsp_valid&&state==IDLE;
    assign req_ready=!rst&&!fault&&!cfg_rsp_valid&&state==IDLE&&!(cfg_valid&&cfg_ready);
    assign rsp_valid=!rst&&state==REPLY;
    assign m_arvalid=!rst&&!fault&&state==ADDRESS;
    assign m_rready=!rst&&!fault&&state==DATA;
    assign m_arlen=0;assign m_arsize=6;assign m_arburst=1;assign m_arid=0;
    wire [31:0] current_word=m_rdata[word_offset*32+:32];
    wire [31:0] next_word=m_rdata[(word_offset+1)*32+:32];
    task address(input [63:0] a,input [1:0] next_kind);
        begin m_araddr<={a[63:6],6'b0};kind<=next_kind;state<=ADDRESS;end
    endtask
    task fail(input [3:0] status);
        begin stopped<=1;rsp_status<=status;state<=REPLY;end
    endtask
    task offsets_complete(input [31:0] first,last);
        reg [31:0] edge_position;
        begin
            if(first>last||last>edges||(source_node==0&&first!=0)||(source_node==nodes-1'b1&&last!=edges))fail(4);
            else begin
                start_offset<=first;degree<=last-first;
                if(edge_request)begin
                    if(source_index>=last-first)begin rsp_status<=2;state<=REPLY;end
                    else begin
                        edge_position=first+source_index;word_offset<=edge_position[3:0];
                        address(edges_base+({32'b0,edge_position}<<2),EDGE);
                    end
                end else begin
                    selected_node<=source_node;attr_half<=source_node[0];
                    address(attrs_base+({32'b0,source_node}<<5),ATTR);
                end
            end
        end
    endtask
    always @(posedge clk)begin
        if(rst)begin
            state<=IDLE;kind<=0;stopped<=0;edge_request<=0;attr_half<=0;word_offset<=0;
            offsets_base<=0;edges_base<=0;attrs_base<=0;nodes<=0;edges<=0;source_node<=0;source_index<=0;
            start_offset<=0;degree<=0;selected_node<=0;m_araddr<=0;
            configured<=0;cfg_rsp_valid<=0;cfg_status<=0;
            rsp_status<=0;rsp_cookie<=0;rsp_parent<=0;rsp_index<=0;rsp_node<=0;rsp_start<=0;rsp_count<=0;rsp_attrs<=0;
        end else begin
            if(cfg_rsp_valid&&cfg_rsp_ready)cfg_rsp_valid<=0;
            if(state==REPLY&&rsp_ready)state<=IDLE;
            if(!stopped&&unexpected)begin
                stopped<=1;
                if(state!=IDLE&&state!=REPLY)begin rsp_status<=5;state<=REPLY;end
            end else if(!stopped)begin
                if(cfg_valid&&cfg_ready)begin
                    cfg_rsp_valid<=1;cfg_status<=0;
                    if(cfg_offsets_base[5:0]!=0||cfg_edges_base[5:0]!=0||cfg_attrs_base[5:0]!=0)cfg_status<=1;
                    else if(cfg_nodes==0||cfg_nodes>32'h01000000||offsets_last[64]||edges_last[64]||attrs_last[64])cfg_status<=2;
                    else if(overlap)cfg_status<=3;
                    else begin
                        configured<=1;offsets_base<=cfg_offsets_base;edges_base<=cfg_edges_base;attrs_base<=cfg_attrs_base;nodes<=cfg_nodes;edges<=cfg_edges;
                    end
                end
                case(state)
                    IDLE:if(req_valid&&req_ready)begin
                        rsp_cookie<=req_cookie;rsp_parent<=req_node;rsp_index<=req_index;
                        rsp_status<=0;rsp_node<=0;rsp_start<=0;rsp_count<=0;rsp_attrs<=0;
                        source_node<=req_node;source_index<=req_index;edge_request<=req_op==1;
                        if(!configured)begin rsp_status<=1;state<=REPLY;end
                        else if(req_op>1||req_node>=nodes||(req_op==0&&req_index!=0))begin rsp_status<=2;state<=REPLY;end
                        else begin word_offset<=req_node[3:0];address(offsets_base+({32'b0,req_node}<<2),OFF_FIRST);end
                    end
                    ADDRESS:if(m_arready)state<=DATA;
                    DATA:if(m_rvalid&&m_rready)begin
                        if(m_rid!=0||m_rresp!=0||!m_rlast)fail(3);
                        else case(kind)
                            OFF_FIRST:begin
                                if(word_offset==15)begin
                                    start_offset<=current_word;word_offset<=0;
                                    address(offsets_base+(({32'b0,source_node}+64'd1)<<2),OFF_SECOND);
                                end else offsets_complete(current_word,next_word);
                            end
                            OFF_SECOND:offsets_complete(start_offset,current_word);
                            EDGE:begin
                                if(current_word>=nodes)fail(4);
                                else begin selected_node<=current_word;attr_half<=current_word[0];address(attrs_base+({32'b0,current_word}<<5),ATTR);end
                            end
                            ATTR:begin
                                rsp_node<=selected_node;rsp_start<=start_offset;rsp_count<=degree;
                                rsp_attrs<=attr_half?m_rdata[511:256]:m_rdata[255:0];state<=REPLY;
                            end
                        endcase
                    end
                    default:begin end
                endcase
            end
        end
    end
endmodule
