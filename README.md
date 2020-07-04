# dogcam

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/6b37aa9b42a04808a9c091e0692f1e88)](https://app.codacy.com/manual/roguedarkjedi/dogcam?utm_source=github.com&utm_medium=referral&utm_content=roguedarkjedi/dogcam&utm_campaign=Badge_Grade_Settings)

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

* TowerPro MG90D (pan)
* [ANNIMOS DS3218MG](https://www.amazon.com/gp/product/B076CNKQX4/) (tilt)


## Improvements to this project

Hindsight is 20/20. If you take on dogcam for your own project, here's some changes that can be made that would totally improve the overall result:

* Fix the pan hat so that a servo horn fits properly into the existing groove. This would eliminate a lot of issues with precision when it comes to moving the pan servo.
* Use a different panoramic base servo, while the TowerPro is powerful enough, it is limited by a small turning angle. To switch servos would require a rework of the base model for space.
* Make the tilt arm easier to install (likely by shortening the servo horn). It is very hard to modify and fit onto the existing space.
* Make the control webpage less jank by actually bothering to write it correctly.
* Shorten the clamps used to hold the phone, they are slightly too large.
