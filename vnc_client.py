
from sshtunnel import SSHTunnelForwarder
import os
import sys
import subprocess
import signal

servers = {}
ports = {}

def get_port():
	i = 6079
	g = 1
	while g is not None:
		i = i+1
		g = servers.get(str(i))
	ports[str(i)]=1
	return i

def free_port(port):
	ports.pop(str(port), None)

def stopVNC(request_data):
	port = 0
	for  key, value in servers.items():
		if(value['REQUEST_DATA']['REMOTE_HOST']['IP']==request_data['REMOTE_HOST']['IP'] and\
			value['REQUEST_DATA']['REMOTE_BIND_ADDRESS']['PORT']==request_data['REMOTE_BIND_ADDRESS']['PORT']\
			):
			os.killpg(value['VNC_PROCESS'].pid, signal.SIGINT)
			value['TUNNEL'].stop()
			free_port(int(key))
			servers.pop(key)



def startVNC(request_data):
	server = SSHTunnelForwarder(
	    request_data['REMOTE_HOST']['IP'],
	    ssh_username=request_data['REMOTE_HOST']['USERNAME'],
	    ssh_password=request_data['REMOTE_HOST']['PASSWORD'],
	    remote_bind_address=('127.0.0.1', int(request_data['REMOTE_BIND_ADDRESS']['PORT']))
	)
	server.start()
	new_port = get_port()
	cmd  = "./noVNC/utils/launch.sh --vnc localhost:"+str(server.local_bind_port)+" --listen "+str(new_port)+""
	print(cmd)
#	os.system(cmd)
	srvproc = subprocess.Popen(cmd, shell=True)
	proc_pid = srvproc.pid
	print(str(server.local_bind_port))
	vnc = {
		'REQUEST_DATA':request_data,
		'TUNNEL':server,
		'VNC_PROCESS':srvproc
	}
	print("ProcID:"+str(srvproc.pid))
	return new_port,vnc

def get_vnc(request_data):
	port = 0
	for  key, value in servers.items():
		if(value['REQUEST_DATA']['REMOTE_HOST']['IP']==request_data['REMOTE_HOST']['IP'] and\
			value['REQUEST_DATA']['REMOTE_BIND_ADDRESS']['PORT']==request_data['REMOTE_BIND_ADDRESS']['PORT']\
			):
			print("ProcID:"+str(value['VNC_PROCESS'].pid))
			port = str(key)
	if(int(port)==0):
		vnc_port,vnc = startVNC(request_data)
		servers[str(vnc_port)] = vnc
		port = str(vnc_port)
	return port
