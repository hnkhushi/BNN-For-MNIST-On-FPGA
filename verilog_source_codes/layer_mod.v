`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/29/2026 09:06:24 PM
// Design Name: 
// Module Name: layer_mod
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


module layer_mod #(parameter WIDTH=784,parameter DEPTH=256,parameter MEM_FILE="fc1_binary.mem",parameter MEM_FILE1="fc1_thresholds.mem", parameter MEM_FILE2="fc1_dirns.mem")
(input clk,rst,start,input [WIDTH-1:0] inp,output [255:0] layer_out,output done1);
wire [WIDTH-1:0] out;
wire signed [15:0] prod;
wire valid;
xnor_pop #(.WIDTH(WIDTH),.DEPTH(DEPTH),.MEM_FILE(MEM_FILE))l1(clk,rst,start,inp,out,valid,done);
pop_count #(.WIDTH(WIDTH))l11(out,prod);
comparator #(.WIDTH(WIDTH),.MEM_FILE1(MEM_FILE1),.MEM_FILE2(MEM_FILE2))l12(clk,start,valid,prod,layer_out,done1);
endmodule
