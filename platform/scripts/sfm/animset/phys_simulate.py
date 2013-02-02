# Echo client program
import socket
import sys
import vs
import sfmUtils
import bernt_utils
bernt_utils = reload(bernt_utils)
import bernt_conversion
bernt_conversion = reload(bernt_conversion)

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

#see which animsets have phys rigs applied
animSets = GetAnimationSets()
kinematicProps = []
dynamicProps = []

for i in animSets:
	phys = GetPhysProperties(i, time)
	
	if (phys != None):
		if (phys["kinematic"] == 1):
			sys.stderr.write("adding kinematic "+phys["name"]+"\n")
			kinematicProps.append(phys)
		else:
			sys.stderr.write("adding dynamic "+phys["name"]+"\n")
			dynamicProps.append(phys)
		#end
	#end
#end

if (len(kinematicProps) == 0 and len(dynamicProps) == 0):
	raise Exception("phys_simulate.py: No animation sets with a rig_physics found.")

#open a connection
s = connect(False, 52600)
request(s, "reset")

#add all our phys props
for p in kinematicProps+dynamicProps:
	# add [name] [pos] [rot] [kinematic] [shape] [shape size] [center of mass] [friction] [bounce] [density]
	request(s, "add "+p["name"]+" "+VecToString(p["pos"])+" "+VecToString(p["rot"])+" "+
			str(p["kinematic"])+" "+p["shape"]+" "+VecToString(p["shapesize"])+" "+VecToString(p["centerofmass"])+" "+
			str(p["friction"])+" "+str(p["bounce"])+" "+str(p["density"]))
#end

#for every frame in the time selection
nframes = (timeSelection["hold_right"] - timeSelection["hold_left"]) / dt.GetSeconds()
for i in range(nframes):
	#move kinematic objects
	for p in kinematicProps:
		#move [name] [pos] [rot]
		trans = GetRootTransform(p["name"], time)
		request(s, "move "+p["name"]+" "+VecToString(trans["pos"])+" "+VecToString(trans["rot"]))
	#end
	#apply forces to, and grab positions of, dynamic objects
	for p in dynamicProps:
		#force [name] [pos] [rot]
		trans = GetForceTransform(p["name"], time)
		request(s, "force "+p["name"]+" "+VecToString(trans["pos"])+" "+VecToString(trans["rot"]))
		
		response = request(s, "get "+p["name"]).split(' ')
		SetRootTransform(p["name"], time, StringToVec(response[1]), StringToVec(response[2]))
	#end
	
	#advance the simulation
	time += dt
	request(s, "step "+str(dt.GetSeconds()))
#end

#tell the server we're done
s.send("end")
s.close()