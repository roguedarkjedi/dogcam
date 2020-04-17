# dogcam

The controller software used for the current dog camera that's used on stream.

## Features:
---------------
* Servo motor controllers with stepping
* HTML web interface for controlling the servos easily via a browser (includes a "nice" html page!)
* Websocket server controllers for pushing commands directly to the controllers (allowing for other methods of control)
* Highly configurable
* Smallish in size, quick to deploy

## How to use

Once physically built and installed, run main.py. The servo web interface is accessible on the Pi's IP address on port 8080. This repro contains only the basic drivers and movement controllers, and does not do computer vision (see the AI project for this). The websocket server is located at the IP address on port 5867.

## Servo Control

This project supports moving the servos directly from the GPIO or using a [servo hat](https://www.adafruit.com/product/2327) for the Raspberry Pi. If it's decided to use the servo hat, make sure to mark all servos in the configs as having a type of "ada". This will use ServoKit over the GPIO library.

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
* clamp_holed.stl

These above parts are licensed under the [Creative Commons - Attribution - Share Alike license](https://creativecommons.org/licenses/by-sa/3.0/) and are under different license terms than the code.

Servos used:

* TowerPro MG90D (base)
* Futaba S3004
