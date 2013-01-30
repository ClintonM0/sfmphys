# Echo client program
from ode_connect import *
from ode_data import *
from ode_util import *
import socket
import sys
import vs

#open a connection
s = connect(False, 52600)

name = sfm.GetCurrentAnimationSet().GetName()
root = sfm.FindDag("RootTransform")
root_poslog = root.FindTransformControl().GetPositionChannel().GetLog()
root_rotlog = root.FindTransformControl().GetOrientationChannel().GetLog()

timeSelection = GetCurrentTimeSelection()
posvec = root_poslog.GetValue(vs.DmeTime_t(timeSelection["hold_left"]))
pos = UnitsToMeters([posvec[0], posvec[1], posvec[2]])

rotMatrix = vs.matrix3x4_t()
rotvec = root_rotlog.GetValue(vs.DmeTime_t(timeSelection["hold_left"]))
vs.QuaternionMatrix(rotvec, rotMatrix)
rot = [rotMatrix[0], rotMatrix[1], rotMatrix[2],
		rotMatrix[4], rotMatrix[5], rotMatrix[6],
		rotMatrix[8], rotMatrix[9], rotMatrix[10]]

box_minvec = vs.Vector()
box_maxvec = vs.Vector()
root_mdlhandle = root.GetModelHandle()
vs.GetMDLBoundingBox(box_minvec, box_maxvec, root_mdlhandle, 0)

box_min = UnitsToMeters([box_minvec[0], box_minvec[1], box_minvec[2]])
box_max = UnitsToMeters([box_maxvec[0], box_maxvec[1], box_maxvec[2]])

static = 0
kinematic = 0

#send our request
request(s, "add "+str(name)+" "+VecToString(pos)+" "+VecToString(rot)+" "+VecToString(box_min)+" "+VecToString(box_max)+" "+str(static)+" "+str(kinematic))

#tell the server we're done
s.send("end")
s.close()