import tkinter as tk
from tkinter import messagebox
import serial
import time
import math


# ============================================================
# USER SETTINGS
# ============================================================

COM_PORT = "COM9"          # CHANGE THIS
BAUD_RATE = 9600

GRID_SIZE = 28

# Display canvas is larger than the actual 28x28 image
DISPLAY_SIZE = 280
CELL_SIZE = DISPLAY_SIZE / GRID_SIZE

# Brush radius in 28x28 image pixels
BRUSH_RADIUS = 2.2

# FPGA timeout
FPGA_TIMEOUT = 10


# ============================================================
# GLOBALS
# ============================================================

# 28x28 grayscale image
#
# 0   = black
# 255 = white
#
pixels = [
    [0.0 for _ in range(GRID_SIZE)]
    for _ in range(GRID_SIZE)
]

ser = None


# ============================================================
# UART
# ============================================================

def open_uart():

    global ser

    try:

        ser = serial.Serial(
            port=COM_PORT,
            baudrate=BAUD_RATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )

        ser.reset_input_buffer()
        ser.reset_output_buffer()

        uart_status.config(
            text=f"UART connected: {COM_PORT}"
        )

    except serial.SerialException as e:

        ser = None

        uart_status.config(
            text="UART not connected"
        )

        messagebox.showerror(
            "UART Error",
            str(e)
        )


# ============================================================
# PIXEL COLOR
# ============================================================

def gray_to_color(value):

    value = max(0, min(255, int(value)))

    # Black background -> white digit
    return f"#{value:02x}{value:02x}{value:02x}"


# ============================================================
# UPDATE CANVAS
# ============================================================

def update_canvas():

    for row in range(GRID_SIZE):

        for col in range(GRID_SIZE):

            value = pixels[row][col]

            canvas.itemconfig(
                pixel_rect[row][col],
                fill=gray_to_color(value)
            )


# ============================================================
# DRAW GRADIENT BRUSH
# ============================================================

def draw_brush(event):

    # Convert screen position to 28x28 coordinates

    cx = event.x / CELL_SIZE
    cy = event.y / CELL_SIZE

    radius = BRUSH_RADIUS

    # Only update pixels around brush

    min_x = max(
        0,
        int(math.floor(cx - radius - 1))
    )

    max_x = min(
        GRID_SIZE - 1,
        int(math.ceil(cx + radius + 1))
    )

    min_y = max(
        0,
        int(math.floor(cy - radius - 1))
    )

    max_y = min(
        GRID_SIZE - 1,
        int(math.ceil(cy + radius + 1))
    )


    for row in range(min_y, max_y + 1):

        for col in range(min_x, max_x + 1):

            # Distance from pixel center to mouse

            dx = (col + 0.5) - cx
            dy = (row + 0.5) - cy

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance > radius:
                continue


            # ------------------------------------------------
            # Gradient
            #
            # Center = white
            # Edge   = gray
            #
            # Smooth falloff
            # ------------------------------------------------

            normalized = distance / radius

            intensity = (
                math.cos(
                    normalized * math.pi / 2
                ) ** 2
            )

            # Maximum brightness
            new_value = 255.0 * intensity


            # Accumulate strokes instead of overwriting them
            old_value = pixels[row][col]

            pixels[row][col] = max(
                old_value,
                new_value
            )


    update_canvas()


# ============================================================
# ERASE BRUSH
# ============================================================

def erase_brush(event):

    cx = event.x / CELL_SIZE
    cy = event.y / CELL_SIZE

    radius = BRUSH_RADIUS


    min_x = max(
        0,
        int(math.floor(cx - radius - 1))
    )

    max_x = min(
        GRID_SIZE - 1,
        int(math.ceil(cx + radius + 1))
    )

    min_y = max(
        0,
        int(math.floor(cy - radius - 1))
    )

    max_y = min(
        GRID_SIZE - 1,
        int(math.ceil(cy + radius + 1))
    )


    for row in range(min_y, max_y + 1):

        for col in range(min_x, max_x + 1):

            dx = (col + 0.5) - cx
            dy = (row + 0.5) - cy

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance > radius:
                continue

            normalized = distance / radius

            erase_strength = (
                math.cos(
                    normalized * math.pi / 2
                ) ** 2
            )

            pixels[row][col] *= (
                1.0 - erase_strength
            )


    update_canvas()


# ============================================================
# CLEAR
# ============================================================

def clear_image():

    for row in range(GRID_SIZE):

        for col in range(GRID_SIZE):

            pixels[row][col] = 0.0


    update_canvas()


    prediction_label.config(
        text="Prediction: ---"
    )

    status_label.config(
        text="Draw a digit"
    )


# ============================================================
# 28x28 GRAYSCALE -> 784 BITS
# ============================================================

def pixels_to_bits():

    bits = []

    for row in range(GRID_SIZE):

        for col in range(GRID_SIZE):

            # Same 0.5 threshold as MNIST
            #
            # Python MNIST:
            # (x >= 0.5).float()
            #
            # Here:
            # 128/255 ≈ 0.502

            if pixels[row][col] >= 128:

                bits.append("1")

            else:

                bits.append("0")


    assert len(bits) == 784

    return bits


# ============================================================
# 784 BITS -> 98 BYTES
# ============================================================

def bits_to_bytes(bits):

    assert len(bits) == 784

    image_bytes = []

    for i in range(0, 784, 8):

        byte = 0

        for b in bits[i:i + 8]:

            byte = (
                byte << 1
            ) | int(b)


        image_bytes.append(byte)


    assert len(image_bytes) == 98

    return image_bytes


# ============================================================
# WAIT FOR FPGA LINE
# ============================================================

def wait_for_line(expected, timeout=FPGA_TIMEOUT):

    start_time = time.time()

    while time.time() - start_time < timeout:

        line = ser.readline().decode(
            "ascii",
            errors="ignore"
        ).strip()

        if not line:
            continue

        print("FPGA:", line)

        if line == expected:

            return True


    return False


# ============================================================
# SEND IMAGE TO FPGA
# ============================================================

def send_to_fpga():

    if ser is None or not ser.is_open:

        messagebox.showerror(
            "UART Error",
            "UART is not connected."
        )

        return


    # --------------------------------------------------------
    # Convert drawing to binary
    # --------------------------------------------------------

    bits = pixels_to_bits()

    image_bytes = bits_to_bytes(bits)


    print()
    print("=" * 60)
    print("Sending image to FPGA")
    print("=" * 60)

    print(
        "Number of bits:",
        len(bits)
    )

    print(
        "Number of bytes:",
        len(image_bytes)
    )

    print(
        "Bytes:",
        " ".join(
            f"{x:02X}"
            for x in image_bytes
        )
    )


    # --------------------------------------------------------
    # Clear stale UART data
    # --------------------------------------------------------

    ser.reset_input_buffer()


    # --------------------------------------------------------
    # Request transaction
    # --------------------------------------------------------

    status_label.config(
        text="Requesting FPGA..."
    )

    root.update_idletasks()


    ser.write(b"S")
    ser.flush()


    # --------------------------------------------------------
    # Wait for READY
    # --------------------------------------------------------

    status_label.config(
        text="Waiting for READY..."
    )

    root.update_idletasks()


    if not wait_for_line("READY"):

        messagebox.showerror(
            "FPGA Timeout",
            "FPGA did not respond with READY."
        )

        status_label.config(
            text="FPGA timeout"
        )

        return


    # --------------------------------------------------------
    # Send 98 bytes
    # --------------------------------------------------------

    status_label.config(
        text="Sending 98 bytes..."
    )

    root.update_idletasks()


    ser.write(bytes(image_bytes))
    ser.flush()


    print("98 bytes sent.")


    # --------------------------------------------------------
    # Wait for prediction
    # --------------------------------------------------------

    status_label.config(
        text="BNN inference running..."
    )

    root.update_idletasks()


    start_time = time.time()

    prediction = None


    while time.time() - start_time < FPGA_TIMEOUT:

        line = ser.readline().decode(
            "ascii",
            errors="ignore"
        ).strip()


        if not line:

            continue


        print("FPGA:", line)


        if line.startswith("PREDICTION:"):

            try:

                prediction = int(
                    line.split(":")[1]
                )

            except ValueError:

                prediction = None

            break


    # --------------------------------------------------------
    # Display result
    # --------------------------------------------------------

    if prediction is None:

        prediction_label.config(
            text="Prediction: TIMEOUT"
        )

        status_label.config(
            text="No prediction received"
        )

        return


    prediction_label.config(
        text=f"Prediction: {prediction}"
    )

    status_label.config(
        text="Inference complete"


    )

    print(
        "FPGA prediction:",
        prediction
    )


# ============================================================
# CLOSE APPLICATION
# ============================================================

def close_application():

    global ser

    if ser is not None:

        if ser.is_open:

            ser.close()


    root.destroy()


# ============================================================
# GUI
# ============================================================

root = tk.Tk()

root.title(
    "Arty A7 BNN - Handwritten Digit"
)

root.geometry(
    "600x600"
)

root.resizable(
    False,
    False
)


# ============================================================
# TITLE
# ============================================================

title = tk.Label(
    root,
    text="MNIST → Arty A7 BNN Accelerator",
    font=("Arial", 20, "bold")
)

title.pack(pady=10)


subtitle = tk.Label(
    root,
    text="Draw a digit",
    font=("Arial", 12)
)

subtitle.pack()


# ============================================================
# CANVAS
# ============================================================

canvas_frame = tk.Frame(
    root
)

canvas_frame.pack(pady=15)


canvas = tk.Canvas(
    canvas_frame,
    width=DISPLAY_SIZE,
    height=DISPLAY_SIZE,
    bg="black",
    highlightthickness=2,
    highlightbackground="gray"
)

canvas.pack()


# ============================================================
# CREATE 28x28 PIXELS
# ============================================================

pixel_rect = [
    [None for _ in range(GRID_SIZE)]
    for _ in range(GRID_SIZE)
]


for row in range(GRID_SIZE):

    for col in range(GRID_SIZE):

        x1 = col * CELL_SIZE
        y1 = row * CELL_SIZE

        x2 = (col + 1) * CELL_SIZE
        y2 = (row + 1) * CELL_SIZE


        pixel_rect[row][col] = (
            canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill="black",
                outline=""
            )
        )


# ============================================================
# MOUSE CONTROLS
# ============================================================

canvas.bind(
    "<Button-1>",
    draw_brush
)

canvas.bind(
    "<B1-Motion>",
    draw_brush
)


# Right mouse button = erase

canvas.bind(
    "<Button-3>",
    erase_brush
)

canvas.bind(
    "<B3-Motion>",
    erase_brush
)


# ============================================================
# BUTTONS
# ============================================================

button_frame = tk.Frame(
    root
)

button_frame.pack(pady=5)


clear_button = tk.Button(
    button_frame,
    text="CLEAR",
    command=clear_image,
    width=15,
    height=2,
    font=("Arial", 11)
)

clear_button.pack(
    side=tk.LEFT,
    padx=10
)


send_button = tk.Button(
    button_frame,
    text="SEND TO FPGA",
    command=send_to_fpga,
    width=18,
    height=2,
    font=("Arial", 11, "bold")
)

send_button.pack(
    side=tk.LEFT,
    padx=10
)


# ============================================================
# PREDICTION
# ============================================================

prediction_label = tk.Label(
    root,
    text="Prediction: ---",
    font=("Arial", 20, "bold")
)

prediction_label.pack(
    pady=10
)


# ============================================================
# STATUS
# ============================================================

status_label = tk.Label(
    root,
    text="Draw a digit",
    font=("Arial", 11)
)

status_label.pack()


uart_status = tk.Label(
    root,
    text=f"UART: {COM_PORT} @ {BAUD_RATE}",
    font=("Arial", 10)
)

uart_status.pack(
    pady=5
)


# ============================================================
# OPEN UART
# ============================================================

open_uart()


# ============================================================
# CLOSE HANDLER
# ============================================================

root.protocol(
    "WM_DELETE_WINDOW",
    close_application
)


# ============================================================
# START
# ============================================================

root.mainloop()