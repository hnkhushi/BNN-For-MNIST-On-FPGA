`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/28/2026 08:00:45 PM
// Design Name: 
// Module Name: top_tb
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


module top_tb;
 
    reg clk;
    reg rst;
    reg [7:0] gpio_data;
    reg       byte_valid;
    wire [3:0] bcd_pins;
 
    // storage for the two test images so we can compare against what the
    // shift register actually assembled
    reg [7:0] image_a [0:97];
    reg [7:0] image_b [0:97];
    integer i;
 
    bnn_top_module dut (
        .clk        (clk),
        .rst        (rst),
        .gpio_data  (gpio_data),
        .byte_valid (byte_valid),
        .bcd_pins   (bcd_pins)
    );
 
    // 100MHz clock
    initial clk = 0;
    always #5 clk = ~clk;
 
    // send one byte: hold data steady, pulse strobe high for a few cycles
    // then low. This mimics XGpio_DiscreteWrite(data) followed by
    // XGpio_DiscreteWrite(strobe,1) then XGpio_DiscreteWrite(strobe,0) --
    // deliberately holding the strobe high for MORE than one cycle to
    // prove the edge-detector only captures once per byte, same as it
    // will need to do against real (slower) MicroBlaze bus timing.
    task send_byte(input [7:0] data);
        begin
            gpio_data  = data;
            @(posedge clk);
            byte_valid <= 1'b1;
            @(posedge clk);
            @(posedge clk);   // hold strobe high for 2 extra cycles on purpose
            byte_valid <= 1'b0;
            @(posedge clk);
            @(posedge clk);   // idle gap between bytes, like real software timing
        end
    endtask
 
    task send_image(input integer which); // 0 = image_a, 1 = image_b
        begin
            for (i = 0; i < 98; i = i + 1) begin
                if (which == 0)
                    send_byte(image_a[i]);
                else
                    send_byte(image_b[i]);
            end
        end
    endtask
 
    // watch vector_ready / consume inside the DUT for visibility
    // (hierarchical reference into the DUT's internal signals, sim-only)
    wire vector_ready_probe = dut.vector_ready;
    wire consume_probe      = dut.consume;
    wire start_pulse_probe  = dut.start_pulse;
 
    always @(posedge vector_ready_probe)
        $display("[%0t] vector_ready asserted -> image fully loaded", $time);
 
    always @(posedge start_pulse_probe)
        $display("[%0t] start_pulse fired -> BNN beginning inference", $time);
 
    always @(posedge consume_probe)
        $display("[%0t] consume fired -> shift register released for next image", $time);
 
    initial begin
        rst        = 1'b1;
        gpio_data  = 8'd0;
        byte_valid = 1'b0;
 
        // fill two test images with distinct, easy-to-recognize patterns.
        // replace these with real MNIST test vectors packed into bytes
        // once you want to check an actual predicted digit.
        for (i = 0; i < 98; i = i + 1) begin
            //image_a[i] = i;            // 0x00, 0x01, 0x02 ... 0x61
            image_b[i] = 8'hFF - i;    // 0xFF, 0xFE, 0xFD ...
        end
        image_a[ 0] = 8'h00;
image_a[ 1] = 8'h00;
image_a[ 2] = 8'h00;
image_a[ 3] = 8'h00;
image_a[ 4] = 8'h00;
image_a[ 5] = 8'h00;
image_a[ 6] = 8'h00;
image_a[ 7] = 8'h00;
image_a[ 8] = 8'h00;
image_a[ 9] = 8'h00;
image_a[10] = 8'h00;
image_a[11] = 8'h00;
image_a[12] = 8'h00;
image_a[13] = 8'h00;
image_a[14] = 8'h00;
image_a[15] = 8'h00;
image_a[16] = 8'h00;
image_a[17] = 8'h00;
image_a[18] = 8'h00;
image_a[19] = 8'h00;
image_a[20] = 8'h00;
image_a[21] = 8'h00;
image_a[22] = 8'h00;
image_a[23] = 8'h3F;
image_a[24] = 8'h00;
image_a[25] = 8'h07;
image_a[26] = 8'hFF;
image_a[27] = 8'hF8;
image_a[28] = 8'h00;
image_a[29] = 8'hFF;
image_a[30] = 8'hE3;
image_a[31] = 8'h00;
image_a[32] = 8'h1F;
image_a[33] = 8'h80;
image_a[34] = 8'h00;
image_a[35] = 8'h03;
image_a[36] = 8'h90;
image_a[37] = 8'h00;
image_a[38] = 8'h00;
image_a[39] = 8'h7C;
image_a[40] = 8'h00;
image_a[41] = 8'h00;
image_a[42] = 8'h03;
image_a[43] = 8'hFC;
image_a[44] = 8'h00;
image_a[45] = 8'h00;
image_a[46] = 8'h01;
image_a[47] = 8'hF0;
image_a[48] = 8'h00;
image_a[49] = 8'h00;
image_a[50] = 8'h03;
image_a[51] = 8'hC0;
image_a[52] = 8'h00;
image_a[53] = 8'h00;
image_a[54] = 8'h1E;
image_a[55] = 8'h00;
image_a[56] = 8'h00;
image_a[57] = 8'h00;
image_a[58] = 8'hE0;
image_a[59] = 8'h00;
image_a[60] = 8'h00;
image_a[61] = 8'h03;
image_a[62] = 8'h00;
image_a[63] = 8'h00;
image_a[64] = 8'h00;
image_a[65] = 8'h30;
image_a[66] = 8'h00;
image_a[67] = 8'h00;
image_a[68] = 8'h07;
image_a[69] = 8'h00;
image_a[70] = 8'h00;
image_a[71] = 8'h00;
image_a[72] = 8'hE0;
image_a[73] = 8'h00;
image_a[74] = 8'h00;
image_a[75] = 8'h1E;
image_a[76] = 8'h00;
image_a[77] = 8'h00;
image_a[78] = 8'h07;
image_a[79] = 8'hC0;
image_a[80] = 8'h00;
image_a[81] = 8'h19;
image_a[82] = 8'hF0;
image_a[83] = 8'h00;
image_a[84] = 8'h01;
image_a[85] = 8'hFE;
image_a[86] = 8'h00;
image_a[87] = 8'h00;
image_a[88] = 8'h0F;
image_a[89] = 8'h80;
image_a[90] = 8'h00;
image_a[91] = 8'h00;
image_a[92] = 8'h00;
image_a[93] = 8'h00;
image_a[94] = 8'h00;
image_a[95] = 8'h00;
image_a[96] = 8'h00;
image_a[97] = 8'h00;
        repeat (5) @(posedge clk);
        rst = 1'b0;
        repeat (5) @(posedge clk);
 
        $display("=== Sending image A ===");
        send_image(0);
 
        // wait for the full pipeline to finish: last_layer's final_done
        wait (dut.t1.final_done == 1'b1);
        @(posedge clk);
        $display("[%0t] Image A result: final_out = %0d, bcd_pins = %0d",
                  $time, dut.final_out, bcd_pins);
 
        // give consume a moment to have fired and shift_reg to reset
        repeat (10) @(posedge clk);
 
        $display("=== Sending image B ===");
        send_image(1);
 
        wait (dut.t1.final_done == 1'b1);
        @(posedge clk);
        $display("[%0t] Image B result: final_out = %0d, bcd_pins = %0d",
                  $time, dut.final_out, bcd_pins);
 
        repeat (10) @(posedge clk);
        $display("=== Test complete ===");
        $finish;
    end
 
    // safety timeout in case something never fires (e.g. missing .mem
    // files causing xnor_pop to stall) -- adjust if your pipeline is
    // legitimately slower than this
    initial begin
        #250000;
        $display("!!! TIMEOUT -- something didn't complete in time !!!");
        $finish;
    end
 
endmodule


//wire [255:0] out2;
//wire [783:0] out;
//wire signed [15:0] prod;
//wire[255:0] lay1;
//reg comp1_start;
//xnor_pop #(.WIDTH(784),.DEPTH(256),.MEM_FILE("fc1_binary.mem"))layer1(clk,rst,network_start,1'b1,inp,out,valid);
//pop_count #(.WIDTH(784))l11(out,prod);
//comparator #(.WIDTH(256),.MEM_FILE1("fc1_thresholds.mem"),.MEM_FILE2("fc1_dirns.mem"))l12(clk,rst,valid,prod,lay1,done);
//xnor_pop #(.WIDTH(256),.DEPTH(256),.MEM_FILE("fc2_binary.mem"))layer2(clk,rst,comp1_start,done,lay1,out2,valid2);