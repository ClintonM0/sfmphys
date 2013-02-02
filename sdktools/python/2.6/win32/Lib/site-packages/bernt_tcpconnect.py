import socket
import sys

def connect(isServer, port):
	HOST = None
	if (not isServer):
		HOST = 'localhost'
	
	PORT = port
	s = None
	flags = socket.AI_PASSIVE
	if (not isServer):
		flags = 0
	
	for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
								  socket.SOCK_STREAM, 0, flags):
		af, socktype, proto, canonname, sa = res
		try:
			s = socket.socket(af, socktype, proto)
		except socket.error as msg:
			s = None
			continue
		try:
			if (isServer):
				s.bind(sa)
				s.listen(1)
			else:
				s.connect(sa)
		except socket.error as msg:
			s.close()
			s = None
			continue
		break
	if s is None:
		print 'could not open socket'
		sys.exit(1)
	
	return s
#end

def waitForClient(s):
	conn, addr = s.accept()
	print 'Connected by', addr
	return conn, addr
#end

def request(s, str):
	s.send(str)
	response = s.recv(1024)
	print "response: ", response
	return response
#end