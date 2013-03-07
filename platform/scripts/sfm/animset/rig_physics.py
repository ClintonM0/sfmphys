import vs
import sfmUtils
from bernt_utils import *


shot = sfm.GetCurrentShot()
animSet = sfm.GetCurrentAnimationSet()
model = animSet.gameModel
hdr = vs.CStudioHdr(model.GetStudioHdr())

rootDag = sfmUtils.FindFirstDag(["RootTransform", "rootTransform", "roottransform", "Roottransform"])
rootGroup = animSet.GetRootControlGroup()

rig = sfm.BeginRig("rig_physics_" + animSet.GetName());

physGroup = rootGroup.CreateControlGroup("Physics")

#for every hitbox create a handle at its center
nhitset = hdr.numhitboxsets()
for ihitset in range(nhitset):
	nhitbox = hdr.iHitboxCount(ihitset)
	for ihitbox in range(nhitbox):
		box = hdr.pHitbox(ihitbox, ihitset)
		bone = hdr.pBone(box.bone)
		bonename = bone.pszName()
		bodyname = "Body ("+bonename+")"
		handlename = "Handle ("+bonename+")"

		bonedag = sfm.FindDag(bonename)

		boxsize = (box.bbmax - box.bbmin) / 2
		boxcenter = (box.bbmax + box.bbmin) / 2

		#create the handle
		handleGroup = physGroup.CreateControlGroup(bodyname)
		physHandle = sfm.CreateRigHandle(handlename, group=bodyname)
	
		#position and constrain
		CenterTransform = PosQuatToTransform(boxcenter, vs.Quaternion(0,0,0,1))
		ResultTransform = vs.matrix3x4_t()
		vs.ConcatTransforms(bonedag.GetAbsTransform(), CenterTransform, ResultTransform)

		physHandle.SetAbsTransform(ResultTransform)
		sfmUtils.Parent(physHandle, rootDag)
		sfm.ParentConstraint(handlename, bonename, mo=True)

		#info about bones
		parentbone = hdr.pBone(bone.parent)
		parentname = parentbone.pszName()
		nameAttribute = handleGroup.AddAttribute("BoneName", vs.AT_STRING)
		nameAttribute.SetValue(bonename)
		parentAttribute = handleGroup.AddAttribute("ParentName", vs.AT_STRING)
		parentAttribute.SetValue(parentname)
		twistAttribute = handleGroup.AddAttribute("MaxTwist", vs.AT_FLOAT)
		twistAttribute.SetValue(60)

		#info about hitbox
		centerAttribute = handleGroup.AddAttribute("BoxCenter", vs.AT_VECTOR3)
		centerAttribute.SetValue(boxcenter)
		sizeAttribute = handleGroup.AddAttribute("BoxSize", vs.AT_VECTOR3)
		sizeAttribute.SetValue(boxsize)

		#add phys properties
		forceHandle = sfm.CreateRigHandle("Force ("+bonename+")", group=bodyname)
		forceHandle.SetAbsTransform(physHandle.GetAbsTransform())
		sfmUtils.Parent(forceHandle, physHandle)

		bounceControl, bounceValue = sfmUtils.CreateControlledValue("Bounce ("+bonename+")", "value", vs.AT_FLOAT, 0.2, animSet, shot)
		handleGroup.AddControl(bounceControl)
		frictionControl, frictionValue = sfmUtils.CreateControlledValue("Friction ("+bonename+")", "value", vs.AT_FLOAT, 0.2, animSet, shot)
		handleGroup.AddControl(frictionControl)
		densityControl, densityValue = sfmUtils.CreateControlledValue("Density ("+bonename+")", "value", vs.AT_FLOAT, 0.2, animSet, shot)
		handleGroup.AddControl(densityControl)
		kinematicControl, kinematicValue = sfmUtils.CreateControlledValue("Kinematic ("+bonename+")", "value", vs.AT_FLOAT, 0, animSet, shot)
		handleGroup.AddControl(kinematicControl)
		shapeControl, shapeValue = sfmUtils.CreateControlledValue("Shape ("+bonename+")", "value", vs.AT_FLOAT, 0, animSet, shot)
		handleGroup.AddControl(shapeControl)
	#end
#end

sfmUtils.SetControlGroupColor(physGroup, vs.Color(128,255,128,255))

sfm.EndRig()