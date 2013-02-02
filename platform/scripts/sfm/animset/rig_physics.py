import vs
import sfmUtils

shot = sfm.GetCurrentShot()
animSet = sfm.GetCurrentAnimationSet()
gameModel = animSet.gameModel
rootDag = sfmUtils.FindFirstDag(["RootTransform", "rootTransform", "roottransform", "Roottransform"])
rootGroup = animSet.GetRootControlGroup()

rig = sfm.BeginRig("rig_physics_" + animSet.GetName());

physGroup = rootGroup.CreateControlGroup("Physics")

forceHandle = sfm.CreateRigHandle("Force", group="Physics")
forceHandle.SetAbsTransform(rootDag.GetAbsTransform())
sfmUtils.Parent(forceHandle, rootDag)
centerHandle = sfm.CreateRigHandle("CenterOfMass", group="Physics", rotControl=False)
centerHandle.SetAbsPosition(rootDag.GetAbsPosition())
sfmUtils.Parent(centerHandle, rootDag)

bounceControl, bounceValue = sfmUtils.CreateControlledValue("Bounce", "value", vs.AT_FLOAT, 0.2, animSet, shot)
physGroup.AddControl(bounceControl)
frictionControl, frictionValue = sfmUtils.CreateControlledValue("Friction", "value", vs.AT_FLOAT, 0.2, animSet, shot)
physGroup.AddControl(frictionControl)
densityControl, densityValue = sfmUtils.CreateControlledValue("Density", "value", vs.AT_FLOAT, 0.2, animSet, shot)
physGroup.AddControl(densityControl)
kinematicControl, kinematicValue = sfmUtils.CreateControlledValue("Kinematic", "value", vs.AT_FLOAT, 0, animSet, shot)
physGroup.AddControl(kinematicControl)
shapeControl, shapeValue = sfmUtils.CreateControlledValue("Shape", "value", vs.AT_FLOAT, 0, animSet, shot)
physGroup.AddControl(shapeControl)

sfmUtils.SetControlGroupColor(physGroup, vs.Color(128,255,128,255))

sfm.EndRig()