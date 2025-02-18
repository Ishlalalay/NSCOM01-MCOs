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

# Error handling; interpret the error code from the error packet
def handle_error(message, error_code):
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
    error_message = error_messages.get(error_code, "Unknown error")
    
    print(f"Error: {message}")
    print(f"Error code {hex(error_code)}: {error_message}")

# Option negotiation
def negotiate_options(sock, server_ip, block_size):
    # Implement the logic for additional option negotiation

    '''
    message = f"NEGO blksize {block_size}".encode('ascii') # prep message to server
    sock.sendto(message, (server_ip, TFTP_PORT)) # send the created message to the server

    # Receive the response from the server
    response, server_address = sock.recvfrom(4096)
    print(f"Server responded: {response.decode('ascii')}")

    # Parse and return the negotiated block size
    if response.decode('ascii').startswith("OK blksize"):
        _, _, block_size = response.decode('ascii').split()
        return int(block_size)
    else:
        print("Failed to negotiate block size.")
        return None
    '''

# Functions for packet creation
def create_upload_request_packet(opcode, filename, file_path, mode='octet', block_size=None):
    packet = struct.pack('!H', opcode)  # opcode (2 bytes)
    packet += filename.encode('ascii') + b'\0'  # filename (string, null-terminated)
    packet += mode.encode('ascii') + b'\0'  # mode (string, null-terminated)

    # Add option negotiation (blksize, tsize)
    if block_size:
        packet += b'blksize' + b'\0' + str(block_size).encode('ascii') + b'\0'
        packet += b'tsize' + b'\0' + str(os.path.getsize(file_path)).encode('ascii') + b'\0'

    return packet

def create_download_request_packet(opcode, filename, mode='octet', block_size=None):
    packet = struct.pack('!H', opcode)  # opcode (2 bytes)
    packet += filename.encode('ascii') + b'\0'  # filename (string, null-terminated)
    packet += mode.encode('ascii') + b'\0'  # mode (string, null-terminated)

    # Add option negotiation (blksize, tsize)
    #block_size = negotiate_options(sock, TFTP_PORT, block_size)
    if block_size:
        packet += b'blksize' + b'\0' + str(block_size).encode('ascii') + b'\0'

    return packet

def send_packet(sock, packet, server_ip, server_port):
    sock.sendto(packet, (server_ip, server_port))

def receive_packet(sock):
    try:
        sock.settimeout(TIMEOUT)
        (packet, (host, port)) = sock.recvfrom(516)  # max TFTP packet size (512 data + 4 header bytes)
        return (packet, (host, port))
    except socket.timeout:
        print("Timeout: No response from the server.\n")
        return (None, (None, None))
    except ConnectionResetError:
        print("Error: The connection was forcibly closed by the server.\n")
        return (None, (None, None))
    except Exception as e:
        print(f"An unexpected error occurred: {e}\n")
        return (None, (None, None))

# Upload File Function
def upload_file(server_ip, file_path, remote_filename, block_size=BLOCK_SIZE):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send WRQ (write request)
    request_packet = create_upload_request_packet(OPCODE_WRITE, remote_filename, file_path, block_size=block_size)
    send_packet(sock, request_packet, server_ip, TFTP_PORT)
    
    # Handle OACK (option acknowledgment) from server
    (packet, (host, port)) = receive_packet(sock)
    if packet is None:
        return
    new_server_ip = host
    new_TFTP_PORT = port
    if not packet:
        handle_error("Timeout waiting for OACK.")
        sock.close()
        return

    opcode, block_num = struct.unpack('!HH', packet[:4])

    if opcode == OPCODE_ERROR:
        handle_error("Error in WRQ response.", opcode)
        sock.close()
        return

    # Start sending data blocks
    with open(file_path, 'rb') as file:
        block_number = 1
        while True:
            data = file.read(block_size)
            if not data:
                break  # End of file
            #print(data)
            data_packet = struct.pack('!HH', OPCODE_DATA, block_number) + data
            send_packet(sock, data_packet, new_server_ip, new_TFTP_PORT)
            
            # Wait for acknowledgment (ACK)
            (ack_packet, (host, port)) = receive_packet(sock)
            if not ack_packet:
                handle_error("Timeout waiting for ACK.")
                sock.close()
                return
            #print(ack_packet)
            
            ack_opcode, ack_block_num = struct.unpack('!HH', ack_packet)

            if ack_opcode == OPCODE_ERROR:
                handle_error("Error in ACK response.")
                sock.close()
                return

            if ack_block_num != block_number:
                handle_error("Duplicate ACK detected.")
                sock.close()
                return
            
            block_number += 1
            print("Acknowledged: Block number #", ack_block_num)
    
    print(f"File {remote_filename} uploaded successfully.\n")
    sock.close()

# Download File Function
def download_file(server_ip, remote_filename, local_filename, block_size=BLOCK_SIZE):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send RRQ (read request)
    request_packet = create_download_request_packet(OPCODE_READ, remote_filename, block_size=block_size)
    send_packet(sock, request_packet, server_ip, TFTP_PORT)
    
    # Handle OACK (option acknowledgment) from server
    (packet, (host, port)) = receive_packet(sock)
    if packet is None:
        return

    new_server_ip = host
    new_TFTP_PORT = port
    if not packet:
        handle_error("Timeout waiting for OACK.")
        sock.close()
        return
    #print(packet)

    opcode, blksize = struct.unpack('!HH', packet[:4])
    if opcode == OPCODE_ERROR:
        error_code = struct.unpack('!H', packet[2:4])[0]
        handle_error("Error in RRQ response.", error_code)
        sock.close()
        return
    
    ack_packet = struct.pack('!HH', OPCODE_ACK, 0)
    send_packet(sock, ack_packet, new_server_ip, new_TFTP_PORT)

    with open(local_filename, 'wb') as file:
        print("Start receiving data...")
        while True:
            (packet, (host, port)) = receive_packet(sock)
            if host != server_ip:
                continue

            num_recv = struct.unpack('!H', packet[2:4])[0]
            data = packet[4:]
            opcode, block_num = struct.unpack('!HH', packet[:4])

            if opcode == OPCODE_ERROR:
                error_code = struct.unpack('!H', packet[2:4])[0]
                handle_error("Error in data block.", error_code)
                return

            if num_recv > 0:
                file.write(data)

                # Send acknowledgment (ACK)
                ack_packet = struct.pack('!HH', OPCODE_ACK, block_num)
                send_packet(sock, ack_packet, new_server_ip, new_TFTP_PORT)
                print("Sent: ACK Block number #", block_num)

            if len(data) < block_size:
                break  # End of file

    print(f"File '{remote_filename}' downloaded successfully.\n")
    sock.close()

def check_local_file_exists(file_path):
    if os.path.isfile(file_path):
        return True
    else:
        print(f"Error: The file '{file_path}' does not exist.\n")
        return False