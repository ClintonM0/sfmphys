import sys
import vs
import sfmUtils
import Tkinter

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

#get info about the shot
timeSelection = GetCurrentTimeSelection()

#check for "infinite"
if (timeSelection.IsEitherInfinite()):
	raise Exception("phys_simulate.py: Please select a finite time range.")

time = timeSelection.GetValue("hold_left")
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
			bodyrig = RigidbodyRig(group=group, time=time)
			bodyrig.body = Rigidbody(bodyrig)
			world.addRigidBody(bodyrig.body)
			rigidBodies[animSet.GetName()+":"+bodyrig.target] = bodyrig
		#end
	#end

	if root_group.HasChildGroup("PhysConstraints", False):
		phys_group = root_group.FindChildByName("PhysConstraints", False)

		for group in phys_group.GetValue("children"):
			consrig = ConstraintRig(group=group, time=time)
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
			softrig = SoftbodyRig(group=group, time=time)
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
class App(Tkinter.Tk):
	def __init__(self):
		sys.argc=1
		sys.argv=["sfm.exe"]

		Tkinter.Tk.__init__(self)
		self.geometry("200x50")
		self.title("Phys Progress")

		self.canvas = Tkinter.Canvas(self, width=200, height=50)
		self.rect = self.canvas.create_rectangle(0, 0, 0, 50, fill="#7C8DC9")
		self.label = self.canvas.create_text(100, 25, text="")
		self.canvas.pack()
	#end
#end

app = App()

currentFrame = 0
def doFrame():
	global currentFrame, time, nframes
	global rigidBodies, softBodies
	global world
	global app

	if currentFrame >= nframes:
		app.destroy()
		return
	#end

	progress = float(currentFrame)/float(nframes)

	app.canvas.coords(app.rect, 0,0,200*progress,50)
	app.canvas.itemconfigure(app.label, text=str(int(100*progress))+"/100")

	#move objects
	for key, b in rigidBodies.iteritems():
		if b.mass == 0:
			trans = GetAbsTransformAtTime(b.handle, time)
			pos, quat = TransformToPosQuat(trans)
			b.body.setTransform(pos, quat)
		else:
			trans = GetTransformAtTime(b.force, time) #LOCAL transform
			pos, rot = TransformToPosEuler(trans)
			b.body.addForce(pos, rot)
		#end
	#end

	for b in softBodies:
		for i in range(len(b.nodelist)):
			node = b.nodelist[i]
			dag = b.daglist[i]
			if node[1] == 0:
				trans = GetAbsTransformAtTime(dag, time)
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
			SetAbsTransformAtTime(b.handle, time, trans)
		#end
	#end

	for b in softBodies:
		for i in range(len(b.nodelist)):
			node = b.nodelist[i]
			dag = b.daglist[i]
			if node[1] != 0:
				oldtrans = GetAbsTransformAtTime(dag, time)
				oldpos, oldquat = TransformToPosQuat(oldtrans)
				newtrans = PosQuatToTransform(b.body.getPosition(i), oldquat)
				SetAbsTransformAtTime(dag, time, newtrans)
			#end
		#end
	#end
	
	time += dt
	currentFrame+=1
	app.after(1, doFrame)
#end

app.after(250, doFrame)
app.mainloop()

sys.stderr.write("phys_simulate.py: cleaning up\n")
world.destroy()
del rigidBodies
del softBodies
del constraints