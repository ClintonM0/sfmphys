If you are updating to this version from a previous version, try to remove the files from the previous version to avoid any conflicts; there aren't be any specific problems that I am aware of, but just to be sure.

#SFM Physics Scripts
### What does this do?
* Incorporates physics simulation into SFM via python scripts
* Handles collision detection and response
* Can create physics-controlled, static, and kinematic bodies
* Can create ragdolls and ropes, assuming the source model is set up with proper hitboxes
* Can simulate cloth physics, given a properly set-up model
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

### How to use
* Start sfm, and set up your scene. Attach a rig_physics to any objects you want included in the simulation.
* The "shape" control works as follows: if value < 0.5 (slider on the left half), "box" is selected; if value > 0.5 (slider on the right half), "sphere" is selected.
* The "kinematic" control is "dynamic" for values < 0.5; "kinematic" for values > 0.5.
* The "center of mass" control currently does not function properly, and the "force" control will need some tweaking to be more useful (note that you can also rotate the "force" control to apply torque to an object).
* The "damping" controls determine how quickly objects lose momentum over time. If objects are shaking uncontrollably, try increasing the damping; if they are moving too slowly, try decreasing. The defaults are generally fine for rigidbodies; you may want to increase for ragdolls, and cloth physics will require tweaking on an individual basis.
* Select a period of time to simulate over in the motion editor (ie, with the floating modification layer). The simulation will not run if the time selection is infinite in either direction.
* Once the scene is set up, right-click any animation set and run "phys_simulate". The simulation might take a few seconds.
* To run a simulation again, just run "phys_simulate" again. There's no need to re-rig objects or to restart the server (the sim is reset automatically every time "phys_simulate" runs).

### Some notes on ragdolls etc.
* Animation with ragdolls is difficult since you have to use the physics handles. I'll add an option to use the model's normal bones for fully-kinematic objects in the future.
* Ropes use the positions of bones at the start of the time selection to determine how joints should line up. So for the best results, leave the model in its default position (ie, t-pose for ragdolls, straight line for ropes) and then animate any kinematic bones into position before the scene starts and give the sim a second to stabilize.

### Videos
Day 1 http://www.youtube.com/watch?v=LDMB95El9GA  
Day 2 http://www.youtube.com/watch?v=a99sJrXWOxo  
Day 3 http://www.youtube.com/watch?v=GtQ50YWORcA  
Day 5 http://www.youtube.com/watch?v=vyzgnJhkdeQ  
Day 5.5 http://www.youtube.com/watch?v=AyKmftF3ZX0  
Day whatever: http://www.youtube.com/watch?v=-GgTciTTUs8
Day whatever + 1: http://www.youtube.com/watch?v=6ELrKtixYog
Day cloth: http://www.youtube.com/watch?v=zY2TTc0GKh4
Day cloth2: http://www.youtube.com/watch?v=uy2ICpS0znw
Cloth Parameters Reference: http://www.youtube.com/watch?v=AxK6saPpbW8

This project uses the bullet physics library. Check out http://bulletphysics.org for more info.
The included python bindings for bullet are based on https://github.com/ousttrue/swigbullet
See the bindings plus modifications at https://github.com/btdavis/swig-bullet
