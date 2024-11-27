import serial
import time
port="COM25"
baud_rate=115200
def connect_to_grbl(port, baud_rate):
    """
    Connects to the GRBL controller over the specified serial port.
    """
    try:
        print(f"Connecting to GRBL on port {port} with baud rate {baud_rate}...")
        grbl = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(1)  # Pause for GRBL to initialize
        grbl.write(b"\r\n\r\n")  # Reset GRBL
        time.sleep(2)
        grbl.flushInput()  # Clear the input buffer
        print("Connected to GRBL.")
        return grbl
    except Exception as e:
        print(f"Error connecting to GRBL: {e}")
        return None





connect_to_grbl(port, baud_rate)

