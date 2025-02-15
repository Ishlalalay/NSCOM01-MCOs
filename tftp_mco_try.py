import socket

# Note: 1 # - short desc of part, 4 # - im not sure if correct code, 6 # - divide part

def errorHandling():
    # 1 - Timeout
    print()
    # 2 - Duplicate Acknowledgement/ACK
        
    # 3 - File Not Found

###### Option negotiation as per RFCs 2347, 2348, and 2349

def blockSizeNegotiation(): #blksize
    # content
    print()

def transferSizeCommunication(): #tsize
    # content
    print()

###### Main Program

Server_IP = "0.0.0.0"
Action = 0

Server_IP = input("Enter the Server IP Address you would like to connect to: ")

# create socket connection (java try catch but python version asudhuisadhuashd)
####sock = socket.socket(socket.AF_INET, # Internet
####                     socket.SOCK_DGRAM) # UDP
####sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

print("Currently connected to Server:" + Server_IP)

print("What action would you like to perform?")
print("[1] - Upload")
print("[2] - Download")
print("[3] - Exit")
Action = input("Enter: ")

if (Action == 1): 
    # Store file in server
    print()
elif (Action == 2):
    #retreive file from server
    print()
elif (Action == 3):
    #close socket or leave this blank
    print()
else: 
    # do invalid input moment
    print()