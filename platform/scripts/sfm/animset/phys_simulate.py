# Echo client program
import socket
import sys
import vs
import sfmUtils
#import bernt_utils
#bernt_utils = reload(bernt_utils)
#import bernt_conversion
#bernt_conversion = reload(bernt_conversion)

from bernt_utils import *
from bernt_tcpconnect import *
from bernt_conversion import *

#get info about the shot
timeSelection = GetCurrentTimeSelection()

#check for "infinite"
if (timeSelection["hold_left"] < -50000.0 or timeSelection["hold_right"] > 50000.0):
	raise Exception("phys_simulate.py: Please select a finite time range.")

time = vs.DmeTime_t(timeSelection["hold_left"])
dt = vs.DmeTime_t(1.0 / GetFrameRate())

#see which animsets have phys rigs applied and grab the relevant info
kinematicProps = []
dynamicProps = []

animationSets = GetAnimationSets()

for animSet in animationSets:
	root_group = animSet.GetRootControlGroup()
	
	#check if the phys rig is present
	if (root_group.HasChildGroup("Physics", False)):
		phys_group = root_group.FindChildByName("Physics", False)

		bodies = phys_group.GetValue("children")

		for body in bodies:
			phys = PhysProperties(body, time)
			if (phys.kinematic == 1):
				kinematicProps.append(phys)
			else:
				dynamicProps.append(phys)
		#end
	#end
#end

if (len(kinematicProps) == 0 and len(dynamicProps) == 0):
	raise Exception("phys_simulate.py: No animation sets with a rig_physics found.")

#open a connection
s = connect(False, 52600)
request(s, "reset")

#add all of our phys props
for p in kinematicProps+dynamicProps:
	trans = GetAbsTransformAtTime(p.handle, time)
	pos, quat = TransformToPosQuat(trans)
	# add [name] [pos] [rot] [kinematic] [shape] [shape size] [center of mass] [friction] [bounce] [density]
	request(s, "add "+p.name+" "+VectorToString(pos)+" "+QuaternionToString(quat)+" "+
			str(p.kinematic)+" "+p.shape+" "+VectorToString(p.boxsize)+" "+
			VectorToString(p.centerofmass)+" "+str(p.friction)+" "+str(p.bounce)+" "+str(p.density))
#end

#look for joints

for p in kinematicProps+dynamicProps:
	parentname = p.parentname
	
	#HAX here to make the biped fully connected
	#there are bones in between (collar_L/R and neck) that don't have hitboxes
	#there's probably a better way to do this (ie, walk the bone tree)
	if p.name.find("bip_upperArm_R") != -1:
		parentname = p.animset + ":bip_spine_3"
	if p.name.find("bip_upperArm_L") != -1:
		parentname = p.animset + ":bip_spine_3"
	if p.name.find("bip_head") != -1:
		parentname = p.animset + ":bip_spine_3"
		
	#sys.stderr.write("Looking for joint: "+parentname+" -> "+p["name"]+"\n")
	
	for q in kinematicProps+dynamicProps:
		#sys.stderr.write("    "+q["name"]+" "+parentname+"\n")
		if q.name == parentname: #q is the parent of p
			trans_q = GetRelativeTransformAtTime(q.handle, p.dag, time)
			trans_p = GetRelativeTransformAtTime(p.handle, p.dag, time)
			pos_q, quat_q = TransformToPosQuat(trans_q)
			pos_p, quat_p = TransformToPosQuat(trans_p)

			#joint [type] [body a] [pos a] [rot a] [body b] [pos b] [rot b] [twist]
			request(s, "joint cone "+
					q.name+" "+VectorToString(pos_q)+" "+QuaternionToString(quat_q)+" "+
					p.name+" "+VectorToString(pos_p)+" "+QuaternionToString(quat_p)+" "+
					str(p.twist))
			break
		#end
	#end
#end

#for every frame in the time selection
nframes = (timeSelection["hold_right"] - timeSelection["hold_left"]) / dt.GetSeconds()
for i in range(nframes):
	#move kinematic objects
	for p in kinematicProps:
		#move [name] [pos] [rot]
		trans = GetAbsTransformAtTime(p.handle, time)
		pos, quat = TransformToPosQuat(trans)
		request(s, "move "+p.name+" "+VectorToString(pos)+" "+QuaternionToString(quat))
	#end
	#apply forces to, and grab positions of, dynamic objects
	for p in dynamicProps:
		#force [name] [pos] [rot]
		trans = GetTransformAtTime(p.force, time) #LOCAL transform
		pos, rot = TransformToPosEuler(trans)
		request(s, "force "+p.name+" "+VectorToString(pos)+" "+VectorToString(rot))
		
		#get [name]
		response = request(s, "get "+p.name).split(' ') #returns ["ok", pos, quat]
		trans = PosQuatToTransform(StringToVector(response[1]), StringToQuaternion(response[2]))
		SetAbsTransformAtTime(p.handle, time, trans)
	#end
	
	#advance the simulation
	time += dt
	request(s, "step "+str(dt.GetSeconds()))
#end

#tell the server we're done
s.send("end")
s.close()