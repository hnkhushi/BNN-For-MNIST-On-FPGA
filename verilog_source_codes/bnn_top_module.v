`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07/01/2026 03:18:01 PM
// Design Name: 
// Module Name: bnn_top_module
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


module bnn_top_module(input clk,rst,input [7:0] gpio_data,input byte_valid,output [3:0] bcd_pins,output bnn_done,vector_ready,start_pulse,consume,done2);
    wire [783:0] image_vector;
    //wire         vector_ready;
    //wire         consume;
    image_shift uu(clk,rst,gpio_data,byte_valid,consume,image_vector,vector_ready);
    reg vector_ready_d;
    always @(posedge clk) begin
        if (rst)
            vector_ready_d <= 1'b0;
        else
            vector_ready_d <= vector_ready;
    end
    assign start_pulse = vector_ready & ~vector_ready_d;
    wire [3:0] final_out;
    top_module t1(clk,rst,start_pulse,image_vector,final_out,consume,done2,final_done);
    assign bcd_pins = final_out;
    assign bnn_done=final_done;

endmodule
