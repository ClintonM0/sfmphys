# Echo client program
from ode_connect import *
from ode_data import *
import socket
import sys
import vs

unitsPerMeter = 53.33

#open a connection
s = connect(False, 52600)

time = 5.0
dt = 1.0/24.0

name = sfm.GetCurrentAnimationSet().GetName()
root = sfm.FindDag("RootTransform")
root_poslayer = root.FindTransformControl().GetPositionChannel().GetLog().GetLayer(0)
root_rotlayer = root.FindTransformControl().GetOrientationChannel().GetLog().GetLayer(0)

#send our request
for i in range(120):
	s.send("getobj "+str(name))
	response = s.recv(1024)
	print "response: ", response
	
	data = response.split()
	pos = StringToVec(data[1])
	pos[0] *= unitsPerMeter
	pos[1] *= unitsPerMeter
	pos[2] *= unitsPerMeter
	posvec = vs.Vector(pos[0], pos[1], pos[2])
	
	rot = StringToVec(data[2])
	quat = vs.Quaternion(rot[1], rot[2], rot[3], rot[0])
	
	root_poslayer.InsertKey(vs.DmeTime_t(time), posvec);
	root_rotlayer.InsertKey(vs.DmeTime_t(time), quat);
	
	s.send("step "+str(dt))
	response = s.recv(1024)
	print "response: ", response
	
	time += dt
#end for

#tell the server we're done
s.send("end")
s.close()