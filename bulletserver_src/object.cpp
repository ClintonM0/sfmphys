#include "object.h"

#include <algorithm>
#include <cmath>
#include <boost/lexical_cast.hpp>
#include <boost/unordered_map.hpp>
#include <LinearMath/btGeometryUtil.h>
#include <BulletCollision/CollisionShapes/btShapeHull.h>

#define PI 3.14159265358979323846

//float toFloat(string)
std::string (&toString)(const float&) = boost::lexical_cast<std::string, float>;
//string toString(float)
float (&toFloat)(const std::string&) = boost::lexical_cast<float, std::string>;

std::string VectorToString(const std::vector<float>& vec)
{
    std::string ret("");

    std::vector<float>::const_iterator iter;
    for (iter=vec.begin(); iter!=vec.end(); iter++) {
        ret += boost::lexical_cast<std::string>(*iter)+",";
    }

    unsigned int strsize = ret.size();
    if (strsize > 0) {
        ret.resize(strsize-1); //remove trailing comma
    }

    return ret;
}

std::vector<float> StringToVector(const std::string& str)
{
    std::vector<float> ret;
    std::vector<std::string> splitstr;
    boost::split(splitstr, str, boost::is_any_of(","));

    std::vector<std::string>::iterator iter;
    for (iter=splitstr.begin(); iter!=splitstr.end(); iter++) {
        ret.push_back(boost::lexical_cast<float>(*iter));
    }

    return ret;
}

///////////////////////////////////////////////////////////////////////

std::vector<btVector3> hull;
typedef boost::unordered_map<std::string, Object *> ObjectMap;
ObjectMap objects;

typedef std::pair<std::string, std::string> strpair;
typedef boost::unordered_map<strpair, btTypedConstraint *> JointMap;
JointMap joints;

bool getKinematic(const Object *obj)
{
    return (obj->body->getCollisionFlags() & btCollisionObject::CF_KINEMATIC_OBJECT);
}

// add [name] [pos] [rot] [kinematic] [shape] [shape size]
//          [center of mass] [friction] [bounce] [density]
Object *createObject(const std::string& name, const btVector3& pos,
        const btQuaternion& quat, bool isKinematic, const std::string& shape,
        const btVector3& shapeSize, const btVector3& center, float friction,
        float bounce, float density)
{
    std::cout << "Adding object " << name << std::endl;
    std::cout.flush();

    //create the object
    Object *obj = new Object;

    //create a shape
    btScalar mass;
    if (shape == "hull") {
        //make a "complete" hull shape
        btConvexHullShape *temp = new btConvexHullShape();
        std::vector<btVector3>::iterator iter;
        for (iter=hull.begin(); iter!=hull.end(); iter++) {
            temp->addPoint(*iter);
        }
        hull.clear();

        //simplify it
        btShapeHull *simplified = new btShapeHull(temp);
        simplified->buildHull(0.04f);
        delete temp;

        //then build the simplified hull
        obj->shape = new btConvexHullShape((btScalar *)simplified->getVertexPointer(), simplified->numVertices());
        delete simplified;
    }
    else if (shape == "sphere") {
        //in practice, if "sphere" is selected in SFM, the client should send
        //a vector <radius, 0, 0>
        btScalar radius = std::max(shapeSize.x(),std::max(shapeSize.y(), shapeSize.z()));
        obj->shape = new btSphereShape(radius);
    }
    else { //default is "box"
        obj->shape = new btBoxShape(shapeSize);
    }

    if (isKinematic) {
        mass = 0;
    }
    else {
        float size = (shapeSize.x() + shapeSize.y() + shapeSize.z()) / 3.0f;
        mass = 1.0f + std::sqrt(density * size);
        std::cout << "Mass = " << mass << std::endl;
    }

    //create a motion state
    obj->motion = new btDefaultMotionState(btTransform(quat,pos));

    btVector3 inertia = btVector3(0,0,0);
    obj->shape->calculateLocalInertia(mass, inertia);
    btRigidBody::btRigidBodyConstructionInfo fallRigidBodyCI(
            mass,obj->motion,obj->shape,inertia);

    //create a body and set properties
    obj->body = new btRigidBody(fallRigidBodyCI);

    if (isKinematic) {
        obj->body->setCollisionFlags(obj->body->getCollisionFlags() |
                btCollisionObject::CF_KINEMATIC_OBJECT);
    }

    obj->body->setActivationState(DISABLE_DEACTIVATION);

    obj->body->setRestitution(bounce);
    obj->body->setFriction(friction * 100);
    obj->body->setCenterOfMassTransform(btTransform(quat, pos + center));
    obj->body->setDamping(0.05, 0.1);

    //add to store and return
    ObjectMap::iterator iter = objects.insert(std::make_pair(name, obj)).first;

    return iter->second;
}

// joint [type] [body a] [pos a] [rot a] [body b] [pos b] [rot b] [twist]
btTypedConstraint *createJoint(const std::string& type,
        const std::string& bodya, const btVector3& posa, const btQuaternion& quata,
        const std::string& bodyb, const btVector3& posb, const btQuaternion& quatb,
        float twist)
{
    if (type == "point") {
        Object *obja = getObject(bodya);
        Object *objb = getObject(bodyb);

        btPoint2PointConstraint *pjoint = new btPoint2PointConstraint(
                *(obja->body), *(objb->body), posa, posb);

        joints.insert(std::make_pair(strpair(bodya, bodyb), pjoint));

        return pjoint;
    }

    if (type == "cone") {
        Object *obja = getObject(bodya);
        Object *objb = getObject(bodyb);

        btTransform transa(quata, posa);
        btTransform transb(quatb, posb);

        btConeTwistConstraint *pjoint = new btConeTwistConstraint(
                *(obja->body), *(objb->body), transa, transb);
        pjoint->setLimit(PI/2.0, PI/2.0, twist);

        return pjoint;
    }

    return NULL;
}

// get [name]                returns [pos], [rot]
std::string getObjectTransform(const std::string& name)
{
    ObjectMap::iterator iter = objects.find(name);

    btTransform trans;
    iter->second->motion->getWorldTransform(trans);
    btVector3 pos = trans.getOrigin();
    btQuaternion quat = trans.getRotation();

    return toString(pos.x()) + "," + toString(pos.y()) + "," +
            toString(pos.z()) + " " +
            toString(quat.x()) + "," + toString(quat.y()) + "," +
            toString(quat.z()) + "," + toString(quat.w());
}

// move [name] [pos] [rot]   for kinematic bodies
void moveObject(const std::string& name, const btVector3& pos,
        const btQuaternion& quat)
{
    ObjectMap::iterator iter = objects.find(name);
    Object *obj = iter->second;

    if (getKinematic(obj)) {
        btTransform newTrans;
        obj->body->getMotionState()->getWorldTransform(newTrans);
        newTrans.setOrigin(pos);
        newTrans.setRotation(quat);
        obj->body->getMotionState()->setWorldTransform(newTrans);
    }
}

// force [obj] [pos] [rot]   for dynamic bodies
void forceObject(const std::string& name, const btVector3& pos,
        const btVector3& rot)
{
    ObjectMap::iterator iter = objects.find(name);
    Object *obj = iter->second;

    if (!getKinematic(obj)) {
        obj->body->applyCentralForce(pos);
        obj->body->applyTorque(rot);
    }
}

// list [type]               types: dynamic kinematic
std::string listObjects(const std::string& type)
{
    std::string ret;
    if (type == "dynamic") {
        ObjectMap::iterator iter;
        for (iter=objects.begin(); iter != objects.end(); iter++) {
            if (!getKinematic(iter->second)) {
                ret += iter->first + " ";
            }
        }
    }
    else if (type == "kinematic") {
        ObjectMap::iterator iter;
        for (iter=objects.begin(); iter != objects.end(); iter++) {
            if (getKinematic(iter->second)) {
                ret += iter->first + " ";
            }
        }
    }

    unsigned int strsize = ret.size();
    if (strsize > 0) {
        ret.resize(strsize-1); //remove trailing whitespace
    }

    return ret;
}

void addHullVertex(const btVector3& pos, const btVector3& norm)
{
    //bullet adds a margin around objects so we need to shrink out object
    //but calculating normals can be expensive at runtime
    //so instead we ask for a normal and use that
    hull.push_back(pos - norm*0.04f);
}

Object *getObject(const std::string& name)
{
    ObjectMap::iterator iter = objects.find(name);
    if (iter != objects.end()) {
        return iter->second;
    }
    else {
        return NULL;
    }
}

void destroyObject(const std::string& name)
{
    ObjectMap::iterator iter = objects.find(name);
    if (iter != objects.end()) {
        delete iter->second->body;
        delete iter->second->motion;
        delete iter->second->shape;
        delete iter->second;
        objects.erase(iter);
    }

    JointMap::iterator jiter;
    for (jiter=joints.begin(); jiter!=joints.end(); jiter++) {
        const strpair& key(jiter->first);
        if (key.first == name || key.second == name) {
            delete jiter->second;
            joints.erase(jiter);
        }
    }
}

void destroyAllObjects()
{
    ObjectMap::iterator iter;
    for (iter=objects.begin(); iter!=objects.end(); iter++) {
        delete iter->second->body;
        delete iter->second->motion;
        delete iter->second->shape;
        delete iter->second;
    }
    objects.clear();

    //does deleting the world automatically remove joints?
    /*JointMap::iterator jiter;
    for (jiter=joints.begin(); jiter!=joints.end(); jiter++) {
        delete iter->second;
    }*/
    joints.clear();
}