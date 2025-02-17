import sys
from tftp_funcs import upload_file, download_file

###### Main Program
def main():
    server_ip = "0.0.0.0"
    action = 0

    server_ip = input("Enter the Server IP Address you would like to connect to: ")
    print("Currently connected to Server: " + server_ip + "\n")

    while True:
        print("Which action would you like to perform?")
        print("[1] - Upload")
        print("[2] - Download")
        print("[3] - Exit")
        action = input("Enter: ")

        if action == "1": 
            # Store file in server
            file_to_upload = input("Enter the path of the file to upload: ")
            remote_filename = input("Enter the filename to use on the server: ")
            block_size = int(input("Enter block size for upload (default 512): "))
            upload_file(server_ip, file_to_upload, remote_filename, block_size)

        elif action == "2":
            # Retrieve file from server
            remote_filename = input("Enter the filename to download: ")
            local_filename = input("Enter the local filename to save the downloaded file: ")
            block_size = int(input("Enter block size for download (default 512): "))
            download_file(server_ip, remote_filename, local_filename, block_size)

        elif action == "3":
            # Exit the program
            print("Exiting the program.")
            sys.exit(0)

        else: 
            # Do invalid input check
            print("Invalid action. Please choose 1 for 'upload' or 2 for 'download.'")

        print("\n")

if __name__ == "__main__":
    main()