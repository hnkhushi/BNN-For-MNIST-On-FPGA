#include "platform.h"
#include "xparameters.h"
#include "xgpio.h"
#include "xuartlite.h"
#include "xil_printf.h"
#include "xstatus.h"
#include "sleep.h"


/* ============================================================
 * UART
 * ============================================================ */

#define UARTLITE_BASEADDR     XPAR_AXI_UARTLITE_0_BASEADDR


/* ============================================================
 * BNN GPIO base addresses
 *
 * GPIO0 = 8-bit image data
 * GPIO1 = 1-bit byte_valid
 * GPIO2 = 4-bit BCD prediction
 * GPIO3 = 1-bit bnn_done
 * ============================================================ */

#define GPIO_DATA_BASEADDR    XPAR_XGPIO_0_BASEADDR
#define GPIO_VALID_BASEADDR   XPAR_XGPIO_1_BASEADDR
#define GPIO_BCD_BASEADDR     XPAR_XGPIO_2_BASEADDR
#define GPIO_DONE_BASEADDR    XPAR_XGPIO_3_BASEADDR


/* ============================================================
 * Image size
 * ============================================================ */

#define IMAGE_BYTES           98


/* ============================================================
 * Peripheral instances
 * ============================================================ */

XUartLite UartLite0;

XGpio GpioData;
XGpio GpioValid;
XGpio GpioBCD;
XGpio GpioDone;


/* ============================================================
 * Image buffer
 * ============================================================ */

u8 image[IMAGE_BYTES];


/* ============================================================
 * UART initialization
 * ============================================================ */

int UARTLite_Init(UINTPTR BaseAddress)
{
    int Status;

    Status = XUartLite_Initialize(
                &UartLite0,
                BaseAddress
             );

    if (Status != XST_SUCCESS)
        return XST_FAILURE;


    Status = XUartLite_SelfTest(&UartLite0);

    if (Status != XST_SUCCESS)
        return XST_FAILURE;


    XUartLite_ResetFifos(&UartLite0);

    return XST_SUCCESS;
}


/* ============================================================
 * GPIO initialization
 * ============================================================ */

int GPIO_Init(void)
{
    int Status;


    /* GPIO0 - image data */

    Status = XGpio_Initialize(
                &GpioData,
                GPIO_DATA_BASEADDR
             );

    if (Status != XST_SUCCESS)
        return XST_FAILURE;


    /* GPIO1 - byte valid */

    Status = XGpio_Initialize(
                &GpioValid,
                GPIO_VALID_BASEADDR
             );

    if (Status != XST_SUCCESS)
        return XST_FAILURE;


    /* GPIO2 - BCD prediction */

    Status = XGpio_Initialize(
                &GpioBCD,
                GPIO_BCD_BASEADDR
             );

    if (Status != XST_SUCCESS)
        return XST_FAILURE;


    /* GPIO3 - BNN done */

    Status = XGpio_Initialize(
                &GpioDone,
                GPIO_DONE_BASEADDR
             );

    if (Status != XST_SUCCESS)
        return XST_FAILURE;


    /*
     * GPIO0:
     * 8-bit output
     */

    XGpio_SetDataDirection(
        &GpioData,
        1,
        0x00
    );


    /*
     * GPIO1:
     * 1-bit output
     */

    XGpio_SetDataDirection(
        &GpioValid,
        1,
        0x00
    );


    /*
     * GPIO2:
     * 4-bit input
     */

    XGpio_SetDataDirection(
        &GpioBCD,
        1,
        0x0F
    );


    /*
     * GPIO3:
     * 1-bit input
     */

    XGpio_SetDataDirection(
        &GpioDone,
        1,
        0x01
    );


    /*
     * Initial GPIO values
     */

    XGpio_DiscreteWrite(
        &GpioData,
        1,
        0x00
    );

    XGpio_DiscreteWrite(
        &GpioValid,
        1,
        0x00
    );


    return XST_SUCCESS;
}


/* ============================================================
 * Receive exactly 98 bytes from PC
 *
 * XUartLite_Recv() is non-blocking, so we keep calling it
 * until all 98 bytes have arrived.
 * ============================================================ */

int ReceiveImage(void)
{
    unsigned int received = 0;
    unsigned int count;


    while (received < IMAGE_BYTES)
    {
        count = XUartLite_Recv(
                    &UartLite0,
                    &image[received],
                    IMAGE_BYTES - received
                );

        received += count;
    }


    return received;
}


/* ============================================================
 * Send one byte to the BNN
 *
 * GPIO0 = data
 * GPIO1 = byte_valid
 * ============================================================ */

void SendByteToBNN(u8 data)
{
    /*
     * Put data on GPIO0.
     */

    XGpio_DiscreteWrite(
        &GpioData,
        1,
        data
    );


    /*
     * Allow data to settle.
     *
     * MicroBlaze is 100 MHz.
     * BNN is 50 MHz.
     */

    usleep(100);


    /*
     * Assert byte_valid.
     */

    XGpio_DiscreteWrite(
        &GpioValid,
        1,
        1
    );


    /*
     * Keep valid high long enough for the
     * 50 MHz BNN clock domain to see it.
     */

    usleep(100);


    /*
     * Deassert byte_valid.
     */

    XGpio_DiscreteWrite(
        &GpioValid,
        1,
        0
    );


    /*
     * Gap before next byte.
     */

    usleep(100);
}


/* ============================================================
 * Send complete 98-byte image to BNN
 * ============================================================ */

void SendImageToBNN(void)
{
    int i;

    for (i = 0; i < IMAGE_BYTES; i++)
    {
        SendByteToBNN(image[i]);
    }
}


/* ============================================================
 * Send prediction to PC
 *
 * Format:
 *
 * PREDICTION:5\r\n
 * ============================================================ */

void SendPrediction(u32 prediction)
{
    xil_printf("PREDICTION:%lu\r\n", prediction);
}


/* ============================================================
 * Wait for BNN completion
 *
 * Returns:
 *   1 = BNN done
 *   0 = timeout
 * ============================================================ */

int WaitForBNNDone(void)
{
    u32 done;

    unsigned int timeout = 0;


    while (1)
    {
        done = XGpio_DiscreteRead(
                    &GpioDone,
                    1
               );


        if (done & 0x01)
        {
            return 1;
        }


        /*
         * 1 ms per iteration.
         *
         * 10000 iterations = approximately 10 seconds.
         */

        usleep(1000);

        timeout++;


        if (timeout >= 10000)
        {
            return 0;
        }
    }
}


/* ============================================================
 * MAIN
 * ============================================================ */

int main(void)
{
    int Status;

    u32 prediction;


    init_platform();


    /* --------------------------------------------------------
     * UART initialization
     * -------------------------------------------------------- */

    Status = UARTLite_Init(
                UARTLITE_BASEADDR
             );

    if (Status != XST_SUCCESS)
    {
        xil_printf(
            "ERROR: UART initialization failed\r\n"
        );

        cleanup_platform();

        return XST_FAILURE;
    }


    /* --------------------------------------------------------
     * GPIO initialization
     * -------------------------------------------------------- */

    Status = GPIO_Init();

    if (Status != XST_SUCCESS)
    {
        xil_printf(
            "ERROR: GPIO initialization failed\r\n"
        );

        cleanup_platform();

        return XST_FAILURE;
    }


    /*
     * Initial startup message.
     *
     * This is useful if you open a terminal manually.
     */

    xil_printf(
        "\r\n"
    );

    xil_printf(
        "========================================\r\n"
    );

    xil_printf(
        "      MicroBlaze BNN UART Interface\r\n"
    );

    xil_printf(
        "========================================\r\n"
    );


    /* ========================================================
     * Continuous inference loop
     * ======================================================== */

    while (1)
{
    u8 command;

    /*
     * Wait for PC to request a transaction.
     */
    while (XUartLite_Recv(
               &UartLite0,
               &command,
               1) == 0)
    {
        /* wait */
    }

    /*
     * PC sent 'S'.
     */
    if (command == 'S')
    {
        xil_printf("READY\r\n");

        /*
         * Receive exactly 98 image bytes.
         */
        ReceiveImage();

        xil_printf("Received 98 bytes\r\n");

        /*
         * Send image to BNN.
         */
        SendImageToBNN();

        xil_printf("Image sent to BNN\r\n");

        /*
         * Wait for BNN.
         */
        Status = WaitForBNNDone();

        if (Status != 1)
        {
            xil_printf("ERROR: BNN timeout\r\n");
            continue;
        }

        xil_printf("BNN DONE\r\n");

        /*
         * Read prediction.
         */
        prediction = XGpio_DiscreteRead(
                         &GpioBCD,
                         1
                     );

        prediction &= 0x0F;

        SendPrediction(prediction);
    }
}


    cleanup_platform();

    return XST_SUCCESS;
}