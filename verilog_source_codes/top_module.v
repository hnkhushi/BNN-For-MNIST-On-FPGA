`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/30/2026 07:43:05 PM
// Design Name: 
// Module Name: top_module
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


module top_module(input clk,rst,start,input [783:0] inp, output [3:0] final_out,output done1,done2,final_done);
wire [255:0] layer_out,layer_out2;
//wire done2,final_done; 
 
layer_mod #(.WIDTH(784),.DEPTH(256),.MEM_FILE("fc1_binary.mem"),.MEM_FILE1("fc1_thresholds.mem"),.MEM_FILE2("fc1_dirns.mem"))layer1(clk,rst,start,inp,layer_out,done1);
layer_mod #(.WIDTH(256),.DEPTH(256),.MEM_FILE("fc2_binary.mem"),.MEM_FILE1("fc2_thresholds.mem"),.MEM_FILE2("fc2_dirns.mem"))layer2(clk,rst,done1,layer_out,layer_out2,done2);
last_layer #(.WIDTH(256),.DEPTH(10),.MEM_FILE("fc3_binary.mem"))layer3(clk,rst,done2,start,layer_out2,final_out,final_done);
endmodule
