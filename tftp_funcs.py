# Package Imports
from platform import node
import socket
import struct
import os
import sys

# Constants
TFTP_PORT = 69
TIMEOUT = 5
BLOCK_SIZE = 512

# Opcodes (defined in RFC 1350)
OPCODE_READ = 1
OPCODE_WRITE = 2
OPCODE_DATA = 3
OPCODE_ACK = 4
OPCODE_ERROR = 5

# FUNCTION: Error handling - interpret the error code from the error packet
def handle_error(message, error_code):
    ## List of error codes and their corresponding messages
    error_messages = {          
        0x01: "File not found",
        0x02: "Access violation",
        0x03: "Disk full",
        0x04: "Illegal TFTP operation",
        0x05: "Unknown port",
        0x06: "File already exists",
        0x07: "No such user",
        0x08: "Invalid option"
    }
    ## Takes error message based on the matching error code
    error_message = error_messages.get(error_code, "Unknown error")
    ## Displays error message
    print(f"Error: {message}")
    print(f"Error code {hex(error_code)}: {error_message}")

# FUNCTION: Upload Request Packet Creation - creates the packet to be sent during WRQ
def create_upload_request_packet(opcode, filename, file_path, mode='octet', block_size=None):
    # Include opcode, filename, and mode in packet
    packet = struct.pack('!H', opcode)              # opcode (2 bytes)
    packet += filename.encode('ascii') + b'\0'      # filename (string, null-terminated)
    packet += mode.encode('ascii') + b'\0'          # mode (string, null-terminated)
    # Include option negotiation features (blksize, tsize) in packet
    if block_size:
        packet += b'blksize' + b'\0' + str(block_size).encode('ascii') + b'\0'
        packet += b'tsize' + b'\0' + str(os.path.getsize(file_path)).encode('ascii') + b'\0'
    if file_path:
        file_size = os.path.getsize(file_path)
        packet += b'tsize' + b'\0' + str(file_size).encode('ascii') + b'\0'
    ## Returns the resulting packet
    return packet

# FUNCTION: Download Request Packet Creation - creates the packet to be sent during RRQ
def create_download_request_packet(opcode, filename, mode='octet', block_size=None):
    # Include opcode, filename, and mode in packet
    packet = struct.pack('!H', opcode)              # opcode (2 bytes)
    packet += filename.encode('ascii') + b'\0'      # filename (string, null-terminated)
    packet += mode.encode('ascii') + b'\0'          # mode (string, null-terminated)
    # Include option negotiation features (blksize) in packet
    if block_size:
        packet += b'blksize' + b'\0' + str(block_size).encode('ascii') + b'\0'
    ## Returns the resulting packet
    return packet

# FUNCTION: Packet Sending - Sends a packet to the connected socket
def send_packet(sock, packet, server_ip, server_port):
    sock.sendto(packet, (server_ip, server_port))

# FUNCTION: Packet Receiving - Retreives packet from the socket
def receive_packet(sock):
    try:                                             ## Try-catch execution of reeceiving a packet
        sock.settimeout(TIMEOUT)
        (packet, (host, port)) = sock.recvfrom(516)  # max TFTP packet size (512 data + 4 header bytes)
        return (packet, (host, port))
    except socket.timeout:                           # Exception: Socket experiences timeout       
        print("Timeout: No response from the server.\n")
        return (None, (None, None))
    except ConnectionResetError:                     # Exception: Disconnected from the server
        print("Error: The connection was forcibly closed by the server.\n")
        return (None, (None, None))
    except Exception as e:                           # Exception: Other
        print(f"An unexpected error occurred: {e}\n")
        return (None, (None, None))

# FUNCTION: Specifically used for checking for duplicate acknowledgement packet in uploading process. Removed timeout error message
def receive_packet_ack(sock):
    try:                                             ## Try-catch execution of reeceiving a packet
        sock.settimeout(TIMEOUT)
        (packet, (host, port)) = sock.recvfrom(516)  # max TFTP packet size (512 data + 4 header bytes)
        return (packet, (host, port))
    except socket.timeout:                           # Check timeout
        return (None, (None, None))
    except ConnectionResetError:                     # Exception: Disconnected from the server
        print("Error: The connection was forcibly closed by the server.\n")
        return (None, (None, None))
    except Exception as e:                           # Exception: Other
        print(f"An unexpected error occurred: {e}\n")
        return (None, (None, None))

# MAIN FUNCTION: Upload File Function - Handles the user's WRQ
def upload_file(server_ip, file_path, remote_filename, block_size=BLOCK_SIZE):
    # Creates a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Creates a WRQ (write request) packet and sends the packet using functions defined above
    request_packet = create_upload_request_packet(OPCODE_WRITE, remote_filename, file_path, block_size=block_size)
    send_packet(sock, request_packet, server_ip, TFTP_PORT)
    
    # Handles OACK (option acknowledgment) from server
    (packet, (host, port)) = receive_packet(sock)   # Receives the packet from the server and stores the necessary variables
    if packet is None:
        return                                      # End upload file process if there is no more packets to be received
    new_server_ip = host
    new_TFTP_PORT = port                            # Take the values obtained from received packet
    if not packet:
        print("Timeout waiting for OACK.")
        sock.close()                                # Closes socket if packet's value is null and end upload file process (Server timeout)
        return
    # Check OPCODE value of packet
    opcode, block_num = struct.unpack('!HH', packet[:4])    # Takes the opcode from the packet
    if opcode == OPCODE_ERROR:                              # If opcode is an error, calls handle error to determine experienced error
        handle_error("Error in WRQ response.", opcode)
        sock.close()                                        # Closes the socket and ends the process 
        return

    # Start sending data blocks to the server
    with open(file_path, 'rb') as file:             # Opens file path as file in read mode
        block_number = 1                            # Declare variables to be used later on
        last_received_ack = None
        while True:                                                                 # Continue looping until a condition to stop occurs
            # Begin by reading data packet
            data = file.read(block_size)
            if not data:                                                            # If data is not received
                (ack_packet, (host, port)) = receive_packet_ack(sock)
                if ack_packet:                                                      # Check if a double acknowledgement was received
                    ack_opcode, ack_block_num = struct.unpack('!HH', ack_packet)
                    if last_received_ack == ack_block_num:                          # Condition runs if most recent acknowledgement is equal to previous received acknowledgement
                        print("Duplicate ACK detected.")
                        sock.close()                                                # Displays error of double acknowledgement, closes socket and ends process
                        return
                else: 
                    break                                                           # Marks end of file and stops loop

            data_packet = struct.pack('!HH', OPCODE_DATA, block_number) + data      # Prepares data packet for sending
            send_packet(sock, data_packet, new_server_ip, new_TFTP_PORT)            # Send data packet to desired server
            
            # Checks for acknowledgement packet
            (ack_packet, (host, port)) = receive_packet(sock)
            if not ack_packet:                                                      # If no packet is received and server times out
                print("Timeout waiting for ACK.")
                sock.close()                                                        # Close the socket and ends process
                return
            ack_opcode, ack_block_num = struct.unpack('!HH', ack_packet)            # Unpack acknowledgement packet for opcode and block number
            if ack_opcode == OPCODE_ERROR:                                          # Checks opcode for error
                handle_error("Error in ACK response.")
                sock.close()                                                        # Handle error, close socket, end process if acknowledgement opcode indicates error
                return
            
            last_received_ack = ack_block_num                                       # Replaces last_received_ack variable with the latest acknowledgement block number
            block_number += 1                                                       # Increments block_number variable for the next 
            print("Acknowledged: Block number #", ack_block_num)                    # Displays tracked block number of acknowledgement

    print(f"File {remote_filename} uploaded successfully.\n")
    sock.close()                                                                    # Closes socket after completion

# MAIN FUNCTION: Download File Function - Handles the user's RRQ
def download_file(server_ip, remote_filename, local_filename, block_size=BLOCK_SIZE):
    # Creates a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Creates a RRQ (read request) packet and sends the packet using functions defined above
    request_packet = create_download_request_packet(OPCODE_READ, remote_filename, block_size=block_size)
    send_packet(sock, request_packet, server_ip, TFTP_PORT)
    
    # Handles OACK (option acknowledgment) from server
    (packet, (host, port)) = receive_packet(sock)   # Receives the packet from the server and stores the necessary variables
    if packet is None:
        return                                      # End upload file process if there is no more packets to be received
    new_server_ip = host
    new_TFTP_PORT = port                            # Take the values obtained from received packet
    if not packet:
        print("Timeout waiting for OACK.")
        sock.close()                                # Closes socket if packet's value is null and end upload file process (Server timeout)
        return
    # Check OPCODE value of packet
    opcode, blksize = struct.unpack('!HH', packet[:4])      # Takes the opcode from the packet
    if opcode == OPCODE_ERROR:                              # If opcode is an error, calls handle error to determine experienced error
        error_code = struct.unpack('!H', packet[2:4])[0]
        handle_error("Error in RRQ response.", error_code)  # Closes the socket and ends the process
        sock.close()
        return
    
    ack_packet = struct.pack('!HH', OPCODE_ACK, 0)
    send_packet(sock, ack_packet, new_server_ip, new_TFTP_PORT)

    # Opens file to write data in write mode
    with open(local_filename, 'wb') as file:
        print("Start receiving data...")
        while True:                                                         # Continue looping until a condition to stop occurs
            (packet, (host, port)) = receive_packet(sock)                   # Receive packet
            if host != server_ip:
                continue                                                    # Skip to next iteration

            num_recv = struct.unpack('!H', packet[2:4])[0]                  # Unpack received packet
            data = packet[4:]
            opcode, block_num = struct.unpack('!HH', packet[:4])

            if opcode == OPCODE_ERROR:                                      # If opcode signals error, handle error and end process
                error_code = struct.unpack('!H', packet[2:4])[0]
                handle_error("Error in data block.", error_code)
                return

            if num_recv > 0:
                file.write(data)                                            # Input received data into file

                # Send acknowledgment (ACK) to signal packet has been received
                ack_packet = struct.pack('!HH', OPCODE_ACK, block_num)
                send_packet(sock, ack_packet, new_server_ip, new_TFTP_PORT)
                print("Sent: ACK Block number #", block_num)

            if len(data) < block_size:
                break                                                        # Marks end of file and stops loop

    print(f"File '{remote_filename}' downloaded successfully.\n")
    sock.close()                                                             # Close socket after completion

# Checks if the local file, given file path, exists
def check_local_file_exists(file_path):     # Returns true if file on path exists
    if os.path.isfile(file_path):
        return True
    else:                                   # Returns false otherwise
        print(f"Error: The file '{file_path}' does not exist.\n")
        return False