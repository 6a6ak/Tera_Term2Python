from tkinter import Button
import serial
import time
import RPi.GPIO as GPIO
# Configuration variables
port = 'COM25'  # Replace with your GRBL device port
baud_rate = 115200  # GRBL's default baud rate
movement_distance = 10  # Distance to move on the X-axis in mm
unit_system = 'mm'  # 'mm' for millimeters or 'inch' for inches
positioning_mode = 'relative'  # 'relative' or 'absolute'

# Initialize the serial connection
try:
    serial_connection = serial.Serial(port, baud_rate)
    # Wait for GRBL to initialize
    time.sleep(2)
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit(1)

# Function to send a command to GRBL
def send_gcode_command(command):
    if serial_connection.isOpen():
        serial_connection.write((command + '\n').encode())
        print(f"Sent: {command}")
        time.sleep(0.1)  # Short delay to ensure GRBL processes the command
    else:
        print("Serial connection is not open.")

def goto0_command(command):
    if serial_connection.isOpen():
        serial_connection.write(command)
        print(f"Sent: {command}")
        time.sleep(0.1)  # Short delay to ensure GRBL processes the command
    else:
        print("Serial connection is not open.")

try:
    # Unlock GRBL
    send_gcode_command('$X')  # Unlock the controller if it’s locked

    # Set unit system
    if unit_system == 'mm':
        send_gcode_command('G21')  # Set units to millimeters

    send_gcode_command('G90')  # Set to absolute positioning

    # Move motor on the X-axis
    send_gcode_command(f'G0 X{movement_distance}')  # Move X-axis by the specified distance

    while True:
        # Example menu handling
        menu = input("Enter menu selection (1 or 2): ")  # Get user input for menu selection
        if menu == '1':
            goto0_command(b'G91 g1  x-4' + b'F' + str(150).encode('ascii') + b'\r')  # open ferrite holder
        elif menu == '2':
            goto0_command(b'G91 g1  x+4' + b'F' + str(100).encode('ascii') + b'\r')
        else:
            print("Invalid menu selection.")
except KeyboardInterrupt:
    print("Program interrupted by user.")
finally:
    if serial_connection.isOpen():
        serial_connection.close()
    print("Connection closed.")


# Initialize GPIO
Button_z_pin = 2
Button_y_pin = 3
GPIO.setmode(GPIO.BCM)
GPIO.setup(Button_z_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(Button_y_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        # Check button states
        if GPIO.input(Button_z_pin) == GPIO.LOW:
            send_gcode_command('G91')  # Set to relative positioning
            send_gcode_command('G0 Z10')  # Move Z-axis up by 10 mm
            send_gcode_command('G90')  # Set back to absolute positioning
            time.sleep(0.2)  # Debounce delay

        if GPIO.input(Button_y_pin) == GPIO.LOW:
            send_gcode_command('G91')  # Set to relative positioning
            send_gcode_command('G0 Y10')  # Move Y-axis up by 10 mm
            send_gcode_command('G90')  # Set back to absolute positioning
            time.sleep(0.2)  # Debounce delay

except KeyboardInterrupt:
    print("Program interrupted by user.")
finally:
    if serial_connection.isOpen():
        serial_connection.close()
    GPIO.cleanup()
    print("Connection closed.")

