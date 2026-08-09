`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07/01/2026 03:20:43 PM
// Design Name: 
// Module Name: image_shift
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


module image_shift (
    input         clk,
    input         rst,
    input  [7:0]  gpio_data,
    input         byte_valid,
    input         consume,
    output [783:0] image_vector,
    output        vector_ready
);
    reg [783:0] shift_reg;
    reg [6:0]   byte_count;   // 0..97
    reg         ready;
    reg         byte_valid_d;
 
    wire byte_valid_pulse = byte_valid & ~byte_valid_d;
 
    always @(posedge clk) begin
        if (rst) begin
            byte_count   <= 7'd0;
            ready        <= 1'b0;
            byte_valid_d <= 1'b0;
            shift_reg    <= 784'd0;
        end else begin
            byte_valid_d <= byte_valid;
 
            if (consume) begin
                ready      <= 1'b0;
                byte_count <= 7'd0;
            end
            else if (byte_valid_pulse && !ready) begin
                shift_reg <= {shift_reg[775:0], gpio_data}; // MSB-first packing
                if (byte_count == 7'd97)
                    ready <= 1'b1;
                else
                    byte_count <= byte_count + 1'b1;
            end
        end
    end
 
    assign image_vector = shift_reg;
    assign vector_ready = ready;
endmodule
