# dogcam

The controller software used for the current dog cam that powers the stream.

## How to use

Once physically built and installed, run main.py. The servo web interface is accessible on the Pi's IP address on port 8080. This repro contains only the basic drivers and movement controllers, and does not do automatic tracking. With additional work, automatic following is possible.

## Robotics

This repo includes the 3D model files used for this project. These have been modified for compatibility and modularity between the various parts used. 

This [project by apetrone](https://www.thingiverse.com/thing:242438): 

* middle_tier_preholed.stl
* lift_arm_holed.stl
* base.stl

This [project from metaform3d](https://www.thingiverse.com/thing:207404):

* servo_head.stl

This [project from Vicharian](https://www.thingiverse.com/thing:3317345):

* phone_mount_bar.stl
* clamp.stl

These above parts are licensed under the [Creative Commons - Attribution - Share Alike license](https://creativecommons.org/licenses/by-sa/3.0/) and are under different terms than the code provided.

Servos used:

* TowerPro MG90D (base)
* Futaba S3004
