import os
import sys
import json

import vs
import sfmUtils
from filesystem import *

import sfmphys.rigutils
sfmphys.rigutils = reload(sfmphys.rigutils)

from sfmphys.rigutils import *
from sfmphys.dagutils import *

def unicodeToStr(data):
	if isinstance(data, dict):
		return dict((unicodeToStr(key), unicodeToStr(value)) for (key, value) in data.iteritems())
	elif isinstance(data, list):
		return [unicodeToStr(element) for element in data]
	elif isinstance(data, unicode):
		return data.encode('utf-8')
	else:
		return data
#end

def vectorToList(vec):
	return [vec.x, vec.y, vec.z]
#end
def listToVector(tup):
	return vs.Vector(tup[0], tup[1], tup[2])
#end
def quatToList(quat):
	return [quat.x, quat.y, quat.z, quat.w]
#end
def listToQuat(tup):
	return vs.Quaternion(tup[0], tup[1], tup[2], tup[3])
#end

shot = sfm.GetCurrentShot()
animSet = sfm.GetCurrentAnimationSet()
model = animSet.gameModel

// .physics.txt detection completely broken. Will break vertex animation.
//mdl_path = RelativePathToFullPath(model.GetModelName(), game())
//if mdl_path is None:
	phys_path = "<FILE NOT FOUND>"
//else:
//	phys_path = os.path.splitext(mdl_path)[0] + ".physics.txt"

data = dict()

sys.stderr.write("rig_physics.py: looking for config file at: "+str(phys_path)+"\n")

if os.path.isfile(phys_path):
	#load data from the file
	sys.stderr.write("rig_physics.py: loading config\n")
	infile = open(phys_path, "r")
	data = unicodeToStr(json.load(infile))
	infile.close()
else:
	#try to guess with rigidbodies
	sys.stderr.write("rig_physics.py: no config found, assuming rigidbody\n")
	hdr = vs.CStudioHdr(model.GetStudioHdr())
	parents = {}

	data["rigidbodies"] = list()
	data["constraints"] = list()

	nhitset = hdr.numhitboxsets()
	for ihitset in range(nhitset):
		nhitbox = hdr.iHitboxCount(ihitset)
		for ihitbox in range(nhitbox):
			box = hdr.pHitbox(ihitbox, ihitset)
			bone = hdr.pBone(box.bone)
			bonename = bone.pszName()
			boxsize = (box.bbmax - box.bbmin) / 2
			boxcenter = (box.bbmax + box.bbmin) / 2

			body = {"target": bonename,
					"boxcenter": vectorToList(boxcenter),
					"boxsize": vectorToList(boxsize)}
			data["rigidbodies"].append(body)

			tempBone = bone
			parents[bonename] = []
			while tempBone.parent != -1:
				parent = hdr.pBone(tempBone.parent)
				parents[bonename].append(parent.pszName())
				tempBone = parent
			#end
		#end
	#end

	#create constraints
	for i in parents:
		par = parents[i]
		for j in par:
			if j in parents: #if j is an ancestor of i *and* has an associated rigidbody
				cons = {"constype": "cone",
						"bodya": j,
						"bodyb": i,
						"rotx": 90,
						"roty": 90,
						"twist": 35}

				data["constraints"].append(cons)
				break #we can only have 1 parent per bone
			#end
		#end
	#end

	#don't do this yet.
	#if the rig doesn't work, it'll save the faulty rig and that's a Bad Thing
	#outfile = open(phys_path, "w")
	#json.dump(data, outfile, indent=2)
	#outfile.close()
	#sys.stderr.write("rig_physics.py: saved rigidbody config to "+str(phys_path)+"\n")
#end

#create the rig
rig = sfm.BeginRig("rig_physics_" + animSet.GetName(), True)
rootGroup = animSet.GetRootControlGroup()

rigidbodyGroup = rootGroup.CreateControlGroup("Rigidbodies")
constraintGroup = rootGroup.CreateControlGroup("PhysConstraints")
softbodyGroup = rootGroup.CreateControlGroup("Softbodies")

if "rigidbodies" in data:
	for body in data["rigidbodies"]:
		body["boxcenter"] = listToVector(body["boxcenter"])
		body["boxsize"] = listToVector(body["boxsize"])
		group = rigidbodyGroup.CreateControlGroup("Body ("+body["target"]+")")
		bodyrig = RigidbodyRig(data=body)
		bodyrig.writeToGroup(group)
	#end
#end
if "constraints" in data:
	for cons in data["constraints"]:
		group = constraintGroup.CreateControlGroup(cons["constype"] + "_constraint ("+cons["bodya"]+" -> "+cons["bodyb"]+")")
		consrig = ConstraintRig(data=cons)
		consrig.writeToGroup(group)
	#end
#end

if "cloths" in data:
	for cloth in data["cloths"]:
		body = dict(cloth)
		body["nodelist"] = list()
		body["linklist"] = list()
		body["facelist"] = list()

		boneformat = cloth["boneformat"]
		ranges = cloth["formatranges"]
		body["boneprefix"] = boneformat.format(*["" for r in ranges])
		counters = [r[0] for r in ranges]

		while 1:
			name = boneformat.format(*counters)
			body["nodelist"].append( (name, 1) )

			endLoop = True
			for n in range(len(counters)):
				counters[n]+=1
				if counters[n] <= ranges[n][1]:
					endLoop = False
					break
				#end

				counters[n] = ranges[n][0]
			#end

			#if we go through the for-loop without breaking then the range is completed
			if endLoop:
				break
		#end

		width = cloth["width"]
		height = cloth["height"]

		for row in range(height):
			for column in range(width):
				index = row*width+column
				#only create links along face edges
				#no shear/bend links, since those are handled more or less by bullet
				if row != 0:
					body["linklist"].append( (index, index-width) )
				if column != 0:
					body["linklist"].append( (index, index-1) )

				if (row != 0) and (column != 0):
					body["facelist"].append( (index, index-1, index-width-1, index-width) )
			#end
		#end

		if not "softbodies" in data:
			data["softbodies"] = list()

		data["softbodies"].append(body)
	#end
#end

if "softbodies" in data:
	for body in data["softbodies"]:
		group = softbodyGroup.CreateControlGroup("Softbody ("+body["boneprefix"]+")")
		softrig = SoftbodyRig(data=body)
		softrig.writeToGroup(group)
	#end
#end

sfmUtils.SetControlGroupColor(rigidbodyGroup, vs.Color(128,255,128,255))
sfmUtils.SetControlGroupColor(constraintGroup, vs.Color(128,200,200,255))
sfmUtils.SetControlGroupColor(softbodyGroup, vs.Color(128,128,255,255))

sfm.EndRig()
