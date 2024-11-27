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
