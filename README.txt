Sophia Pauline V. Sena
Isha Daphne E. Zulueta
NSCOM01 S13 Machine Project 1

**Instructions for compiling and running the program:**
1. Download the .zip file and extract it.
2. Open the tftpd64 app and set the server directory to server_dir.
3. Run the tftp_client code in the terminal ("python tftp_client.py"). Make sure that the directory is correct.
4. Input "127.0.0.1" when prompted for the Server IP Address you would like to connect to.

**Implemented features and error-handling mechanisms:**
For the User Interface portion, the program allows the user to specify the following:
- server address
- file to be uploaded
- filename to be used on the server when uploading
- file to be downloaded

For the Upload portion, the uploading of file starts with WRQ octet mode. The File WRQ uses the filename specified by the user.
Upload only begins after ACK or OACK, and data blocks follow the standard byte size, which is 512 bytes (default size).
The program displays the sending and receiving of acknowledged block numbers to show the progress of messages sent for file divisible by block size.
Uploaded files can be opened on the directory of the server.

For the Download portion, the downloading of file starts with RRQ octet mode. The File RRQ uses the filename specified by the user.
ACK messages correspond to the DATA message block numbers.
Download only completes upon receiving the data block smaller than block size.
Downloaded files can be opened on the directory of the client.

Both Upload and Download portions can be traced via Wireshark.

For the Error Handling portion, client times out when server does not ACK a WRQ/RRQ.
Additionally, client interprets TFTP error messages correctly, as error messages are specified and displayed accordingly.

For the Negotiation Features, client uses both WRQ and RRQ with blksize option, which are customizable.
Both actual upload and download uses custom transfer block size.
Client is also allowed to use WRQ with tsize option.

**Test cases and sample outputs demonstrating functionality:**
1. Server Connection
Enter and connect to the server

Output:
Enter the Server IP Address you would like to connec to: 127.0.0.1
Currently connected to Server: 127.0.0.1

2. Uploading File/WRQ
Upload file with default blocksize

Output:
Enter: 1
Enter the path of the file to upload: C:\Users\sophi\Documents\dlsu\2024-2025 Term 2\NSCOM01 MP 1\NSCOM01-MCOs\upload_test.txt
Enter the filename to use on the server: upload_test.txt
Enter block size for upload (default 512):
File upload_test.txt uploaded successfully.
// File can now be viewed in the server directory.


Upload file with custom blocksize

Output:
Enter: 1
Enter the path of the file to upload: C:\Users\sophi\Documents\dlsu\2024-2025 Term 2\NSCOM01 MP 1\NSCOM01-MCOs\upload_test.txt
Enter the filename to use on the server: upload_test.txt
Enter block size for upload (default 512): 1024
File upload_test.txt uploaded successfully.

Uploaded file is sequenced correctly

Output:
Enter: 1
Enter the path of the file to upload: C:\Users\sophi\Documents\dlsu\2024-2025 Term 2\NSCOM01 MP 1\NSCOM01-MCOs\1024.txt
Enter the filename to use on the server: 1025.txt
Enter block size for upload (default 512):
Acknowledged: Block number # 1
Acknowledged: Block number # 2
Acknowledged: Block number # 3
File upload_test.txt uploaded successfully.

3. Downloading File/RRQ
Download file with default blocksize

Output:
Enter: 2
Enter the filename to download: 1025.txt
Enter the local filename to save the downloaded file: 1025.txt
Enter block size for download (default 512 bytes):
Start receiving data...
Sent: ACK Block number # 1
Sent: ACK Block number # 2
Sent: ACK Block number # 3
File '1025.txt' downloaded successfully.

Download file with custom blocksize

Output:
Enter: 2
Enter the filename to download: upl.txt
Enter the local filename to save the downloaded file: upl.txt
Enter block size for download (default 512 bytes): 1024
Start receiving data...
Sent: ACK Block number # 1
File 'upl.txt' downloaded successfully.

Downloaded file is sequenced correctly

Output:
Enter: 2
Enter the filename to download: 1025.txt
Enter the local filename to save the downloaded file: 1025.txt
Enter block size for download (default 512 bytes): 500
Start receiving data...
Sent: ACK Block number # 1
Sent: ACK Block number # 2
Sent: ACK Block number # 3
File '1025.txt' downloaded successfully.

4. Error Handling
Error testing: File not found (0x01)

Output:
Enter: 2
Enter the filename to download: download.txt
Enter the local filename to save the downloaded file: dl.txt
Enter block size for download (default 512 bytes): 
Error: Error in RRQ response.
Error code 0x1: File not found

Error testing: Timeout

Output:
Enter: 1
Enter the path of the file to upload: C:\Users\sophi\Documents\dlsu\2024-2025 Term 2\NSCOM01 MP 1\NSCOM01-MCOs\upload.txt
Enter the filename to use on the server: upl.txt
Enter block size for upload (default 512): 5
Acknowledged: Block number # 1
Error: The connection was forcibly closed by the server.
Timeout waiting for ACK.

Error testing: Duplicate ACK

Output:
Enter: 1
Enter the path of the file to upload: C:\Users\sophi\Documents\dlsu\2024-2025 Term 2\NSCOM01 MP 1\NSCOM01-MCOs\bin.bin
Enter the filename to use on the server: bin.bin
Enter block size for upload (default 512): 
Acknowledged: Block number # 1
Acknowledged: Block number # 2
Acknowledged: Block number # 3
Acknowledged: Block number # 4
Acknowledged: Block number # 5
Acknowledged: Block number # 6
Acknowledged: Block number # 7
Acknowledged: Block number # 8
Duplicate ACK detected.

References:
http://www.tcpipguide.com/free/t_TFTPDetailedOperationandMessaging-3.htm
https://dlsu.instructure.com/courses/196573/files/24029209?module_item_id=5461537
https://docs.python.org/3/library/struct.html