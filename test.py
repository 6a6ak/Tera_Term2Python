import serial
import time

def send_command(ser, command, wait_for='ok', wait_msg=None):
    ser.write((command + '\n').encode())
    while True:
        line = ser.readline().decode().strip()
        if wait_msg and wait_msg in line:
            break
        if wait_for in line:
            break
    return line

def move(ser):
    while True:
        ser.write(b'?')
        response = ser.readline().decode().strip()
        if '<Idle' in response:
            break

def weld(ser):
    send_command(ser, 'M4')
    # Wait for welding process here
    send_command(ser, 'M3')
    # Wait for welding process here

def main():
    serial_port = 'COM25'  # replace with your actual serial port on Windows
    baud_rate = 115200

    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    time.sleep(1)  # wait for the serial connection to initialize

    ser.write(b'\r\n\r\n')  # wake up Grbl
    time.sleep(2)  # wait for Grbl to initialize
    ser.flushInput()  # flush startup text in serial input

    # Send commands to Grbl
    send_command(ser, '$1=255', wait_msg='[MSG:Chec')
    send_command(ser, '$21=0', wait_msg='[MSG:Chec')
    send_command(ser, 'G10 P0 L20 X0 Y0 Z0')
    send_command(ser, 'G1 G21 F300')
    send_command(ser, 'G90 x-2.5')

    while True:
        # Replace with actual logic for your application
        send_command(ser, 'G90 x0')
        move(ser)
        weld(ser)
        send_command(ser, 'G90 x-3.45')
        move(ser)
        time.sleep(0.5)
        send_command(ser, 'G90 x-2.5')
        move(ser)

if __name__ == "__main__":
    main()