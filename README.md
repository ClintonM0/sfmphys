Bullet release note: It is recommended you delete the *rig_obj_add** scripts from the previous version to avoid confusion, as these are no longer used. Refer to the "How to Use" section for more information.
Go ahead and delete the ode_server files as well - it has been replaced by bulletserver.exe.

#SFM Physics Scripts
### What does this do?
* Incorporates physics simulation into SFM via python scripts
* Handles collision detection and response
* Can create physics-controlled, static, and kinematic bodies
* Can create ragdolls and ropes, assuming the source model is set up with proper hitboxes
* You can adjust the density, bounciness, and friction of objects
* You can animate external forces on objects
* It *might* crash SFM. If you're concerned, *backup your important files*, just in case.

### What does this not do? (Planned or Impractical Features)
* Handle collisions with the level
    * You can get around this by adding kinematic objects where the level geometry is. (Models do not have to be visible to be included in the simulation!)
* Use .mdl or collision meshes
    * Only the bounding boxes are used for simulation. Support for capsules and spheres will be added at a later date.
    * Loading from .mdl probably isn't going to happen. Loading from .smd or other formats might, but not for a while.
* Springs, explosions, etc.
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
* Select a period of time to simulate over in the motion editor (ie, with the floating modification layer). The simulation will not run if the time selection is infinite in either direction.
* Once the scene is set up, right-click any animation set and run "phys_simulate". The simulation might take a few seconds. If SFM doesn't respond immediately just be patient.
* To run a simulation again, just run "phys_simulate" again. There's no need to re-rig objects or to restart the server (the sim is reset automatically every time "phys_simulate" runs).

### Some notes on ragdolls etc.
* The hwm engineer and scout have some issues as they have body parts not connected to the rest of the model (engineer apparently has no pelvis hitbox, and scout's pack moves freely).
* If parts of a model appear disconnected, you can manually edit the joints. Open the animation set in the element viewer and browse to RootControlGroup -> children -> Physics -> children -> body (bone name). There you can change the "ParentName" attribute appropriately. You can also change the "max twist" and "box size" attributes if necessary for fine tuning.
* Animation with ragdolls is difficult since you have to use the physics handles. I'll add an option to use the model's normal bones for fully-kinematic objects in the future.

### Videos
Day 1 http://www.youtube.com/watch?v=LDMB95El9GA  
Day 2 http://www.youtube.com/watch?v=a99sJrXWOxo  
Day 3 http://www.youtube.com/watch?v=GtQ50YWORcA  
Day 5 http://www.youtube.com/watch?v=vyzgnJhkdeQ  
Day 5.5 http://www.youtube.com/watch?v=AyKmftF3ZX0  
Day whatever: http://www.youtube.com/watch?v=-GgTciTTUs8
Day whatever + 1: http://www.youtube.com/watch?v=6ELrKtixYog

This project uses the bullet physics library. Check out http://bulletphysics.org for more info.
