import serial
import time

arduino_port = "COM25" 
baud_rate = 115200  
timeout = 1  

try:
    
    ser = serial.Serial(arduino_port, baud_rate, timeout=timeout)
    print(f"Connected to GRBL at {arduino_port}")

   
    ser.write(b"?\n")  
    time.sleep(0.1)  

    while True:
        response = ser.readline().decode().strip() 
        if response:
            print(f"GRBL Response: {response}")
           
            if "Pn:" in response:  
                if "Z" in response:
                    print("Z+ Limit Switch is triggered!")
                else:
                    print("Z+ Limit Switch is not triggered.")
            break

except Exception as e:
    print(f"Error: {e}")
finally:
    ser.close()
    print("Serial connection closed.")
