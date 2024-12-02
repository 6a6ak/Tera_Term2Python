import serial
import time

# Establish a connection with the CNC shield (adjust '/dev/ttyUSB0' for your setup)
cnc_port = 'COM25'  # Replace with the correct serial port, e.g., COM3 on Windows
baud_rate = 115200  # GRBL typically uses this baud rate

try:
    cnc_serial = serial.Serial(cnc_port, baud_rate, timeout=1)
    print("Connected to GRBL CNC shield.")
except Exception as e:
    print(f"Error connecting to CNC shield: {e}")
    cnc_serial = None
# Function to check button state from GRBL status
def get_button_state():
    if cnc_serial and cnc_serial.isOpen():
        cnc_serial.write(b'?')  # Request GRBL status
        status_response = cnc_serial.readline().decode().strip()
        if 'Pn:' in status_response:
            pin_status = status_response.split('|')
            for field in pin_status:
                if field.startswith('Pn:'):
                    return field.split(':')[1]  # Return active pins (e.g., "Y", "Z")
    return ""
  
# Define functions to control motors using GRBL commands
def motor01_move_absolute(x_position: float, feed_rate: float):
    """
    Moves motor01 (X-axis motor) to an absolute position using G90.
    
    Args:
    x_position (float): Target position in mm.
    feed_rate (float): Speed in mm/min.
    """
    if cnc_serial:
        cnc_serial.write("G90\n".encode())  # Set absolute positioning mode
        command = f"G1 X{x_position} F{feed_rate}\n"  # Move X to the target position
        cnc_serial.write(command.encode())
        print(f"Command sent to motor01: {command.strip()}")
        time.sleep(0.1)

def motor02_move_relative(x_offset: float, feed_rate: float):
    """
    Moves motor02 (X-axis motor) by a relative distance using G91.
    
    Args:
    x_offset (float): Offset in mm (positive for CW, negative for CCW).
    feed_rate (float): Speed in mm/min.
    """
    if cnc_serial:
        cnc_serial.write("G91\n".encode())  # Set relative positioning mode
        command = f"G1 X{x_offset} F{feed_rate}\n"  # Move X by the offset
        cnc_serial.write(command.encode())
        print(f"Command sent to motor02: {command.strip()}")
        time.sleep(0.1)

# Function to send G-code commands to the CNC
def send_gcode(command: str):
    if cnc_serial:
        cnc_serial.write(f"{command}\n".encode())
        print(f"G-code sent: {command}")
        time.sleep(0.1)

# Example usage
if __name__ == "__main__":
    if cnc_serial:
        # Unlock GRBL (if necessary)
        cnc_serial.write("$X\n".encode())
        time.sleep(1)

        # Example: Move motor01 to an absolute position (X=50mm at 500mm/min)
        motor01_move_absolute(50.0, 500.0)
        time.sleep(2)  # Wait for 2 seconds
        
        # Example: Move motor02 by a relative offset (+20mm at 300mm/min)
        motor02_move_relative(20.0, 300.0)
        time.sleep(2)
        
        # Close the serial connection
        cnc_serial.close()


    step_distance = 1.0  # Define step distance in mm
    feed_rate = 100.0  # Define feed rate in mm/min
    debounce_time = 0.2  # Define debounce time in seconds

    while True:
            button_state = get_button_state()
            if 'Y' in button_state:  # Y+ button pressed
                print("Y+ Button pressed!")
                send_gcode(f'G1 X{step_distance} F{feed_rate}')  # Move +X by small distance
                time.sleep(debounce_time)  # Debounce delay

            elif 'Z' in button_state:  # Z+ button pressed
                print("Z+ Button pressed!")
                send_gcode(f'G1 X-{step_distance} F{feed_rate}')  # Move -X by small distance
                time.sleep(debounce_time)  # Debounce delay
