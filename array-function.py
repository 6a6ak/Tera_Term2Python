i, j = 0, 0  # Arduino ports and motor identifiers
ard = ["COM1", "COM2"]
R1motors = ["X", "Y", "Z"]  # Motor labels
R2motors = ["X", "Y", "Z"]  # Motor labels
# Address matrix linking COM ports to motors
address = [
    [ard[0], R1motors[0]],  # COM1 -> X
    [ard[0], R1motors[1]],  # COM1 -> Y
    [ard[0], R1motors[2]],  # COM1 -> Z
    [ard[1], R2motors[0]],  # COM2 -> X
    [ard[1], R2motors[1]],  # COM2 -> Y
    [ard[1], R2motors[2]]   # COM2 -> Z
    
]

# Function to fetch the address dynamically
def select_address(i,j): # Function to select the address based on the COM port and motor index

  print(f"G91 g1 {address[i][j]}-(destination) F150\r")  # Print the selected address

# Example usage
if __name__ == "__main__": 
    i = int(input("Enter the index for COM port (0 or 1): "))
    j = int(input("Enter the index for the motor (0-2): "))
   # destination = int(input("Enter the index for the motor (0-100): "))
    select_address(i, j)  # Select the address based on user input

