#include <iostream>
#include <btBulletDynamicsCommon.h>

#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>

#include <winsock2.h>
#include <windows.h>
#include "object.h"

#define SOCKET_BUFSIZE 1024

/*
 * Functions:
 * reset
 * halt
 * step [dt]
 * add [name] [pos] [rot] [kinematic] [shape] [shape size]
 *          [center of mass] [friction] [bounce] [density]
 * joint [type] [body a] [pos a] [rot a] [body b] [pos b] [rot b] [twist]
 * get [name]                returns [pos], [rot]
 * move [name] [pos] [rot]   for kinematic bodies
 * force [obj] [pos] [rot]   for dynamic bodies; **rot is x,y,z, not quaternion
 * list [type]               types: dynamic kinematic
 *
 * addvertex [pos] [norm]    add a point to the convex hull
 */

using namespace boost;
using namespace std;

int main(int argc, char** argv) {
    // Set up the physics world
    std::cout << "Initializing Bullet... ";
    btBroadphaseInterface* broadphase = new btDbvtBroadphase();
    btDefaultCollisionConfiguration* collisionConfiguration = new btDefaultCollisionConfiguration();
    btCollisionDispatcher* dispatcher = new btCollisionDispatcher(collisionConfiguration);
    btSequentialImpulseConstraintSolver* solver = new btSequentialImpulseConstraintSolver;
    btDiscreteDynamicsWorld* dynamicsWorld = new btDiscreteDynamicsWorld(dispatcher,broadphase,solver,collisionConfiguration);
    dynamicsWorld->setGravity(btVector3(0,0,-10));
    std::cout << "done" << std::endl;

    std::cout << "Starting server... ";;
    // Set up a tcp service
    WORD version = MAKEWORD(2,0);
    WSADATA wsaData;
    WSAStartup(version, &wsaData);

    SOCKET s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

    struct sockaddr_in sin;
    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = INADDR_ANY;
    sin.sin_port = htons(52600);
    if (bind(s, (sockaddr *)&sin, sizeof sin) == SOCKET_ERROR)
    {
        return 1;
    }
    listen(s, 16);

    std::cout << "server open on port 52600" << std::endl;
    std::cout << "Ready." << std::endl;

    float elapsed_time = 0;

    SOCKET client = INVALID_SOCKET;
    char buf[SOCKET_BUFSIZE+1];
    while (1) {
        //wait for client to connect
        if (client == INVALID_SOCKET) {
            client = accept(s, NULL, NULL);
        }

        memset(buf, 0, SOCKET_BUFSIZE);
        int bytes = recv(client, buf, SOCKET_BUFSIZE, 0);
        if (bytes == SOCKET_ERROR) {
            strcpy(buf, "end");
        }

        buf[bytes] = '\0';
        //cout << "in: " << buf << endl;
        std::vector<std::string> args;
        boost::split(args, buf, boost::is_space());

        std::string result;
        std::vector<float> temp;

        if (args[0] == "add") {
            std::string& name(args[1]);

            temp = StringToVector(args[2]);
            btVector3 pos(temp[0], temp[1], temp[2]);
            temp = StringToVector(args[3]);
            btQuaternion quat(temp[0], temp[1], temp[2], temp[3]);

            bool isKinematic = boost::lexical_cast<int>(args[4]);

            std::string& shape(args[5]);
            temp = StringToVector(args[6]);
            btVector3 shapeSize(temp[0], temp[1], temp[2]);
            temp = StringToVector(args[7]);
            btVector3 center(temp[0], temp[1], temp[2]);

            float friction = toFloat(args[8]);
            float bounce = toFloat(args[9]);
            float density = toFloat(args[10]);

            Object *obj = createObject(name, pos, quat, isKinematic,
                    shape, shapeSize, center, friction, bounce, density);
            dynamicsWorld->addRigidBody(obj->body);
            result = "ok";
        }
        else if (args[0] == "joint") {
            std::string& type(args[1]);

            std::string& bodya(args[2]);
            temp = StringToVector(args[3]);
            btVector3 posa(temp[0], temp[1], temp[2]);
            temp = StringToVector(args[4]);
            btQuaternion quata(temp[0], temp[1], temp[2], temp[3]);

            std::string& bodyb(args[5]);
            temp = StringToVector(args[6]);
            btVector3 posb(temp[0], temp[1], temp[2]);
            temp = StringToVector(args[7]);
            btQuaternion quatb(temp[0], temp[1], temp[2], temp[3]);

            float twist = toFloat(args[8]);

            btTypedConstraint *joint = createJoint(type, bodya, posa, quata, bodyb, posb, quatb, twist);
            dynamicsWorld->addConstraint(joint, true);
            result = "ok";
        }
        else if (args[0] == "get") {
            result = "ok "+getObjectTransform(args[1]);
        }
        else if (args[0] == "move") {
            std::string& name(args[1]);

            temp = StringToVector(args[2]);
            btVector3 pos(temp[0], temp[1], temp[2]);
            temp = StringToVector(args[3]);
            btQuaternion quat(temp[0], temp[1], temp[2], temp[3]);

            moveObject(name, pos, quat);
            result = "ok";
        }
        else if (args[0] == "force") {
            std::string& name(args[1]);

            temp = StringToVector(args[2]);
            btVector3 pos(temp[0], temp[1], temp[2]);
            temp = StringToVector(args[3]);
            btVector3 rot(temp[0], temp[1], temp[2]);

            forceObject(name, pos, rot);
            result = "ok";
        }
        else if (args[0] == "list") {
            result = "ok "+listObjects(args[1]);
        }
        else if (args[0] == "step") {
            float dt = toFloat(args[1]);
            dynamicsWorld->stepSimulation(dt, 120, 1.0/120.0);
            result = "ok";
            elapsed_time += dt;

            std::cout << "Elapsed time: " << elapsed_time << std::endl;
        }
        else if (args[0] == "hullvertex") {
            temp = StringToVector(args[1]);
            btVector3 pos(temp[0], temp[1], temp[2]);
            temp = StringToVector(args[2]);
            btVector3 norm(temp[0], temp[1], temp[2]);

            addHullVertex(pos, norm);
            result = "ok";
        }
        else if (args[0] == "reset") {
            delete dynamicsWorld;
            delete solver;
            delete collisionConfiguration;
            delete dispatcher;
            delete broadphase;

            destroyAllObjects();

            broadphase = new btDbvtBroadphase();
            collisionConfiguration = new btDefaultCollisionConfiguration();
            dispatcher = new btCollisionDispatcher(collisionConfiguration);
            solver = new btSequentialImpulseConstraintSolver;
            dynamicsWorld = new btDiscreteDynamicsWorld(dispatcher,broadphase,solver,collisionConfiguration);
            dynamicsWorld->setGravity(btVector3(0,0,-10));
            result = "ok";

            elapsed_time = 0;
        }
        else if (args[0] == "end") {
            closesocket(client);
            client = INVALID_SOCKET;
            continue;
        }
        else if (args[0] == "halt") {
            closesocket(client);
            client = INVALID_SOCKET;
            break;
        }
        else {
            result = "ERROR: unrecognized command";
        }

        //cout << "out: " << result << endl;
        send(client, result.c_str(), result.size(), 0);
    }

    delete dynamicsWorld;
    delete solver;
    delete collisionConfiguration;
    delete dispatcher;
    delete broadphase;

    return 0;
}

