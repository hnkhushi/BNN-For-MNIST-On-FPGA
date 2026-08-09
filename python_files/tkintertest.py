import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import torch
from torchvision import datasets, transforms
import serial
import time


# ============================================================
# Configuration
# ============================================================

BAUD_RATE = 9600

# Change this to your Arty A7 COM port
COM_PORT = "COM9"

IMAGE_BYTES = 98


# ============================================================
# Load MNIST
# ============================================================

transform = transforms.ToTensor()

test_dataset = datasets.MNIST(
    root="./data",
    train=False,
    download=True,
    transform=transform
)


# ============================================================
# Global variables
# ============================================================

current_image = None
current_label = None
current_index = None


# ============================================================
# Convert 784 binary pixels -> 98 bytes
# ============================================================

def bits_to_bytes(bits):

    assert len(bits) == 784

    image_bytes = []

    for i in range(0, 784, 8):

        byte = 0

        for b in bits[i:i+8]:
            byte = (byte << 1) | int(b)

        image_bytes.append(byte)

    return image_bytes


# ============================================================
# Get selected MNIST image
# ============================================================

def load_image():

    global current_image
    global current_label
    global current_index

    try:
        index = int(index_entry.get())

    except ValueError:
        messagebox.showerror(
            "Invalid index",
            "Enter an integer from 0 to 9999."
        )
        return

    if index < 0 or index >= len(test_dataset):

        messagebox.showerror(
            "Invalid index",
            "MNIST test index must be between 0 and 9999."
        )

        return

    # Get image
    image, label = test_dataset[index]

    current_image = image
    current_label = int(label)
    current_index = index

    # --------------------------------------------------------
    # Display image
    # --------------------------------------------------------

    # Convert tensor -> PIL image
    pil_image = transforms.ToPILImage()(image)

    # Enlarge for GUI
    pil_image = pil_image.resize(
        (280, 280),
        Image.Resampling.NEAREST
    )

    photo = ImageTk.PhotoImage(pil_image)

    image_label.configure(image=photo)
    image_label.image = photo

    # --------------------------------------------------------
    # Update information
    # --------------------------------------------------------

    index_value_label.config(
        text=f"Index: {index}"
    )

    true_label_value.config(
        text=f"True label: {label}"
    )

    prediction_value.config(
        text="Prediction: ---"
    )

    status_value.config(
        text="Ready to send"
    )


# ============================================================
# Send image to FPGA
# ============================================================

def send_to_fpga():

    global current_image
    global current_label

    if current_image is None:

        messagebox.showwarning(
            "No image",
            "Load an MNIST image first."
        )

        return

    try:

        # ----------------------------------------------------
        # Convert image to 784 binary bits
        # ----------------------------------------------------

        pix = torch.flatten(current_image)

        img = []

        for p in pix:

            if p >= 0.5:
                img.append("1")
            else:
                img.append("0")

        # ----------------------------------------------------
        # Convert 784 bits -> 98 bytes
        # ----------------------------------------------------

        image_bytes = bits_to_bytes(img)

        assert len(image_bytes) == 98

        # ----------------------------------------------------
        # Open UART
        # ----------------------------------------------------

        status_value.config(
            text="Opening UART..."
        )

        root.update_idletasks()

        ser = serial.Serial(
            port=COM_PORT,
            baudrate=BAUD_RATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=5
        )

        # Give UART/board a moment
        time.sleep(0.2)

        # ----------------------------------------------------
        # Wait for MicroBlaze READY
        # ----------------------------------------------------

        status_value.config(
            text="Waiting for FPGA..."
        )

        root.update_idletasks()

        # Clear anything left over in the UART receive buffer
        ser.reset_input_buffer()

        # Ask MicroBlaze to start a transaction
        ser.write(b'S')
        ser.flush()

        print("Waiting for FPGA READY...")

        ready = ser.readline().decode(
            "ascii",
            errors="ignore"
        ).strip()

        print("FPGA:", repr(ready))

        if ready != "READY":
            messagebox.showerror(
                "FPGA communication error",
                f"Expected READY but received: {repr(ready)}"
            )
            ser.close()
            return

        # ----------------------------------------------------
        # Send 98 bytes
        # ----------------------------------------------------

        status_value.config(
            text="Sending image..."
        )

        root.update_idletasks()

        ser.write(bytes(image_bytes))
        ser.flush()

        print("98 bytes sent")

        # ----------------------------------------------------
        # Wait for prediction
        # ----------------------------------------------------

        status_value.config(
            text="Running BNN..."
        )

        root.update_idletasks()

        prediction = None

        start_time = time.time()

        while time.time() - start_time < 10:

            response = ser.readline().decode(
                "ascii",
                errors="ignore"
            ).strip()

            if not response:
                continue

            print("FPGA:", response)

            if response.startswith("PREDICTION:"):

                prediction = int(
                    response.split(":")[1]
                )

                break

        ser.close()

        # ----------------------------------------------------
        # Display result
        # ----------------------------------------------------

        if prediction is None:

            prediction_value.config(
                text="Prediction: TIMEOUT"
            )

            status_value.config(
                text="FPGA timeout"
            )

            return

        prediction_value.config(
            text=f"Prediction: {prediction}"
        )

        # Compare
        if prediction == current_label:

            status_value.config(
                text="✓ CORRECT"
            )

        else:

            status_value.config(
                text="✗ INCORRECT"
            )

    except serial.SerialException as e:

        messagebox.showerror(
            "UART Error",
            str(e)
        )

        status_value.config(
            text="UART error"
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )

        status_value.config(
            text="Error"


        )


# ============================================================
# GUI
# ============================================================

root = tk.Tk()

root.title("MNIST → Arty A7 BNN")
root.geometry("600x600")
root.resizable(False, False)


# ------------------------------------------------------------
# Title
# ------------------------------------------------------------

title = tk.Label(
    root,
    text="MNIST → Arty A7 BNN Accelerator",
    font=("Arial", 18, "bold")
)

title.pack(pady=15)


# ------------------------------------------------------------
# Index frame
# ------------------------------------------------------------

index_frame = tk.Frame(root)

index_frame.pack(pady=5)

tk.Label(
    index_frame,
    text="MNIST Test Index:"
).pack(side=tk.LEFT)

index_entry = tk.Entry(
    index_frame,
    width=10
)

index_entry.pack(
    side=tk.LEFT,
    padx=10
)

index_entry.insert(0, "420")


load_button = tk.Button(
    index_frame,
    text="Load Image",
    command=load_image,
    width=12
)

load_button.pack(side=tk.LEFT)


# ------------------------------------------------------------
# Image display
# ------------------------------------------------------------

image_label = tk.Label(
    root,
    width=280,
    height=280,
    relief=tk.SUNKEN,
    bd=2
)

image_label.pack(pady=15)


# ------------------------------------------------------------
# Image information
# ------------------------------------------------------------

index_value_label = tk.Label(
    root,
    text="Index: ---",
    font=("Arial", 12)
)

index_value_label.pack()


true_label_value = tk.Label(
    root,
    text="True label: ---",
    font=("Arial", 12)
)

true_label_value.pack()


# ------------------------------------------------------------
# Send button
# ------------------------------------------------------------

send_button = tk.Button(
    root,
    text="SEND TO FPGA",
    command=send_to_fpga,
    font=("Arial", 14, "bold"),
    width=20,
    height=2
)

send_button.pack(pady=15)


# ------------------------------------------------------------
# Prediction
# ------------------------------------------------------------

prediction_value = tk.Label(
    root,
    text="Prediction: ---",
    font=("Arial", 16, "bold")
)

prediction_value.pack(pady=5)


status_value = tk.Label(
    root,
    text="Load an image",
    font=("Arial", 13)
)

status_value.pack(pady=5)


# ------------------------------------------------------------
# UART information
# ------------------------------------------------------------

uart_label = tk.Label(
    root,
    text=f"UART: {COM_PORT} @ {BAUD_RATE} baud",
    font=("Arial", 10)
)

uart_label.pack(pady=10)


# ============================================================
# Start GUI
# ============================================================

root.mainloop()