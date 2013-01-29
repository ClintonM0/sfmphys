# Echo client program
from ode_connect import *
from ode_data import *
import socket
import sys

s = connect(False, 52600)

while 1:
	data = raw_input("Enter something: ")
	s.send(data)
	if (data == "end" or data == "halt"): break;
	
	data = s.recv(1024)
	print "recieved: ", data
#end while

s.close()
