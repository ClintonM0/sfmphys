#ifndef OBJECT_H
#define	OBJECT_H

#include <btBulletDynamicsCommon.h>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>
#include <string>
#include <vector>

extern std::string (&toString)(const float&);
extern float (&toFloat)(const std::string&);
std::string VectorToString(const std::vector<float>& vec);
std::vector<float> StringToVector(const std::string& str);

struct Object
{
    btCollisionShape *shape;
    btMotionState *motion;
    btRigidBody *body;
};

// add [name] [pos] [rot] [kinematic] [shape] [shape size]
//          [center of mass] [friction] [bounce] [density]
Object *createObject(const std::string& name, const btVector3& pos,
        const btQuaternion& quat, bool isKinematic, const std::string& shape,
        const btVector3 shapeSize, const btVector3& center, float friction,
        float bounce, float density);

// get [name]                returns [pos], [rot]
std::string getObjectTransform(const std::string& name);

// move [name] [pos] [rot]   for kinematic bodies
void moveObject(const std::string& name, const btVector3& pos,
        const btQuaternion& quat);

// force [obj] [pos] [rot]   for dynamic bodies
void forceObject(const std::string& name, const btVector3& pos,
        const btVector3& rot);

// list [type]               types: dynamic kinematic
std::string listObjects(const std::string& type);

Object *getObject(const std::string& name);
std::vector<Object *> getAllObjects();
void destroyObject(const std::string& name);
void destroyAllObjects();

#endif	/* OBJECT_H */

