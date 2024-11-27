import serial
import time

# Configuration variables
port = 'COM25'  # Replace with your Arduino's port
baud_rate = 115200  # GRBL's default baud rate
feed_rate = 100  # Movement speed in mm/min
one_turn_distance = 16  # Distance in mm for one full motor turn (adjust as per your setup)
debounce_time = 0.2  # Debounce delay in seconds

# Initialize the serial connection
try:
    serial_connection = serial.Serial(port, baud_rate, timeout=1)
    time.sleep(2)  # Wait for GRBL to initialize
    print("Connected to GRBL.")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit(1)

# Function to send a G-code command and wait for 'ok' response
def send_gcode(command):
    if serial_connection.isOpen():
        command = command.strip() + '\n'  # Ensure proper formatting
        serial_connection.write(command.encode())
        print(f"Sent: {command}")
        
        # Wait for 'ok' response from GRBL
        while True:
            response = serial_connection.readline().decode().strip()
            if response == 'ok':
                print(f"Response: {response}")
                break
    else:
        print("Serial connection is not open.")

# Function to check button state from GRBL status
def get_button_state():
    if serial_connection.isOpen():
        serial_connection.write(b'?\n')  # Request GRBL status
        status_response = serial_connection.readline().decode().strip()
        if 'Pn:' in status_response:
            pin_status = status_response.split('|')
            for field in pin_status:
                if field.startswith('Pn:'):
                    return field.split(':')[1]  # Return active pins (e.g., "Y", "Z")
    return ""

try:
    # Unlock GRBL and configure settings
    send_gcode('$X')  # Unlock the controller
    send_gcode('G21')  # Set units to millimeters
    send_gcode('G91')  # Set to relative positioning mode

    print("Listening for button presses...")

    while True:
        button_state = get_button_state()

        if 'Y' in button_state:  # Y+ button pressed
            print("Y+ Button pressed!")
            send_gcode(f'G1 X{one_turn_distance} F{feed_rate}')  # Move +X for one turn
            print(f"Moving motor by {one_turn_distance} mm with feed rate {feed_rate}.")
            time.sleep(debounce_time)  # Debounce delay

        elif 'Z' in button_state:  # Z+ button pressed
            print("Z+ Button pressed!")
            send_gcode(f'G1 X-{one_turn_distance} F{feed_rate}')  # Move -X for one turn
            print(f"Moving motor by -{one_turn_distance} mm with feed rate {feed_rate}.")
            time.sleep(debounce_time)  # Debounce delay

except KeyboardInterrupt:
    print("\nProgram interrupted by user.")
finally:
    if serial_connection.isOpen():
        serial_connection.close()
    print("Serial connection closed.")
