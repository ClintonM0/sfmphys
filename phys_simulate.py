# Echo client program
from ode_connect import *
from ode_data import *
import socket
import sys
import vs

#open a connection
s = connect(False, 52600)

time = 5.0
dt = 1.0/24.0

#find all the bodies in our simulation
response = request(s, "list bodies")
bodies = response.split(' ')[1:]

roots = {}
for name in bodies:
	dag = sfm.FindDag(name+":RootTransform")
	roots.update( {name: (dag.FindTransformControl().GetPositionChannel().GetLog().GetLayer(0),
						dag.FindTransformControl().GetOrientationChannel().GetLog().GetLayer(0))} )
#end for

#send our request
for i in range(120):
	#grab info for objects
	for name in bodies:
		response = request(s, "getobj "+str(name))
		
		data = response.split()
		pos = MetersToUnits(StringToVec(data[1]))
		posvec = vs.Vector(pos[0], pos[1], pos[2])
		
		rot = StringToVec(data[2])
		quat = vs.Quaternion(rot[1], rot[2], rot[3], rot[0])
		
		roots[name][0].InsertKey(vs.DmeTime_t(time), posvec);
		roots[name][1].InsertKey(vs.DmeTime_t(time), quat);
	
	#simulate the world
	request(s, "step "+str(dt))
	time += dt
#end for

#tell the server we're done
s.send("end")
s.close()