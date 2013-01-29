# Echo client program
from ode_connect import *
from ode_data import *
import socket
import sys
import vs

unitsPerMeter = 53.33

#open a connection
s = connect(False, 52600)

sfm.SetOperationMode("Play");
name = sfm.GetCurrentAnimationSet().GetName()
root = sfm.FindDag("RootTransform")
root_poslayer = root.FindTransformControl().GetPositionChannel().GetLog().GetLayer(0)
root_rotlayer = root.FindTransformControl().GetOrientationChannel().GetLog().GetLayer(0)

posvec = root_poslayer.GetKeyValue(0)
pos = [posvec[0], posvec[1], posvec[2]]
pos[0] /= unitsPerMeter
pos[1] /= unitsPerMeter
pos[2] /= unitsPerMeter

quat = root_rotlayer.GetKeyValue(0)
rot = [quat.x, quat.y, quat.z, quat.w]

size = [40,40,40]
size[0] /= unitsPerMeter
size[1] /= unitsPerMeter
size[2] /= unitsPerMeter

static = 0

sfm.SetOperationMode("Pass");

#send our request
s.send("add "+str(name)+" "+VecToString(pos)+" "+VecToString(rot)+" box "+VecToString(size)+" "+str(static))
response = s.recv(1024)
print "response: ", response

#tell the server we're done
s.send("end")
s.close()