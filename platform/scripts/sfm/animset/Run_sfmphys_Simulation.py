import sys
import time
import vs
import sfmUtils
import sfmClipEditor

from PySide import QtCore
from PySide import QtGui

import sfmphys.dagutils
sfmphys.dagutils = reload(sfmphys.dagutils)
import sfmphys.sessionutils
sfmphys.sessionutils = reload(sfmphys.sessionutils)
import sfmphys.rigutils
sfmphys.rigutils = reload(sfmphys.rigutils)
import sfmphys.bullet_utils
sfmphys.bullet_utils = reload(sfmphys.bullet_utils)

from sfmphys.dagutils import *
from sfmphys.rigutils import *
from sfmphys.sessionutils import *
from sfmphys.bullet_utils import *

if len(sfmClipEditor.GetSelectedShots()) == 1:
	setCurrentShot(sfmClipEditor.GetSelectedShots()[0])
else:
	raise Exception("phys_simulate.py: Please select exactly one shot.")

#get info about the shot
timeSelection = GetCurrentTimeSelection()

#check for "infinite"
if (timeSelection.IsEitherInfinite()):
	raise Exception("phys_simulate.py: Please select a finite time range.")

currenttime = timeSelection.GetValue("hold_left")
dt = vs.DmeTime_t(1.0 / GetFrameRate())

#create a physics world
world = World()

#see which animsets have phys rigs applied and grab the relevant info
rigidBodies = {}
softBodies = []
constraints = []

for animSet in GetAnimationSets():
	root_group = animSet.GetRootControlGroup()
	
	if root_group.HasChildGroup("Rigidbodies", False):
		phys_group = root_group.FindChildByName("Rigidbodies", False)

		for group in phys_group.GetValue("children"):
			bodyrig = RigidbodyRig(group=group, time=currenttime)
			bodyrig.body = Rigidbody(bodyrig)
			world.addRigidBody(bodyrig.body)
			rigidBodies[animSet.GetName()+":"+bodyrig.target] = bodyrig
		#end
	#end

	if root_group.HasChildGroup("PhysConstraints", False):
		phys_group = root_group.FindChildByName("PhysConstraints", False)

		for group in phys_group.GetValue("children"):
			consrig = ConstraintRig(group=group, time=currenttime)
			bodya = rigidBodies[animSet.GetName()+":"+consrig.bodya].body
			bodyb = rigidBodies[animSet.GetName()+":"+consrig.bodyb].body
			consrig.cons = Constraint(consrig, bodya, bodyb)
			world.addConstraint(consrig.cons)
			constraints.append(consrig)
		#end
	#end

	if root_group.HasChildGroup("Softbodies", False):
		phys_group = root_group.FindChildByName("Softbodies", False)

		for group in phys_group.GetValue("children"):
			softrig = SoftbodyRig(group=group, time=currenttime)
			softrig.body = Softbody(softrig, world.getWorldInfo())
			world.addSoftBody(softrig.body)
			softBodies.append(softrig)
		#end
	#end
#end

if (len(rigidBodies) == 0 and len(softBodies) == 0):
	raise Exception("phys_simulate.py: No animation sets with a rig_physics found.")

#do the simulation over this time period
t_left = timeSelection.GetValue("hold_left").GetSeconds()
t_right = timeSelection.GetValue("hold_right").GetSeconds()
nframes = (t_right - t_left) / dt.GetSeconds()

#create a window for a progress bar
app = QtGui.QApplication.instance()
window = QtGui.QWidget()
window.resize(500, 25)
window.setWindowTitle('Simple')

progressbar = QtGui.QProgressBar(window)
progressbar.resize(500,25)
progressbar.setMinimum(0)
progressbar.setMaximum(nframes)
progressbar.setValue(0)

window.show()

currentFrame = 0
def doFrame():
	global currentFrame, currenttime, nframes
	global rigidBodies, softBodies
	global world
	global window
	global progressbar

	if currentFrame >= nframes:
		window.close()
		return 0
	#end

	progressbar.setValue(currentFrame)

	#move objects
	for key, b in rigidBodies.iteritems():
		if b.mass == 0:
			trans = GetAbsTransformAtTime(b.handle, currenttime)
			pos, quat = TransformToPosQuat(trans)
			b.body.setTransform(pos, quat)
		else:
			trans = GetTransformAtTime(b.force, currenttime) #LOCAL transform
			pos, rot = TransformToPosEuler(trans)
			b.body.addForce(pos, rot)
		#end
	#end

	for b in softBodies:
		for i in range(len(b.nodelist)):
			node = b.nodelist[i]
			dag = b.daglist[i]
			if node[1] == 0:
				trans = GetAbsTransformAtTime(dag, currenttime)
				pos, quat = TransformToPosQuat(trans)
				b.body.setPosition(i, pos)
			#end
		#end
	#end

	#update the simulation
	world.stepWorld(dt.GetSeconds())

	#grab new positions of dynamic objects
	for key, b in rigidBodies.iteritems():
		if (b.mass != 0):
			pos, quat = b.body.getTransform()
			trans = PosQuatToTransform(pos, quat)
			SetAbsTransformAtTime(b.handle, currenttime, trans)
		#end
	#end

	for b in softBodies:
		for i in range(len(b.nodelist)):
			node = b.nodelist[i]
			dag = b.daglist[i]
			if node[1] != 0:
				oldtrans = GetAbsTransformAtTime(dag, currenttime)
				oldpos, oldquat = TransformToPosQuat(oldtrans)
				newtrans = PosQuatToTransform(b.body.getPosition(i), oldquat)
				SetAbsTransformAtTime(dag, currenttime, newtrans)
			#end
		#end
	#end
	
	currenttime += dt
	currentFrame+=1

	time.sleep(0)

	return 1
#end

while (doFrame()):
	pass

sys.stderr.write("phys_simulate.py: cleaning up\n")
world.destroy()
del rigidBodies
del softBodies
del constraints
