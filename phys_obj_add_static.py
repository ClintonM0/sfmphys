# Echo client program
from ode_connect import *
from ode_data import *
import socket
import sys
import vs

#open a connection
s = connect(False, 52600)

name = sfm.GetCurrentAnimationSet().GetName()
root = sfm.FindDag("RootTransform")
root_poslayer = root.FindTransformControl().GetPositionChannel().GetLog().GetLayer(0)
root_rotlayer = root.FindTransformControl().GetOrientationChannel().GetLog().GetLayer(0)

posvec = root_poslayer.GetKeyValue(0)
pos = UnitsToMeters([posvec[0], posvec[1], posvec[2]])

quat = root_rotlayer.GetKeyValue(0)
rot = [quat.x, quat.y, quat.z, quat.w]

box_minvec = vs.Vector()
box_maxvec = vs.Vector()
root_mdlhandle = root.GetModelHandle()
vs.GetMDLBoundingBox(min, max, root_mdlhandle, 0)

box_min = UnitsToMeters([box_minvec[0], box_minvec[1], box_minvec[2]])
box_max = UnitsToMeters([box_maxvec[0], box_maxvec[1], box_maxvec[2]])

static = 0

#send our request
request(s, "add "+str(name)+" "+VecToString(pos)+" "+VecToString(rot)+" "+VecToString(box_min)+" "+VecToString(box_max)+" "+str(static))

#tell the server we're done
s.send("end")
s.close()