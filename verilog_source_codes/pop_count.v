`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/28/2026 02:11:28 PM
// Design Name: 
// Module Name: pop_count
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


module pop_count#(parameter WIDTH=784)
(input [WIDTH-1:0] xnor_in, output reg signed [15:0] dotprod);
reg [$clog2(WIDTH)-1:0] popcnt;
integer i;
    always @ (*) begin
        popcnt=0;
        for (i=0;i<WIDTH;i=i+1) begin
            popcnt=popcnt+xnor_in[i];
        end
        dotprod=(popcnt<<1) - WIDTH;
    end

endmodule
