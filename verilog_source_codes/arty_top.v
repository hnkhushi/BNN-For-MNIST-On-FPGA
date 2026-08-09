`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// arty_top
//
// Instantiates the AXI/MicroBlaze/Uartlite/GPIO block design (system_wrapper)
// alongside the BNN system (bnn_top_module). Port names on system_wrapper
// (gpio_data_tri_o etc.) must match exactly what Vivado generated for your
// block design -- check system_wrapper.v after "Create HDL Wrapper" and
// correct the names below if they differ.
//////////////////////////////////////////////////////////////////////////////////

module arty_top (
    input        clk_100MHz,    // board 100MHz oscillator, pin E3 on Arty A7
    input        reset_rtl_0,   // active-high reset (wire to a board button/switch)
    input        uart_rtl_0_rxd,// from USB-UART bridge (RX into FPGA)
    output       uart_rtl_0_txd,// to USB-UART bridge (TX out of FPGA)
    output [3:0] bcd_pins       // to external BCD-to-7seg decoder chip
);
 
    wire [7:0] gpio_data_w;
    wire       byte_valid_w;
 
    system_wrapper u_system (
        .clk_100MHz     (clk_100MHz),
        .bnn_clk (bnn_clk),
        .reset_rtl_0    (reset_rtl_0),
        .uart_rtl_0_rxd (uart_rtl_0_rxd),
        .uart_rtl_0_txd (uart_rtl_0_txd),
        .GPIO_0_tri_o   (gpio_data_w),
        .GPIO_1_tri_o   (byte_valid_w)
        // .interrupt_0 left unconnected -- unused output, fine to omit
    );
 
    bnn_top_module u_bnn_system (
        .clk        (bnn_clk),
        .rst        (reset_rtl_0),
        .gpio_data  (gpio_data_w),
        .byte_valid (byte_valid_w),
        .bcd_pins   (bcd_pins)
    );
 
endmodule