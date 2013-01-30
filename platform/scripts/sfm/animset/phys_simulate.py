# Echo client program
from ode_connect import *
from ode_data import *
from ode_util import *
import socket
import sys
import vs
import sfmUtils

#open a connection
s = connect(False, 52600)

dt = 1.0 / GetFrameRate()

#find all the bodies in our simulation
response = request(s, "list physbodies")
physbodies = response.split(' ')[1:]

response = request(s, "list kinematicbodies")
kinematicbodies = response.split(' ')[1:]

dags = {}
logs = {}

for name in physbodies + kinematicbodies:
	sfm.UsingAnimationSet(name)
	dag = sfmUtils.FindFirstDag(["RootTransform", "rootTransform", "roottransform"], True )
	dags.update( {name: dag} )
	logs.update( {name: (dag.FindTransformControl().GetPositionChannel().GetLog(),
						dag.FindTransformControl().GetOrientationChannel().GetLog())} )
#end for

timeSelection = GetCurrentTimeSelection()
time = timeSelection["hold_left"] + 5.0
frames = (timeSelection["hold_right"] - timeSelection["hold_left"]) / dt

#send our request
for i in range(frames):
	dmetime = vs.DmeTime_t(time)
	#send info for kinematic bodies
	for name in kinematicbodies:
		#GetValue returns a reference so we have to copy the vectors
		temp = logs[name][0].GetValue(dmetime)
		posvec_this = vs.Vector(temp[0], temp[1], temp[2])
		temp = logs[name][0].GetValue(vs.DmeTime_t(time + dt))
		posvec_next = vs.Vector(temp[0], temp[1], temp[2])
		
		velocity = (posvec_next - posvec_this) / dt
		vel = UnitsToMeters([velocity[0], velocity[1], velocity[2]])
		
		request(s, "velocity "+name+" "+VecToString(vel))
		
		#rotMatrix = vs.matrix3x4_t()
		#rotvec = logs[name][1].GetValue(dmetime)
		#vs.QuaternionMatrix(rotvec, rotMatrix)
		#rot = [rotMatrix[0], rotMatrix[1], rotMatrix[2],
		#		rotMatrix[4], rotMatrix[5], rotMatrix[6],
		#		rotMatrix[8], rotMatrix[9], rotMatrix[10]]
		
	#grab info for phys bodies
	for name in physbodies:
		response = request(s, "getobj "+str(name))
		data = response.split(' ')
		
		pos = MetersToUnits(StringToVec(data[1]))
		posvec = vs.Vector(pos[0], pos[1], pos[2])
		
		rot = StringToVec(data[2])
		rotMatrix = vs.matrix3x4_t(rot[0], rot[1], rot[2], 0, rot[3], rot[4], rot[5], 0, rot[6], rot[7], rot[8], 0)
		quat = vs.Quaternion()
		vs.MatrixQuaternion(rotMatrix, quat)
		
		logs[name][0].SetKey(dmetime, posvec);
		logs[name][1].SetKey(dmetime, quat);
	
	#simulate the world
	request(s, "step "+str(dt))
	time += dt
#end for

#tell the server we're done
s.send("end")
s.close()