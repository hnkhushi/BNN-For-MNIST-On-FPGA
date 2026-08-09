`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/28/2026 01:58:28 PM
// Design Name: 
// Module Name: xnor_pop
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


module xnor_pop #(parameter WIDTH=784, parameter DEPTH=256,parameter MEM_FILE = "fc1_binary.mem")
(input clk, rst,start, input [WIDTH-1:0] input_vec, output reg [WIDTH-1:0] xnor_res, output reg valid,done);
    reg [WIDTH-1:0] rom [0:DEPTH-1];
    reg [$clog2(DEPTH)-1:0] addr=0;
    reg running;
    initial begin
        $readmemb(MEM_FILE,rom);
    end
    always @ (posedge clk) begin
        valid<=0;
        done<=0;
        if (rst) begin
            addr<=0;
            xnor_res<=0;
            valid<=0;
            running<=0;
        end
        else begin
            if (start) begin
                running<=1;
                addr<=0;
            end
            if (running) begin
                xnor_res<=~(input_vec ^ rom[addr]);
                valid<=1;
                if (addr==DEPTH-1) begin
                    running<=0;
                    done<=1'b1;
                end
                else begin
                    addr<=addr+1'b1;
                end
        end
    end
    end
endmodule
