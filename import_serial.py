import serial
import time

# Function to send a command to the serial device and wait for a specific response
def send_command(ser, command, expected_response):
    ser.write(command.encode())
    while True:
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            print(f"Response: {response}")
            if expected_response in response:
                return True
            elif "error" in response:
                print(f"Error: {response}")
                return False
        time.sleep(0.1)

# Function to check if serial data is available
def serial_data_available(ser):
    return ser.in_waiting > 0

# Welding functionality
def weld(ser):
    if send_command(ser, "M4\n", "ok"):
        wait_for_switch_on(ser)
        send_command(ser, "M3\n", "ok")

# Wait for welding switch to turn on
def wait_for_switch_on(ser, timeout=10):
    print("Waiting for switch on")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if send_command(ser, "?", "Z"):
            break
        time.sleep(0.2)
    else:
        print("Timeout waiting for switch on")

# Wait for welding switch to turn off
def wait_for_switch_off(ser, timeout=10):
    print("Waiting for switch off")
    start_time = time.time()
    while time.time() - start_time < timeout:
        send_command(ser, "?", "Z")
        if serial_data_available(ser):
            response = ser.readline().decode().strip()
            print(f"Switch status: {response}")
            if "Z" not in response:
                print("Switch is off.(Z)")
                break
        time.sleep(0.2)
    else:
        print("Timeout waiting for switch off")

# Ball pickup functionality
def get_ball(ser, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Add your ball pickup logic here
        pass
    else:
        print("Timeout waiting to get ball")