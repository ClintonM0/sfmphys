### Changelog
Update 19 August 2013
* Fixed some errors in the sim script

Update 13 August 2013

* Updated to Python 2.7.5 (for the July 31 SFM update)
* Updated all guis to use PySide qt bindings
* Moved phys_simulate to the global scripts menu; it is no longer a "rig" script
* Started work on some fancy GUI things -- not included in this update, just thought I'd mention.

Update 2 May 2013

* Updated to Python 2.7 (for the May 1 SFM update)
* Added a "mass" attribute for rigid and soft bodies, accessible through the *element viewer*. The default of 1 should serve well enough for most props, but for exceptionally large or small props (or if you want to simulate, say, something like a seesaw) it's now there for you to adjust. See also: large cloth needs extra mass to scale well, so if you're working with large cloth and things pass through or break entirely, consider adjusting the mass.

Update 23 April 2013

* If you are updating to this version from a previous version, try to remove the files from the previous version to avoid any conflicts; there aren't be any specific problems that I am aware of, but just to be sure.
* bullet_server is no longer needed. Just run the scripts and go!
* better automatic rigging for ragdolls, and more configurable joint constraints
* soft-body physics, with an emphasis on cloth (and the possibility for some other limited applications)

Older versions

* Nyeh, I didn't have a changelog. And it's not all that interesting. Just pretend I started with the April 23 release if it makes any difference :P.

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
* Grab this repository with git, or download the .zip ("Download ZIP" button in the right margin)
* Extract and copy the "platform" and "sdktools" folders to [steamapps]/common/SourceFilmmaker/game. Choose to merge folders.

### How to use
* Start sfm, and set up your scene. Attach a rig_physics to any objects you want included in the simulation.
* The "shape" control works as follows: if value < 0.5 (slider on the left half), "box" is selected; if value > 0.5 (slider on the right half), "sphere" is selected.
* The "kinematic" control is "dynamic" for values < 0.5; "kinematic" for values > 0.5.
* The "center of mass" control currently does not function properly, and the "force" control will need some tweaking to be more useful (note that you can also rotate the "force" control to apply torque to an object).
* The "damping" controls determine how quickly objects lose momentum over time. If objects are shaking uncontrollably, try increasing the damping; if they are moving too slowly, try decreasing. The defaults are generally fine for rigidbodies; you may want to increase for ragdolls, and cloth physics will require tweaking on an individual basis.
* Select a period of time to simulate over in the motion editor (ie, with the floating modification layer). The simulation will not run if the time selection is infinite in either direction.
* Once the scene is set up, go to "Scripts" in the main menu bar and select "Run sfmphys Simulation"

### Some notes on ragdolls
* Animation with ragdolls is difficult since you have to use the physics handles. I'll add an option to use the model's normal bones for fully-kinematic objects in the future.
* Ropes use the positions of bones at the start of the time selection to determine how joints should line up. So for the best results, leave the model in its default position (ie, t-pose for ragdolls, straight line for ropes) and then animate any kinematic bones into position before the scene starts and give the sim a second to stabilize.

### Some notes on cloth
* You *need* a .physics.txt file to create cloth bodies. An example cloth model is included in the /usermod/models/narry/ folder. Another file, windrunner_cape.physics.txt is also included as an example of rigging a cloth model from DOTA 2. The "width" and "height" parameters are self-explanatory; the "boneformat" parameter is described in more detail at http://docs.python.org/2/library/string.html#format-examples. The script iterates each variable {0}, {1}, ..., {n} over the ranges provided in "formatranges" and creates a bone for each. The order of iteration is to increment {0} first, then {1}, etc. The cloth is assumed to always be a 2D plane with dimensions defined by the "width" and "height" parameters regardless of how many variables are in the "boneformat" string.
* To make kinematic cloth, open the rigged animation set in the Element Viewer and navigate to "Root Control Group -> children -> SoftBodies -> children -> (cloth name)" and open the node list. From there you can edit the masses of nodes (use 1 for dynamic and 0 for kinematic). If you're feeling adventurous, feel free to poke around the other parts of the physics rigs in the element viewer. There are some parameters there that I either didn't or couldn't turn into sliders for the rig.

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
Credit for the included example cloth model goes to OSFM member "Narry Gewman"  
