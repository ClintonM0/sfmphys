#SFM Physics Scripts
### What does this do?
* Incorporates physics simulation into SFM via python scripts
* Handles collision detection and response
* Can create physics-controlled, static, and kinematic bodies
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
* External forces
    * You can't give physics-controlled objects an initial velocity, or animate forces. This will be in a later release.
* Set physics properties or gravity
    * Density, bounciness, friction, etc. This will be added in a later release.

### How to install
* Grab this repository with git, or download the .zip (the button with a cloud symbol near the top of the page)
* Extract and copy the files to [steamapps]/common/SourceFilmmaker/game. If you did this correctly,
  "sfm.exe" and "ode_server_start.bat" will be in the same folder.

### How to use
* Start sfm, and set up your scene. Position physics objects, animate kinematic objects, etc. (Also, in this version,
  you must ensure that the RootTransform node is in the center of the model. Move the static_prop or other bones around
  if your models need adjustment.)
* Select a period of time to simulate over in the motion editor (ie, with the floating modification layer).
  ***THIS IS A CRUCIAL STEP.*** The simulation goes over the entire range of your time selection so if you leave it
  at the default (infinite in either direction) SFM will probably crash (at the very least, the simulation will run for a very long time).
* Run "ode_server_start.bat"
* For each object you want to include in the simulation (phys, kinematic, *and* static):
    - Right-click the animation set and select from the rigs menu:
        * "phys_obj_add" for physics-controlled objects
        * "phys_obj_add_static" for non-moving, colliding objects (this may be removed in favor of phys_obj_kinematic)
        * "phys_obj_kinematic" for hand-animated, colliding objects (this can also be used for static objects)
* Once you have added every object, right-click any animation set and select "phys_simulate" from the rigs menu.
  The simulation might take a few seconds. If SFM doesn't respond immediately just be patient.
* It doesn't matter in which order you add objects
* If you want to perform another simulation, close the ode_server.bat window and start it again.
  Support for resetting the sim from within SFM will be added in the future.

### Videos
Day 1 http://www.youtube.com/watch?v=LDMB95El9GA  
Day 2 http://www.youtube.com/watch?v=a99sJrXWOxo  
Day 3 http://www.youtube.com/watch?v=GtQ50YWORcA

This repository contains a copy of the pyODE binaries for Windows; see http://pyode.sourceforge.net/ for more information.
