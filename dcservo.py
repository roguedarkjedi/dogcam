import asyncio
import time

class DogCamServoBase():
  Name=""
  Pin=0
  
  def __init__(self, InName, InPin, InZeroAngle=0.0, InLowerBounds=0.0, InUpperBounds=180.0, InSteps=1.0):
    self.Name = InName.lower()
    self.Pin = InPin
    
    self._CurrentAngle = 0.0
    self._TargetAngle = 0.0
    self._ServoDelta = 0.0
    self._Steps = InSteps
    self._LowerBounds = InLowerBounds
    self._UpperBounds = InUpperBounds
    
    # The angle that we should set to when resetting
    self._ZeroAngle = InZeroAngle
    
    self.Reset()
    
    # Servo main loop
    self.ShouldLoop = True
    asyncio.get_event_loop().create_task(self.__ServoLoop())
    
    print(f"{self.Name}: ready for motion")
    
  def __del__(self):
    print(f"{self.Name}: Shutting off hardware")
    self.ShouldLoop = False
    self.Reset()
  
  # Must be overridden
  def _MoveToPosition(self, angle):
    print(f"{self.Name}: Unhandled Movement command!")
  
  
  def _SetTargetAngle(self, angle):
    if angle < self._LowerBounds:
      angle = self._LowerBounds
    elif angle > self._UpperBounds:
      angle = self._UpperBounds
      
    self._TargetAngle = angle
    self._ServoDelta = abs(self._CurrentAngle - angle) / self._Steps
    
  def MoveToRelativeAngle(self, angle):
    self._SetTargetAngle(self._CurrentAngle + angle)
    print(f"{self.Name}: Setting relative location to {self._CurrentAngle + angle}")

  def MoveToAbsoluteAngle(self, angle):
    if angle == self._ZeroAngle:
      self.Reset()
    else:
      self._MoveToPosition(angle)
      self._TargetAngle = self._CurrentAngle = angle
      print(f"{self.Name}: Moving to {angle}")
    
  def MoveToInterpAngle(self, angle):
    if angle == self._ZeroAngle:
      self._SetTargetAngle(self._ZeroAngle)
    else:
      self._SetTargetAngle(angle)

    print(f"{self.Name}: Moving location to {angle}")
    
  def GetCurrentAngle(self):
    return self._CurrentAngle
    
  def Reset(self, Smooth=False):
    if Smooth is True:
      self._SetTargetAngle(self._ZeroAngle)
    else:
      self._TargetAngle = self._CurrentAngle = self._ZeroAngle
      
      self._MoveToPosition(self._ZeroAngle)
      time.sleep(1)
      self._MoveToPosition(self._ZeroAngle)
    
    print(f"{self.Name}: reset")
    
  async def __InterpPosition(self, angle):
    self._CurrentAngle = angle
    self._MoveToPosition(self._CurrentAngle)

  async def __ServoLoop(self):
    while self.ShouldLoop is True:
      # We need to move
      if self._TargetAngle != self._CurrentAngle:
        AdjustedLoc = self._CurrentAngle
        if AdjustedLoc == 0.0:
          AdjustedLoc = 1.0
          
        # Determine where we should go
        if self._CurrentAngle > self._TargetAngle:
          Movement = self._CurrentAngle - self._ServoDelta
          WillOverShot = Movement <= self._TargetAngle
        else:
          Movement = self._CurrentAngle + self._ServoDelta
          WillOverShot = Movement >= self._TargetAngle
        
        print(f"{self.Name}: moving {Movement} to {self._TargetAngle}")

        if WillOverShot or self._TargetAngle < self._LowerBounds or self._TargetAngle > self._UpperBounds:
          print(f"{self.Name}: We there")
          self._ServoDelta = 0.0
          self._MoveToPosition(self._TargetAngle)
          self._TargetAngle = self._CurrentAngle = self._TargetAngle
        else:
          await self.__InterpPosition(Movement)

      await asyncio.sleep(0.2)
