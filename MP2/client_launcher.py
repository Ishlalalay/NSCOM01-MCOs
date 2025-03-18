import sys
from tkinter import Tk
from client import client

if __name__ == "__main__":
	try:
		serverAddr = sys.argv[1]
		serverPort = sys.argv[2]
		rtpPort = sys.argv[3]
		fileName = sys.argv[4]	
	except:
		print("[Usage: ClientLauncher.py Server_name Server_port RTP_port Audio_file]")	
	
	root = Tk()
	
	# Create a new client
	app = client(root, serverAddr, serverPort, rtpPort, fileName)
	app.master.title("AudioClient")	
	root.mainloop()
	