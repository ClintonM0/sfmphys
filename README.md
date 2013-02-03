Bullet release note: It is recommended you delete the *rig_obj_add** scripts from the previous version to avoid confusion, as these are no longer used. Refer to the "How to Use" section for more information.
Go ahead and delete the ode_server files as well - it has been replaced by bulletserver.exe.

#SFM Physics Scripts
### What does this do?
* Incorporates physics simulation into SFM via python scripts
* Handles collision detection and response
* Can create physics-controlled, static, and kinematic bodies
* You can adjust the density, bounciness, and friction of objects
* You can animate external forces on objects
* It *might* crash SFM. If you're concerned, *backup your important files*, just in case.

### What does this not do? (Planned or Impractical Features)
* Handle collisions with the level
    * You can get around this by adding non-renderable objects where the level geometry is.
      For example, there are some nice big wall segments in the Portal 2 files for large flat areas or walls.
* Use .mdl or collision meshes
    * Only the bounding boxes are used for simulation. Support for capsules and spheres will be added at a later date.
    * Also, the code currently assumes the root node is in the center of the model. This will be fixed soon.
    * Loading from .mdl probably isn't going to happen. Loading from .smd or other formats might, but not for a while.
* Ragdolls, springs, cloth, etc.
    * These will (hopefully) be in a later release

### How to install
* Grab this repository with git, or download the .zip (the button with a cloud symbol near the top of the page)
* Extract and copy the "platform" and "sdktools" folders to [steamapps]/common/SourceFilmmaker/game. Choose to merge folders.
* Put bulletserver.exe wherever you like.

### How to use
* Start sfm, and set up your scene. Attach a rig_physics to any objects you want included in the simulation. Also start bullet_server.exe, and let it run in the background.
* NOTE: If Windows asks whether to allow the program on private/public networks, select private and say yes. If it does not ask, make sure sfm and bullet_server are allowed to create connections in Windows Firewall (the programs communicate via sockets; it's not unlike running a local TF2 server or the like).
* The "shape" control works as follows: if value < 0.5 (slider on the left half), "box" is selected; if value > 0.5 (slider on the right half), "sphere" is selected.
* The "kinematic" control is "dynamic" for values < 0.5; "kinematic" for values > 0.5.
* The "center of mass" control currently does not function properly, and the "force" control will need some tweaking to be more useful (note that you can also rotate the "force" control to apply torque to an object).
* The RootTransform of each object must be at its center. This should be fixed in a later release.
* Select a period of time to simulate over in the motion editor (ie, with the floating modification layer). The simulation will not run if the time selection is infinite in either direction.
* Once the scene is set up, right-click any animation set and run "phys_simulate". The simulation might take a few seconds. If SFM doesn't respond immediately just be patient.
* To run a simulation again, just run "phys_simulate" again. There's no need to re-rig objects or to restart the server (the sim is reset automatically every time "phys_simulate" runs).

### Videos
Day 1 http://www.youtube.com/watch?v=LDMB95El9GA  
Day 2 http://www.youtube.com/watch?v=a99sJrXWOxo  
Day 3 http://www.youtube.com/watch?v=GtQ50YWORcA  
Day 5 http://www.youtube.com/watch?v=vyzgnJhkdeQ

This project uses the bullet physics library. Check out http://bulletphysics.org for more info.
