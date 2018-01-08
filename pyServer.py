import threading
import json
import time
import socket
from io import StringIO
import mail_notify
import vnc_client
import sys
import queue
import hadoop_cluster

q = queue.Queue()

class ClientHandler(threading.Thread):
	def __init__(self, clientsocket, client_addr):
		threading.Thread.__init__(self)
		self.clientsocket = clientsocket
		self.client_addr = client_addr

	def run(self):
		handle_client(self.clientsocket, self.client_addr)
		q.get(self)			

def handle_client(clientsocket, client_addr):
	raw_data = clientsocket.recv(1024)
	request = json.loads(str(raw_data.decode('utf-8')))
	print(request)
	if(request['REQUEST_TYPE']=='get_console'):
		request_data = request['REQUEST_DATA']
		port = vnc_client.get_vnc(request_data)
		clientsocket.send(port.encode('utf-8'),1024)

	if(request['REQUEST_TYPE']=='release_console'):
		request_data = request['REQUEST_DATA']
		vnc_client.stopVNC(request_data)
		clientsocket.send("success".encode('utf-8'),1024)

	if(request['REQUEST_TYPE']=='mail'):
		mail_notify.main(request['REQUEST_DATA']['TO'], 
							request['REQUEST_DATA']['MESSAGE'], 
							request['REQUEST_DATA']['SUBJECT'],
							request['REQUEST_DATA']['TO_NAME']);
		
	if(request['REQUEST_TYPE']=='create_hadoop_cluster'):
		hadoop_cluster.main(request['REQUEST_DATA'])

		
if __name__=="__main__":
	srv_port = 0
	if(len(sys.argv)<2):
		print("USAGE: python3 "+sys.argv[0]+" <SERVER_PORT>")
		print("using default Port : 1234")
		srv_port = 1234
	else:
		srv_port = int(sys.argv[1])
	srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	srvsock.bind(('',int(srv_port)))
	srvsock.listen(5)

	while True:
		try:
			(clientsocket, address) = srvsock.accept()
			handle = ClientHandler(clientsocket, address)
			print(handle)
			q.put(handle)
			handle.start()
		except KeyboardInterrupt:
			print("Received Stop Signal...")
			print("Stopping Server...")
			print("waiting for running threads to stop ... ")
			while not q.empty():
				thread = q.get()
				print(thread)
				thread.join()
			break
	print("Done.")

	
