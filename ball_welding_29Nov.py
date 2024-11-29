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

# Function to clear initial messages from the device
def clear_initial_messages(ser):
    time.sleep(1)  # Allow time for initial messages
    while True:
        response = ser.readline().decode().strip()
        if "Grbl" in response or "$" in response:
            print(f"Ignoring Grbl initialization message: {response}")
            return
        else:
            print(f"Initial message: {response}")

# Function to send commands to Arduino and check response
def send_command(ser, command, expected_response=None, delay=0.5):
    ser.write((command ).encode())
    print (f"Sent: {command}")
    time.sleep(delay)
    responses = []
    while serial_data_available(ser):
        response = ser.readline().decode().strip()
        responses.append(response)
#        print(f"Received: {response}")
        if expected_response and expected_response in response:
            return True
    if expected_response:
#        print(f"Expected '{expected_response}' not found in responses: {responses}")
        return False
    return True

def send_command_noexpect(ser, command, delay=0.5):
    ser.write((command ).encode())
    time.sleep(delay)
    response = ser.readline()
#    print(f"scn: {response}")
    return response.decode("utf-8")

# Wait for a specific response with a timeout
def wait_for_response(ser, expected_response, timeout=5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if serial_data_available(ser):
            response = ser.readline().decode().strip()
            print(f"Received: {response}")
            if expected_response in response:
                return True
    print(f"Timeout waiting for: {expected_response}")
    return False

# Movement handling
def move(ser):
    while True:
        response = send_command_noexpect(ser, "?")
        print(f"Movement status: {response}")
        if "<Idle" in response:
            break
        elif "<Run" in response:
            continue
        else:
            print(f"Unexpected movement status: {response}")
            break


# Wait for welding switch to turn on
def wait_for_switch_on(ser):
    print ("Waiting for switch on")
    while True:
        if send_command(ser, "?", "Z"):
            break
        time.sleep(0.2)

# Wait for welding switch to turn off
def wait_for_switch_off(ser):
    print ("Waiting for switch off")
    while True:
        if not send_command(ser, "?", "Z"):
            print("Switch is off.(Z)")
            break
        time.sleep(0.2)

# Ball pickup functionality
def get_ball(ser, timeout=10):
    start_time = time.time()
    while True:
        if send_command(ser, "?", "Y"):
            print("Ball detected.")
            return True
        
#        if serial_data_available(ser):
#        response =ser.readline().decode().strip()  # "Pn:Y" "Pn:Y" #
#        print(f"Ball status: {response}")
#        if "Y" in response:

            print("Ball detected.")
            return True
#        else: 
#            print("Ball not detected.") 
        time.sleep(0.05)    
    print("Timeout waiting for ball placement.")
    return False

# Function to fix the motor position and hold it
def hold_motor_position(ser, position):
    """
    Fixes the motor at a specific position by sending a G-code command
    and ensures the motor remains stable at that position.
    
    Args:
        ser: Serial connection to Grbl
        position: Target position as a tuple (X, Y, Z)
    """
    x, y, z = position
    command = f"G90 X{x} Y{y} Z{z}\n"  # Set absolute positioning at the given coordinates
    if send_command(ser, command, "ok"):  # Send the movement command
        print(f"Motor moved to position: X={x}, Y={y}, Z={z}")
    else:
        print("Failed to move motor to the desired position.")
    
    # Query Grbl status until it reports being idle at the target position
    while True:
        response = send_command_noexpect(ser, "?")  # Query the status
        print(f"Grbl Status: {response}")
        if "<Idle" in response:  # Ensure the motor is idle
            print("Motor is fixed at the desired position.")
            break
        elif "Run" in response:  # If still running, wait
            time.sleep(0.1)
        else:
            print("Unexpected status. Ensuring stability...")
        time.sleep(0.1)

# Main function
def main():
    ser = connect_serial(port="COM25")
    if not ser:
        return

    clear_initial_messages(ser)

    # Initial setup commands
    if send_command(ser, "$1=255\n", "ok"):
        send_command(ser, "$X\n", "ok")

    send_command(ser, "$21=0\n", "ok")
    send_command(ser, "$X\n", "ok")

    send_command(ser, "G10 P0 L20 X0 Y0 Z0\n", "ok")
    send_command(ser, "G1 G21 F300\n", "ok")
    send_command(ser, "G90 X-2.5\n", "ok")

    # Infinite loop for operation
    while True:
        print("Place the ball")
        get_ball(ser)

        send_command(ser, "G90 X0\n", "ok")
        move(ser)
        
        # WELD
        wait_for_switch_on(ser)
        send_command(ser, "M4\n", "ok")
        wait_for_switch_off(ser)
        wait_for_switch_on(ser)
        send_command(ser, "M3\n", "ok")

        # Move motor to a fixed position and hold it
#        hold_motor_position(ser, position=(-3.45, 0, 0))  # Example position
        send_command(ser, "G90 X-3.25\n", "ok")
        move(ser)
        time.sleep(0.5)
        

        send_command(ser, "G90 X-2.5\n", "ok")
        move(ser)

# Run the main function
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted.")
    except Exception as e:
        print(f"Error: {e}")
