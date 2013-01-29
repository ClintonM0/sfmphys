import socket
import math
import sys

unitsPerMeter = 53.33

def UnitsToMeters(vec):
	ret = vec;
	for i in range(len(ret)):
		ret[i] /= unitsPerMeter
	
	return ret
#end

def MetersToUnits(vec):
	ret = vec;
	for i in range(len(ret)):
		ret[i] *= unitsPerMeter
	
	return ret
#end

def EulerToQuaternion(angles):
	cosx = math.cos(angles[0]/2)
	cosy = math.cos(angles[1]/2)
	cosz = math.cos(angles[2]/2)
	sinx = math.sin(angles[0]/2)
	siny = math.sin(angles[1]/2)
	sinz = math.sin(angles[2]/2)
	
	return [cosx*cosy*cosz + sinx*siny*sinz,
			sinx*cosy*cosz - cosx*siny*sinz,
			cosx*siny*cosz + sinx*cosy*sinz,
			cosx*cosy*sinz - sinx*siny*cosz]
#end

def QuaternionToEuler(quat):
	q0 = quat[0]
	q1 = quat[1]
	q2 = quat[2]
	q3 = quat[3]
	
	return [math.atan2(2*(q0*q1+q2*q3), 1 - 2*(q1*q1+q2*q2)),
			math.asin(2*(q0*q2-q3*q1)),
			math.atan2(2*(q0*q3+q1*q2), 1 - 2*(q2*q2+q3*q3))]
#end

def VecToString(vec):
	return ','.join([str(i) for i in vec])
#end

def StringToVec(data):
	return [float(x) for x in data.split(',')]
#end