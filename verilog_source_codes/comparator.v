`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/28/2026 04:33:13 PM
// Design Name: 
// Module Name: comparator
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


module comparator#(parameter WIDTH=256, parameter MEM_FILE1="fc1_thresholds.mem",parameter MEM_FILE2="fc1_dirns.mem")
(input clk,start,valid, input signed [15:0] dotprod, output reg [255:0]vec_out,output reg done);
reg signed [15:0] thresh [0:255];
reg direct [0:255];
reg [7:0] count;
reg running;
    initial begin
        $readmemh(MEM_FILE1,thresh);
        $readmemb(MEM_FILE2,direct);
        count=0;
    end
    always @(posedge clk) begin
        done<=0;
        if (start) begin
            count <= 0;
            vec_out <= 0;
            done <= 0;
            running<=1'b1;
        end
        else if (running&&valid) begin
            if (direct[count])
                vec_out[255-count] <= (dotprod >= thresh[count]);
            else
                vec_out[255-count] <= (dotprod <= thresh[count]);
    
            if (count == 8'd255) begin
                done <= 1'b1;
                running<=1'b0;
            end    
            
            else
                count <= count + 1;
        end
    end
endmodule
