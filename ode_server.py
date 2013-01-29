# Echo server program
from ode_connect import *
from ode_data import *
import socket
import sys
import ode

geoms = {}
bodies = {}

world = ode.World()
world.setGravity([0,0,-9.8])
world.setERP(0.8)
world.setCFM(1E-8)

space = ode.Space()
contacts = ode.JointGroup()

floor = ode.GeomPlane(space, (0,0,1), 0)

def addObject(name, pos, rot, boxmin, boxmax, isStatic):
	boxsize = [boxmax[0]-boxmin[0], boxmax[1]-boxmin[1], boxmax[2]-boxmin[2]]
	center = [(boxmin[0]+boxmax[0])/2.0,
				(boxmin[1]+boxmax[1])/2.0,
				(boxmin[2]+boxmax[2])/2.0]
	#TODO: what to do with center?
	#TODO: consider different geomtypes here
	g = ode.GeomBox(space, lengths = boxsize)
	#g.setCollideBits(0x1)
	
	if (not isStatic):
		b = ode.Body(world)
		m = ode.Mass()
		m.setBox(1, boxsize[0], boxsize[1], boxsize[2])
		b.setMass(m)
		g.setBody(b)
		bodies.update({name: b})
	
	g.setPosition(pos)
	g.setQuaternion(rot)
	
	geoms.update({name: g})
#end

def removeObject(name):
	space.remove(geom[name])
	del geom[name]
	del body[name]
#end

def listObjects(type):
	if (type == "geoms"):
		return ' '.join(geoms.keys())
	elif (type == "bodies"):
		return ' '.join(bodies.keys())
	
	return ""
#end

def near_callback(args, geom1, geom2):
	# Check if the objects do collide
	contact = ode.collide(geom1, geom2)
	
	# Create contact joints
	for c in contact:
		c.setBounce(0.01)
		c.setMu(5000)
		j = ode.ContactJoint(world, contacts, c)
		j.attach(geom1.getBody(), geom2.getBody())
	#end for
#end

def step(t):
	iterations = 4
	for i in range(iterations):
		space.collide(None, near_callback)
		world.step(t/iterations)
		contacts.empty()
	#end for
#end

def getobj(objname):
	g = None
	
	try:
		g = geoms[objname]
	except KeyError:
		return "ERROR"
	
	ret = VecToString(g.getPosition()) + " " + VecToString(g.getQuaternion())
	#print "getobj: ", ret
	return ret
#end

s = connect(True, 52600)
conn, addr = None, None

while 1:
	if (conn == None):
		conn, addr = waitForClient(s)
	
	rec = conn.recv(1024)
	print "received: ", rec
	data = rec.split()
	
	try:
		if (data[0] == "add"): #add objname pos rot boxmin boxmax static
			name = data[1]
			pos = StringToVec(data[2])
			rot = StringToVec(data[3])
			boxmin = StringToVec(data[4])
			boxmax = StringToVec(data[5])
			static = int(data[6])
			addObject(name, pos, rot, boxmin, boxmax, static)
			conn.send("ok")
		elif (data[0] == "remove"): #remove objname
			objname = data[1]
			removeObject(objname)
			conn.send("ok")
		elif (data[0] == "list"): #list type [geoms / bodies]
			type = data[1]
			conn.send("ok "+listObjects(type))
		elif (data[0] == "step"): #step time
			t = float(data[1])
			step(t)
			conn.send("ok")
		elif (data[0] == "getobj"): #getobj objname
			objname = data[1]
			conn.send("ok " + getobj(objname))
		elif (data[0] == "end"): #end
			conn = None
		elif (data[0] == "halt"): #halt
			break
		else:
			conn.send("ERROR Unknown Command")
		#end if
	except:
		e = sys.exc_info()[0]
		print "ERROR " + str(e)
		conn.send("ERROR " + str(e))
	#end try
	
#end while

conn.close()