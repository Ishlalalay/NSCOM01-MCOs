Sophia Pauline V. Sena
Isha Daphne E. Zulueta
NSCOM01 S13 Machine Project 1

**Instructions for compiling and running the program:**
1. Download the .zip file and extract it.
2. Run the tftp_client code in the terminal ("python tftp_client.py"). Make sure that the directory is correct.
3. Input "127.0.0.1" when prompted for the Server IP Address you would like to connect to.

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


References:
http://www.tcpipguide.com/free/t_TFTPDetailedOperationandMessaging-3.htm
https://dlsu.instructure.com/courses/196573/files/24029209?module_item_id=5461537
https://docs.python.org/3/library/struct.html