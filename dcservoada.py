from adafruit_servokit import ServoKit
from dcservo import DogCamServoBase
import time

# Don't export ServoLib
__all__ = ("DogCamServoAda")

# Bring in global instance
ServoLib = ServoKit(channels=16)

class DogCamServoAda(DogCamServoBase):
  def __init__(InName, InPin, InZeroAngle=0.0, InSteps=1.0, InLowerBounds=0.0, InUpperBounds=180.0, PulseWidthMin=1000, PulseWidthMax=2000):
    
    ServoLib.servo[InPin].actuation_range = UpperBounds
    ServoLib.servo[InPin].set_pulse_width_range(PulseWidthMin, PulseWidthMax)
    
    super().__init__(InName, InPin, InZeroAngle=ZeroAngle, InSteps=Steps, InLowerBounds=LowerBounds, InUpperBounds=UpperBounds)

  def _MoveToPosition(self, angle):
    print(f"{self.Name}: Moving to position {angle}")
    
    ServoLib.servo[self.Pin].angle = angle
    time.sleep(1)
    
