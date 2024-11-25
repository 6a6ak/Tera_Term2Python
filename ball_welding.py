import serial
import time

# Function to connect to the serial port
def connect_serial(port="COM25", baudrate=115200, timeout=1):
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        ser.flushInput()
        print(f"Connected to {port} at {baudrate} baud.")
        return ser
    except Exception as e:
        print(f"Error connecting to serial port: {e}")
        return None

# Function to check if data is available on the serial port
def serial_data_available(ser):
    try:
        return ser.in_waiting > 0  # For pyserial versions that support 'in_waiting'
    except AttributeError:
        return ser.inWaiting() > 0  # Fallback for older pyserial versions

# Function to send commands to Arduino and check response
def send_command(ser, command, expected_response=None, delay=0.5):
    ser.write((command + '\n').encode())
    time.sleep(delay)
    if expected_response:
        if serial_data_available(ser):
            response = ser.readline().decode().strip()
            if expected_response in response:
                return True
            else:
                print(f"Unexpected response: {response}")
                return False
    return True

# Wait for a specific response with a timeout
def wait_for_response(ser, expected_response, timeout=5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if serial_data_available(ser):
            response = ser.readline().decode().strip()
            if expected_response in response:
                return True
    print(f"Timeout waiting for: {expected_response}")
    return False

# Movement handling
def move(ser):
    send_command(ser, "?")
    while True:
        if serial_data_available(ser):
            response = ser.readline().decode().strip()
            if "<Idle" in response:
                break
            elif "<Run" in response:
                continue
            else:
                print(f"Unexpected movement status: {response}")
                break

# Welding functionality
def weld(ser):
    send_command(ser, "M4", "ok")
    wait_for_switch_on(ser)
    send_command(ser, "M3", "ok")

# Wait for welding switch to turn on
def wait_for_switch_on(ser):
    while True:
        send_command(ser, "?")
        if serial_data_available(ser):
            response = ser.readline().decode().strip()
            if "Z" in response:
                break
        time.sleep(0.2)

# Wait for welding switch to turn off
def wait_for_switch_off(ser):
    while True:
        send_command(ser, "?")
        if serial_data_available(ser):
            response = ser.readline().decode().strip()
            if "Z" not in response:
                break
        time.sleep(0.2)

# Ball pickup functionality
def get_ball(ser):
    while True:
        send_command(ser, "?")
        if serial_data_available(ser):
            response = ser.readline().decode().strip()
            if "Pn:XYZ" in response:
                break
        time.sleep(0.05)

# Ball drop functionality
def drop_ball(ser):
    while True:
        send_command(ser, "?")
        if serial_data_available(ser):
            response = ser.readline().decode().strip()
            if "Y" not in response:
                break
        time.sleep(0.5)

# Main function
def main():
    # Connect directly to COM25
    ser = connect_serial(port="COM25")

    if not ser:
        return

    # Initial setup commands
    if send_command(ser, "$1=255", "ok"):
        send_command(ser, "$X", "ok")

    send_command(ser, "$21=0", "ok")
    send_command(ser, "$X", "ok")

    send_command(ser, "G10 P0 L20 X0 Y0 Z0", "ok")
    send_command(ser, "G1 G21 F300", "ok")
    send_command(ser, "G90 X-2.5", "ok")

    # Infinite loop for operation
    while True:
        print("Place the ball")
        get_ball(ser)
        send_command(ser, "G90 X0", "ok")
        move(ser)

        weld(ser)

        send_command(ser, "G90 X-3.45", "ok")
        move(ser)
        time.sleep(0.5)

        send_command(ser, "G90 X-2.5", "ok")
        move(ser)

# Run the main function
if __name__ == "__main__":
    main()
