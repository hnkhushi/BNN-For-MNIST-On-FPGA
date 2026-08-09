`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/30/2026 02:35:53 PM
// Design Name: 
// Module Name: last_layer
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module last_layer#(parameter WIDTH=256,parameter DEPTH=10,parameter MEM_FILE="fc1_binary.mem")
(input clk,rst,start,start_pulse,input [WIDTH-1:0] input_vector,output reg [3:0] final_out, output reg final_done);
wire [WIDTH-1:0] out;
wire valid;
reg [$clog2(DEPTH)-1:0] count;
reg signed [15:0] max_val;
reg [3:0] max_idx;
wire signed [15:0] prod;
xnor_pop #(.WIDTH(WIDTH),.DEPTH(DEPTH),.MEM_FILE(MEM_FILE))l3(clk,rst,start,input_vector,out,valid,done);
pop_count #(.WIDTH(WIDTH))l31(out,prod);
always @(posedge clk) begin
    //final_done<=1'b0;
    if (rst) begin
        final_done<=1'b0;
        final_out <= 4'd0;
        count <= 0;
        max_val <= -16'sd32768;
        max_idx <= 0;
    end
    else if (start_pulse) begin
        final_done<=1'b0;
    end
    else if (start) begin
        count <= 0;
        max_val <= -16'sd32768;
        max_idx <= 0;
    end

    else if(valid) begin
        //$display("start=%b valid=%b count=%0d prod=%0d",start, valid, count, prod);
            if(prod > max_val) begin
            max_val <= prod;
            max_idx <= count;
        end

        if(count < DEPTH-1)
            count <= count + 1;
            
        if(count == DEPTH-1)
begin
    final_out  <= (prod > max_val) ? count : max_idx;
    final_done <= 1'b1;
end
    end
end



endmodule
