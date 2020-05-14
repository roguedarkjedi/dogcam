from adafruit_servokit import ServoKit
from dcservo import DogCamServoBase

# Don't export ServoLib
__all__ = ("DogCamServoAda")

# Bring in global instance
ServoLib = ServoKit(channels=16)

class DogCamServoAda(DogCamServoBase):
  def __init__(self, InName, InPin, ZeroAngle=0.0, Steps=1.0, LowerBounds=0.0, UpperBounds=180.0, PulseWidthMin=1000, PulseWidthMax=2000):

    ServoLib.servo[InPin].actuation_range = UpperBounds
    ServoLib.servo[InPin].set_pulse_width_range(PulseWidthMin, PulseWidthMax)

    super().__init__(InName, InPin, InZeroAngle=ZeroAngle, InSteps=Steps, InLowerBounds=LowerBounds, InUpperBounds=UpperBounds)

  def _MoveToPosition(self, angle):
    print(f"{self.Name}: Moving to position {angle}")
    try:
      ServoLib.servo[self.Pin].angle = angle
    except Exception as ex:
      print(f"{self.Name}: Could not move position to {angle}!\n{ex}")
